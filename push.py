# -*- coding: utf-8 -*-
"""إرسال إشعارات الويب.

مكتوب على مكتبة cryptography وحدها، فلا حاجة إلى pywebpush ولا http-ece
(الأخيرة تفشل في البناء على إصدارات بايثون الحديثة).

المعايير المتّبعة:
    RFC 8291  تعمية حمولة إشعار الويب  (aes128gcm)
    RFC 8188  ترميز المحتوى aes128gcm
    RFC 8292  توثيق الخادم أمام خدمة الدفع (VAPID / ES256)
"""
import base64
import hashlib
import hmac
import json
import os
import struct
import time
import urllib.error
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CURVE = ec.SECP256R1()
RECORD_SIZE = 4096
DEFAULT_TTL = 12 * 3600


# ─────────────────────────────────── ترميز base64url بلا حشو
def b64e(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')


def b64d(txt):
    if isinstance(txt, str):
        txt = txt.encode('ascii')
    return base64.urlsafe_b64decode(txt + b'=' * (-len(txt) % 4))


def _hkdf(salt, ikm, info, length):
    """HKDF بخطوتيه. الأطوال المطلوبة هنا لا تتجاوز 32 بايت، فتكفي جولة توسيع واحدة."""
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    return hmac.new(prk, info + b'\x01', hashlib.sha256).digest()[:length]


# ─────────────────────────────────── المفاتيح
def _priv_from_raw(raw32):
    return ec.derive_private_key(int.from_bytes(raw32, 'big'), CURVE)


def _raw_public(private_key):
    return private_key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def generate_keys():
    """يولّد زوج مفاتيح VAPID ويرجّعه (سرّي، معلن) بترميز base64url."""
    priv = ec.generate_private_key(CURVE)
    raw = priv.private_numbers().private_value.to_bytes(32, 'big')
    return b64e(raw), b64e(_raw_public(priv))


def public_from_private(private_b64):
    return b64e(_raw_public(_priv_from_raw(b64d(private_b64))))


# ─────────────────────────────────── تعمية الحمولة
def encrypt(payload, p256dh, auth):
    """يعمّي الحمولة لمتصفّح بعينه ويرجّع جسم الطلب كاملًا."""
    ua_public_raw = b64d(p256dh)
    auth_secret = b64d(auth)
    ua_public = ec.EllipticCurvePublicKey.from_encoded_point(CURVE, ua_public_raw)

    as_private = ec.generate_private_key(CURVE)
    as_public_raw = _raw_public(as_private)
    shared = as_private.exchange(ec.ECDH(), ua_public)

    ikm = _hkdf(auth_secret, shared,
                b'WebPush: info\x00' + ua_public_raw + as_public_raw, 32)
    salt = os.urandom(16)
    cek = _hkdf(salt, ikm, b'Content-Encoding: aes128gcm\x00', 16)
    nonce = _hkdf(salt, ikm, b'Content-Encoding: nonce\x00', 12)

    # 0x02 تعني أن هذا آخر سِجلّ، وهي جزء من النص المعمّى لا من الترويسة
    body = AESGCM(cek).encrypt(nonce, payload + b'\x02', None)
    header = salt + struct.pack('!L', RECORD_SIZE) + bytes([len(as_public_raw)]) + as_public_raw
    return header + body


def decrypt(body, ua_private_b64, auth):
    """فكّ التعمية. لا يستخدمه التطبيق، وإنما الاختبارات للتحقّق من المطابقة."""
    salt, body = body[:16], body[16:]
    body = body[4:]                       # حجم السِجلّ
    idlen, body = body[0], body[1:]
    as_public_raw, ciphertext = body[:idlen], body[idlen:]

    ua_private = _priv_from_raw(b64d(ua_private_b64))
    ua_public_raw = _raw_public(ua_private)
    shared = ua_private.exchange(
        ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(CURVE, as_public_raw))

    ikm = _hkdf(b64d(auth), shared,
                b'WebPush: info\x00' + ua_public_raw + as_public_raw, 32)
    cek = _hkdf(salt, ikm, b'Content-Encoding: aes128gcm\x00', 16)
    nonce = _hkdf(salt, ikm, b'Content-Encoding: nonce\x00', 12)
    return AESGCM(cek).decrypt(nonce, ciphertext, None).rstrip(b'\x02').rstrip(b'\x00')


# ─────────────────────────────────── توثيق الخادم أمام خدمة الدفع
def vapid_headers(endpoint, private_b64, public_b64, subject, hours=12):
    origin = urllib.parse.urlsplit(endpoint)
    aud = '%s://%s' % (origin.scheme, origin.netloc)
    head = b64e(json.dumps({'typ': 'JWT', 'alg': 'ES256'}, separators=(',', ':')).encode())
    body = b64e(json.dumps({'aud': aud, 'exp': int(time.time()) + hours * 3600,
                            'sub': subject}, separators=(',', ':')).encode())
    signing_input = ('%s.%s' % (head, body)).encode('ascii')
    der = _priv_from_raw(b64d(private_b64)).sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    token = '%s.%s' % (signing_input.decode(), b64e(r.to_bytes(32, 'big') + s.to_bytes(32, 'big')))
    return {'Authorization': 'vapid t=%s, k=%s' % (token, public_b64)}


# ─────────────────────────────────── الإرسال
class PushGone(Exception):
    """اشتراك ملغى أو منتهٍ: على المُستدعي حذفه من قاعدة البيانات."""


def send(subscription, data, private_b64, public_b64, subject,
         ttl=DEFAULT_TTL, timeout=10):
    """يرسل إشعارًا واحدًا. يرجّع رمز حالة HTTP، ويرفع PushGone للاشتراك الميّت."""
    endpoint = subscription['endpoint']
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    body = encrypt(payload, subscription['p256dh'], subscription['auth'])

    headers = {'Content-Encoding': 'aes128gcm',
               'Content-Type': 'application/octet-stream',
               'Content-Length': str(len(body)),
               'TTL': str(ttl),
               'Urgency': 'normal'}
    headers.update(vapid_headers(endpoint, private_b64, public_b64, subject))

    req = urllib.request.Request(endpoint, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):        # الاشتراك لم يعد صالحًا
            raise PushGone(str(exc.code))
        raise
