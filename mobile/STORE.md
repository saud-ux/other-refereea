# بيانات المتجر

ما يُلصق في App Store Connect عند إرسال الإصدار الأول للمراجعة. الحدود بين
قوسين هي حدود آبل لعدد الأحرف.

## معلومات التطبيق

| الحقل | القيمة |
|---|---|
| الاسم (30) | قوانين اللعبة |
| العنوان الفرعي (30) | تدريب الحكّام على قانون الكرة |
| الفئة الأساسية | Education |
| الفئة الثانوية | Sports |
| رابط الخصوصية | https://other-refereea.onrender.com/privacy |
| رابط الدعم | https://other-refereea.onrender.com/support |
| التصنيف العمري | 4+ (أجب «لا» أو «None» عن كل أسئلة الاستبيان) |
| السعر | مجاني |

## النص الترويجي (170)

٣٥٠ سؤالًا من قانون كرة القدم 2026/27 بالشرح ورقم الصفحة، واختبارات مؤقّتة، ومراجعة ذكية لأخطائك، وتذكير يومي بسؤال جديد.

## الوصف (4000)

```
تطبيق لإعداد حكّام كرة القدم على قانون اللعبة 2026/27، بالعربية.

بنك من ٣٥٠ سؤالًا مبنيّ من الكتاب مباشرة، يغطّي المواد السبع عشرة كاملة، وبروتوكول حكم الفيديو المساعد، وتعديلات الموسم الجديد. لكل سؤال شرح ومرجع ورقم صفحة.

سؤال اليوم
سؤال جديد كل يوم، وتذكير في الوقت الذي تختاره. لا يصلك التذكير إن كنت حللته.

اختبارات كالامتحان
اختر المادة وعدد الأسئلة، مع مؤقّت دقيقة لكل سؤال أو بدونه. التنقّل حرّ بين الأسئلة، والتصحيح كلّه في النهاية. والأسئلة موزّعة على المواد بالتساوي فلا تطغى مادة على أخرى.

مراجعة متباعدة للأخطاء
السؤال الذي أخطأت فيه يعود إليك على فترات حتى تتقنه ثلاث مرات متتالية.

المذاكرة
تصفّح كل الأسئلة مع إجاباتها وشروحها، وابحث فيها، وصفّها حسب المادة أو حالتك فيها، واحفظ ما تريد في المفضلة.

إحصائياتك
دقّتك في كل مادة، وتغطيتك للمواد، ورزنامة نشاطك، وسجلّ اختباراتك، واثنا عشر إنجازًا.

لوحة الترتيب
ترتيب الحكّام حسب عدد الأسئلة المتقنة، مع سلسلة أيام كل حكم.

خصوصيتك
يكفي اسم مستخدم وكلمة مرور. لا بريد ولا رقم جوال، ولا إعلانات ولا تتبّع. وتحذف حسابك وكل بياناتك من التطبيق متى شئت.
```

## الكلمات المفتاحية (100)

```
حكم,حكام,تحكيم,قانون,كرة القدم,تسلل,فار,ركلة جزاء,اختبار,مراجعة,بطاقة حمراء,حكم مساعد
```

## اللقطات

من مجلد `store-screenshots/`:

- **iPhone 6.9"**: الملفات `iphone-*.png` بالترتيب ١ إلى ٥.
- **iPad 13"**: الملفات `ipad-*.png`.

## خصوصية التطبيق (App Privacy)

في App Store Connect ← App Privacy ← Get Started:

- **Do you or your third-party partners collect data from this app?** نعم.
- **Identifiers ← User ID**: اسم المستخدم. Linked to user: نعم. Tracking: لا. الغرض: App Functionality.
- **Usage Data ← Product Interaction**: الإجابات والتقدّم ونتائج الاختبارات. Linked to user: نعم. Tracking: لا. الغرض: App Functionality.
- لا شيء غير ذلك: لا موقع، ولا جهات اتصال، ولا بيانات مالية، ولا معرّف إعلانات.

## حساب تجريبي للمراجِع

آبل تشترط حسابًا يدخل به المراجِع. أنشئ من الموقع حسابًا باسم مثل `apple_review`
وكلمة مرور من أرقام، وحلّ فيه أسئلة قليلة حتى لا تبدو الصفحات فارغة، ثم اكتبه
في App Review Information ← Sign-in required.

## ملاحظات للمراجِع (App Review Notes)

المراجِع يقرأ الإنجليزية، فتُلصق كما هي:

```
Laws of the Game is a training app for Arabic-speaking football referees, built around the
2026/27 Laws of the Game: 350 questions with explanations, timed tests, spaced-repetition review
of mistakes, per-law statistics and a referee leaderboard.

Native iOS functionality:
- Daily reminder delivered through Apple Push Notifications (APNs). Enable it in the Account tab
  (top-left avatar on iPhone), then tap "إرسال تجربة" (Send test) to receive one immediately.
- Haptic feedback when answering the daily question and while answering test questions.
- System share sheet for sharing a test result (button "مشاركة" on the result screen).
- Status bar follows the light/dark theme; native launch screen that waits for the server
  and explains connection problems.
- Full iPad support with a sidebar layout.

Account: the account holds the referee's progress, the spaced-repetition schedule for wrong
answers and their leaderboard position, so the app requires signing in. Registration needs only
a username and a numeric password. Account deletion: Account tab > "حذف الحساب نهائيًا".

Demo account — username: apple_review   password: <اكتب الرقم هنا>
```
