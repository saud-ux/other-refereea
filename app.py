# -*- coding: utf-8 -*-
"""قوانين اللعبة.

تطبيق فلاسك بملفات في جذر المستودع فقط:
    app.py        الخادم وواجهات البيانات
    questions.py  بنك الأسئلة
    ui.py         الواجهة (صفحة واحدة)
"""

import json
import os
import re
import random
import time
from collections import defaultdict
from datetime import date, datetime, timedelta

from flask import Flask, Response, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from werkzeug.security import check_password_hash, generate_password_hash

import questions as QB
import ui

# ─────────────────────────────────────────────────────────── الإعداد
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-change-me')

db_url = os.environ.get('DATABASE_URL', 'sqlite:///lotg.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif db_url.startswith('postgresql://') and '+psycopg' not in db_url:
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# يسمح بمشاركة قاعدة بيانات واحدة مع تطبيق آخر بوضع جداول هذا التطبيق
# في مخطّط (schema) مستقل، فلا تتصادم أسماء الجداول.
DB_SCHEMA = os.environ.get('DB_SCHEMA', '').strip()
if DB_SCHEMA and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}', DB_SCHEMA):
    raise SystemExit('DB_SCHEMA غير صالح: يجب أن يكون معرّفًا بسيطًا بالحروف والأرقام والشرطة السفلية.')

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,     # يتخلّص من الاتصالات الميتة بعد سبات القاعدة
    'pool_recycle': 280,       # قواعد البيانات المجانية تقطع الاتصالات الخاملة
    'pool_size': 3,
    'max_overflow': 2,
}
# نسمّي المخطّط صراحةً على الجداول بدل الاعتماد على search_path، فيعمل الربط
# مع الاتصال المباشر ومع وسطاء الاتصال (pooler) في كلا وضعيهما.
_USE_SCHEMA = bool(DB_SCHEMA) and db_url.startswith('postgresql')

if db_url.startswith('postgresql'):
    STORAGE = 'postgresql' + (' مخطّط %s' % DB_SCHEMA if _USE_SCHEMA else '')
    STORAGE_PERSISTENT = True
else:
    STORAGE = 'sqlite'
    STORAGE_PERSISTENT = False   # ملف داخل الحاوية يُمحى عند كل إعادة تشغيل

_secure_default = '1' if os.environ.get('RENDER') else '0'
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE', _secure_default) == '1',
    PERMANENT_SESSION_LIFETIME=timedelta(days=60),
    JSON_AS_ASCII=False,
)
app.json.ensure_ascii = False

db = SQLAlchemy(app, metadata=MetaData(schema=DB_SCHEMA) if _USE_SCHEMA else MetaData())


# ─────────────────────────────────────────────────────────── النماذج
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    pin_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(60))
    test_minutes = db.Column(db.Integer, default=10)
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    public = db.Column(db.Boolean, default=True)
    last_active = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def name(self):
        return self.display_name or self.username


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    qid = db.Column(db.String(32), nullable=False, index=True)
    wrong_count = db.Column(db.Integer, default=0)
    correct_streak = db.Column(db.Integer, default=0)
    seen_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    mastered = db.Column(db.Boolean, default=False)
    bookmarked = db.Column(db.Boolean, default=False)
    next_due = db.Column(db.Date, nullable=True)
    last_answer = db.Column(db.String(200), nullable=True)
    last_correct = db.Column(db.Boolean, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'qid', name='uq_user_q'),)


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    scope = db.Column(db.String(60), nullable=False)
    mode = db.Column(db.String(20), default='mixed')
    seconds_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    day = db.Column(db.Date, nullable=False, index=True)
    answers = db.Column(db.Integer, default=0)
    correct = db.Column(db.Integer, default=0)
    daily_qid = db.Column(db.String(32))      # سؤال اليوم المثبّت لهذا المستخدم
    __table_args__ = (db.UniqueConstraint('user_id', 'day', name='uq_user_day'),)


# ─────────────────────────────────── ترقية بنية قاعدة بيانات قائمة
NEW_COLUMNS = {
    'user': {'display_name': 'VARCHAR(60)', 'best_streak': 'INTEGER DEFAULT 0',
             'public': 'BOOLEAN DEFAULT TRUE'},
    'progress': {'seen_count': 'INTEGER DEFAULT 0', 'correct_count': 'INTEGER DEFAULT 0',
                 'bookmarked': 'BOOLEAN DEFAULT FALSE'},
    'test_result': {'mode': "VARCHAR(20) DEFAULT 'mixed'"},
    'activity': {'daily_qid': 'VARCHAR(32)'},
}


