# -*- coding: utf-8 -*-
"""إشعارات آبل (APNs) لتطبيق آيفون.

إشعار الويب لا يصل إلى تطبيق مغلّف، فالتطبيق يسجّل رمز جهازه لدى آبل
ويرسله إلى الخادم، والخادم يرسل التذكير اليومي عبر APNs.

التوثيق بمفتاح ‎.p8‎ واحد من حساب المطوّر (توثيق بالرمز، JWT بخوارزمية ES256)،
فلا شهادات تتجدّد كل سنة. وخدمة آبل لا تقبل إلا HTTP/2، ولذلك httpx.
"""
import json
import threading
import time

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from push import b64e

HOSTS = {'production': 'https://api.push.apple.com',
         'sandbox': 'https://api.sandbox.push.apple.com'}
# آبل ترفض رمزًا عمره فوق ساعة، وترفض تجديده أكثر من مرة كل عشرين دقيقة
TOKEN_AGE = 50 * 60
# رموز لا رجعة فيها: التطبيق حُذف، أو الرمز لا يخصّ هذا التطبيق
DEAD = {'Unregistered', 'BadDeviceToken', 'DeviceTokenNotForTopic'}


class Gone(Exception):
    """رمز جهاز لم يعد صالحًا: على المُستدعي حذفه."""


class Client:
    def __init__(self, key_pem, key_id, team_id, topic):
        # لوحة ريندر قد تحفظ المفتاح في سطر واحد بفواصل \n حرفية
        key_pem = key_pem.replace('\\n', '\n').strip().encode()
        self.key = serialization.load_pem_private_key(key_pem, password=None)
        self.key_id, self.team_id, self.topic = key_id, team_id, topic
        self._jwt, self._jwt_at = None, 0
        self._lock = threading.Lock()
        self._http = httpx.Client(http2=True, timeout=10)

    def _token(self):
        with self._lock:
            if not self._jwt or time.time() - self._jwt_at > TOKEN_AGE:
                now = int(time.time())
                head = b64e(json.dumps({'alg': 'ES256', 'kid': self.key_id},
                                       separators=(',', ':')).encode())
                body = b64e(json.dumps({'iss': self.team_id, 'iat': now},
                                       separators=(',', ':')).encode())
                signing_input = ('%s.%s' % (head, body)).encode('ascii')
                r, s = decode_dss_signature(self.key.sign(signing_input, ec.ECDSA(hashes.SHA256())))
                self._jwt = '%s.%s' % (signing_input.decode(),
                                       b64e(r.to_bytes(32, 'big') + s.to_bytes(32, 'big')))
                self._jwt_at = now
            return self._jwt

    def _post(self, token, body, env, collapse):
        headers = {'authorization': 'bearer ' + self._token(),
                   'apns-topic': self.topic,
                   'apns-push-type': 'alert',
                   'apns-priority': '10',
                   'apns-expiration': str(int(time.time()) + 12 * 3600)}
        if collapse:
            headers['apns-collapse-id'] = collapse[:64]
        r = self._http.post('%s/3/device/%s' % (HOSTS[env], token), content=body, headers=headers)
        reason = ''
        if r.status_code != 200:
            try:
                reason = r.json().get('reason', '')
            except ValueError:
                pass
            if reason in ('ExpiredProviderToken', 'InvalidProviderToken'):
                with self._lock:
                    self._jwt = None
        return r.status_code, reason

    def send(self, token, data, env='production'):
        """يرسل إشعارًا واحدًا ويرجّع البيئة التي قبلته.

        نسخ TestFlight والمتجر تأخذ رموزها من بيئة الإنتاج، والنسخ المبنيّة من
        Xcode مباشرةً من بيئة الاختبار. فإن رفضت إحداهما الرمز جُرّبت الأخرى،
        وتُحفظ التي قبلته للمرّات القادمة."""
        body = json.dumps({
            'aps': {'alert': {'title': data.get('title', ''), 'body': data.get('body', '')},
                    'sound': 'default', 'thread-id': data.get('tag', 'daily')},
            'url': data.get('url', '/'),
        }, ensure_ascii=False).encode('utf-8')
        status, reason = self._post(token, body, env, data.get('tag'))
        if status == 200:
            return env
        if reason == 'BadDeviceToken':
            other = 'sandbox' if env == 'production' else 'production'
            status, reason = self._post(token, body, other, data.get('tag'))
            if status == 200:
                return other
        if status == 410 or reason in DEAD:
            raise Gone(reason or str(status))
        raise RuntimeError('APNs %s %s' % (status, reason))
