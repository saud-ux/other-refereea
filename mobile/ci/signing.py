# -*- coding: utf-8 -*-
"""توقيع تطبيق آيفون على خادم البناء، بلا جهاز ماك وبلا شهادات محفوظة.

كل بناء ينشئ عبر واجهة App Store Connect شهادة توزيع مؤقّتة وملف تعريف
للمتجر، ويوقّع بهما، ثم يلغيهما بعد الرفع. التطبيقات المرفوعة إلى TestFlight
والمتجر لا تتأثّر بإلغاء الشهادة، لأن آبل تعيد توقيعها بنفسها. والحدّ الأعلى
لشهادات التوزيع ثلاث، فلا تتراكم شهادة مع كل بناء.

السرّ الوحيد المطلوب مفتاح واجهة App Store Connect بدور Admin.

    python signing.py prepare <مجلد العمل>   قبل البناء
    python signing.py cleanup <مجلد العمل>   بعده، حتى لو فشل

المتغيّرات: ASC_KEY_ID و ASC_ISSUER_ID و ASC_KEY_P8 و APPLE_TEAM_ID و BUNDLE_ID
و APP_VERSION و BUILD_NUMBER و RUN_ID، و PBXPROJ مسار ملف المشروع.
"""
import base64
import json
import os
import plistlib
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

API = 'https://api.appstoreconnect.apple.com/v1'
PREFIX = 'LOTG CI'           # اسم ملفات التعريف المؤقّتة، ومنه تُعرف بقاياها


def env(name):
    v = os.environ.get(name, '').strip()
    if not v:
        sys.exit('::error::المتغيّر %s غير مضبوط. أضفه في أسرار المستودع.' % name)
    return v


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode()


def jwt():
    key = serialization.load_pem_private_key(env('ASC_KEY_P8').replace('\\n', '\n').encode(), None)
    now = int(time.time())
    head = b64u(json.dumps({'alg': 'ES256', 'kid': env('ASC_KEY_ID'), 'typ': 'JWT'}).encode())
    body = b64u(json.dumps({'iss': env('ASC_ISSUER_ID'), 'iat': now, 'exp': now + 1100,
                            'aud': 'appstoreconnect-v1'}).encode())
    r, s = decode_dss_signature(key.sign(('%s.%s' % (head, body)).encode(), ec.ECDSA(hashes.SHA256())))
    return '%s.%s.%s' % (head, body, b64u(r.to_bytes(32, 'big') + s.to_bytes(32, 'big')))


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + jwt(),
                                          'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors='replace')
        hint = {401: 'المفتاح أو معرّف المُصدِر (Issuer ID) غير صحيح.',
                403: 'دور مفتاح الواجهة يجب أن يكون Admin.',
                409: 'تعارض: قد تكون بلغت الحدّ الأعلى لشهادات التوزيع (ثلاث). ألغِ واحدة من بوّابة المطوّر.'}
        print('::error::%s %s ← %s\n%s\n%s' % (method, path, exc.code, hint.get(exc.code, ''), detail))
        raise


def bundle_id():
    ident = env('BUNDLE_ID')
    found = call('GET', '/bundleIds?filter[identifier]=%s&limit=50' % ident)['data']
    found = [b for b in found if b['attributes']['identifier'] == ident]
    if found:
        bid = found[0]['id']
    else:
        print('تسجيل المعرّف %s' % ident)
        bid = call('POST', '/bundleIds', {'data': {'type': 'bundleIds', 'attributes': {
            'identifier': ident, 'name': 'LOTG', 'platform': 'IOS'}}})['data']['id']
    caps = call('GET', '/bundleIds/%s/bundleIdCapabilities' % bid)['data']
    if not any(c['attributes']['capabilityType'] == 'PUSH_NOTIFICATIONS' for c in caps):
        print('تفعيل الإشعارات للمعرّف')
        call('POST', '/bundleIdCapabilities', {'data': {
            'type': 'bundleIdCapabilities',
            'attributes': {'capabilityType': 'PUSH_NOTIFICATIONS'},
            'relationships': {'bundleId': {'data': {'type': 'bundleIds', 'id': bid}}}}})
    return bid