def _q(table):
    """اسم الجدول مؤهَّلًا بالمخطّط عند استخدامه."""
    return '"%s"."%s"' % (DB_SCHEMA, table) if _USE_SCHEMA else '"%s"' % table


def ensure_schema():
    """يضيف الأعمدة الجديدة إلى جداول موجودة مسبقًا (create_all لا يعدّل الجداول)."""
    insp = db.inspect(db.engine)
    sch = DB_SCHEMA if _USE_SCHEMA else None
    tables = set(insp.get_table_names(schema=sch))
    added = False
    for table, cols in NEW_COLUMNS.items():
        if table not in tables:
            continue
        have = {c['name'] for c in insp.get_columns(table, schema=sch)}
        for col, ddl in cols.items():
            if col in have:
                continue
            try:
                db.session.execute(db.text('ALTER TABLE %s ADD COLUMN %s %s' % (_q(table), col, ddl)))
                db.session.commit()
                added = True
                app.logger.info('added column %s.%s', table, col)
            except Exception as exc:  # عمود موجود أو صلاحيات ناقصة
                db.session.rollback()
                app.logger.warning('skip column %s.%s: %s', table, col, exc)
    if added:          # التعبئة تلزم مرة واحدة فقط بعد الترقية، لا في كل إقلاع
        backfill()


BACKFILL = [
    # الصفوف القديمة لا تحمل عدّادات المشاهدة، فنشتقّها من البيانات المتاحة
    '''UPDATE {progress}
         SET seen_count = CASE WHEN COALESCE(wrong_count,0)+COALESCE(correct_streak,0) > 0
                               THEN COALESCE(wrong_count,0)+COALESCE(correct_streak,0) ELSE 1 END,
             correct_count = COALESCE(correct_streak,0)
       WHERE COALESCE(seen_count,0) = 0
         AND (COALESCE(wrong_count,0) > 0 OR COALESCE(correct_streak,0) > 0
              OR last_correct IS NOT NULL)''',
    'UPDATE {progress} SET bookmarked = FALSE WHERE bookmarked IS NULL',
    'UPDATE {user} SET best_streak = streak WHERE COALESCE(best_streak,0) < COALESCE(streak,0)',
    'UPDATE {user} SET public = TRUE WHERE public IS NULL',
    "UPDATE {test_result} SET mode = 'mixed' WHERE mode IS NULL",
]


def backfill():
    """يملأ الأعمدة الجديدة للصفوف التي أُنشئت بالنسخة السابقة من التطبيق."""
    names = {t: _q(t) for t in ('progress', 'user', 'test_result')}
    for sql in BACKFILL:
        try:
            db.session.execute(db.text(sql.format(**names)))
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.warning('backfill skipped: %s', exc)


_schema_ready = False
_last_try = 0.0


def init_db(force=False):
    """يجهّز الجداول. لا يُسقِط التطبيق إذا كانت القاعدة نائمة أو غير متاحة
    لحظة الإقلاع، بل يعيد المحاولة عند أول طلب لاحق."""
    global _schema_ready, _last_try
    if _schema_ready and not force:
        return True
    now = time.time()
    if not force and now - _last_try < 10:
        return False
    _last_try = now
    try:
        if _USE_SCHEMA:
            db.session.execute(db.text('CREATE SCHEMA IF NOT EXISTS "%s"' % DB_SCHEMA))
            db.session.commit()
        db.create_all()
        ensure_schema()
        _schema_ready = True
        app.logger.info('قاعدة البيانات جاهزة، التخزين: %s', STORAGE)
        if not STORAGE_PERSISTENT:
            app.logger.warning(
                'تحذير: التخزين مؤقّت داخل الحاوية وسيُمحى عند إعادة التشغيل. '
                'اضبط DATABASE_URL على قاعدة بيانات دائمة.')
    except Exception as exc:
        db.session.rollback()
        app.logger.error('تعذّر تجهيز قاعدة البيانات، ستُعاد المحاولة: %s', exc)
    return _schema_ready


@app.before_request
def _lazy_init():
    if not _schema_ready:
        init_db()


with app.app_context():
    init_db()
    if app.config['SECRET_KEY'] == 'dev-change-me' and os.environ.get('RENDER'):
        app.logger.warning('SECRET_KEY غير مضبوط في بيئة الإنتاج!')


