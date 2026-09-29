import os, random, hashlib
from datetime import datetime, date, timedelta, timezone
from flask import Flask, render_template_string, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-change-me')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///lotg.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif db_url.startswith('postgresql://') and '+psycopg' not in db_url:
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    pin_hash = db.Column(db.String(255), nullable=False)
    test_minutes = db.Column(db.Integer, default=10)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    qid = db.Column(db.String(32), nullable=False, index=True)
    wrong_count = db.Column(db.Integer, default=0)
    correct_streak = db.Column(db.Integer, default=0)
    mastered = db.Column(db.Boolean, default=False)
    next_due = db.Column(db.Date, nullable=True)
    last_answer = db.Column(db.String(200), nullable=True)
    last_correct = db.Column(db.Boolean, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id','qid', name='uq_user_q'),)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    scope = db.Column(db.String(60), nullable=False)
    seconds_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

QUESTIONS = [
# Law 1
{'id':'L1-01','category':'ميدان اللعب','type':'mcq','q':'ما الحد الأقصى لعرض خطوط ميدان اللعب؟','options':['8 سم','10 سم','12 سم','15 سم'],'a':2,'exp':'جميع الخطوط يجب أن تكون بنفس العرض وألا يزيد عرضها على 12 سم.','ref':'المادة 1 – ميدان اللعب','page':47},
{'id':'L1-02','category':'ميدان اللعب','type':'mcq','q':'في المباريات الدولية، ما الحد الأدنى لطول خط التماس؟','options':['90 م','95 م','100 م','110 م'],'a':2,'exp':'في المباريات الدولية الحد الأدنى لطول خط التماس هو 100 متر.','ref':'المادة 1 – ميدان اللعب','page':48},
{'id':'L1-03','category':'ميدان اللعب','type':'mcq','q':'كم تبعد علامة الجزاء عن منتصف المسافة بين قائمي المرمى؟','options':['9.15 م','10 م','11 م','12 م'],'a':2,'exp':'توضع علامة الجزاء على بعد 11 مترًا من منتصف المسافة بين القائمين.','ref':'المادة 1 – ميدان اللعب','page':48},
{'id':'L1-04','category':'ميدان اللعب','type':'tf','q':'نصف قطر المنطقة الركنية متر واحد.','options':['صح','خطأ'],'a':0,'exp':'المنطقة الركنية ربع دائرة نصف قطرها 1 متر.','ref':'المادة 1 – ميدان اللعب','page':48},
{'id':'L1-05','category':'ميدان اللعب','type':'scenario','q':'لاحظ الحكم أثناء اللعب أن لاعبًا وضع علامة غير مسموح بها على أرض الملعب. ما الإجراء الانضباطي؟','options':['لا شيء','إنذار عند أول توقف','طرد مباشر','إيقاف اللعب فورًا دائمًا'],'a':1,'exp':'اللاعب الذي يضع علامات غير مسموح بها يُنذر للسلوك غير الرياضي، وإذا لاحظها الحكم أثناء اللعب يكون الإنذار عند أول توقف.','ref':'المادة 1 – ميدان اللعب','page':47},
# Law 3
{'id':'L3-01','category':'اللاعبون','type':'mcq','q':'ما الحد الأقصى لعدد اللاعبين في كل فريق داخل الملعب عند بدء المباراة؟','options':['9','10','11','12'],'a':2,'exp':'كل فريق يتكون من 11 لاعبًا كحد أقصى، أحدهم حارس مرمى.','ref':'المادة 3 – اللاعبون','page':59},
{'id':'L3-02','category':'اللاعبون','type':'mcq','q':'لا يمكن بدء المباراة أو استمرارها إذا أصبح عدد لاعبي أحد الفريقين أقل من:','options':['5','6','7','8'],'a':2,'exp':'الحد الأدنى هو سبعة لاعبين.','ref':'المادة 3 – اللاعبون','page':59},
{'id':'L3-03','category':'اللاعبون','type':'scenario','q':'أصبح فريق مكوّنًا من 6 لاعبين لأن لاعبًا خرج عمدًا، والكرة ما زالت في اللعب مع فرصة واعدة للمنافس. ما الذي يمكن للحكم فعله؟','options':['يوقف اللعب فورًا وجوبًا','يطبق إتاحة الفرصة، لكن لا يستأنف بعد خروج الكرة إذا بقي العدد أقل من 7','يلغي المباراة مباشرة دون انتظار','يسمح باستمرار المباراة حتى النهاية'],'a':1,'exp':'الحكم غير مجبر على الإيقاف فورًا ويمكنه تطبيق مبدأ إتاحة الفرصة، لكن لا يمكن استكمال المباراة بعد أن تصبح الكرة خارج اللعب إذا بقي الفريق بأقل من سبعة.','ref':'المادة 3 – اللاعبون','page':59},
{'id':'L3-04','category':'اللاعبون','type':'mcq','q':'وفق بروتوكول 2026/27، خلال كم ثانية يجب على اللاعب المستبدل مغادرة الملعب عادة؟','options':['5','8','10','15'],'a':2,'exp':'المهلة الزمنية المحددة للمغادرة هي 10 ثوانٍ، مع استثناءات تتعلق بالإصابة أو السلامة/الأمن.','ref':'المادة 3 / بروتوكول وقت التبديل','page':61},
{'id':'L3-05','category':'اللاعبون','type':'scenario','q':'تجاوز اللاعب المستبدل مهلة 10 ثوانٍ دون عذر. متى يمكن للبديل الدخول؟','options':['فورًا بعد خروج اللاعب','بعد 30 ثانية','عند أول توقف بعد مرور دقيقة واحدة على استئناف اللعب وبإذن الحكم','لا يمكنه الدخول نهائيًا'],'a':2,'exp':'لا يُسمح للبديل بالدخول حتى أول توقف للعب بعد مرور دقيقة واحدة على استئناف اللعب وبإذن الحكم.','ref':'بروتوكول الوقت المحدد للتبديل','page':22},
# Law 4
{'id':'L4-01','category':'معدات اللاعبين','type':'mcq','q':'أي مما يلي من المعدات الإلزامية للاعب؟','options':['قفازات','واقي الساق','قبعة','ساعة'],'a':1,'exp':'واقي الساق جزء من المعدات الإلزامية ويجب أن تغطيه الجوارب.','ref':'المادة 4 – معدات اللاعبين','page':67},
{'id':'L4-02','category':'معدات اللاعبين','type':'tf','q':'يجوز تغطية قطعة خطرة بشريط لاصق بدل إزالتها.','options':['صح','خطأ'],'a':1,'exp':'العنصر الخطر يجب إزالته، ولا يجوز مجرد تغطيته أو لصقه بدل الإزالة.','ref':'المادة 4 – معدات اللاعبين','page':67},
{'id':'L4-03','category':'معدات اللاعبين','type':'scenario','q':'رفض لاعب الامتثال لطلب الحكم بإزالة معدات غير مسموح بها. ما القرار؟','options':['تحذير فقط','إنذار','طرد مباشر','لا إجراء'],'a':1,'exp':'اللاعب الذي يرفض الامتثال أو يعيد ارتداء معدات مخالفة يجب إنذاره.','ref':'المادة 4 – معدات اللاعبين','page':67},
# Law 5
{'id':'L5-01','category':'الحكم','type':'tf','q':'قرارات الحكم المتعلقة بأحداث اللعب، ومنها احتساب هدف من عدمه، نهائية.','options':['صح','خطأ'],'a':0,'exp':'قرارات الحكم المتعلقة بأحداث اللعب ونتيجة المباراة نهائية ويجب احترامها.','ref':'المادة 5 – الحكم','page':73},
{'id':'L5-02','category':'الحكم','type':'mcq','q':'أي تقنية يمكن أن تساعد الحكم في قرار التسلل وفق نسخة 2026/27؟','options':['GLT فقط','SAOT','GPS','تقنية صوتية'],'a':1,'exp':'يسمح باستخدام تقنية التسلل شبه الآلي SAOT للمساعدة في قرارات التسلل.','ref':'المادة 5 – الحكم','page':73},
{'id':'L5-03','category':'الحكم','type':'scenario','q':'اكتشف الحكم أن قرار استئناف سابق كان خاطئًا بعد أن استؤنف اللعب. هل يمكنه تغيير قرار الاستئناف؟','options':['نعم دائمًا','لا، بعد استئناف اللعب لا يغيّر قرار الاستئناف السابق','فقط بموافقة القائدين','فقط إن كان الخطأ داخل منطقة الجزاء'],'a':1,'exp':'لا يمكن للحكم تغيير قرار استئناف اللعب بعد أن يكون اللعب قد استؤنف.','ref':'المادة 5 – الحكم','page':73},
# Law 8
{'id':'L8-01','category':'ابتداء واستئناف اللعب','type':'mcq','q':'إذا أوقف الحكم اللعب ولا يحدد القانون طريقة استئناف أخرى، فكيف يُستأنف؟','options':['ركلة حرة مباشرة','ركلة حرة غير مباشرة','إسقاط الكرة','رمية تماس'],'a':2,'exp':'يستأنف اللعب بإسقاط الكرة عندما لا يتطلب القانون طريقة استئناف أخرى.','ref':'المادة 8 – ابتداء واستئناف اللعب','page':97},
{'id':'L8-02','category':'ابتداء واستئناف اللعب','type':'tf','q':'حدوث مخالفة أثناء كون الكرة خارج اللعب يغيّر دائمًا طريقة الاستئناف المقررة.','options':['صح','خطأ'],'a':1,'exp':'إذا حدث خطأ والكرة خارج اللعب فهذا لا يغيّر طريقة الاستئناف الأصلية.','ref':'المادة 8 – ابتداء واستئناف اللعب','page':97},
# Law 10
{'id':'L10-01','category':'تحديد نتيجة المباراة','type':'scenario','q':'في ركلات الترجيح، ركل المنفذ الكرة بكلتا القدمين في الوقت نفسه دون قصد ودخلت الكرة المرمى. القرار؟','options':['هدف','إعادة الركلة','ركلة مهدرة','إنذار وإعادة'],'a':1,'exp':'في اللمسة المزدوجة غير المتعمدة: إذا دخلت الكرة المرمى تُعاد الركلة.','ref':'المادة 10 – تحديد نتيجة المباراة','page':106},
{'id':'L10-02','category':'تحديد نتيجة المباراة','type':'scenario','q':'في ركلات الترجيح، حدثت لمسة مزدوجة غير متعمدة ولم تدخل الكرة المرمى. القرار؟','options':['إعادة الركلة','تحتسب مهدرة','ركلة حرة','يستمر اللعب'],'a':1,'exp':'إذا لم تدخل الكرة المرمى بعد اللمسة المزدوجة غير المتعمدة فتُحتسب الركلة مهدرة.','ref':'المادة 10 – تحديد نتيجة المباراة','page':106},
# Law 11
{'id':'L11-01','category':'التسلل','type':'tf','q':'مجرد وجود اللاعب في موقف تسلل يعد مخالفة تستوجب العقوبة.','options':['صح','خطأ'],'a':1,'exp':'الوجود في موقف تسلل ليس مخالفة في حد ذاته.','ref':'المادة 11 – التسلل','page':109},
{'id':'L11-02','category':'التسلل','type':'mcq','q':'أي أجزاء الجسم لا تؤخذ في الاعتبار عند تحديد موقف التسلل؟','options':['الرأس','القدم','اليد والذراع','الجذع'],'a':2,'exp':'اليدان والذراعان لا تؤخذان في الاعتبار، بما في ذلك لحارس المرمى.','ref':'المادة 11 – التسلل','page':109},
{'id':'L11-03','category':'التسلل','type':'tf','q':'اللاعب على نفس مستوى آخر ثاني منافس لا يعد في موقف تسلل.','options':['صح','خطأ'],'a':0,'exp':'إذا كان اللاعب على نفس المستوى مع آخر ثاني منافس فهو ليس في موقف تسلل.','ref':'المادة 11 – التسلل','page':109},
{'id':'L11-04','category':'التسلل','type':'scenario','q':'لاعب في موقف تسلل لم يلمس الكرة ولم يتداخل مع منافس. هل يعاقب؟','options':['نعم','لا','فقط إذا كان داخل منطقة الجزاء','فقط إذا رفع المساعد الراية'],'a':1,'exp':'لا يعاقب إلا إذا شارك في اللعب النشط، مثل التداخل في اللعب أو مع منافس أو اكتساب ميزة.','ref':'المادة 11 – التسلل','page':109},
# Law 12
{'id':'L12-01','category':'الأخطاء وسوء السلوك','type':'mcq','q':'أي من الآتي إذا ارتكب ضد منافس بإهمال أو تهور أو قوة مفرطة ويشمل تلامسًا يُعاقب بركلة حرة مباشرة؟','options':['العرقلة','الاعتراض اللفظي','التسلل','التأخر في التبديل فقط'],'a':0,'exp':'العرقلة أو محاولة العرقلة من مخالفات الركلة الحرة المباشرة، وإذا شمل الخطأ تلامسًا يعاقب بركلة حرة مباشرة.','ref':'المادة 12 – الأخطاء وسوء السلوك','page':115},
{'id':'L12-02','category':'الأخطاء وسوء السلوك','type':'tf','q':'الركلات الحرة المباشرة وغير المباشرة وركلات الجزاء بسبب المخالفات تُحتسب فقط عندما تكون الكرة في اللعب.','options':['صح','خطأ'],'a':0,'exp':'هذه العقوبات على المخالفات تُحتسب عندما تكون الكرة في اللعب.','ref':'المادة 12 – الأخطاء وسوء السلوك','page':115},
{'id':'L12-03','category':'الأخطاء وسوء السلوك','type':'scenario','q':'لاعب أخر تنفيذ استئناف اللعب بصورة مفرطة. ما الإجراء الانضباطي المعتاد؟','options':['لا شيء','إنذار','طرد مباشر','ركلة جزاء'],'a':1,'exp':'التأخير المفرط لاستئناف اللعب من الحالات التي تستوجب الإنذار.','ref':'المادة 12 – الإجراءات الانضباطية','page':123},
{'id':'L12-04','category':'الأخطاء وسوء السلوك','type':'mcq','q':'أي مما يلي من اعتبارات DOGSO؟','options':['لون القميص','المسافة بين الخطأ والمرمى','عدد الجماهير','زمن المباراة فقط'],'a':1,'exp':'من اعتبارات DOGSO المسافة بين الخطأ والمرمى، والاتجاه العام للعب، واحتمالية السيطرة على الكرة وغيرها.','ref':'المادة 12 – DOGSO','page':124},
{'id':'L12-05','category':'الأخطاء وسوء السلوك','type':'scenario','q':'مهاجم حُرم من فرصة واضحة لتسجيل هدف، لكن الحكم طبق إتاحة الفرصة وسُجل هدف. وفق تعديل 2026/27، ماذا عن الإنذار بسبب DOGSO؟','options':['إنذار دائمًا','لا إنذار بسبب DOGSO في هذه الحالة','طرد مباشر','إنذاران'],'a':1,'exp':'تعديل 2026/27 يوضح أنه لا يتم إنذار اللاعب بسبب DOGSO إذا طبقت إتاحة الفرصة وتم تسجيل هدف.','ref':'تغييرات 2026/27 – المادة 12','page':170},
# Law 13
{'id':'L13-01','category':'الركلات الحرة','type':'scenario','q':'نُفذت ركلة حرة غير مباشرة مباشرة إلى مرمى المنافس دون أن تلمس لاعبًا آخر. القرار؟','options':['هدف','ركلة مرمى','ركلة ركنية','إعادة الركلة'],'a':1,'exp':'إذا دخلت الركلة الحرة غير المباشرة مباشرة مرمى المنافس تُحتسب ركلة مرمى.','ref':'المادة 13 – الركلات الحرة','page':131},
{'id':'L13-02','category':'الركلات الحرة','type':'scenario','q':'نُفذت ركلة حرة مباشرة أو غير مباشرة مباشرة إلى مرمى نفس الفريق. القرار؟','options':['هدف عكسي','ركلة ركنية','ركلة مرمى','إعادة الركلة'],'a':1,'exp':'إذا دخلت ركلة حرة مباشرة أو غير مباشرة مباشرة مرمى نفس الفريق تُحتسب ركلة ركنية للمنافس.','ref':'المادة 13 – الركلات الحرة','page':131},
{'id':'L13-03','category':'الركلات الحرة','type':'tf','q':'في الركلة الحرة غير المباشرة يرفع الحكم ذراعه فوق الرأس ويستمر بالإشارة حتى تلمس الكرة لاعبًا آخر أو تصبح خارج اللعب أو يتضح تعذر تسجيل هدف مباشر.','options':['صح','خطأ'],'a':0,'exp':'هذه هي إشارة الركلة الحرة غير المباشرة كما وردت في المادة 13.','ref':'المادة 13 – الركلات الحرة','page':131},
# Law 14
{'id':'L14-01','category':'ركلة الجزاء','type':'mcq','q':'أين يجب أن يكون اللاعبون الآخرون غير المنفذ وحارس المرمى عند تنفيذ ركلة الجزاء؟','options':['داخل منطقة الجزاء','على بعد 9.15م على الأقل، خلف علامة الجزاء، داخل الملعب وخارج منطقة الجزاء','خلف خط المرمى','أي مكان'],'a':1,'exp':'يشترط أن يكونوا على بعد 9.15م على الأقل، خلف علامة الجزاء، داخل الملعب وخارج منطقة الجزاء.','ref':'المادة 14 – ركلة الجزاء','page':135},
{'id':'L14-02','category':'ركلة الجزاء','type':'tf','q':'يجوز تنفيذ ركلة الجزاء بالكعب إذا تحركت الكرة إلى الأمام.','options':['صح','خطأ'],'a':0,'exp':'يجوز لعب الكرة بالكعب بشرط أن تتحرك إلى الأمام.','ref':'المادة 14 – ركلة الجزاء','page':135},
{'id':'L14-03','category':'ركلة الجزاء','type':'mcq','q':'أين يجب أن يبقى حارس المرمى المدافع حتى تُركل الكرة؟','options':['أمام خط المرمى بمتر','على خط المرمى بين القائمين ومواجهًا للمنفذ','خارج منطقة المرمى','على علامة الجزاء'],'a':1,'exp':'يجب أن يبقى على خط المرمى بين القائمين ومواجهًا لمنفذ الركلة حتى تُركل الكرة.','ref':'المادة 14 – ركلة الجزاء','page':135},
# Law 15
{'id':'L15-01','category':'رمية التماس','type':'mcq','q':'ما المسافة الدنيا التي يجب أن يبتعدها المنافسون عن نقطة تنفيذ رمية التماس؟','options':['1 م','1.5 م','2 م','5 م'],'a':2,'exp':'يجب أن يكون المنافسون على بعد لا يقل عن مترين.','ref':'المادة 15 – رمية التماس','page':141},
{'id':'L15-02','category':'رمية التماس','type':'scenario','q':'دخلت رمية تماس مباشرة إلى مرمى الفريق المنافس دون لمس أحد. القرار؟','options':['هدف','ركلة مرمى','ركلة ركنية','إعادة الرمية'],'a':1,'exp':'لا يمكن تسجيل هدف مباشرة من رمية التماس؛ إذا دخلت مرمى المنافس تحتسب ركلة مرمى.','ref':'المادة 15 – رمية التماس','page':141},
{'id':'L15-03','category':'رمية التماس','type':'scenario','q':'دخلت رمية تماس مباشرة إلى مرمى نفس الفريق دون لمس أحد. القرار؟','options':['هدف عكسي','ركلة ركنية','ركلة مرمى','إعادة الرمية'],'a':1,'exp':'إذا دخلت رمية التماس مباشرة مرمى نفس الفريق تحتسب ركلة ركنية للمنافس.','ref':'المادة 15 – رمية التماس','page':141},
{'id':'L15-04','category':'رمية التماس','type':'scenario','q':'نفذت رمية تماس بطريقة غير صحيحة. لمن تُمنح الرمية؟','options':['لنفس الفريق لإعادتها','للفريق المنافس','إسقاط كرة','ركلة حرة غير مباشرة'],'a':1,'exp':'إذا نُفذت رمية التماس بطريقة غير صحيحة، تُمنح للفريق المنافس.','ref':'المادة 15 – رمية التماس','page':141},
# New protocols
{'id':'N-01','category':'تعديلات 2026/27','type':'mcq','q':'إذا تعمد فريق تأخير تنفيذ رمية التماس وبدأ الحكم العد التنازلي لخمس ثوانٍ ولم تصبح الكرة في اللعب، ما القرار؟','options':['إنذار فقط','رمية تماس للفريق المنافس من نفس المكان','ركلة حرة غير مباشرة','إسقاط كرة'],'a':1,'exp':'عند انتهاء العد دون التنفيذ تُمنح رمية تماس للفريق المنافس من نفس المكان.','ref':'بروتوكول العد التنازلي لرمية التماس وركلة المرمى','page':26},
{'id':'N-02','category':'تعديلات 2026/27','type':'scenario','q':'تأخر فريق عمدًا في تنفيذ ركلة المرمى، وانتهى العد التنازلي لخمس ثوانٍ دون أن تصبح الكرة في اللعب. القرار؟','options':['ركلة حرة مباشرة','ركلة ركنية للمنافس من الجهة الأقرب','إعادة ركلة المرمى','إسقاط كرة'],'a':1,'exp':'تُحتسب ركلة ركنية للفريق المنافس من الجهة الأقرب إلى مكان تنفيذ ركلة المرمى.','ref':'بروتوكول العد التنازلي لرمية التماس وركلة المرمى','page':26},
{'id':'N-03','category':'تعديلات 2026/27','type':'tf','q':'عند تطبيق عقوبة العد التنازلي لخمس ثوانٍ على رمية التماس أو ركلة المرمى، يُشهر الإنذار تلقائيًا دائمًا.','options':['صح','خطأ'],'a':1,'exp':'لا يُشهر الإنذار تلقائيًا؛ يُنذر فقط إذا كان هناك تأخير مفرط إضافي لاستئناف المنافس.','ref':'بروتوكول العد التنازلي','page':26},
{'id':'N-04','category':'الإصابات','type':'scenario','q':'أوقف الحكم اللعب بسبب إصابة لاعب وجرى تقييمه داخل الملعب، ولا ينطبق استثناء. ما المتطلب الجديد؟','options':['يعود فورًا','يبقى خارج الملعب دقيقة واحدة من وقت استئناف اللعب','يبقى خارج الملعب 30 ثانية','يُستبدل وجوبًا'],'a':1,'exp':'يلزم اللاعب بالبقاء خارج الميدان لمدة دقيقة واحدة تبدأ من لحظة استئناف اللعب، ما لم تنطبق إحدى حالات الاستثناء.','ref':'بروتوكول العلاج والتقييم خارج ميدان اللعب','page':24},
{'id':'N-05','category':'الإصابات','type':'mcq','q':'إذا كانت الكرة في اللعب، من أين يعاود اللاعب الدخول بعد انتهاء دقيقة العلاج خارج الملعب وبإذن الحكم؟','options':['من أي خط','من خط المرمى فقط','من خط التماس','من دائرة المنتصف'],'a':2,'exp':'إذا كانت الكرة في اللعب، تكون العودة من خط التماس وبإذن الحكم.','ref':'بروتوكول العلاج والتقييم خارج ميدان اللعب','page':25},
{'id':'N-06','category':'قائد الفريق فقط','type':'mcq','q':'متى ستصبح إرشادات «قائد الفريق فقط» إلزامية لجميع المسابقات وفق الكتاب؟','options':['1 يناير 2027','1 يوليو 2027','1 يوليو 2026','1 يناير 2028'],'a':1,'exp':'تنص النسخة على أنها تصبح إلزامية للمسابقات التي تبدأ في أو بعد 1 يوليو 2027.','ref':'إرشادات قائد الفريق فقط','page':28},
{'id':'N-07','category':'قائد الفريق فقط','type':'scenario','q':'إذا كان قائد الفريق هو حارس المرمى، من المسموح له بالاقتراب من الحكم عند تطبيق الإرشادات؟','options':['الحارس واللاعب المعين معًا','الحارس أو اللاعب المعين فقط، وليس كلاهما','أي لاعب','المدرب فقط'],'a':1,'exp':'يسمح لحارس المرمى أو اللاعب المعين فقط، وليس لكليهما، بالاقتراب من الحكم.','ref':'إرشادات قائد الفريق فقط','page':29},
{'id':'N-08','category':'الارتجاج','type':'mcq','q':'كم فرصة كحد أقصى لكل فريق لاستخدام التبديل الإضافي الدائم لحالة ارتجاج في المباراة؟','options':['واحدة','اثنتان','ثلاث','غير محدود'],'a':0,'exp':'يسمح لكل فريق بفرصة واحدة كحد أقصى لاستخدام تبديل ارتجاج إضافي دائم في كل مباراة.','ref':'بروتوكول الاستبدالات الدائمة الإضافية لحالات الارتجاج','page':39},
]
QMAP = {q['id']: q for q in QUESTIONS}
CATEGORIES = sorted(set(q['category'] for q in QUESTIONS))

def uid(): return session.get('uid')
def user(): return db.session.get(User, uid()) if uid() else None

def touch_streak(u):
    today = date.today()
    if u.last_active == today: return
    if u.last_active == today - timedelta(days=1): u.streak += 1
    else: u.streak = 1
    u.last_active = today
    db.session.commit()

def due_priority(u, q):
    p = Progress.query.filter_by(user_id=u.id, qid=q['id']).first()
    if not p: return (2,0)
    if p.next_due and p.next_due <= date.today() and not p.mastered: return (0,-p.wrong_count)
    if p.last_correct is False: return (1,-p.wrong_count)
    return (3,p.correct_streak)

def public_q(q):
    return {k:q[k] for k in ['id','category','type','q','options']}

def record_answer(u, qid, choice):
    q = QMAP[qid]; correct = int(choice) == q['a']
    p = Progress.query.filter_by(user_id=u.id, qid=qid).first()
    if not p:
        p = Progress(user_id=u.id, qid=qid); db.session.add(p)
    p.last_answer = q['options'][int(choice)] if 0 <= int(choice) < len(q['options']) else str(choice)
    p.last_correct = correct
    if correct:
        p.correct_streak += 1
        if p.wrong_count > 0:
            if p.correct_streak >= 3:
                p.mastered = True; p.next_due = None
            else:
                p.next_due = date.today() + timedelta(days=[2,5][min(p.correct_streak-1,1)])
    else:
        p.wrong_count += 1; p.correct_streak = 0; p.mastered = False
        days = 1 if p.wrong_count >= 2 else 2
        p.next_due = date.today() + timedelta(days=days)
    db.session.commit()
    return correct, q

INDEX_HTML = r'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0b1510"><title>LOTG Referee</title><style>
:root{--bg:#08110c;--card:#101c15;--line:#20372a;--txt:#eff7f1;--muted:#94aa9a;--accent:#c7f542;--danger:#ff6b6b;--ok:#6ee7a8}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#13271a 0,#08110c 42%);color:var(--txt);font-family:system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;min-height:100vh}header{display:flex;justify-content:space-between;align-items:center;padding:18px 5vw;border-bottom:1px solid #1c3024;position:sticky;top:0;background:#08110ce8;backdrop-filter:blur(10px);z-index:5}header div{display:flex;flex-direction:column}.brand{font-size:22px;color:var(--accent)}header span{font-size:12px;color:var(--muted)}main{max-width:1050px;margin:auto;padding:28px 16px 60px}.card{background:linear-gradient(180deg,#132118,#0f1913);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 16px 44px #0004}.auth{max-width:470px;margin:8vh auto}.auth input,.card input,select{width:100%;padding:14px;border-radius:13px;border:1px solid #294433;background:#0a130e;color:#fff;margin:8px 0 12px;font-size:16px}button{border:0;border-radius:13px;padding:13px 18px;background:var(--accent);font-weight:800;color:#11200f;cursor:pointer;font-size:15px}.secondary{background:#22412d;color:#eaf7ed}.ghost{background:transparent;color:#dfece3;border:1px solid #31523c}.full{width:100%;margin-top:10px}.row{display:flex;gap:10px;align-items:center}.between{justify-content:space-between}.hidden{display:none!important}.error{color:var(--danger)}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:15px}.stat{background:#0f1a13;border:1px solid var(--line);padding:16px;border-radius:18px;text-align:center}.stat b{display:block;font-size:26px;color:var(--accent)}.stat span{font-size:13px;color:var(--muted)}.grid{display:grid;grid-template-columns:1.25fr 1fr;gap:15px}.hero{grid-row:span 2}.badge{display:inline-block;background:#203721;color:var(--accent);padding:6px 10px;border-radius:999px;font-size:13px;margin-bottom:8px}.options{display:grid;gap:10px;margin:16px 0}.option{width:100%;text-align:right;background:#0b150f;color:#f4faf5;border:1px solid #2b4935;font-weight:600}.option:hover{border-color:var(--accent)}.option.correct{background:#183d29;border-color:var(--ok)}.option.wrong{background:#432222;border-color:var(--danger)}.feedback{margin-top:12px;padding:14px;border-radius:14px;background:#0a130e;border:1px solid #274331}.feedback b{color:var(--accent)}.testbox{max-width:760px;margin:auto}.testhead{display:flex;justify-content:space-between;align-items:center}.timer{font-size:30px;font-weight:900;color:var(--accent);font-variant-numeric:tabular-nums}.mistake{padding:14px 0;border-bottom:1px solid var(--line)}.mistake small{color:var(--muted)}@media(max-width:720px){.grid{grid-template-columns:1fr}.hero{grid-row:auto}.stats{grid-template-columns:repeat(3,1fr)}.card{padding:17px}.row{flex-wrap:wrap}.auth .row button{flex:1}}

</style></head><body>
<div id="app">
  <header><div><b class="brand">LOTG Referee</b><span>اختبر نفسك في قوانين كرة القدم</span></div><button id="logout" class="ghost hidden">خروج</button></header>
  <main>
    <section id="auth" class="auth card"><h1>مرحبًا بالحكم 👋</h1><p>دخول سريع باسم مستخدم ورقم PIN. تقدمك محفوظ على حسابك.</p><input id="username" placeholder="اسم المستخدم" autocomplete="username"><input id="pin" placeholder="PIN من 4–8 أرقام" inputmode="numeric" type="password"><div class="row"><button onclick="login()">دخول</button><button class="secondary" onclick="register()">إنشاء حساب</button></div><p id="authMsg" class="error"></p></section>
    <section id="home" class="hidden">
      <div class="stats"><div class="stat"><b id="streak">0</b><span>🔥 ستريك</span></div><div class="stat"><b id="mastered">0</b><span>تم إتقانه</span></div><div class="stat"><b id="wrong">0</b><span>تحتاج مراجعة</span></div></div>
      <div class="grid">
        <div class="card hero"><div class="badge">سؤال اليوم</div><h2 id="dq">...</h2><div id="dopts" class="options"></div><div id="dfeedback"></div></div>
        <div class="card"><h2>اختبر نفسك</h2><p>10 أسئلة • مستوى متوسط إلى صعب • مؤقت واحد للاختبار كامل</p><label>نطاق الاختبار</label><select id="scope"></select><button class="full" onclick="startTest()">ابدأ الاختبار</button></div>
        <div class="card"><h2>أخطائي</h2><p>الأسئلة التي أخطأت فيها ترجع لك بنظام مراجعة ذكي حتى تتقنها.</p><button class="secondary full" onclick="showMistakes()">فتح صفحة أخطائي</button><button class="ghost full" onclick="startMistakeTest()">اختبرني بأخطائي</button></div>
        <div class="card"><h2>الإعدادات</h2><label>مدة اختبار 10 أسئلة بالدقائق</label><input id="minutes" type="number" min="1" max="60"><button class="secondary full" onclick="saveSettings()">حفظ</button></div>
      </div>
    </section>
    <section id="test" class="hidden card testbox"><div class="testhead"><div><span id="testScope" class="badge"></span><b id="progress"></b></div><div id="timer" class="timer">10:00</div></div><h2 id="tq"></h2><div id="topts" class="options"></div><div class="row between"><button class="ghost" onclick="finishTest(true)">إنهاء الاختبار</button><button id="nextBtn" class="hidden" onclick="nextQuestion()">التالي</button></div></section>
    <section id="results" class="hidden card"></section>
    <section id="mistakes" class="hidden card"><div class="row between"><h2>أخطائي</h2><button class="ghost" onclick="goHome()">رجوع</button></div><div id="mistakeList"></div></section>
  </main>
</div><script>
let ME=null, daily=null, TEST=null, tIndex=0, answers=[], timerId=null, remain=0, startedAt=0;
const $=s=>document.querySelector(s); const show=id=>{['#auth','#home','#test','#results','#mistakes'].forEach(x=>$(x).classList.add('hidden'));$(id).classList.remove('hidden')};
async function api(url,opt={}){opt.headers={'Content-Type':'application/json',...(opt.headers||{})};let r=await fetch(url,opt);let d=await r.json().catch(()=>({}));if(!r.ok)throw d;return d}
async function boot(){try{ME=await api('/api/me');if(!ME.auth){show('#auth');return}$('#logout').classList.remove('hidden');show('#home');renderMe();await loadDaily()}catch(e){show('#auth')}}
function renderMe(){$('#streak').textContent=ME.streak;$('#mastered').textContent=ME.mastered;$('#wrong').textContent=ME.wrong;$('#minutes').value=ME.test_minutes;$('#scope').innerHTML=['القانون كامل',...ME.categories].map(x=>`<option>${x}</option>`).join('')}
async function register(){try{await api('/api/register',{method:'POST',body:JSON.stringify({username:$('#username').value,pin:$('#pin').value})});boot()}catch(e){$('#authMsg').textContent=e.error||'تعذر إنشاء الحساب'}}
async function login(){try{await api('/api/login',{method:'POST',body:JSON.stringify({username:$('#username').value,pin:$('#pin').value})});boot()}catch(e){$('#authMsg').textContent=e.error||'تعذر الدخول'}}
$('#logout').onclick=async()=>{await api('/api/logout',{method:'POST'});location.reload()}
async function loadDaily(){let d=await api('/api/daily');daily=d.question;$('#dq').textContent=daily.q;$('#dfeedback').innerHTML='';$('#dopts').innerHTML=daily.options.map((o,i)=>`<button class="option" onclick="answerDaily(${i},this)">${o}</button>`).join('')}
async function answerDaily(i,el){[...$('#dopts').children].forEach(x=>x.disabled=true);let d=await api('/api/answer',{method:'POST',body:JSON.stringify({qid:daily.id,choice:i})});[...$('#dopts').children].forEach((x,j)=>{if(j===d.correct_index)x.classList.add('correct');if(j===i&&!d.correct)x.classList.add('wrong')});$('#dfeedback').innerHTML=`<div class="feedback"><b>${d.correct?'إجابة صحيحة ✓':'إجابة غير صحيحة'}</b><p>${d.explanation}</p><small>${d.reference} • صفحة ${d.page}</small></div>`;ME=await api('/api/me');renderMe()}
async function startTest(scope){let s=scope||$('#scope').value;let d=await api('/api/test?scope='+encodeURIComponent(s));beginTest(d)}
async function startMistakeTest(){let d=await api('/api/mistake-test');if(!d.questions.length){alert('لا توجد أخطاء تحتاج مراجعة حاليًا 👏');return}beginTest(d)}
function beginTest(d){TEST=d;tIndex=0;answers=[];remain=d.minutes*60;startedAt=Date.now();show('#test');$('#testScope').textContent=d.scope;renderT();clearInterval(timerId);tick();timerId=setInterval(()=>{remain--;tick();if(remain<=0)finishTest(false)},1000)}
function tick(){let m=Math.floor(remain/60),s=remain%60;$('#timer').textContent=`${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`}
function renderT(){let q=TEST.questions[tIndex];$('#progress').textContent=`السؤال ${tIndex+1} من ${TEST.questions.length}`;$('#tq').textContent=q.q;$('#nextBtn').classList.add('hidden');$('#topts').innerHTML=q.options.map((o,i)=>`<button class="option" onclick="chooseT(${i},this)">${o}</button>`).join('')}
function chooseT(i,el){[...$('#topts').children].forEach(x=>x.disabled=true);answers[tIndex]={qid:TEST.questions[tIndex].id,choice:i};el.style.borderColor='#c7f542';$('#nextBtn').classList.remove('hidden');$('#nextBtn').textContent=tIndex===TEST.questions.length-1?'إظهار النتيجة':'التالي'}
function nextQuestion(){if(!answers[tIndex])return;if(tIndex===TEST.questions.length-1){finishTest(false);return}tIndex++;renderT()}
async function finishTest(manual){if(manual&&!confirm('هل تريد إنهاء الاختبار الآن؟'))return;clearInterval(timerId);TEST.questions.forEach((q,i)=>{if(!answers[i])answers[i]={qid:q.id,choice:-1}});let valid=answers.filter(x=>x.choice>=0);let d=await api('/api/test/submit',{method:'POST',body:JSON.stringify({scope:TEST.scope,answers:valid,seconds_used:Math.floor((Date.now()-startedAt)/1000)})});show('#results');let wrong=d.details.filter(x=>!x.correct);$('#results').innerHTML=`<h1>${d.score}/${TEST.questions.length}</h1><p>نتيجتك في ${TEST.scope}</p>${wrong.length?`<h3>راجع الأخطاء</h3>`+wrong.map(x=>`<div class="feedback"><b>${x.question}</b><p>إجابتك: ${x.your}<br>الصحيح: ${x.correct_answer}</p><p>${x.explanation}</p><small>${x.reference} • صفحة ${x.page}</small></div>`).join(''):'<div class="feedback"><b>ممتاز! لا توجد أخطاء في الأسئلة المجابة.</b></div>'}<button class="full" onclick="goHome()">العودة للرئيسية</button>`}
async function showMistakes(){let d=await api('/api/mistakes');show('#mistakes');$('#mistakeList').innerHTML=d.items.length?d.items.map(x=>`<div class="mistake"><b>${x.question}</b><p>آخر إجابة خاطئة: ${x.last_answer||'-'}<br>الإجابة الصحيحة: ${x.correct_answer}</p><small>${x.category} • أخطأت ${x.wrong_count} مرة ${x.next_due?'• المراجعة القادمة '+x.next_due:''}</small></div>`).join(''):'<p>لا توجد أخطاء تحتاج مراجعة 👏</p>'}
async function saveSettings(){try{await api('/api/settings',{method:'POST',body:JSON.stringify({test_minutes:+$('#minutes').value})});alert('تم حفظ الإعدادات')}catch(e){alert(e.error||'تعذر الحفظ')}}
async function goHome(){ME=await api('/api/me');show('#home');renderMe();loadDaily()}
boot();

</script></body></html>
'''

@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.post('/api/register')
def register():
    d=request.get_json(force=True); username=(d.get('username') or '').strip(); pin=str(d.get('pin') or '')
    if len(username)<3 or len(pin)<4 or len(pin)>8 or not pin.isdigit(): return jsonify(error='اسم المستخدم 3 أحرف على الأقل، والـPIN من 4 إلى 8 أرقام.'),400
    if User.query.filter_by(username=username).first(): return jsonify(error='اسم المستخدم مستخدم بالفعل.'),409
    u=User(username=username,pin_hash=generate_password_hash(pin)); db.session.add(u); db.session.commit(); session['uid']=u.id; touch_streak(u)
    return jsonify(ok=True)

@app.post('/api/login')
def login():
    d=request.get_json(force=True); u=User.query.filter_by(username=(d.get('username') or '').strip()).first(); pin=str(d.get('pin') or '')
    if not u or not check_password_hash(u.pin_hash,pin): return jsonify(error='اسم المستخدم أو PIN غير صحيح.'),401
    session['uid']=u.id; touch_streak(u); return jsonify(ok=True)

@app.post('/api/logout')
def logout(): session.clear(); return jsonify(ok=True)

@app.get('/api/me')
def me():
    u=user()
    if not u: return jsonify(auth=False,categories=CATEGORIES)
    touch_streak(u)
    total=Progress.query.filter_by(user_id=u.id).count(); wrong=Progress.query.filter_by(user_id=u.id, mastered=False).filter(Progress.wrong_count>0).count(); mastered=Progress.query.filter_by(user_id=u.id,mastered=True).count()
    results=TestResult.query.filter_by(user_id=u.id).order_by(TestResult.created_at.desc()).limit(5).all()
    return jsonify(auth=True,username=u.username,test_minutes=u.test_minutes,streak=u.streak,total_answered=total,wrong=wrong,mastered=mastered,categories=CATEGORIES,recent=[{'score':r.score,'total':r.total,'scope':r.scope,'date':r.created_at.strftime('%Y-%m-%d')} for r in results])

@app.get('/api/daily')
def daily():
    u=user();
    if not u: return jsonify(error='login'),401
    touch_streak(u)
    qs=sorted(QUESTIONS,key=lambda q: due_priority(u,q))
    best=due_priority(u,qs[0])[0]
    pool=[q for q in qs if due_priority(u,q)[0]==best]
    seed=f'{date.today().isoformat()}-{u.id}'
    q=random.Random(seed).choice(pool)
    return jsonify(question=public_q(q))

@app.post('/api/answer')
def answer():
    u=user();
    if not u:return jsonify(error='login'),401
    d=request.get_json(force=True); qid=d.get('qid'); choice=d.get('choice')
    if qid not in QMAP:return jsonify(error='question'),404
    correct,q=record_answer(u,qid,choice)
    return jsonify(correct=correct,correct_index=q['a'],explanation=q['exp'],reference=q['ref'],page=q['page'])

@app.get('/api/test')
def test():
    u=user();
    if not u:return jsonify(error='login'),401
    scope=request.args.get('scope','القانون كامل')
    base=QUESTIONS if scope=='القانون كامل' else [q for q in QUESTIONS if q['category']==scope]
    if len(base)<10: base=base* ((10+len(base)-1)//len(base))
    rnd=random.Random(os.urandom(16)); chosen=rnd.sample(base,10)
    return jsonify(scope=scope,minutes=u.test_minutes,questions=[public_q(q) for q in chosen])

@app.post('/api/test/submit')
def submit_test():
    u=user();
    if not u:return jsonify(error='login'),401
    d=request.get_json(force=True); answers=d.get('answers',[]); score=0; details=[]
    for item in answers:
        qid=item.get('qid'); choice=item.get('choice')
        if qid not in QMAP or choice is None: continue
        correct,q=record_answer(u,qid,choice); score += int(correct)
        details.append({'qid':qid,'question':q['q'],'correct':correct,'your':q['options'][int(choice)],'correct_answer':q['options'][q['a']],'explanation':q['exp'],'reference':q['ref'],'page':q['page']})
    r=TestResult(user_id=u.id,score=score,total=len(answers),scope=d.get('scope','القانون كامل'),seconds_used=int(d.get('seconds_used',0))); db.session.add(r); db.session.commit()
    return jsonify(score=score,total=len(answers),details=details)

@app.get('/api/mistakes')
def mistakes():
    u=user();
    if not u:return jsonify(error='login'),401
    ps=Progress.query.filter_by(user_id=u.id,mastered=False).filter(Progress.wrong_count>0).order_by(Progress.wrong_count.desc()).all()
    out=[]
    for p in ps:
        q=QMAP.get(p.qid)
        if q: out.append({'qid':p.qid,'question':q['q'],'category':q['category'],'wrong_count':p.wrong_count,'last_answer':p.last_answer,'correct_answer':q['options'][q['a']],'next_due':p.next_due.isoformat() if p.next_due else None})
    return jsonify(items=out)

@app.get('/api/mistake-test')
def mistake_test():
    u=user();
    if not u:return jsonify(error='login'),401
    ps=Progress.query.filter_by(user_id=u.id,mastered=False).filter(Progress.wrong_count>0).all(); qs=[QMAP[p.qid] for p in ps if p.qid in QMAP]
    if not qs:return jsonify(questions=[])
    chosen=(qs if len(qs)<=10 else random.sample(qs,10))
    return jsonify(scope='مراجعة الأخطاء',minutes=u.test_minutes,questions=[public_q(q) for q in chosen])

@app.post('/api/settings')
def settings():
    u=user();
    if not u:return jsonify(error='login'),401
    m=int(request.get_json(force=True).get('test_minutes',10))
    if m<1 or m>60:return jsonify(error='الوقت من 1 إلى 60 دقيقة.'),400
    u.test_minutes=m; db.session.commit(); return jsonify(ok=True)

@app.get('/health')
def health(): return 'ok',200

with app.app_context(): db.create_all()
if __name__=='__main__': app.run(debug=True)