def sweep(bid):
    """يلغي بقايا بناء سابق انقطع قبل التنظيف: ملفاته وشهاداته وحدها."""
    for p in call('GET', '/bundleIds/%s/profiles?limit=200' % bid)['data']:
        if not p['attributes']['name'].startswith(PREFIX):
            continue
        for c in call('GET', '/profiles/%s/certificates' % p['id'])['data']:
            print('إلغاء شهادة مؤقّتة سابقة %s' % c['id'])
            call('DELETE', '/certificates/%s' % c['id'])
        try:
            call('DELETE', '/profiles/%s' % p['id'])
        except urllib.error.HTTPError:
            pass        # إلغاء الشهادة قد يحذف الملف معها


def sh(*args, **kw):
    return subprocess.run(args, check=True, **kw)


def keychain(work, p12, p12_pass):
    kc = os.path.join(work, 'ci.keychain-db')
    kc_pass = secrets.token_hex(16)
    sh('security', 'create-keychain', '-p', kc_pass, kc)
    sh('security', 'set-keychain-settings', '-lut', '21600', kc)
    sh('security', 'unlock-keychain', '-p', kc_pass, kc)
    wwdr = os.path.join(work, 'AppleWWDRCAG3.cer')
    urllib.request.urlretrieve('https://www.apple.com/certificateauthority/AppleWWDRCAG3.cer', wwdr)
    sh('security', 'import', wwdr, '-k', kc, '-t', 'cert', '-f', 'x509', '-A')
    sh('security', 'import', p12, '-k', kc, '-P', p12_pass, '-f', 'pkcs12', '-A',
       '-T', '/usr/bin/codesign', '-T', '/usr/bin/security')
    sh('security', 'set-key-partition-list', '-S', 'apple-tool:,apple:,codesign:', '-s',
       '-k', kc_pass, kc, stdout=subprocess.DEVNULL)
    current = subprocess.run(['security', 'list-keychains', '-d', 'user'],
                             capture_output=True, text=True).stdout.split()
    sh('security', 'list-keychains', '-d', 'user', '-s', kc, *[c.strip('"') for c in current])
    return kc


def patch_project(profile_name, kc):
    """التوقيع اليدوي يُكتب في إعداد هدف التطبيق وحده. لو مُرّر من سطر الأوامر
    لطُبّق على حزم Swift أيضًا ففشل البناء. التعديل على نسخة البناء فقط."""
    path = env('PBXPROJ')
    s = open(path, encoding='utf-8').read()
    team, version, build = env('APPLE_TEAM_ID'), env('APP_VERSION'), env('BUILD_NUMBER')

    def fix(m):
        block = m.group(0)
        if 'PRODUCT_BUNDLE_IDENTIFIER = %s;' % env('BUNDLE_ID') not in block:
            return block
        block = block.replace('CODE_SIGN_STYLE = Automatic;', 'CODE_SIGN_STYLE = Manual;')
        block = re.sub(r'CURRENT_PROJECT_VERSION = [^;]+;', 'CURRENT_PROJECT_VERSION = %s;' % build, block)
        block = re.sub(r'MARKETING_VERSION = [^;]+;', 'MARKETING_VERSION = %s;' % version, block)
        return block.replace('buildSettings = {', 'buildSettings = {\n%s' % '\n'.join(
            '\t\t\t\t%s;' % x for x in (
                'CODE_SIGN_IDENTITY = "Apple Distribution"',
                '"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "Apple Distribution"',
                'DEVELOPMENT_TEAM = %s' % team,
                'PROVISIONING_PROFILE_SPECIFIER = "%s"' % profile_name,
                'OTHER_CODE_SIGN_FLAGS = "--keychain %s"' % kc)), 1)

    s2 = re.sub(r'isa = XCBuildConfiguration;\s*(?:baseConfigurationReference = [^;]+;\s*)?buildSettings = \{.*?\n\t\t\t\};',
                fix, s, flags=re.S)
    if s2.count('CODE_SIGN_STYLE = Manual;') != 2:
        sys.exit('::error::تعذّر ضبط التوقيع في ملف المشروع')
    open(path, 'w', encoding='utf-8').write(s2)

    # ملف تعريف المتجر يحمل بيئة الإشعارات production، فتُطابَق بها
    ent = os.path.join(os.path.dirname(os.path.dirname(path)), 'App', 'App.entitlements')
    with open(ent, 'rb') as f:
        e = plistlib.load(f)
    e['aps-environment'] = 'production'
    with open(ent, 'wb') as f:
        plistlib.dump(e, f)