# ─────────────────────────────────────────────────────────── أدوات
def current_user():
    uid = session.get('uid')
    return db.session.get(User, uid) if uid else None


def need_user():
    u = current_user()
    if not u:
        return None, (jsonify(error='انتهت الجلسة، سجّل الدخول من جديد.'), 401)
    return u, None


def touch_streak(u):
    today = date.today()
    if u.last_active == today:
        return
    if u.last_active == today - timedelta(days=1):
        u.streak = (u.streak or 0) + 1
    else:
        u.streak = 1
    u.best_streak = max(u.best_streak or 0, u.streak)
    u.last_active = today
    db.session.commit()


def progress_map(u):
    return {p.qid: p for p in Progress.query.filter_by(user_id=u.id).all()}


def today_activity(u):
    """صف نشاط اليوم، يُنشأ إن لم يكن موجودًا."""
    today = date.today()
    a = Activity.query.filter_by(user_id=u.id, day=today).first()
    if not a:
        a = Activity(user_id=u.id, day=today, answers=0, correct=0)
        db.session.add(a)
        db.session.flush()
    return a


def bump_activity(u, correct):
    a = today_activity(u)
    a.answers = (a.answers or 0) + 1
    a.correct = (a.correct or 0) + (1 if correct else 0)


SPACING = [2, 5, 9]


def record_answer(u, qid, choice):
    """يسجّل إجابة ويحدّث جدولة المراجعة المتباعدة. يرجع (صحيحة؟, السؤال)."""
    q = QB.QMAP[qid]
    try:
        choice = int(choice)
    except (TypeError, ValueError):
        choice = -1
    correct = 0 <= choice < len(q['options']) and choice == q['a']

    p = Progress.query.filter_by(user_id=u.id, qid=qid).first()
    if not p:
        p = Progress(user_id=u.id, qid=qid, wrong_count=0, correct_streak=0,
                     seen_count=0, correct_count=0, mastered=False, bookmarked=False)
        db.session.add(p)

    p.seen_count = (p.seen_count or 0) + 1
    p.last_answer = q['options'][choice] if 0 <= choice < len(q['options']) else 'لم يُجب'
    p.last_correct = correct

    today = date.today()
    if correct:
        p.correct_count = (p.correct_count or 0) + 1
        p.correct_streak = (p.correct_streak or 0) + 1
        if not p.wrong_count:
            p.mastered, p.next_due = True, None
        elif p.correct_streak >= 3:
            p.mastered, p.next_due = True, None
        else:
            p.next_due = today + timedelta(days=SPACING[min(p.correct_streak - 1, 2)])
    else:
        p.wrong_count = (p.wrong_count or 0) + 1
        p.correct_streak = 0
        p.mastered = False
        p.next_due = today + timedelta(days=1 if p.wrong_count >= 2 else 2)

    bump_activity(u, correct)
    db.session.commit()
    return correct, q


def was_seen(p):
    """هل أُجيب عن السؤال؟ يشمل الصفوف القديمة التي لا تحمل عدّاد مشاهدة."""
    return bool(p) and bool((p.seen_count or 0) or (p.wrong_count or 0)
                            or (p.correct_streak or 0) or p.last_correct is not None)


def status_of(p):
    if not was_seen(p):
        return 'unseen'
    if p.mastered:
        return 'mastered'
    if p.wrong_count:
        return 'wrong'
    return 'seen'


def priority(p, today):
    """أصغر = أولى بالعرض."""
    if not was_seen(p):
        return 1                      # لم يُحلّ بعد
    if p.mastered:
        return 4
    if p.next_due and p.next_due <= today:
        return 0                      # حان موعد مراجعته
    if p.wrong_count:
        return 2
    return 3


def filtered(scope, filt, search, pmap):
    out = QB.in_scope(scope)
    if search:
        s = search.strip()
        if s:
            out = [q for q in out if s in q['q'] or s in q['topic'] or s in q['category']]
    if filt and filt != 'all':
        if filt == 'saved':
            out = [q for q in out if pmap.get(q['id']) and pmap[q['id']].bookmarked]
        else:
            out = [q for q in out if status_of(pmap.get(q['id'])) == filt]
    return out


def user_stats(u, pmap=None):
    pmap = pmap if pmap is not None else progress_map(u)
    today = date.today()
    seen = sum(p.seen_count or 0 for p in pmap.values())
    ok = sum(p.correct_count or 0 for p in pmap.values())
    mastered = sum(1 for p in pmap.values() if p.mastered)
    wrong = sum(1 for p in pmap.values() if not p.mastered and (p.wrong_count or 0) > 0)
    due = sum(1 for p in pmap.values() if not p.mastered and p.next_due and p.next_due <= today)
    best = db.session.query(TestResult).filter_by(user_id=u.id) \
        .order_by(TestResult.score.desc(), TestResult.total.desc()).first()
    return {
        'streak': u.streak or 0, 'best_streak': u.best_streak or 0,
        'mastered': mastered, 'wrong': wrong, 'due': due,
        'answered': seen, 'accuracy': round(ok / seen * 100, 1) if seen else 0.0,
        'total_questions': QB.TOTAL, 'laws': len(QB.LAWS),
        'tests': TestResult.query.filter_by(user_id=u.id).count(),
        'best_score': best.score if best else None,
        'best_total': best.total if best else None,
    }


def ago(dt):
    d = (datetime.utcnow() - dt).days
    if d <= 0:
        return 'اليوم'
    if d == 1:
        return 'أمس'
    if d == 2:
        return 'قبل يومين'
    if d < 11:
        return 'قبل %d أيام' % d
    if d < 30:
        return 'قبل %d يومًا' % d
    m = d // 30
    return 'قبل شهر' if m == 1 else 'قبل %d أشهر' % m


# ─────────────────────────────────────────────── حد لمحاولات الدخول
_attempts = defaultdict(list)
MAX_TRIES, WINDOW = 12, 300


def client_ip():
    fwd = request.headers.get('X-Forwarded-For', '')
    return (fwd.split(',')[0].strip() if fwd else (request.remote_addr or '?'))


def rate_limited(key):
    now = time.time()
    hits = [t for t in _attempts[key] if now - t < WINDOW]
    _attempts[key] = hits
    if len(hits) >= MAX_TRIES:
        return True
    hits.append(now)
    return False


# ─────────────────────────────────────────────────────────── الصفحات
@app.get('/')
def index():
    return Response(ui.INDEX_HTML, mimetype='text/html; charset=utf-8')


@app.get('/manifest.webmanifest')
def manifest():
    return Response(json.dumps(ui.MANIFEST, ensure_ascii=False),
                    mimetype='application/manifest+json; charset=utf-8')


@app.get('/sw.js')
def service_worker():
    r = Response(ui.SW_JS, mimetype='application/javascript; charset=utf-8')
    r.headers['Cache-Control'] = 'no-cache'
    return r


@app.get('/icon.svg')
def icon():
    r = Response(ui.ICON_SVG, mimetype='image/svg+xml')
    r.headers['Cache-Control'] = 'public, max-age=86400'
    return r


@app.get('/health')
def health():
    """فحص خفيف يصلح لخدمات المراقبة: يلمس قاعدة البيانات ليمنع سباتها،
    ويعيد 200 دائمًا حتى لا توقف منصّة الاستضافة الخدمة عند تعثّر القاعدة."""
    ok = True
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db.session.rollback()
        ok = False
    r = jsonify(status='ok', db=ok, questions=QB.TOTAL,
                storage=STORAGE, persistent=STORAGE_PERSISTENT)
    r.headers['Cache-Control'] = 'no-store'
    return r, 200


# ─────────────────────────────────────────────────────────── الحساب
@app.post('/api/register')
def register():
    if rate_limited('reg|' + client_ip()):
        return jsonify(error='محاولات كثيرة. انتظر بضع دقائق ثم أعد المحاولة.'), 429
    d = request.get_json(silent=True) or {}
    username = (d.get('username') or '').strip()
    pin = str(d.get('pin') or '')
    name = (d.get('display_name') or '').strip()[:60]
    if len(username) < 3 or len(username) > 40:
        return jsonify(error='اسم المستخدم من 3 إلى 40 حرفًا.'), 400
    if not (4 <= len(pin) <= 8) or not pin.isdigit():
        return jsonify(error='كلمة المرور من 4 إلى 8 أرقام.'), 400
    if User.query.filter_by(username=username).first():
        return jsonify(error='اسم المستخدم مستخدم بالفعل.'), 409
    u = User(username=username, pin_hash=generate_password_hash(pin),
             display_name=name or None, public=True, streak=0, best_streak=0)
    db.session.add(u)
    db.session.commit()
    session.permanent = True
    session['uid'] = u.id
    touch_streak(u)
    return jsonify(ok=True)