def prepare(work):
    os.makedirs(work, exist_ok=True)
    bid = bundle_id()
    sweep(bid)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    csr = (x509.CertificateSigningRequestBuilder()
           .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, PREFIX)]))
           .sign(key, hashes.SHA256()))
    cert = call('POST', '/certificates', {'data': {'type': 'certificates', 'attributes': {
        'certificateType': 'DISTRIBUTION',
        'csrContent': csr.public_bytes(serialization.Encoding.PEM).decode()}}})['data']
    state = {'certificate': cert['id']}
    json.dump(state, open(os.path.join(work, 'state.json'), 'w'))

    name = '%s %s' % (PREFIX, env('RUN_ID'))
    prof = call('POST', '/profiles', {'data': {
        'type': 'profiles',
        'attributes': {'name': name, 'profileType': 'IOS_APP_STORE'},
        'relationships': {
            'bundleId': {'data': {'type': 'bundleIds', 'id': bid}},
            'certificates': {'data': [{'type': 'certificates', 'id': cert['id']}]}}}})['data']
    state['profile'] = prof['id']
    json.dump(state, open(os.path.join(work, 'state.json'), 'w'))

    # ملف التعريف حيث يبحث عنه Xcode، في مساره القديم والجديد
    raw = base64.b64decode(prof['attributes']['profileContent'])
    uuid = prof['attributes']['uuid']
    for d in ('~/Library/MobileDevice/Provisioning Profiles',
              '~/Library/Developer/Xcode/UserData/Provisioning Profiles'):
        d = os.path.expanduser(d)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, uuid + '.mobileprovision'), 'wb').write(raw)

    # تعمية p12 القديمة، فأداة security في ماك لا تقرأ الحديثة دائمًا
    p12_pass = secrets.token_hex(16)
    enc = (serialization.PrivateFormat.PKCS12.encryption_builder()
           .kdf_rounds(50000).key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
           .hmac_hash(hashes.SHA1()).build(p12_pass.encode()))
    der = base64.b64decode(cert['attributes']['certificateContent'])
    p12 = os.path.join(work, 'dist.p12')
    open(p12, 'wb').write(pkcs12.serialize_key_and_certificates(
        PREFIX.encode(), key, x509.load_der_x509_certificate(der), None, enc))
    kc = keychain(work, p12, p12_pass)
    os.remove(p12)

    patch_project(name, kc)
    with open(os.path.join(work, 'ExportOptions.plist'), 'wb') as f:
        plistlib.dump({
            'method': 'app-store-connect',
            'destination': 'upload',
            'teamID': env('APPLE_TEAM_ID'),
            'signingStyle': 'manual',
            'signingCertificate': 'Apple Distribution',
            'provisioningProfiles': {env('BUNDLE_ID'): name},
            'uploadSymbols': True,
            'manageAppVersionAndBuildNumber': False,
        }, f)
    print('جاهز: الشهادة %s وملف التعريف «%s»' % (cert['id'], name))


def cleanup(work):
    path = os.path.join(work, 'state.json')
    state = json.load(open(path)) if os.path.exists(path) else {}
    if state.get('certificate'):
        try:
            call('DELETE', '/certificates/%s' % state['certificate'])
            print('أُلغيت الشهادة المؤقّتة')
        except urllib.error.HTTPError:
            pass
    if state.get('profile'):
        try:
            call('DELETE', '/profiles/%s' % state['profile'])
        except urllib.error.HTTPError:
            pass        # يُحذف عادةً مع إلغاء شهادته
    kc = os.path.join(work, 'ci.keychain-db')
    if os.path.exists(kc):
        subprocess.run(['security', 'delete-keychain', kc])


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('prepare', 'cleanup'):
        sys.exit(__doc__)
    {'prepare': prepare, 'cleanup': cleanup}[sys.argv[1]](sys.argv[2])