@app.post('/api/login')
def login():
    d = request.get_json(silent=True) or {}
    username = (d.get('username') or '').strip()
    pin = str(d.get('pin') or '')
    key = client_ip() + '|' + username.lower()
    if rate_limited(key):
        return jsonify(error='محاولات كثيرة. انتظر بضع دقائق ثم أعد المحاولة.'), 429
    u = User.query.filter_by(username=username).first()
    if not u or not check_password_hash(u.pin_hash, pin):
        return jsonify(error='اسم المستخدم أو كلمة المرور غير صحيحة.'), 401
    _attempts.pop(key, None)
    session.permanent = True
    session['uid'] = u.id
    touch_streak(u)
    return jsonify(ok=True)


@app.post('/api/logout')
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get('/api/me')
def me():
    u = current_user()
    if not u:
        return jsonify(auth=False)
    touch_streak(u)
    return jsonify(
        auth=True,
        user={'username': u.username, 'display_name': u.display_name or '', 'name': u.name,
              'test_minutes': u.test_minutes or 10, 'public': bool(u.public)},
        stats=user_stats(u),
        scopes=[QB.ALL_SCOPE] + QB.CATEGORIES,
        all_scope=QB.ALL_SCOPE,
    )


@app.post('/api/settings')
def settings():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    if 'test_minutes' in d:
        try:
            m = int(d['test_minutes'])
        except (TypeError, ValueError):
            return jsonify(error='قيمة غير صحيحة لمدة الاختبار.'), 400
        if not 1 <= m <= 60:
            return jsonify(error='مدة الاختبار من 1 إلى 60 دقيقة.'), 400
        u.test_minutes = m
    if 'display_name' in d:
        u.display_name = ((d.get('display_name') or '').strip()[:60]) or None
    if 'public' in d:
        u.public = bool(d['public'])
    db.session.commit()
    return jsonify(ok=True)


@app.post('/api/pin')
def change_pin():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    cur, new = str(d.get('current') or ''), str(d.get('new') or '')
    if not check_password_hash(u.pin_hash, cur):
        return jsonify(error='كلمة المرور الحالية غير صحيحة.'), 401
    if not (4 <= len(new) <= 8) or not new.isdigit():
        return jsonify(error='كلمة المرور الجديدة من 4 إلى 8 أرقام.'), 400
    u.pin_hash = generate_password_hash(new)
    db.session.commit()
    return jsonify(ok=True)


@app.post('/api/account/delete')
def delete_account():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    if not check_password_hash(u.pin_hash, str(d.get('pin') or '')):
        return jsonify(error='كلمة المرور غير صحيحة.'), 401
    Progress.query.filter_by(user_id=u.id).delete()
    TestResult.query.filter_by(user_id=u.id).delete()
    Activity.query.filter_by(user_id=u.id).delete()
    db.session.delete(u)
    db.session.commit()
    session.clear()
    return jsonify(ok=True)


@app.get('/api/export')
def export():
    u, err = need_user()
    if err:
        return err
    pmap = progress_map(u)
    data = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'user': {'username': u.username, 'display_name': u.display_name,
                 'streak': u.streak, 'best_streak': u.best_streak},
        'stats': user_stats(u, pmap),
        'progress': [{'qid': p.qid, 'question': QB.QMAP[p.qid]['q'] if p.qid in QB.QMAP else None,
                      'seen': p.seen_count or 0, 'correct': p.correct_count or 0,
                      'wrong': p.wrong_count or 0, 'mastered': bool(p.mastered),
                      'bookmarked': bool(p.bookmarked),
                      'next_due': p.next_due.isoformat() if p.next_due else None}
                     for p in pmap.values()],
        'tests': [{'score': t.score, 'total': t.total, 'scope': t.scope, 'mode': t.mode,
                   'seconds': t.seconds_used, 'at': t.created_at.isoformat() + 'Z'}
                  for t in TestResult.query.filter_by(user_id=u.id)
                  .order_by(TestResult.created_at.desc()).all()],
    }
    r = Response(json.dumps(data, ensure_ascii=False, indent=2),
                 mimetype='application/json; charset=utf-8')
    r.headers['Content-Disposition'] = 'attachment; filename="lotg-progress.json"'
    return r


# ─────────────────────────────────────────────────────── الأسئلة واللعب
@app.get('/api/daily')
def daily():
    u, err = need_user()
    if err:
        return err
    touch_streak(u)
    today = date.today()
    act = today_activity(u)

    # يُختار سؤال اليوم مرة واحدة ثم يُثبَّت، فلا يتغيّر بالتنقّل بين الصفحات
    # ولا بتغيّر تقدّم المستخدم خلال اليوم.
    q = QB.QMAP.get(act.daily_qid or '')
    if q is None:
        pmap = progress_map(u)
        ranked = sorted(QB.QUESTIONS, key=lambda x: priority(pmap.get(x['id']), today))
        best = priority(pmap.get(ranked[0]['id']), today)
        pool = [x for x in ranked if priority(pmap.get(x['id']), today) == best]
        q = random.Random('%s-%s' % (today.isoformat(), u.id)).choice(pool)
        act.daily_qid = q['id']
    db.session.commit()

    out = {'question': QB.public_view(q), 'answered': False}
    p = Progress.query.filter_by(user_id=u.id, qid=q['id']).first()
    if p and p.updated_at and p.updated_at.date() == today and p.last_correct is not None:
        your = p.last_answer
        out.update(answered=True, correct=bool(p.last_correct),
                   correct_index=q['a'], your=your,
                   your_index=q['options'].index(your) if your in q['options'] else -1,
                   explanation=q['exp'], reference=q['ref'], page=q['page'])
    return jsonify(**out)


@app.post('/api/answer')
def answer():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    qid = d.get('qid')
    if qid not in QB.QMAP:
        return jsonify(error='سؤال غير معروف.'), 404
    correct, q = record_answer(u, qid, d.get('choice'))
    return jsonify(correct=correct, correct_index=q['a'], explanation=q['exp'],
                   reference=q['ref'], page=q['page'])


@app.get('/api/study')
def study():
    u, err = need_user()
    if err:
        return err
    pmap = progress_map(u)
    scope = request.args.get('scope', QB.ALL_SCOPE)
    filt = request.args.get('filter', 'all')
    search = (request.args.get('search') or '')[:60]
    try:
        limit = min(max(int(request.args.get('limit', 60)), 1), 200)
    except ValueError:
        limit = 60
    rows = filtered(scope, filt, search, pmap)
    items = []
    for q in rows[:limit]:
        p = pmap.get(q['id'])
        v = QB.public_view(q, reveal=True)
        v['saved'] = bool(p and p.bookmarked)
        v['status'] = status_of(p)
        items.append(v)
    return jsonify(items=items, total=len(rows), shown=len(items))


@app.post('/api/bookmark')
def bookmark():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    qid = d.get('qid')
    if qid not in QB.QMAP:
        return jsonify(error='سؤال غير معروف.'), 404
    p = Progress.query.filter_by(user_id=u.id, qid=qid).first()
    if not p:
        p = Progress(user_id=u.id, qid=qid, wrong_count=0, correct_streak=0,
                     seen_count=0, correct_count=0, mastered=False)
        db.session.add(p)
    p.bookmarked = bool(d.get('on'))
    db.session.commit()
    return jsonify(ok=True, on=p.bookmarked)


def pick_questions(u, pmap, scope, count, mode, filt, search):
    today = date.today()
    rnd = random.Random(os.urandom(16))
    if mode == 'mistakes':
        pool = [QB.QMAP[p.qid] for p in pmap.values()
                if p.qid in QB.QMAP and not p.mastered and (p.wrong_count or 0) > 0]
        scope_name = 'مراجعة الأخطاء'
    else:
        pool = filtered(scope, filt, search, pmap)
        scope_name = scope or QB.ALL_SCOPE
    if not pool:
        return scope_name, []
    if mode == 'random':
        rnd.shuffle(pool)
    elif mode == 'hard':
        rnd.shuffle(pool)
        pool.sort(key=lambda q: -q['diff'])
    elif mode == 'mistakes':
        pool.sort(key=lambda q: -(pmap[q['id']].wrong_count or 0))
    else:  # ذكي
        rnd.shuffle(pool)
        pool.sort(key=lambda q: priority(pmap.get(q['id']), today))
    chosen = pool[:count]
    rnd.shuffle(chosen)
    return scope_name, chosen


@app.get('/api/test')
def build_test():
    u, err = need_user()
    if err:
        return err
    pmap = progress_map(u)
    try:
        count = min(max(int(request.args.get('count', 10)), 1), 50)
    except ValueError:
        count = 10
    mode = request.args.get('mode', 'mixed')
    if mode not in ('mixed', 'random', 'hard', 'mistakes'):
        mode = 'mixed'
    scope_name, chosen = pick_questions(
        u, pmap, request.args.get('scope', QB.ALL_SCOPE), count, mode,
        request.args.get('filter', 'all'), (request.args.get('search') or '')[:60])
    return jsonify(scope=scope_name, mode=mode, minutes=u.test_minutes or 10,
                   questions=[QB.public_view(q) for q in chosen])


@app.post('/api/test/submit')
def submit_test():
    u, err = need_user()
    if err:
        return err
    d = request.get_json(silent=True) or {}
    answers = d.get('answers') or []
    if not isinstance(answers, list):
        return jsonify(error='بيانات غير صحيحة.'), 400
    score, details, seen = 0, [], set()
    for item in answers[:60]:
        if not isinstance(item, dict):
            continue
        qid = item.get('qid')
        if qid not in QB.QMAP or qid in seen:
            continue
        seen.add(qid)
        correct, q = record_answer(u, qid, item.get('choice'))
        score += int(correct)
        try:
            your = q['options'][int(item.get('choice'))]
        except (TypeError, ValueError, IndexError):
            your = 'لم يُجب'
        details.append({'qid': qid, 'question': q['q'], 'category': q['category'],
                        'correct': correct, 'your': your,
                        'correct_answer': q['options'][q['a']], 'explanation': q['exp'],
                        'reference': q['ref'], 'page': q['page']})
    scope = str(d.get('scope') or QB.ALL_SCOPE)[:60]
    mode = str(d.get('mode') or 'mixed')[:20]
    try:
        secs = max(0, min(int(d.get('seconds_used', 0)), 24 * 3600))
    except (TypeError, ValueError):
        secs = 0
    db.session.add(TestResult(user_id=u.id, score=score, total=len(details),
                              scope=scope, mode=mode, seconds_used=secs))
    db.session.commit()
    return jsonify(score=score, total=len(details), scope=scope, details=details)


@app.get('/api/mistakes')
def mistakes():
    u, err = need_user()
    if err:
        return err
    rows = Progress.query.filter_by(user_id=u.id, mastered=False) \
        .filter(Progress.wrong_count > 0).order_by(Progress.wrong_count.desc()).all()
    out = []
    for p in rows:
        q = QB.QMAP.get(p.qid)
        if not q:
            continue
        out.append({'qid': p.qid, 'question': q['q'], 'category': q['category'],
                    'topic': q['topic'], 'wrong_count': p.wrong_count or 0,
                    'last_answer': p.last_answer,
                    'correct_answer': q['options'][q['a']], 'exp': q['exp'],
                    'ref': q['ref'], 'page': q['page'],
                    'next_due': p.next_due.isoformat() if p.next_due else None})
    return jsonify(items=out)


# ─────────────────────────────────────────────── الإحصائيات والترتيب
ACHIEVEMENTS = [
    ('first',    '🎬', 'البداية',        'أجب عن أول سؤال',                 lambda s: s['answered'] >= 1),
    ('streak3',  '🔥', 'ثلاثة أيام',      'ذاكر ثلاثة أيام متتالية',          lambda s: s['best_streak'] >= 3),
    ('streak7',  '📅', 'أسبوع كامل',      'ذاكر سبعة أيام متتالية',           lambda s: s['best_streak'] >= 7),
    ('streak30', '🏅', 'شهر كامل',        'ذاكر ثلاثين يومًا متتاليًا',        lambda s: s['best_streak'] >= 30),
    ('m25',      '📗', 'حافظ القانون',    'أتقن ٢٥ سؤالًا',                   lambda s: s['mastered'] >= 25),
    ('m100',     '📚', 'خبير القوانين',   'أتقن ١٠٠ سؤال',                    lambda s: s['mastered'] >= 100),
    ('m250',     '🧠', 'مرجع',            'أتقن ٢٥٠ سؤالًا',                  lambda s: s['mastered'] >= 250),
    ('acc90',    '🎯', 'دقة عالية',       'حقّق دقة ٩٠٪ بعد ٥٠ إجابة',        lambda s: s['answered'] >= 50 and s['accuracy'] >= 90),
    ('perfect',  '🏆', 'درجة كاملة',      'أنهِ اختبارًا بعلامة كاملة',        lambda s: s['perfect']),
    ('clean',    '🧹', 'صفر أخطاء',       'صفّر قائمة أخطائك بعد أن امتلأت',  lambda s: s['answered'] >= 30 and s['wrong'] == 0),
    ('allLaws',  '🗂️', 'شامل',            'أجب عن سؤال من كل مادة',           lambda s: s['laws_touched'] >= s['laws']),
    ('tests10',  '⏱️', 'مواظب',           'أكمل عشرة اختبارات',               lambda s: s['tests'] >= 10),
]


@app.get('/api/stats')
def stats():
    u, err = need_user()
    if err:
        return err
    pmap = progress_map(u)
    base = user_stats(u, pmap)

    per = {n: {'law': n, 'title': QB.LAW_TITLES[n], 'total': 0, 'answered': 0,
               'correct': 0, 'mastered': 0} for n in QB.LAWS}
    for q in QB.QUESTIONS:
        row = per[q['law']]
        row['total'] += 1
        p = pmap.get(q['id'])
        if was_seen(p):
            row['answered'] += p.seen_count or 0
            row['correct'] += p.correct_count or 0
            if p.mastered:
                row['mastered'] += 1
    by_law = []
    for n in QB.LAWS:
        r = per[n]
        r['accuracy'] = round(r['correct'] / r['answered'] * 100, 1) if r['answered'] else 0.0
        by_law.append(r)

    today = date.today()
    start = today - timedelta(days=27)
    acts = {a.day: a.answers or 0 for a in Activity.query.filter_by(user_id=u.id)
            .filter(Activity.day >= start).all()}
    calendar = []
    for i in range(28):
        d = start + timedelta(days=i)
        c = acts.get(d, 0)
        calendar.append({'day': d.isoformat(), 'count': c,
                         'level': 0 if not c else 1 if c < 5 else 2 if c < 15 else 3})

    rows = TestResult.query.filter_by(user_id=u.id) \
        .order_by(TestResult.created_at.desc()).limit(10).all()
    history = [{'score': t.score, 'total': t.total, 'scope': t.scope,
                'when': ago(t.created_at), 'seconds': t.seconds_used or 0} for t in rows]

    done = db.session.query(db.func.count(TestResult.id)).filter(
        TestResult.user_id == u.id, TestResult.total > 0,
        TestResult.score == TestResult.total).scalar() or 0
    avg = db.session.query(db.func.avg(TestResult.score * 100.0 / TestResult.total)) \
        .filter(TestResult.user_id == u.id, TestResult.total > 0).scalar()
    laws_touched = len({QB.QMAP[p.qid]['law'] for p in pmap.values()
                        if was_seen(p) and p.qid in QB.QMAP})
    ctx = dict(base, perfect=done > 0, laws_touched=laws_touched)
    ach = [{'id': a[0], 'icon': a[1], 'name': a[2], 'desc': a[3], 'got': bool(a[4](ctx))}
           for a in ACHIEVEMENTS]

    overall = dict(base, avg_test=round(float(avg), 1) if avg is not None else None)
    return jsonify(overall=overall, by_law=by_law, calendar=calendar,
                   history=history, achievements=ach)


@app.get('/api/leaderboard')
def leaderboard():
    u, err = need_user()
    if err:
        return err
    mastered = db.func.sum(db.case((Progress.mastered == True, 1), else_=0))  # noqa: E712
    rows = (db.session.query(User.id, User.username, User.display_name,
                             mastered.label('m'),
                             db.func.sum(Progress.seen_count).label('seen'),
                             db.func.sum(Progress.correct_count).label('ok'))
            .join(Progress, Progress.user_id == User.id)
            .filter(User.public == True)  # noqa: E712
            .group_by(User.id, User.username, User.display_name)
            .order_by(db.text('m DESC'))
            .limit(25).all())
    items, my_row = [], None
    for r in rows:
        seen, ok, m = int(r.seen or 0), int(r.ok or 0), int(r.m or 0)
        entry = {'name': r.display_name or r.username, 'mastered': m,
                 'accuracy': round(ok / seen * 100, 1) if seen else 0.0,
                 'me': r.id == u.id}
        if entry['me']:
            my_row = entry
        items.append(entry)
    me_stats = user_stats(u)
    me_info = my_row or {'name': u.name, 'mastered': me_stats['mastered'],
                         'accuracy': me_stats['accuracy'], 'me': True}
    me_info['listed'] = my_row is not None
    me_info['rank'] = (items.index(my_row) + 1) if my_row else None
    return jsonify(items=items, me=me_info, hidden=not bool(u.public))


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
