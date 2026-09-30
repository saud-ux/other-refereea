# -*- coding: utf-8 -*-
"""واجهة الموقع: الصفحة الواحدة، ملف التعريف، وعامل الخدمة والأيقونة."""

import json

CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;min-height:100dvh;background:var(--bg-grad);color:var(--text);
  font-family:"IBM Plex Sans Arabic",system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;
  font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}
button,input,select,textarea{font:inherit;color:inherit}
h1,h2,h3,h4{margin:0;line-height:1.4;font-weight:700}
p{margin:0}
a{color:inherit}
[hidden]{display:none!important}
::selection{background:var(--brand);color:#fff}

/* ══════════════ الألوان ══════════════ */
:root{
  --brand:#16a34a; --brand-2:#a3e635; --hot:#f97316; --info:#0ea5e9;
  --r:18px; --r-sm:12px; --r-lg:24px;
  --bg:#f1f6f2;
  --bg-grad:radial-gradient(1100px 500px at 85% -14%, #dcf5e2 0%, transparent 62%), #f1f6f2;
  --surface:#fff; --surface-2:#f4f9f5; --surface-3:#eaf2ec;
  --line:#dbe7de; --line-soft:#e8f0ea;
  --text:#0d1f14; --muted:#5c7566;
  --ok:#15803d; --ok-bg:#dcfce7; --bad:#c2410c; --bad-bg:#ffedd5;
  --shadow:0 2px 4px #0f291b0a, 0 14px 34px #0f291b12;
  --btn-grad:linear-gradient(135deg,#22c55e,#15803d); --btn-ink:#fff;
  --ring:#16a34a55;
  --mark-book:#0f3d22; --mark-line:#a3e635;
}
:root[data-theme="dark"]{
  --bg:#071410;
  --bg-grad:radial-gradient(1200px 520px at 80% -10%, #12331f 0%, transparent 60%), #071410;
  --surface:#0f2318; --surface-2:#132b1d; --surface-3:#17341f;
  --line:#1e4230; --line-soft:#173525;
  --text:#eaf5ee; --muted:#8fae9c;
  --ok:#4ade80; --ok-bg:#14532d66; --bad:#f87171; --bad-bg:#7f1d1d55;
  --shadow:0 18px 44px #0006;
  --btn-grad:linear-gradient(135deg,var(--brand-2),var(--brand)); --btn-ink:#06210f;
  --ring:#a3e63566;
  --mark-book:#a3e635; --mark-line:#0a2e18;
}
.ic{width:1.25em;height:1.25em;flex:none;vertical-align:-.25em}

/* ══════════════ الدخول ══════════════ */
.authwrap{min-height:100dvh;display:grid;place-items:center;padding:24px 16px}
.authcard{width:100%;max-width:430px;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r-lg);padding:30px 26px;box-shadow:var(--shadow)}
.authcard .logo{justify-content:center;padding:0 0 18px}
.authcard h1{font-size:22px;text-align:center}
.authcard .sub{color:var(--muted);text-align:center;font-size:13.5px;margin:6px 0 22px}
.seg{display:grid;grid-template-columns:1fr 1fr;gap:4px;background:var(--surface-2);
  border:1px solid var(--line);border-radius:var(--r-sm);padding:4px;margin-bottom:18px}
.seg button{border:0;background:transparent;border-radius:9px;padding:9px;font-weight:600;
  font-size:14px;cursor:pointer;color:var(--muted)}
.seg button.on{background:var(--surface);color:var(--text);box-shadow:0 1px 3px #0002}
:root[data-theme="dark"] .seg button.on{background:var(--surface-3);color:var(--brand-2)}

/* ══════════════ الحقول ══════════════ */
.field{margin-bottom:14px}
.field label{display:block;font-size:12.5px;font-weight:600;color:var(--muted);margin-bottom:6px}
input,select{width:100%;padding:12px 14px;border-radius:var(--r-sm);border:1px solid var(--line);
  background:var(--surface-2);color:var(--text);font-size:15px;outline:none;transition:.15s}
input:focus,select:focus{border-color:var(--brand);box-shadow:0 0 0 3px var(--ring);background:var(--surface)}
input[type=number]{-moz-appearance:textfield}
.hint{font-size:12px;color:var(--muted);margin-top:6px}
.err{color:var(--bad);font-size:13px;margin-top:10px;min-height:1.2em;font-weight:600}

/* ══════════════ الأزرار ══════════════ */
.btn{border:0;border-radius:var(--r-sm);padding:12px 18px;font-weight:700;font-size:14.5px;
  cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:8px;
  transition:transform .08s, filter .15s; white-space:nowrap}
.btn:active{transform:translateY(1px)}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn:focus-visible{outline:3px solid var(--ring);outline-offset:2px}
.btn.primary{background:var(--btn-grad);color:var(--btn-ink);box-shadow:0 8px 22px #16a34a3d}
.btn.primary:hover:not(:disabled){filter:brightness(1.06)}
.btn.soft{background:var(--surface-2);color:var(--text);border:1px solid var(--line)}
.btn.soft:hover:not(:disabled){background:var(--surface-3)}
.btn.ghost{background:transparent;color:var(--muted);border:1px solid var(--line)}
.btn.ghost:hover:not(:disabled){color:var(--text);border-color:var(--brand)}
.btn.danger{background:transparent;color:var(--bad);border:1px solid var(--bad)}
.btn.block{width:100%}
.btn.sm{padding:8px 13px;font-size:13px;border-radius:10px}
.btnrow{display:flex;gap:9px;flex-wrap:wrap}

/* ══════════════ الهيكل ══════════════ */
.shell{display:grid;grid-template-columns:238px 1fr;min-height:100dvh}
.side{border-inline-end:1px solid var(--line);background:var(--surface);padding:20px 14px;
  display:flex;flex-direction:column;gap:4px;position:sticky;top:0;height:100dvh;overflow-y:auto}
.logo{display:flex;align-items:center;gap:11px;padding:4px 8px 20px}
.logomark{width:46px;height:46px;flex:none;display:grid;place-items:center}
.logomark .mark{width:100%;height:100%;display:block;
  filter:drop-shadow(0 6px 14px #06210f26)}
.logotxt b{display:block;font-size:15.5px;line-height:1.25}
.logotxt small{color:var(--muted);font-size:11.5px}
.nav{display:flex;flex-direction:column;gap:3px}
.nav button{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:var(--r-sm);
  color:var(--muted);border:0;background:transparent;font-size:14.5px;font-weight:500;
  cursor:pointer;text-align:start;width:100%}
.nav button:hover{background:var(--surface-2);color:var(--text)}
.nav button.on{background:linear-gradient(90deg,#1c7a3f,#15803d);color:#fff;font-weight:600;
  box-shadow:0 8px 20px #16a34a33}
:root[data-theme="dark"] .nav button.on{background:linear-gradient(90deg,#1c7a3f,#123f24);color:#eaffef}
.nav .badge-n{margin-inline-start:auto;background:var(--hot);color:#fff;font-size:11px;
  font-weight:700;border-radius:999px;padding:1px 7px;min-width:20px;text-align:center}
.nav button.on .badge-n{background:#ffffff33}
.sidefoot{margin-top:auto;border-top:1px solid var(--line-soft);padding-top:14px}
.userchip{display:flex;align-items:center;gap:10px;padding:8px;border-radius:var(--r-sm);
  background:var(--surface-2);width:100%;border:0;cursor:pointer;text-align:start}
.avatar{width:34px;height:34px;border-radius:10px;flex:none;display:grid;place-items:center;
  background:linear-gradient(140deg,#34d399,#0ea5e9);color:#04231a;font-weight:700;font-size:13px}
.userchip b{font-size:13.5px;display:block}
.userchip small{display:flex;flex-wrap:wrap;gap:2px 10px;color:var(--muted);font-size:11px}
.content{min-width:0;display:flex;flex-direction:column}
main{padding:0 26px 40px;max-width:1120px;width:100%;margin-inline:auto;flex:1}

/* ══════════════ الشريط العلوي ══════════════ */
.top{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:20px 0 18px}
.hello b{font-size:21px;display:block}
.hello span{color:var(--muted);font-size:13.5px}
.topacts{display:flex;align-items:center;gap:9px;flex:none}
.pill{display:inline-flex;align-items:center;gap:7px;padding:8px 13px;border-radius:999px;
  border:1px solid var(--line);background:var(--surface);font-size:13px;font-weight:600}
.pill.fire{border-color:#f9731640;background:linear-gradient(120deg,#f9731622,transparent);color:var(--hot)}
.iconbtn{width:38px;height:38px;border-radius:var(--r-sm);border:1px solid var(--line);
  background:var(--surface);display:grid;place-items:center;cursor:pointer;color:var(--text);flex:none}
.iconbtn:hover{border-color:var(--brand)}

/* ══════════════ البطاقات والإحصاء ══════════════ */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
  padding:19px;box-shadow:var(--shadow)}
.card h3{font-size:16.5px;margin-bottom:4px}
.card .sub{color:var(--muted);font-size:13px;margin-bottom:14px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
  padding:15px 16px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.tile::before{content:"";position:absolute;inset:auto -30px -34px auto;width:96px;height:96px;
  border-radius:50%;background:var(--brand);opacity:.07}
.tile .k{display:flex;align-items:center;gap:7px;color:var(--muted);font-size:12.5px;font-weight:500}
.tile .v{font-size:29px;font-weight:700;line-height:1.25;margin-top:5px;font-variant-numeric:tabular-nums}
.tile .d{font-size:11.5px;color:var(--muted)}
.tile.accent .v{color:var(--brand)}
:root[data-theme="dark"] .tile.accent .v{color:var(--brand-2)}
.tile.hot .v{color:var(--hot)}
.cols{display:grid;grid-template-columns:1.55fr 1fr;gap:15px;margin-top:15px;align-items:start}
.stack{display:flex;flex-direction:column;gap:15px}
.sechead{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:26px 0 12px}
.sechead h2{font-size:18px}

/* ══════════════ السؤال ══════════════ */
.badge{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:600;
  padding:5px 11px;border-radius:999px;background:#16a34a1a;color:var(--brand);margin-bottom:11px}
:root[data-theme="dark"] .badge{background:#a3e6351a;color:var(--brand-2)}
.badge.dim{background:var(--surface-2);color:var(--muted)}
.badgerow{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.badgerow .badge{margin-bottom:11px}
.qtext{font-size:17.5px;font-weight:600;line-height:1.85;margin:0 0 15px}
.opts{display:grid;gap:9px}
.opt{display:flex;align-items:center;gap:11px;padding:13px 14px;border-radius:13px;width:100%;
  border:1px solid var(--line);background:var(--surface-2);font-size:14.5px;font-weight:500;
  cursor:pointer;text-align:start;color:var(--text);transition:.12s}
.opt:hover:not(:disabled){border-color:var(--brand)}
.opt:disabled{cursor:default}
.opt .key{width:25px;height:25px;border-radius:8px;flex:none;display:grid;place-items:center;
  background:var(--surface);border:1px solid var(--line);font-size:12px;color:var(--muted);font-weight:700}
.opt.right{border-color:var(--ok);background:var(--ok-bg)}
.opt.right .key{background:var(--ok);color:#fff;border-color:var(--ok)}
.opt.wrong{border-color:var(--bad);background:var(--bad-bg)}
.opt.wrong .key{background:var(--bad);color:#fff;border-color:var(--bad)}
.opt.picked{border-color:var(--brand);box-shadow:0 0 0 3px var(--ring)}
.explain{margin-top:13px;padding:13px 15px;border-radius:13px;background:var(--surface-2);
  border:1px solid var(--line-soft);font-size:13.5px;line-height:1.85}
.explain b{color:var(--ok)}
.explain b.no{color:var(--bad)}
.explain small{display:flex;flex-wrap:wrap;gap:2px 16px;margin-top:7px;color:var(--muted);font-size:11.5px}

/* ══════════════ عناصر مساعدة ══════════════ */
.chiprow{display:flex;gap:7px;flex-wrap:wrap}
.chip{padding:7px 13px;border-radius:999px;border:1px solid var(--line);background:var(--surface);
  font-size:12.5px;font-weight:600;color:var(--muted);cursor:pointer}
.chip:hover{border-color:var(--brand);color:var(--text)}
.chip.on{background:var(--brand);border-color:var(--brand);color:#fff}
:root[data-theme="dark"] .chip.on{background:var(--brand-2);border-color:var(--brand-2);color:#06210f}
.meter{margin-bottom:13px}
.meter:last-child{margin-bottom:0}
.meter .lab{display:flex;justify-content:space-between;gap:10px;font-size:12.5px;margin-bottom:6px}
.meter .lab b{font-weight:600}
.meter .lab span{color:var(--muted);font-variant-numeric:tabular-nums;flex:none}
.bar{height:8px;border-radius:99px;background:var(--surface-2);overflow:hidden;border:1px solid var(--line-soft)}
.bar i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--brand),var(--brand-2));transition:width .5s}
.lead{display:flex;align-items:center;gap:11px;padding:10px 0;border-bottom:1px solid var(--line-soft);font-size:13.5px}
.lead:last-child{border-bottom:0}
.rank{width:26px;height:26px;border-radius:9px;flex:none;display:grid;place-items:center;
  background:var(--surface-2);font-size:12px;font-weight:700;color:var(--muted)}
.rank.g{background:linear-gradient(140deg,#fde047,#f59e0b);color:#3b2600}
.rank.s{background:linear-gradient(140deg,#e5e7eb,#9ca3af);color:#1f2937}
.rank.b{background:linear-gradient(140deg,#fdba74,#c2762c);color:#3b2600}
.lead b{flex:1;font-weight:600;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lead span{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums;flex:none}
.lead.me{background:var(--surface-2);border-radius:11px;padding:10px;border-bottom:0;margin-top:6px}
.lead .you{flex:none;padding:2px 8px;border-radius:999px;background:var(--brand);color:#fff;
  font-size:10.5px;font-weight:700}
:root[data-theme="dark"] .lead .you{background:var(--brand-2);color:#06210f}
.heat{display:grid;grid-template-columns:repeat(14,1fr);gap:4px}
.heat i{aspect-ratio:1;border-radius:4px;background:var(--surface-2);border:1px solid var(--line-soft)}
.heat i.l1{background:#16a34a40;border-color:transparent}
.heat i.l2{background:#16a34a80;border-color:transparent}
.heat i.l3{background:var(--brand);border-color:transparent}
.empty{text-align:center;color:var(--muted);padding:34px 16px;font-size:14px}
.empty .big{font-size:34px;display:block;margin-bottom:8px}
.timer{font-size:32px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:1px;color:var(--brand)}
:root[data-theme="dark"] .timer{color:var(--brand-2)}
.timer.warn{color:var(--hot)}
.prog{height:6px;border-radius:99px;background:var(--surface-2);overflow:hidden;border:1px solid var(--line-soft)}
.prog i{display:block;height:100%;background:linear-gradient(90deg,var(--brand),var(--brand-2));border-radius:99px;transition:width .3s}
.score{font-size:52px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
.divider{height:1px;background:var(--line-soft);margin:16px 0}
.ach{display:flex;align-items:center;gap:11px;padding:10px 0;font-size:13.5px}
.ach .ico{width:36px;height:36px;border-radius:11px;flex:none;display:grid;place-items:center;
  background:var(--surface-2);font-size:17px;filter:grayscale(1);opacity:.45}
.ach.got .ico{filter:none;opacity:1;background:var(--ok-bg)}
.ach b{display:block;font-weight:600}
.ach small{color:var(--muted);font-size:11.5px}

/* ══════════════ قائمة المذاكرة ══════════════ */
.qitem{border:1px solid var(--line);border-radius:14px;background:var(--surface);margin-bottom:10px;overflow:hidden}
.qitem>button.head{display:flex;align-items:flex-start;gap:11px;width:100%;padding:14px;
  border:0;background:transparent;cursor:pointer;text-align:start;color:var(--text)}
.qitem .qi-body{flex:1;min-width:0}
.qitem .qi-body b{font-weight:600;font-size:14.5px;display:block;line-height:1.7}
.qitem .qi-meta{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px;font-size:11px;color:var(--muted)}
.qitem .qi-meta span{background:var(--surface-2);padding:2px 8px;border-radius:999px}
.qitem .star{background:transparent;border:0;cursor:pointer;color:var(--muted);padding:2px;flex:none}
.qitem .star.on{color:#f59e0b}
.qitem .det{padding:0 14px 14px;border-top:1px solid var(--line-soft);margin-top:-1px}
.qitem .det .opts{margin-top:13px}

/* ══════════════ التنبيهات والنوافذ ══════════════ */
#toasts{position:fixed;inset-block-end:24px;inset-inline:0;z-index:90;display:flex;
  flex-direction:column-reverse;align-items:center;gap:8px;pointer-events:none;padding:0 12px}
.toast{background:var(--surface);border:1px solid var(--line);border-radius:999px;
  padding:10px 18px;box-shadow:var(--shadow);font-size:13.5px;font-weight:600;
  animation:pop .25s ease;max-width:92vw}
.toast.ok{border-color:var(--ok);color:var(--ok)}
.toast.bad{border-color:var(--bad);color:var(--bad)}
@keyframes pop{from{opacity:0;transform:translateY(12px)}}
.modal{position:fixed;inset:0;z-index:100;background:#0008;display:grid;place-items:center;padding:18px;
  backdrop-filter:blur(3px)}
.modal .box{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);
  padding:24px;max-width:400px;width:100%;box-shadow:var(--shadow)}
.modal h3{font-size:18px;margin-bottom:8px}
.modal .sub{color:var(--muted);font-size:13.5px;margin-bottom:18px}

/* ══════════════ شريط الجوال ══════════════ */
.tabbar{display:none;position:sticky;bottom:0;z-index:20;grid-template-columns:repeat(5,1fr);
  gap:2px;padding:8px 6px calc(8px + env(safe-area-inset-bottom));border-top:1px solid var(--line);
  background:color-mix(in srgb, var(--surface) 92%, transparent);backdrop-filter:blur(12px)}
.tabbar button{display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--muted);
  border:0;background:transparent;font-size:10.5px;font-weight:600;cursor:pointer;padding:4px 0;position:relative}
.tabbar button .ic{width:21px;height:21px}
.tabbar button.on{color:var(--brand)}
:root[data-theme="dark"] .tabbar button.on{color:var(--brand-2)}
.tabbar .dot{position:absolute;top:2px;inset-inline-end:26%;width:7px;height:7px;border-radius:50%;background:var(--hot)}

@media(max-width:940px){
  #toasts{inset-block-end:calc(80px + env(safe-area-inset-bottom))}
  .shell{grid-template-columns:1fr}
  .side{display:none}
  .tabbar{display:grid}
  main{padding:0 16px 24px}
  .tiles{grid-template-columns:repeat(2,1fr)}
  .cols{grid-template-columns:1fr}
  .top{padding:16px 0 14px;align-items:flex-start}
  .hello b{font-size:18px}
  .qtext{font-size:16px}
  .heat{grid-template-columns:repeat(10,1fr)}
}
@media(max-width:380px){ .tiles{grid-template-columns:1fr} }
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
'''

HTML = r'''<!doctype html>
<html lang="ar" dir="rtl" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#071410">
<meta name="description" content="منصّة تدريب الحكّام على قوانين كرة القدم: مذاكرة واختبارات ومراجعة ذكية للأخطاء.">
<title>قوانين اللعبة</title>
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icon.svg">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="قوانين اللعبة">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
<script>
(function(){try{
  var t=localStorage.getItem('theme')||'auto';
  var d=t==='dark'||(t==='auto'&&matchMedia('(prefers-color-scheme:dark)').matches);
  document.documentElement.dataset.theme=d?'dark':'light';
  document.querySelector('meta[name=theme-color]').content=d?'#071410':'#f1f6f2';
}catch(e){}})();
</script>
<style>__CSS__</style>
</head>
<body>
<div id="toasts"></div>

<!-- ═══════════ شاشة الدخول ═══════════ -->
<div id="authScreen" class="authwrap" hidden>
  <div class="authcard">
    <div class="logo"><div class="logomark" id="authLogo"></div>
      <div class="logotxt"><b>قوانين اللعبة</b></div></div>
    <div class="seg">
      <button id="tabLogin" class="on" onclick="A.mode('login')">تسجيل الدخول</button>
      <button id="tabReg" onclick="A.mode('register')">حساب جديد</button>
    </div>
    <form id="authForm" onsubmit="return A.submit(event)">
      <div class="field"><label for="u">اسم المستخدم</label>
        <input id="u" autocomplete="username" required minlength="3" placeholder="مثال: saud07"></div>
      <div class="field" id="nameField" hidden><label for="dn">الاسم الظاهر (اختياري)</label>
        <input id="dn" autocomplete="nickname" placeholder="يظهر في لوحة الترتيب"></div>
      <div class="field"><label for="p">كلمة المرور</label>
        <input id="p" type="password" inputmode="numeric" pattern="[0-9]*" required
               minlength="4" maxlength="8" placeholder="من 4 إلى 8 أرقام"
               dir="ltr" lang="en" spellcheck="false" autocapitalize="off" autocorrect="off"></div>
      <button class="btn primary block" id="authBtn" type="submit">دخول</button>
      <p class="err" id="authMsg"></p>
    </form>
  </div>
</div>

<!-- ═══════════ التطبيق ═══════════ -->
<div id="shell" class="shell" hidden>
  <aside class="side">
    <div class="logo"><div class="logomark" id="sideLogo"></div>
      <div class="logotxt"><b>قوانين اللعبة</b></div></div>
    <nav class="nav" id="nav"></nav>
    <div class="sidefoot">
      <button class="userchip" onclick="R.go('account')">
        <div class="avatar" id="avatar"></div>
        <div><b id="sideName"></b><small id="sideMeta"></small></div>
      </button>
    </div>
  </aside>
  <div class="content">
    <main id="view"></main>
    <nav class="tabbar" id="tabbar"></nav>
  </div>
</div>

<script>__JS__</script>
</body>
</html>
'''

JS = r'''
/* ══════════════════ الأيقونات ══════════════════ */
const IC={
 home:'<path d="M3 10.7 12 3l9 7.7V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
 book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
 timer:'<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9.5 2h5"/>',
 flag:'<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
 chart:'<path d="M3 21h18"/><rect x="5" y="10" width="3.6" height="8" rx="1"/><rect x="10.2" y="5" width="3.6" height="13" rx="1"/><rect x="15.4" y="13" width="3.6" height="5" rx="1"/>',
 trophy:'<path d="M8 3h8v5a4 4 0 0 1-8 0z"/><path d="M8 4.5H5.5A2.5 2.5 0 0 0 8 8.5M16 4.5h2.5A2.5 2.5 0 0 1 16 8.5"/><path d="M12 12v4M9.5 21h5M10 18h4"/>',
 user:'<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>',
 sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 moon:'<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
 check:'<path d="M20 6 9 17l-5-5"/>',
 close:'<path d="M18 6 6 18M6 6l12 12"/>',
 star:'<path d="m12 3.2 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.5l-5.6 2.9 1.1-6.2L3 9.8l6.2-.9z"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
 logout:'<path d="M14 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5"/><path d="M10 17 5 12l5-5M5 12h11"/>',
 play:'<path d="M7.5 4.8v14.4L19 12z"/>',
 refresh:'<path d="M20.5 12a8.5 8.5 0 1 1-2.5-6"/><path d="M21 3v5.5h-5.5"/>',
 back:'<path d="M9 6l6 6-6 6"/>',
 next:'<path d="M15 6l-6 6 6 6"/>',
 spark:'<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 whistle:'<circle cx="8.5" cy="13.5" r="5.5"/><path d="M14 11h7l-1.5 3H14M8.5 13.5h0"/>',
 download:'<path d="M12 3v12M7.5 10.5 12 15l4.5-4.5M4 20h16"/>',
 bell:'<path d="M18 8.5a6 6 0 1 0-12 0c0 5.2-2 6.5-2 6.5h16s-2-1.3-2-6.5z"/><path d="M13.7 19a2 2 0 0 1-3.4 0"/>'
};
const MARK=__MARK__;
const ic=(n,c)=>`<svg class="ic ${c||""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${IC[n]||""}</svg>`;

/* ══════════════════ أدوات ══════════════════ */
const $=s=>document.querySelector(s);
const el=(h)=>{const d=document.createElement("div");d.innerHTML=h.trim();return d.firstElementChild;};
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const AR="٠١٢٣٤٥٦٧٨٩";
const num=n=>String(n==null?"":n).replace(/[0-9]/g,d=>AR[+d]);
const pct=n=>num(Math.round(n||0))+"٪";
/* تمييز العدد في العربية يتبع آخر رقمين: مفرد، مثنى، جمع قلّة، ثم مفرد منصوب.
   الترتيب في كل قائمة: واحد، ثم اثنان، ثم من ٣ إلى ١٠، ثم من ١١ إلى ٩٩، ثم مضاعفات المئة */
const NOUN={
  day:["يوم واحد","يومان","أيام","يومًا","يوم"],
  streak:["يوم متتالٍ","يومان متتاليان","أيام متتالية","يومًا متتاليًا","يوم متتالٍ"],
  q:["سؤال واحد","سؤالان","أسئلة","سؤالًا","سؤال"],
  due:["سؤال مستحق اليوم","سؤالان مستحقان اليوم","أسئلة مستحقة اليوم","سؤالًا مستحقًا اليوم","سؤال مستحق اليوم"],
  mastered:["سؤال متقن","سؤالان متقنان","أسئلة متقنة","سؤالًا متقنًا","سؤال متقن"],
  answer:["إجابة واحدة","إجابتان","إجابات","إجابةً","إجابة"],
  test:["اختبار واحد","اختباران","اختبارات","اختبارًا","اختبار"],
  law:["مادة واحدة","مادتان","مواد","مادةً","مادة"],
  min:["دقيقة واحدة","دقيقتان","دقائق","دقيقةً","دقيقة"],
};
function unit(n,k){
  const f=NOUN[k], r=n%100;
  if(n===1) return f[0];
  if(n===2) return f[1];
  if(r>=3&&r<=10) return f[2];
  if(r>=11&&r<=99) return f[3];
  return f[4];
}
// المفرد والمثنى يحملان العدد في لفظهما، فلا يسبقهما رقم
const qty=(n,k)=>(n===1||n===2)?unit(n,k):num(n)+" "+unit(n,k);
function toast(msg,kind){
  const t=el(`<div class="toast ${kind||""}">${esc(msg)}</div>`);
  $("#toasts").appendChild(t);
  setTimeout(()=>{t.style.opacity="0";t.style.transition="opacity .3s";setTimeout(()=>t.remove(),300);},2600);
}
async function api(url,opt){
  opt=opt||{};
  if(opt.body&&typeof opt.body!=="string"){opt.body=JSON.stringify(opt.body);opt.method=opt.method||"POST";}
  opt.headers=Object.assign({"Content-Type":"application/json"},opt.headers||{});
  let r;
  try{ r=await fetch(url,opt); }catch(e){ throw {error:"تعذّر الاتصال بالخادم. تحقّق من الإنترنت."}; }
  let d={}; try{ d=await r.json(); }catch(e){}
  if(r.status===401&&S.me){ S.me=null; boot(); throw {error:"انتهت الجلسة، سجّل الدخول من جديد."}; }
  if(!r.ok) throw (d&&d.error?d:{error:"حدث خطأ غير متوقع."});
  return d;
}
function confirmBox(title,sub,okLabel,danger){
  return new Promise(res=>{
    const m=el(`<div class="modal"><div class="box">
      <h3>${esc(title)}</h3><p class="sub">${esc(sub)}</p>
      <div class="btnrow"><button class="btn ${danger?"danger":"primary"}" data-ok style="flex:1">${esc(okLabel)}</button>
      <button class="btn soft" data-no style="flex:1">إلغاء</button></div></div></div>`);
    const done=v=>{m.remove();res(v);};
    m.querySelector("[data-ok]").onclick=()=>done(true);
    m.querySelector("[data-no]").onclick=()=>done(false);
    m.onclick=e=>{if(e.target===m)done(false);};
    document.body.appendChild(m);
    m.querySelector("[data-ok]").focus();
  });
}

/* ══════════════════ المظهر ══════════════════ */
const Theme={
  get(){ try{return localStorage.getItem("theme")||"auto";}catch(e){return "auto";} },
  apply(){
    const t=this.get();
    const dark=t==="dark"||(t==="auto"&&matchMedia("(prefers-color-scheme:dark)").matches);
    document.documentElement.dataset.theme=dark?"dark":"light";
    const m=document.querySelector("meta[name=theme-color]");
    if(m) m.content=dark?"#071410":"#f1f6f2";
    return dark;
  },
  toggle(){
    const dark=document.documentElement.dataset.theme==="dark";
    try{localStorage.setItem("theme",dark?"light":"dark");}catch(e){}
    this.apply(); R.render();
  }
};
matchMedia("(prefers-color-scheme:dark)").addEventListener("change",()=>{if(Theme.get()==="auto"){Theme.apply();R.render();}});

/* ══════════════════ الحالة ══════════════════ */
const S={me:null,view:"home",daily:null,dailyDone:false,dailyResult:null,
  test:null,tIdx:0,answers:[],timerId:null,remain:0,startedAt:0,result:null,
  cfg:{scope:"",count:10,timer:true,mode:"mixed"},
  study:{scope:"",filter:"all",search:"",items:[],open:null,loading:false},
  stats:null,board:null,mistakes:null};

/* ══════════════════ التنقّل ══════════════════ */
const PAGES=[
  {k:"home",  t:"الرئيسية",   i:"home"},
  {k:"study", t:"المذاكرة",   i:"book"},
  {k:"test",  t:"اختبار",     i:"timer"},
  {k:"mistakes",t:"أخطائي",   i:"flag",  count:()=>S.me&&S.me.stats.wrong},
  {k:"stats", t:"إحصائياتي",  i:"chart"},
  {k:"board", t:"الترتيب",    i:"trophy",desk:true},
  {k:"account",t:"الحساب",    i:"user",  desk:true}
];
const R={
  async go(k){
    if(S.view==="test"&&S.test&&k!=="test"){
      const ok=await confirmBox("إنهاء الاختبار؟","سيُلغى الاختبار الحالي ولن تُحتسب نتيجته.","اخرج",true);
      if(!ok) return;
      stopTimer(); S.test=null;
    }
    S.view=k; window.scrollTo(0,0); this.render();
  },
  paintNav(){
    $("#nav").innerHTML=PAGES.map(p=>{
      const n=p.count?p.count():0;
      return `<button class="${S.view===p.k?"on":""}" onclick="R.go('${p.k}')">${ic(p.i)}<span>${p.t}</span>${n?`<span class="badge-n">${num(n)}</span>`:""}</button>`;
    }).join("");
    $("#tabbar").innerHTML=PAGES.filter(p=>!p.desk).map(p=>{
      const n=p.count?p.count():0;
      return `<button class="${S.view===p.k?"on":""}" onclick="R.go('${p.k}')">${ic(p.i)}${n?`<span class="dot"></span>`:""}<span>${p.t}</span></button>`;
    }).join("");
  },
  render(){
    this.paintNav();
    if(S.me) setSideMeta(S.me.stats);   // وإلا بقي الشريط الجانبي على أرقام قديمة
    const v=VIEWS[S.view]||VIEWS.home;
    $("#view").innerHTML="";
    $("#view").appendChild(el(topBar()));
    v();
  }
};
function mount(html){ $("#view").appendChild(el(html)); }
function themeBtn(){ const d=document.documentElement.dataset.theme==="dark";
  return `<button class="iconbtn" onclick="Theme.toggle()" title="تبديل المظهر" aria-label="تبديل المظهر">${ic(d?"sun":"moon")}</button>`; }
function greet(){ const h=new Date().getHours();
  return h<5?"ليلة موفقة":h<12?"صباح الخير":h<17?"نهارك سعيد":"مساء الخير"; }
function topBar(){
  const m=S.me, st=m.stats;
  const titles={home:`${greet()} يا ${esc(m.user.name)} 👋`,study:"المذاكرة",test:"اختبر نفسك",
    mistakes:"أخطائي",stats:"إحصائياتي",board:"لوحة الترتيب",account:"الحساب"};
  const subs={
    home: st.due?`عندك ${qty(st.due,"due")}`:"ابدأ بسؤال اليوم ثم اختبر نفسك",
    study:`${qty(st.total_questions,"q")} في ${qty(st.laws,"law")}`,
    test:"اختر المادة وعدد الأسئلة وشغّل المؤقت أو أوقفه",
    mistakes:"الأسئلة التي أخطأت فيها ترجع لك بنظام مراجعة متباعدة حتى تتقنها",
    stats:"ملخّص أدائك منذ بداية الاشتراك",
    board:"الترتيب حسب عدد الأسئلة المتقنة",
    account:"بياناتك وإعداداتك"};
  return `<div class="top">
    <div class="hello"><b>${titles[S.view]||""}</b><span>${esc(subs[S.view]||"")}</span></div>
    <div class="topacts">
      ${st.streak?`<div class="pill fire">🔥 ${qty(st.streak,"day")}</div>`:""}
      ${themeBtn()}
    </div></div>`;
}
'''

JS += r'''
/* ══════════════════ الإقلاع والدخول ══════════════════ */
const A={
  cur:"login",
  mode(m){ this.cur=m;
    $("#tabLogin").classList.toggle("on",m==="login");
    $("#tabReg").classList.toggle("on",m==="register");
    $("#nameField").hidden=m!=="register";
    $("#authBtn").textContent=m==="login"?"دخول":"إنشاء الحساب";
    $("#authMsg").textContent="";
  },
  async submit(e){
    e.preventDefault();
    const b=$("#authBtn"); b.disabled=true;
    const body={username:$("#u").value.trim(),pin:$("#p").value};
    if(this.cur==="register") body.display_name=$("#dn").value.trim();
    try{
      await api(this.cur==="login"?"/api/login":"/api/register",{body});
      $("#authMsg").textContent=""; $("#p").value="";
      await boot();
      toast(this.cur==="login"?"تم تسجيل الدخول":"تم إنشاء الحساب","ok");
    }catch(err){ $("#authMsg").textContent=err.error||"تعذّر إتمام العملية."; }
    finally{ b.disabled=false; }
    return false;
  }
};
async function boot(){
  Theme.apply();
  $("#authLogo").innerHTML=MARK; $("#sideLogo").innerHTML=MARK;
  let me=null;
  try{ me=await api("/api/me"); }catch(e){}
  if(!me||!me.auth){
    S.me=null; $("#shell").hidden=true; $("#authScreen").hidden=false; A.mode("login"); return;
  }
  S.me=me; S.cfg.scope=S.cfg.scope||me.all_scope;
  S.study.scope=S.study.scope||me.all_scope;
  $("#authScreen").hidden=true; $("#shell").hidden=false;
  const nm=me.user.name||me.user.username;
  $("#avatar").textContent=nm.slice(0,2);
  $("#sideName").textContent=nm;
  setSideMeta(me.stats);
  R.render();
  Push.init().then(()=>{ if(S.view==="account") R.render(); });
  api("/api/settings",{body:{tz_offset:tzOffset()}}).catch(()=>{});
}
function setSideMeta(st){
  const m=$("#sideMeta"); if(!m||!st) return;
  m.innerHTML=`<span>${st.mastered?qty(st.mastered,"mastered"):"لم تبدأ بعد"}</span>${st.answered?`<span>${pct(st.accuracy)} دقة</span>`:""}`;
}
async function refreshMe(){ try{ S.me=await api("/api/me"); }catch(e){} }
async function logout(){
  if(!await confirmBox("تسجيل الخروج","سيبقى تقدّمك محفوظًا في حسابك.","خروج")) return;
  try{ await api("/api/logout",{body:{}}); }catch(e){}
  location.reload();
}

/* ══════════════════ عرض سؤال ══════════════════ */
function optsHTML(q,handler,state){
  return `<div class="opts">`+q.options.map((o,i)=>{
    let cls="";
    if(state){ if(i===state.correct) cls="right"; else if(i===state.picked) cls="wrong"; }
    const key=state? (i===state.correct?"✓":num(i+1)) : num(i+1);
    return `<button class="opt ${cls}" ${state?"disabled":""} ${handler?`onclick="${handler}(${i},this)"`:""}>
      <span class="key">${key}</span><span>${esc(o)}</span></button>`;
  }).join("")+`</div>`;
}
function explainHTML(d,correct){
  return `<div class="explain"><b class="${correct?"":"no"}">${correct?"إجابة صحيحة ✓":"إجابة غير صحيحة"}</b>
    <p>${esc(d.explanation||d.exp||"")}</p>
    <small><span>${esc(d.reference||d.ref||"")}</span>${(d.page)?"<span>صفحة "+num(d.page)+"</span>":""}</small></div>`;
}

/* ══════════════════ الرئيسية ══════════════════ */
const VIEWS={};
function tilesHTML(){
  const st=S.me.stats;
  return `<div class="tiles">
    <div class="tile accent"><div class="k">${ic("check")} تم إتقانه</div>
      <div class="v">${num(st.mastered)}</div><div class="d">من ${qty(st.total_questions,"q")}</div></div>
    <div class="tile hot"><div class="k">${ic("flag")} يحتاج مراجعة</div>
      <div class="v">${num(st.wrong)}</div><div class="d">${st.due?qty(st.due,"due"):"لا شيء مستحق اليوم"}</div></div>
    <div class="tile"><div class="k">${ic("chart")} دقة الإجابات</div>
      <div class="v">${pct(st.accuracy)}</div><div class="d">${st.answered?qty(st.answered,"answer"):"لم تجب بعد"}</div></div>
    <div class="tile"><div class="k">${ic("timer")} اختبارات</div>
      <div class="v">${num(st.tests)}</div><div class="d">${st.best_score!=null?"أفضل نتيجة "+num(st.best_score)+" من "+num(st.best_total):"لم تبدأ بعد"}</div></div>
  </div>`;
}
function updateChrome(){
  R.paintNav();
  const t=document.querySelector("#view .tiles");
  if(t) t.outerHTML=tilesHTML();
  setSideMeta(S.me.stats);
}
VIEWS.home=function(){
  mount(tilesHTML());

  mount(`<div class="cols">
    <div class="card" id="dailyCard"><div class="empty">جارٍ تحميل سؤال اليوم…</div></div>
    <div class="stack">
      <div class="card">
        <h3>ابدأ اختبارًا</h3><p class="sub">اختر عدد الأسئلة ثم انطلق، أو خصّص المادة والمؤقت من صفحة الاختبار.</p>
        <div class="chiprow" style="margin-bottom:12px">
          ${[5,10,20,30].map(n=>`<button class="chip ${S.cfg.count===n?"on":""}" onclick="S.cfg.count=${n};R.render()">${qty(n,"q")}</button>`).join("")}
        </div>
        <button class="btn primary block" onclick="Test.start()">${ic("play")} ابدأ الآن</button>
        <div class="btnrow" style="margin-top:9px">
          <button class="btn soft" style="flex:1" onclick="Test.mistakes()">اختبرني بأخطائي</button>
          <button class="btn ghost" style="flex:1" onclick="R.go('test')">تخصيص</button>
        </div>
      </div>
      <div class="card" id="progCard"><h3>تقدّمك في المواد</h3><div class="empty">جارٍ التحميل…</div></div>
    </div></div>`);
  loadDaily(); loadHomeProgress();
};
async function loadDaily(){
  const c=$("#dailyCard"); if(!c) return;
  try{
    const d=await api("/api/daily");
    S.daily=d.question; S.dailyDone=!!d.answered; S.dailyResult=d.answered?d:null;
    if(!S.daily){ c.innerHTML=`<div class="empty">${ic("check")}<p style="margin-top:8px">أنهيت كل الأسئلة المتاحة اليوم.</p></div>`; return; }
    renderDaily();
  }catch(e){ c.innerHTML=`<div class="empty">${esc(e.error||"تعذّر تحميل سؤال اليوم")}</div>`; }
}
function dailyHead(q){
  return `<div class="badgerow"><div class="badge">${ic("spark")} سؤال اليوم</div>
    <div class="badge dim">${esc(q.category)}</div>
    ${q.topic?`<div class="badge dim">${esc(q.topic)}</div>`:""}</div>
    <p class="qtext">${esc(q.q)}</p>`;
}
function renderDaily(){
  const c=$("#dailyCard"); if(!c||!S.daily) return;
  const q=S.daily, r=S.dailyResult;
  if(r){   // أُجيب عنه اليوم: يُعرض بحالته، ولا يُستبدل بسؤال جديد
    c.innerHTML=dailyHead(q)+optsHTML(q,null,{correct:r.correct_index,picked:r.your_index})+
      `<div id="dFeed">${explainHTML(r,r.correct)}
        <p class="hint" style="margin-top:12px">${ic("timer")} عد غدًا لسؤال جديد.</p></div>`;
    return;
  }
  c.innerHTML=dailyHead(q)+optsHTML(q,"answerDaily")+`<div id="dFeed"></div>`;
}
async function answerDaily(i){
  if(S.dailyDone) return; S.dailyDone=true;
  const q=S.daily;
  try{
    const d=await api("/api/answer",{body:{qid:q.id,choice:i,mode:"daily"}});
    S.dailyResult=Object.assign({},d,{your_index:i});
    $("#dailyCard").querySelector(".opts").outerHTML=optsHTML(q,null,{correct:d.correct_index,picked:i});
    $("#dFeed").innerHTML=explainHTML(d,d.correct)+
      `<p class="hint" style="margin-top:12px">${ic("timer")} عد غدًا لسؤال جديد.</p>`;
    await refreshMe(); updateChrome();
  }catch(e){ S.dailyDone=false; toast(e.error||"تعذّر إرسال الإجابة","bad"); }
}
async function loadHomeProgress(){
  const c=$("#progCard"); if(!c) return;
  try{
    const d=await api("/api/stats"); S.stats=d;
    const rows=d.by_law.filter(r=>r.answered>0).sort((a,b)=>a.accuracy-b.accuracy).slice(0,4);
    if(!rows.length){ c.innerHTML=`<h3>تقدّمك في المواد</h3><div class="empty">أجب عن بعض الأسئلة ليظهر تقدّمك هنا.</div>`; return; }
    c.innerHTML=`<h3>تقدّمك في المواد</h3><p class="sub">أضعف أربع مواد لديك.</p>`+
      rows.map(r=>meterHTML(r.title,r.accuracy)).join("")+
      `<button class="btn ghost block sm" style="margin-top:14px" onclick="R.go('stats')">كل الإحصائيات</button>`;
  }catch(e){ c.innerHTML=`<h3>تقدّمك في المواد</h3><div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
}
function meterHTML(title,v){
  return `<div class="meter"><div class="lab"><b>${esc(title)}</b><span>${pct(v)}</span></div>
    <div class="bar"><i style="width:${Math.max(2,Math.round(v))}%"></i></div></div>`;
}
'''

JS += r'''
/* ══════════════════ المذاكرة ══════════════════ */
const FILTERS=[["all","الكل"],["unseen","لم أحلّه"],["wrong","أخطأت فيه"],["mastered","أتقنته"],["saved","المفضلة"]];
VIEWS.study=function(){
  const sc=S.study;
  mount(`<div class="card">
    <div class="field" style="margin-bottom:12px">
      <label for="stSearch">ابحث في نص الأسئلة</label>
      <input id="stSearch" placeholder="اكتب كلمة مثل: التسلل، ركلة الجزاء…" value="${esc(sc.search)}">
    </div>
    <div class="field" style="margin-bottom:12px"><label for="stScope">المادة</label>
      <select id="stScope">${S.me.scopes.map(s=>`<option ${s===sc.scope?"selected":""}>${esc(s)}</option>`).join("")}</select></div>
    <div class="chiprow">${FILTERS.map(f=>`<button class="chip ${sc.filter===f[0]?"on":""}" onclick="Study.filter('${f[0]}')">${f[1]}</button>`).join("")}</div>
  </div>`);
  mount(`<div class="sechead"><h2 id="stCount">…</h2>
    <button class="btn soft sm" onclick="Study.quiz()">${ic("play")} اختبرني في هذه القائمة</button></div>`);
  mount(`<div id="stList"><div class="empty">جارٍ التحميل…</div></div>`);
  const si=$("#stSearch");
  si.oninput=()=>{ clearTimeout(Study._t); Study._t=setTimeout(()=>{sc.search=si.value.trim();Study.load();},350); };
  $("#stScope").onchange=e=>{ sc.scope=e.target.value; Study.load(); };
  Study.load();
};
const Study={
  filter(f){ S.study.filter=f; R.render(); },
  async load(){
    const sc=S.study, box=$("#stList"); if(!box) return;
    box.innerHTML=`<div class="empty">جارٍ التحميل…</div>`;
    try{
      const d=await api(`/api/study?scope=${encodeURIComponent(sc.scope)}&filter=${sc.filter}&search=${encodeURIComponent(sc.search)}`);
      sc.items=d.items;
      const cEl=$("#stCount"); if(cEl) cEl.textContent=qty(d.total,"q");
      if(!d.items.length){ box.innerHTML=`<div class="empty"><span class="big">🔍</span>لا توجد أسئلة مطابقة.</div>`; return; }
      box.innerHTML=d.items.map(q=>qItemHTML(q)).join("");
    }catch(e){ box.innerHTML=`<div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
  },
  toggle(id){
    const sc=S.study; sc.open=sc.open===id?null:id;
    const q=sc.items.find(x=>x.id===id); if(!q) return;
    const node=document.getElementById("qi-"+id);
    if(node) node.outerHTML=qItemHTML(q);
  },
  async star(id,ev){
    ev.stopPropagation();
    const q=S.study.items.find(x=>x.id===id); if(!q) return;
    const on=!q.saved;
    try{ await api("/api/bookmark",{body:{qid:id,on}}); q.saved=on;
      const node=document.getElementById("qi-"+id); if(node) node.outerHTML=qItemHTML(q);
      toast(on?"أُضيف إلى المفضلة":"أُزيل من المفضلة","ok");
    }catch(e){ toast(e.error||"تعذّر الحفظ","bad"); }
  },
  quiz(){ const sc=S.study; Test.start({scope:sc.scope,filter:sc.filter,search:sc.search}); }
};
function qItemHTML(q){
  const open=S.study.open===q.id;
  const state=q.status==="mastered"?["متقن","ok"]:q.status==="wrong"?["يحتاج مراجعة","hot"]:null;
  return `<div class="qitem" id="qi-${q.id}">
    <button class="head" onclick="Study.toggle('${q.id}')">
      <div class="qi-body"><b>${esc(q.q)}</b>
        <div class="qi-meta"><span>${esc(q.category)}</span>${q.topic?`<span>${esc(q.topic)}</span>`:""}
          ${state?`<span style="color:var(--${state[1]})">${state[0]}</span>`:""}
          <span>صفحة ${num(q.page)}</span></div></div>
      <span class="star ${q.saved?"on":""}" onclick="Study.star('${q.id}',event)" title="المفضلة">${ic("star")}</span>
    </button>
    ${open?`<div class="det">${optsHTML(q,null,{correct:q.a,picked:-1})}
      <div class="explain"><p>${esc(q.exp)}</p>
        <small><span>${esc(q.ref)}</span><span>صفحة ${num(q.page)}</span></small></div></div>`:""}
  </div>`;
}

/* ══════════════════ الاختبار ══════════════════ */
VIEWS.test=function(){
  if(S.test){ return renderTestRun(); }
  if(S.result){ return renderResult(); }
  const c=S.cfg;
  mount(`<div class="cols"><div class="card">
    <h3>إعدادات الاختبار</h3><p class="sub">النتيجة تُحتسب في إحصائياتك ولوحة الترتيب.</p>
    <div class="field"><label for="cfgScope">المادة</label>
      <select id="cfgScope" onchange="S.cfg.scope=this.value">
        ${S.me.scopes.map(s=>`<option ${s===c.scope?"selected":""}>${esc(s)}</option>`).join("")}</select></div>
    <div class="field"><label>عدد الأسئلة</label>
      <div class="chiprow">${[5,10,20,30,50].map(n=>`<button class="chip ${c.count===n?"on":""}" onclick="S.cfg.count=${n};R.render()">${num(n)}</button>`).join("")}</div></div>
    <div class="field"><label>طريقة الاختيار</label>
      <div class="chiprow">
        <button class="chip ${c.mode==="mixed"?"on":""}" onclick="S.cfg.mode='mixed';R.render()">ذكي</button>
        <button class="chip ${c.mode==="random"?"on":""}" onclick="S.cfg.mode='random';R.render()">عشوائي</button>
        <button class="chip ${c.mode==="hard"?"on":""}" onclick="S.cfg.mode='hard';R.render()">الأصعب</button>
      </div>
      <div class="hint">«ذكي» يقدّم ما لم تحلّه وما أخطأت فيه وما حان موعد مراجعته.</div></div>
    <div class="field"><label>المؤقت</label>
      <div class="chiprow">
        <button class="chip ${c.timer?"on":""}" onclick="S.cfg.timer=true;R.render()">مؤقت (${qty(S.me.user.test_minutes,"min")})</button>
        <button class="chip ${!c.timer?"on":""}" onclick="S.cfg.timer=false;R.render()">بدون مؤقت</button>
      </div></div>
    <button class="btn primary block" onclick="Test.start()">${ic("play")} ابدأ الاختبار</button>
  </div>
  <div class="stack">
    <div class="card"><h3>مراجعة الأخطاء</h3>
      <p class="sub">اختبار سريع من الأسئلة التي أخطأت فيها ولم تتقنها بعد.</p>
      <button class="btn soft block" onclick="Test.mistakes()">${ic("flag")} اختبرني بأخطائي (${num(S.me.stats.wrong)})</button></div>
    <div class="card" id="histCard"><h3>آخر الاختبارات</h3><div class="empty">جارٍ التحميل…</div></div>
  </div></div>`);
  loadHistoryCard();
};
async function loadHistoryCard(){
  const c=$("#histCard"); if(!c) return;
  try{
    const d=S.stats||await api("/api/stats"); S.stats=d;
    if(!d.history.length){ c.innerHTML=`<h3>آخر الاختبارات</h3><div class="empty">لم تخض أي اختبار بعد.</div>`; return; }
    c.innerHTML=`<h3>آخر الاختبارات</h3>`+d.history.slice(0,6).map(h=>{
      const good=h.total&&h.score/h.total>=.8;
      return `<div class="lead"><span class="rank ${good?"g":""}">${num(h.score)}</span>
        <b>${esc(h.scope)}</b><span>${esc(h.when)}</span></div>`;}).join("");
  }catch(e){ c.innerHTML=`<h3>آخر الاختبارات</h3><div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
}
const Test={
  async start(over){
    const c=Object.assign({},S.cfg,over||{});
    try{
      const qs=new URLSearchParams({scope:c.scope,count:c.count,mode:c.mode||"mixed"});
      if(c.filter) qs.set("filter",c.filter);
      if(c.search) qs.set("search",c.search);
      const d=await api("/api/test?"+qs.toString());
      if(!d.questions.length){ toast("لا توجد أسئلة مطابقة لهذا الاختيار","bad"); return; }
      begin(d,c.timer!==false);
    }catch(e){ toast(e.error||"تعذّر بدء الاختبار","bad"); }
  },
  async mistakes(){
    try{
      const d=await api("/api/test?mode=mistakes&count="+S.cfg.count);
      if(!d.questions.length){ toast("لا توجد أخطاء تحتاج مراجعة","ok"); return; }
      begin(d,S.cfg.timer!==false);
    }catch(e){ toast(e.error||"تعذّر بدء المراجعة","bad"); }
  },
  pick(i,node){
    if(S.answers[S.tIdx]!=null) return;
    S.answers[S.tIdx]={qid:S.test.questions[S.tIdx].id,choice:i};
    [...node.parentNode.children].forEach(b=>b.disabled=true);
    node.classList.add("picked");
    const nb=$("#nextBtn"); nb.hidden=false; nb.focus();
  },
  next(){ if(S.answers[S.tIdx]==null) return;
    if(S.tIdx===S.test.questions.length-1) return this.finish(false);
    S.tIdx++; R.render(); },
  async finish(manual){
    if(manual && !await confirmBox("إنهاء الاختبار","سيتم تصحيح ما أجبت عنه فقط.","إنهاء")) return;
    stopTimer();
    const answers=S.answers.filter(a=>a&&a.choice>=0);
    const payload={scope:S.test.scope,answers,seconds_used:Math.floor((Date.now()-S.startedAt)/1000),
                   asked:S.test.questions.length,mode:S.test.mode};
    const total=S.test.questions.length;
    S.test=null; stopTimer();
    try{
      const d=await api("/api/test/submit",{body:payload});
      d.asked=total; S.result=d; await refreshMe(); S.stats=null; R.render();
    }catch(e){ toast(e.error||"تعذّر إرسال النتيجة","bad"); R.render(); }
  },
  close(){ S.result=null; R.render(); }
};
function begin(d,useTimer){
  S.test=d; S.tIdx=0; S.answers=[]; S.result=null; S.startedAt=Date.now();
  S.remain=useTimer?d.minutes*60:0; S.useTimer=useTimer;
  S.view="test"; R.render();
  if(useTimer){ stopTimer(); tick(); S.timerId=setInterval(()=>{ S.remain--; tick(); if(S.remain<=0) Test.finish(false); },1000); }
}
function stopTimer(){ if(S.timerId){clearInterval(S.timerId);S.timerId=null;} }
function tick(){ const t=$("#timer"); if(!t) return;
  const m=Math.max(0,Math.floor(S.remain/60)), s=Math.max(0,S.remain%60);
  t.textContent=num(String(m).padStart(2,"0"))+":"+num(String(s).padStart(2,"0"));
  t.classList.toggle("warn",S.remain<=60); }
function renderTestRun(){
  const t=S.test,q=t.questions[S.tIdx],n=t.questions.length;
  const done=S.answers.filter(a=>a).length;
  mount(`<div class="card">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:14px">
      <div><div class="badge">${esc(t.scope)}</div>
        <div style="font-size:12.5px;color:var(--muted)">السؤال ${num(S.tIdx+1)} من ${num(n)}</div></div>
      ${S.useTimer?`<div style="text-align:start"><div style="font-size:11px;color:var(--muted)">الوقت المتبقي</div>
        <div class="timer" id="timer">--:--</div></div>`:`<div class="badge dim">بدون مؤقت</div>`}
    </div>
    <div class="prog" style="margin-bottom:16px"><i style="width:${Math.round(done/n*100)}%"></i></div>
    <p class="qtext">${esc(q.q)}</p>
    ${optsHTML(q,"Test.pick")}
    <div class="btnrow" style="margin-top:16px;justify-content:space-between">
      <button class="btn ghost sm" onclick="Test.finish(true)">إنهاء الاختبار</button>
      <button class="btn primary" id="nextBtn" hidden onclick="Test.next()">
        ${S.tIdx===n-1?"إظهار النتيجة":"السؤال التالي"} ${ic("next")}</button>
    </div>
    <div class="hint" style="margin-top:10px">اختصار: اضغط الأرقام من ${num(1)} إلى ${num(q.options.length)} للاختيار، و Enter للانتقال.</div>
  </div>`);
  tick();
}
function renderResult(){
  const d=S.result, wrong=d.details.filter(x=>!x.correct), pctv=d.total?d.score/d.total*100:0;
  const mood=pctv>=90?["نتيجة ممتازة"]:pctv>=70?["نتيجة جيدة"]:pctv>=50?["نتيجة متوسطة"]:["تحتاج مراجعة"];
  mount(`<div class="card" style="text-align:center">
    <div class="score" style="margin-top:6px">${num(d.score)}<span style="font-size:22px;color:var(--muted)"> من ${num(d.asked||d.total)}</span></div>
    <p class="sub" style="margin-top:8px">${mood[0]}</p>
    ${d.scope?`<div class="badge dim" style="margin-bottom:14px">${esc(d.scope)}</div>`:""}
    <div class="btnrow" style="justify-content:center;margin-top:6px">
      <button class="btn primary" onclick="S.result=null;Test.start()">${ic("refresh")} اختبار جديد</button>
      <button class="btn soft" onclick="Test.close()">العودة</button></div>
  </div>`);
  if(wrong.length){
    mount(`<div class="sechead"><h2>راجع أخطاءك (${num(wrong.length)})</h2></div>`);
    wrong.forEach(x=>mount(`<div class="card" style="margin-bottom:10px">
      <div class="badge dim">${esc(x.category)}</div>
      <p class="qtext" style="font-size:15.5px">${esc(x.question)}</p>
      <div class="explain"><b class="no">إجابتك: ${esc(x.your)}</b>
        <p style="margin-top:6px"><b style="color:var(--ok)">الصحيح: ${esc(x.correct_answer)}</b></p>
        <p style="margin-top:6px">${esc(x.explanation)}</p>
        <small><span>${esc(x.reference)}</span><span>صفحة ${num(x.page)}</span></small></div></div>`));
  }else if(d.total){
    mount(`<div class="card"><div class="empty">${ic("check")}<p style="margin-top:8px">لا توجد أخطاء في الأسئلة التي أجبت عنها.</p></div></div>`);
  }
}
document.addEventListener("keydown",e=>{
  if(!S.test) return;
  const q=S.test.questions[S.tIdx];
  if(e.key>="1"&&e.key<="9"){
    const i=+e.key-1; if(i<q.options.length){ const b=document.querySelectorAll(".opts .opt")[i]; if(b&&!b.disabled) b.click(); }
  } else if(e.key==="Enter"){ const nb=$("#nextBtn"); if(nb&&!nb.hidden) nb.click(); }
});
'''

JS += r'''
/* ══════════════════ أخطائي ══════════════════ */
VIEWS.mistakes=function(){
  mount(`<div class="card" style="margin-bottom:15px">
    <div class="btnrow">
      <button class="btn primary" style="flex:1" onclick="Test.mistakes()">${ic("play")} اختبرني بأخطائي</button>
      <button class="btn soft" onclick="Mist.load()">${ic("refresh")} تحديث</button>
    </div></div>`);
  mount(`<div id="mList"><div class="empty">جارٍ التحميل…</div></div>`);
  Mist.load();
};
const Mist={
  async load(){
    const box=$("#mList"); if(!box) return;
    try{
      const d=await api("/api/mistakes"); S.mistakes=d.items;
      if(!d.items.length){ box.innerHTML=`<div class="card"><div class="empty">${ic("check")}<p style="margin-top:8px">لا توجد أخطاء تحتاج مراجعة حاليًا.</p></div></div>`; return; }
      box.innerHTML=d.items.map(m=>`<div class="qitem">
        <button class="head" onclick="Mist.toggle('${m.qid}')">
          <div class="qi-body"><b>${esc(m.question)}</b>
            <div class="qi-meta"><span>${esc(m.category)}</span>
              <span style="color:var(--hot)">أخطأت ${num(m.wrong_count)} ${m.wrong_count===1?"مرة":"مرات"}</span>
              ${m.next_due?`<span>المراجعة ${esc(m.next_due)}</span>`:""}</div></div></button>
        <div class="det" id="md-${m.qid}" hidden>
          <div class="explain" style="margin-top:13px">
            <b class="no">آخر إجابة خاطئة: ${esc(m.last_answer||"لم تُسجّل")}</b>
            <p style="margin-top:6px"><b style="color:var(--ok)">الصحيح: ${esc(m.correct_answer)}</b></p>
            <p style="margin-top:6px">${esc(m.exp)}</p>
            <small><span>${esc(m.ref)}</span><span>صفحة ${num(m.page)}</span></small></div></div></div>`).join("");
    }catch(e){ box.innerHTML=`<div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
  },
  toggle(id){ const d=document.getElementById("md-"+id); if(d) d.hidden=!d.hidden; }
};

/* ══════════════════ الإحصائيات ══════════════════ */
VIEWS.stats=function(){
  mount(`<div id="stWrap"><div class="empty">جارٍ التحميل…</div></div>`);
  (async()=>{
    const box=$("#stWrap"); if(!box) return;
    try{
      const d=await api("/api/stats"); S.stats=d;
      const o=d.overall;
      box.innerHTML=`<div class="tiles">
        <div class="tile accent"><div class="k">${ic("chart")} الدقة الكلّية</div><div class="v">${pct(o.accuracy)}</div><div class="d">${o.answered?qty(o.answered,"answer"):"لم تجب بعد"}</div></div>
        <div class="tile"><div class="k">${ic("check")} تم إتقانه</div><div class="v">${num(o.mastered)}</div><div class="d">من ${qty(o.total_questions,"q")}</div></div>
        <div class="tile hot"><div class="k">🔥 أطول سلسلة</div><div class="v">${num(o.best_streak)}</div><div class="d">${unit(o.best_streak,"streak")}</div></div>
        <div class="tile"><div class="k">${ic("timer")} متوسط الاختبار</div><div class="v">${o.avg_test!=null?pct(o.avg_test):"لا يوجد"}</div><div class="d">${o.tests?qty(o.tests,"test"):"لم تبدأ بعد"}</div></div>
      </div>
      <div class="cols">
        <div class="stack">
          <div class="card"><h3>نشاطك خلال آخر أربعة أسابيع</h3>
            <p class="sub">كل مربّع يوم، وكثافة اللون تعني عدد الأسئلة التي أجبت عنها.</p>
            <div class="heat">${d.calendar.map(c=>`<i class="${c.level?"l"+c.level:""}" title="${esc(c.day)}: ${num(c.count)}"></i>`).join("")}</div></div>
          <div class="card"><h3>الدقة حسب المادة</h3><p class="sub">مرتّبة من الأضعف إلى الأقوى.</p>
            ${d.by_law.filter(r=>r.answered>0).sort((a,b)=>a.accuracy-b.accuracy).map(r=>meterHTML(r.title,r.accuracy)).join("")
              ||`<div class="empty">لم تجب عن أي سؤال بعد.</div>`}</div>
        </div>
        <div class="stack">
          <div class="card"><h3>الإنجازات</h3><p class="sub">${num(d.achievements.filter(a=>a.got).length)} من ${num(d.achievements.length)}</p>
            ${d.achievements.map(a=>`<div class="ach ${a.got?"got":""}"><div class="ico">${a.icon}</div>
              <div><b>${esc(a.name)}</b><small>${esc(a.desc)}</small></div></div>`).join("")}</div>
          <div class="card"><h3>آخر الاختبارات</h3>
            ${d.history.length?d.history.map(h=>`<div class="lead">
              <span class="rank ${h.total&&h.score/h.total>=.8?"g":""}">${num(h.score)}</span>
              <b>${esc(h.scope)}</b><span>${esc(h.when)}</span></div>`).join(""):`<div class="empty">لا يوجد سجل بعد.</div>`}</div>
        </div></div>`;
    }catch(e){ box.innerHTML=`<div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
  })();
};

/* ══════════════════ لوحة الترتيب ══════════════════ */
VIEWS.board=function(){
  mount(`<div id="bWrap"><div class="empty">جارٍ التحميل…</div></div>`);
  (async()=>{
    const box=$("#bWrap"); if(!box) return;
    try{
      const d=await api("/api/leaderboard"); S.board=d;
      const medal=i=>i===0?"g":i===1?"s":i===2?"b":"";
      box.innerHTML=`<div class="cols"><div class="card">
        <h3>الأكثر إتقانًا</h3><p class="sub">عدد الأسئلة التي أتقنها كل حكم.</p>
        ${d.items.length?d.items.map((x,i)=>`<div class="lead ${x.me?"me":""}">
          <span class="rank ${medal(i)}">${num(i+1)}</span>
          <b>${esc(x.name)}</b>${x.me?`<span class="you">أنت</span>`:""}
          <span>${qty(x.mastered,"mastered")}</span><span>${pct(x.accuracy)}</span></div>`).join(""):`<div class="empty">لا توجد نتائج بعد.</div>`}
        ${d.me&&!d.me.listed?`<div class="lead me"><span class="rank">${d.me.rank?num(d.me.rank):"؟"}</span>
          <b>${esc(d.me.name)}</b><span class="you">أنت</span>
          <span>${qty(d.me.mastered,"mastered")}</span></div>`:""}
      </div>
      <div class="card"><h3>كيف يُحتسب الترتيب؟</h3>
        <p class="sub" style="margin:0">يُحتسب السؤال «متقنًا» عندما تجيب عنه إجابة صحيحة ثلاث مرات متتالية بعد أن أخطأت فيه، أو عندما تجيب عنه صحيحًا من أول مرة.
        الدقة هي نسبة إجاباتك الصحيحة من مجموع إجاباتك.</p>
        <div class="divider"></div>
        <p class="sub" style="margin:0">${d.hidden?"حسابك مخفي حاليًا من اللوحة.":"حسابك ظاهر في اللوحة."}
        يمكنك تغيير ذلك من صفحة الحساب.</p>
        <button class="btn ghost block sm" style="margin-top:12px" onclick="R.go('account')">إعدادات الظهور</button>
      </div></div>`;
    }catch(e){ box.innerHTML=`<div class="empty">${esc(e.error||"تعذّر التحميل")}</div>`; }
  })();
};

/* ══════════════════ الحساب ══════════════════ */
VIEWS.account=function(){
  const u=S.me.user;
  mount(`<div class="cols"><div class="stack">
    <div class="card"><h3>الملف الشخصي</h3><p class="sub">الاسم الظاهر هو ما يراه الآخرون في لوحة الترتيب.</p>
      <div class="field"><label>اسم المستخدم</label><input value="${esc(u.username)}" disabled></div>
      <div class="field"><label for="acName">الاسم الظاهر</label><input id="acName" maxlength="40" value="${esc(u.display_name||"")}" placeholder="${esc(u.username)}"></div>
      <div class="field"><label for="acMin">مدة الاختبار بالدقائق</label><input id="acMin" type="number" min="1" max="60" value="${u.test_minutes}"></div>
      <div class="field"><label>الظهور في لوحة الترتيب</label>
        <div class="chiprow">
          <button class="chip ${u.public?"on":""}" onclick="Acc.pub(true)">ظاهر</button>
          <button class="chip ${!u.public?"on":""}" onclick="Acc.pub(false)">مخفي</button></div></div>
      <button class="btn primary block" onclick="Acc.save()">حفظ التغييرات</button></div>

    <div class="card"><h3>تغيير كلمة المرور</h3><p class="sub">من 4 إلى 8 أرقام.</p>
      <div class="field"><label for="pOld">كلمة المرور الحالية</label>
        <input id="pOld" type="password" inputmode="numeric" dir="ltr" lang="en" autocapitalize="off"></div>
      <div class="field"><label for="pNew">كلمة المرور الجديدة</label>
        <input id="pNew" type="password" inputmode="numeric" dir="ltr" lang="en" autocapitalize="off"></div>
      <div class="field"><label for="pNew2">تأكيد كلمة المرور</label>
        <input id="pNew2" type="password" inputmode="numeric" dir="ltr" lang="en" autocapitalize="off"></div>
      <button class="btn soft block" onclick="Acc.pin()">تحديث كلمة المرور</button></div>
  </div>
  <div class="stack">
    <div class="card"><h3>المظهر</h3><p class="sub">يُحفظ اختيارك على هذا الجهاز.</p>
      <div class="chiprow">${[["auto","تلقائي"],["light","فاتح"],["dark","داكن"]].map(t=>
        `<button class="chip ${Theme.get()===t[0]?"on":""}" onclick="Acc.theme('${t[0]}')">${t[1]}</button>`).join("")}</div></div>

    <div class="card"><h3>${ic("bell")} الإشعار اليومي</h3>
      <p class="sub">تذكير واحد كل يوم في الوقت الذي تختاره، ولا يصلك إذا كنت قد حللت سؤال اليوم.</p>
      ${notifyBody()}</div>

    <div class="card"><h3>بياناتك</h3><p class="sub">نسخة كاملة من تقدّمك بصيغة JSON.</p>
      <a class="btn soft block" href="/api/export" download>${ic("download")} تصدير التقدّم</a></div>

    <div class="card"><h3>الجلسة</h3>
      <button class="btn ghost block" onclick="logout()">${ic("logout")} تسجيل الخروج</button>
      <div class="divider"></div>
      <h3 style="font-size:14.5px;color:var(--bad)">حذف الحساب</h3>
      <p class="sub">يُحذف حسابك وكل تقدّمك نهائيًا ولا يمكن التراجع.</p>
      <div class="field"><label for="delPin">أدخل كلمة المرور للتأكيد</label>
        <input id="delPin" type="password" inputmode="numeric" dir="ltr" lang="en" autocapitalize="off"></div>
      <button class="btn danger block" onclick="Acc.del()">حذف الحساب نهائيًا</button></div>
  </div></div>`);
};
function hourLabel(h){
  const n=h%12===0?12:h%12;
  const part=h===12?" ظهرًا":h<12?" صباحًا":h<18?" عصرًا":" مساءً";
  return num(n)+part;
}
function notifyBody(){
  if(!Push.ready) return `<div class="empty" style="padding:18px">جارٍ التحقّق…</div>`;
  const st=Push.state;
  if(st==="needs-install") return `<p class="hint">${ic("home")} على الآيفون تصل الإشعارات فقط بعد إضافة الموقع إلى الشاشة الرئيسية. افتح قائمة المشاركة ثم «إضافة إلى الشاشة الرئيسية»، وافتح الموقع من الأيقونة الجديدة وعُد إلى هنا.</p>`;
  if(st==="unsupported") return `<p class="hint">${ic("close")} هذا المتصفّح لا يدعم الإشعارات. جرّب كروم على أندرويد أو سفاري على آيفون بعد إضافة الموقع إلى الشاشة الرئيسية.</p>`;
  if(st==="blocked") return `<p class="hint">${ic("close")} الإشعارات محظورة لهذا الموقع في إعدادات المتصفّح. اسمح بها من إعدادات الموقع ثم عُد إلى هنا.</p>`;
  const hours=[6,7,8,9,12,15,17,18,19,20,21,22];
  const h=S.me.user.notify_hour;
  if(st==="off") return `<button class="btn primary block" onclick="Acc.notifyOn()">${ic("bell")} فعّل الإشعار اليومي</button>`;
  return `<div class="field"><label>وقت التذكير</label>
      <div class="chiprow">${hours.map(x=>
        `<button class="chip ${h===x?"on":""}" onclick="Acc.hour(${x})">${hourLabel(x)}</button>`).join("")}</div></div>
    <div class="btnrow">
      <button class="btn soft" onclick="Acc.notifyTest()">إرسال تجربة</button>
      <button class="btn ghost" onclick="Acc.notifyOff()">إيقاف الإشعار</button></div>`;
}
const Acc={
  _pub:null,
  async notifyOn(){
    try{ await Push.enable(); await refreshMe(); R.render();
      toast("تم تفعيل الإشعار اليومي","ok"); }
    catch(e){ toast(e.error||"تعذّر تفعيل الإشعارات","bad"); R.render(); }
  },
  async notifyOff(){
    try{ await Push.disable(); await refreshMe(); R.render(); toast("تم إيقاف الإشعار","ok"); }
    catch(e){ toast(e.error||"تعذّر الإيقاف","bad"); }
  },
  async notifyTest(){
    try{ await api("/api/push/test",{body:{}}); toast("أُرسلت التجربة، تابع إشعارات جهازك","ok"); }
    catch(e){ toast(e.error||"تعذّر إرسال التجربة","bad"); }
  },
  async hour(h){
    const old=S.me.user.notify_hour; S.me.user.notify_hour=h; R.render();
    try{ await api("/api/settings",{body:{notify_hour:h,tz_offset:tzOffset()}});
      toast("وقت التذكير "+hourLabel(h),"ok"); }
    catch(e){ S.me.user.notify_hour=old; R.render(); toast(e.error||"تعذّر الحفظ","bad"); }
  },
  pub(v){ S.me.user.public=v; R.render(); },
  theme(t){ try{localStorage.setItem("theme",t);}catch(e){} Theme.apply(); R.render(); },
  async save(){
    const body={display_name:$("#acName").value.trim(),test_minutes:+$("#acMin").value,public:!!S.me.user.public};
    try{ await api("/api/settings",{body}); await refreshMe(); R.render();
      $("#sideName").textContent=S.me.user.name; $("#avatar").textContent=S.me.user.name.slice(0,2);
      toast("تم حفظ التغييرات","ok"); }
    catch(e){ toast(e.error||"تعذّر الحفظ","bad"); }
  },
  async pin(){
    const a=$("#pOld").value,b=$("#pNew").value,c=$("#pNew2").value;
    if(b!==c) return toast("كلمة المرور الجديدة غير متطابقة","bad");
    try{ await api("/api/pin",{body:{current:a,new:b}});
      $("#pOld").value=$("#pNew").value=$("#pNew2").value="";
      toast("تم تحديث كلمة المرور","ok"); }
    catch(e){ toast(e.error||"تعذّر التحديث","bad"); }
  },
  async del(){
    const pin=$("#delPin").value;
    if(!pin) return toast("أدخل كلمة المرور أولًا","bad");
    if(!await confirmBox("حذف الحساب","سيُحذف حسابك وكل تقدّمك نهائيًا ولا يمكن استرجاعه.","احذف نهائيًا",true)) return;
    try{ await api("/api/account/delete",{method:"POST",body:{pin}});
      toast("تم حذف الحساب"); setTimeout(()=>location.reload(),900); }
    catch(e){ toast(e.error||"تعذّر الحذف","bad"); }
  }
};

/* ══════════════════ التشغيل ══════════════════ */
/* ══════════════════ الإشعار اليومي ══════════════════ */
const Push={
  reg:null, sub:null, ready:false,
  get supported(){ return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window; },
  // على آيفون لا تعمل الإشعارات إلا بعد إضافة الموقع إلى الشاشة الرئيسية
  get iosNeedsInstall(){
    const ios=/iPad|iPhone|iPod/.test(navigator.userAgent)||
      (navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);
    return ios && !window.matchMedia("(display-mode: standalone)").matches && !navigator.standalone;
  },
  get state(){
    if(!this.supported) return this.iosNeedsInstall?"needs-install":"unsupported";
    if(Notification.permission==="denied") return "blocked";
    return this.sub?"on":"off";
  },
  async init(){
    if(!this.supported||!("serviceWorker" in navigator)) { this.ready=true; return; }
    try{
      this.reg=await navigator.serviceWorker.ready;
      this.sub=await this.reg.pushManager.getSubscription();
    }catch(e){}
    this.ready=true;
    // اشتراك محفوظ على الجهاز لكن الحساب يظنّ الإشعارات مطفأة: نعيد تسجيله
    if(this.sub&&S.me&&!S.me.user.notify_on){ try{ await this.save(); }catch(e){} }
  },
  async save(){
    const j=this.sub.toJSON();
    await api("/api/push/subscribe",{body:{
      endpoint:j.endpoint, keys:j.keys, tz_offset:tzOffset(),
      hour:S.me?S.me.user.notify_hour:20}});
    if(S.me) S.me.user.notify_on=true;
  },
  async enable(){
    if(this.state==="needs-install")
      throw {error:"أضف الموقع إلى الشاشة الرئيسية أولًا، ثم افتحه من هناك وفعّل الإشعارات."};
    if(!this.supported) throw {error:"هذا المتصفّح لا يدعم الإشعارات."};
    const perm=await Notification.requestPermission();
    if(perm!=="granted") throw {error:"لم يُسمح بالإشعارات. فعّلها من إعدادات المتصفّح."};
    this.reg=await navigator.serviceWorker.ready;
    const {key}=await api("/api/push/key");
    this.sub=await this.reg.pushManager.getSubscription();
    if(!this.sub) this.sub=await this.reg.pushManager.subscribe({
      userVisibleOnly:true, applicationServerKey:urlB64(key)});
    await this.save();
  },
  async disable(){
    try{ if(this.sub) await this.sub.unsubscribe(); }catch(e){}
    const ep=this.sub?this.sub.toJSON().endpoint:"";
    this.sub=null;
    await api("/api/push/unsubscribe",{body:{endpoint:ep}});
    if(S.me) S.me.user.notify_on=false;
  }
};
const tzOffset=()=>-new Date().getTimezoneOffset();
function urlB64(s){
  const pad="=".repeat((4-s.length%4)%4);
  const raw=atob((s+pad).replace(/-/g,"+").replace(/_/g,"/"));
  return Uint8Array.from(raw,c=>c.charCodeAt(0));
}
if("serviceWorker" in navigator){
  addEventListener("load",()=>navigator.serviceWorker.register("/sw.js")
    .then(()=>Push.init()).catch(()=>{}));
}
boot();
'''

MARK_SVG = r'''<svg class="mark" viewBox="88 72 336 368" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="قوانين اللعبة"><rect x="108" y="92" width="296" height="328" rx="30" fill="var(--mark-book)"/><rect x="352" y="92" width="52" height="328" fill="#06210f" opacity=".40"/><rect x="352" y="92" width="9" height="328" fill="#06210f" opacity=".18"/><rect x="108" y="116" width="14" height="280" rx="7" fill="#ffffff" opacity=".12"/><g transform="translate(238.000 236.000) scale(0.71483) translate(-181.00 -167.50)"><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z" fill="#ffffff"/><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z M 188.66 293.16 L 184.91 289.33 L 193.71 281.74 C 198.54 277.57 206.32 270.56 211.00 266.15 C 219.05 258.57 220.01 257.98 229.00 255.09 C 234.22 253.42 244.55 249.59 251.94 246.59 L 265.38 241.13 L 271.04 246.04 C 280.65 254.36 280.66 253.20 270.99 262.18 C 252.53 279.34 229.90 290.91 205.89 295.46 C 194.05 297.71 192.95 297.56 188.66 293.16 Z M 154.92 282.28 L 130.33 276.78 L 124.23 265.64 C 116.23 251.03 110.00 238.02 110.00 235.92 C 110.00 235.00 111.46 233.10 113.25 231.72 C 115.04 230.34 117.40 228.36 118.50 227.33 C 120.51 225.45 136.04 212.55 139.19 210.14 C 140.59 209.08 143.07 209.29 153.69 211.40 C 167.93 214.23 187.57 217.53 196.04 218.53 L 201.58 219.18 L 203.94 225.34 C 205.23 228.73 208.96 237.12 212.22 244.00 L 218.15 256.50 L 207.50 266.70 C 193.53 280.07 183.73 288.03 181.39 287.89 C 180.35 287.83 168.44 285.30 154.92 282.28 Z M 114.84 279.20 C 97.50 268.98 80.45 251.50 69.14 232.38 C 64.48 224.51 58.67 210.31 59.36 208.50 C 59.60 207.87 62.78 206.55 66.41 205.56 C 74.16 203.46 72.37 202.52 86.50 216.12 C 92.00 221.41 98.83 227.71 101.68 230.12 C 104.53 232.53 107.18 235.40 107.57 236.50 C 109.20 241.09 117.19 257.18 122.40 266.38 C 125.48 271.81 128.00 276.39 128.00 276.54 C 128.00 276.70 126.01 277.94 123.59 279.30 L 119.17 281.76 L 114.84 279.20 Z M 277.50 249.35 C 275.85 247.91 272.74 245.15 270.59 243.22 L 266.68 239.71 L 271.86 219.11 C 274.71 207.77 277.03 197.92 277.02 197.21 C 277.01 196.50 277.94 194.92 279.08 193.71 C 283.82 188.69 290.30 179.23 296.67 168.07 L 303.43 156.20 L 307.72 159.15 C 311.85 161.99 312.00 162.29 312.00 167.36 C 312.00 182.11 307.25 204.41 300.92 219.39 C 297.30 227.97 288.15 243.38 283.72 248.36 L 280.50 251.98 L 277.50 249.35 Z M 193.00 216.32 C 182.94 214.68 150.55 208.90 146.46 208.01 L 141.42 206.93 L 138.80 199.71 C 130.66 177.34 125.00 161.08 125.00 160.06 C 125.00 156.53 146.59 128.59 157.84 117.57 L 164.92 110.63 L 177.21 112.40 C 203.23 116.12 216.53 119.25 218.00 122.00 C 219.66 125.11 232.46 159.71 235.47 169.24 L 238.23 177.99 L 231.69 184.74 C 223.54 193.17 217.87 199.34 209.25 209.22 C 202.10 217.39 201.42 217.69 193.00 216.32 Z M 55.09 195.80 C 49.49 169.60 51.81 143.64 62.00 118.50 C 65.39 110.11 65.84 109.50 68.50 109.50 C 71.28 109.50 71.40 109.71 72.63 117.00 C 73.33 121.12 75.69 131.44 77.88 139.93 C 81.38 153.48 81.71 155.67 80.57 157.93 C 77.95 163.11 74.02 185.94 74.01 196.03 L 74.00 201.56 L 66.75 203.52 C 62.76 204.60 59.00 205.62 58.40 205.79 C 57.74 205.97 56.41 201.93 55.09 195.80 Z M 265.00 187.75 C 259.77 184.91 251.90 181.12 247.50 179.33 C 242.27 177.21 239.37 175.46 239.14 174.29 C 238.54 171.34 225.45 134.94 222.04 126.76 L 218.88 119.16 L 220.93 115.33 C 222.06 113.22 224.45 109.16 226.24 106.30 C 228.03 103.44 231.45 97.95 233.83 94.11 C 236.21 90.26 238.69 86.69 239.33 86.17 C 240.94 84.88 256.54 88.87 266.00 92.99 C 277.86 98.16 283.72 102.34 285.97 107.24 C 288.41 112.56 295.85 133.62 299.42 145.32 L 302.11 154.14 L 296.95 163.82 C 290.22 176.45 278.43 193.01 276.20 192.96 C 275.27 192.94 270.23 190.60 265.00 187.75 Z M 111.00 156.46 C 105.78 155.75 97.39 154.85 92.36 154.47 L 83.21 153.78 L 79.16 137.14 C 76.94 127.99 74.64 117.85 74.06 114.60 L 73.01 108.70 L 77.76 103.01 C 87.37 91.47 93.36 84.36 98.00 79.00 C 100.61 75.97 103.82 72.26 105.13 70.74 C 108.25 67.11 116.43 65.57 128.50 66.35 C 137.51 66.93 152.90 69.62 154.19 70.85 C 155.14 71.75 158.38 84.34 161.09 97.67 L 163.37 108.85 L 154.87 117.78 C 144.28 128.91 134.29 141.29 128.27 150.75 C 125.54 155.04 123.01 157.95 122.08 157.88 C 121.21 157.81 116.22 157.18 111.00 156.46 Z M 281.45 99.07 C 277.18 94.91 253.07 85.39 244.12 84.33 C 240.16 83.86 238.19 82.83 233.38 78.71 C 226.72 73.00 209.52 59.18 206.00 56.71 L 203.68 55.09 L 205.73 48.29 C 207.76 41.54 207.80 41.50 211.14 41.78 C 220.69 42.58 245.65 53.94 258.34 63.25 C 267.36 69.89 284.49 86.81 285.55 90.15 C 286.22 92.28 284.26 100.00 283.04 100.00 C 282.69 100.00 281.97 99.58 281.45 99.07 Z M 151.26 67.97 C 145.98 65.85 126.39 63.77 117.75 64.42 C 109.47 65.04 109.00 64.97 109.00 63.09 C 109.00 57.40 136.72 44.41 157.13 40.54 C 169.77 38.14 184.20 37.55 195.79 38.97 C 201.40 39.66 206.00 40.51 206.00 40.86 C 206.00 41.21 204.95 44.41 203.66 47.97 L 201.33 54.44 L 190.92 57.29 C 185.19 58.86 174.59 62.14 167.37 64.57 C 160.15 67.01 154.07 68.97 153.87 68.94 C 153.67 68.90 152.49 68.47 151.26 67.97 Z" fill="#0a2e18" fill-rule="evenodd"/></g><rect x="170" y="352" width="136" height="18" rx="9" fill="var(--mark-line)" opacity=".65"/></svg>'''

MANIFEST = {
    "name": "قوانين اللعبة",
    "short_name": "قوانين اللعبة",
    "description": "مذاكرة واختبارات ومراجعة ذكية لقوانين كرة القدم.",
    "lang": "ar", "dir": "rtl",
    "start_url": "/", "scope": "/", "display": "standalone",
    "background_color": "#071410", "theme_color": "#071410",
    "orientation": "portrait-primary",
    "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
              {"src": "/icon-maskable.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "maskable"}],
}

ICON_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a3e635"/><stop offset="1" stop-color="#16a34a"/></linearGradient></defs><rect width="512" height="512" rx="112" fill="url(#g)"/><rect x="108" y="92" width="296" height="328" rx="30" fill="#0f3d22"/><rect x="352" y="92" width="52" height="328" fill="#06210f" opacity=".45"/><rect x="352" y="92" width="9" height="328" fill="#06210f" opacity=".20"/><rect x="108" y="116" width="14" height="280" rx="7" fill="#ffffff" opacity=".10"/><g transform="translate(238.000 236.000) scale(0.71483) translate(-181.00 -167.50)"><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z" fill="#ffffff"/><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z M 188.66 293.16 L 184.91 289.33 L 193.71 281.74 C 198.54 277.57 206.32 270.56 211.00 266.15 C 219.05 258.57 220.01 257.98 229.00 255.09 C 234.22 253.42 244.55 249.59 251.94 246.59 L 265.38 241.13 L 271.04 246.04 C 280.65 254.36 280.66 253.20 270.99 262.18 C 252.53 279.34 229.90 290.91 205.89 295.46 C 194.05 297.71 192.95 297.56 188.66 293.16 Z M 154.92 282.28 L 130.33 276.78 L 124.23 265.64 C 116.23 251.03 110.00 238.02 110.00 235.92 C 110.00 235.00 111.46 233.10 113.25 231.72 C 115.04 230.34 117.40 228.36 118.50 227.33 C 120.51 225.45 136.04 212.55 139.19 210.14 C 140.59 209.08 143.07 209.29 153.69 211.40 C 167.93 214.23 187.57 217.53 196.04 218.53 L 201.58 219.18 L 203.94 225.34 C 205.23 228.73 208.96 237.12 212.22 244.00 L 218.15 256.50 L 207.50 266.70 C 193.53 280.07 183.73 288.03 181.39 287.89 C 180.35 287.83 168.44 285.30 154.92 282.28 Z M 114.84 279.20 C 97.50 268.98 80.45 251.50 69.14 232.38 C 64.48 224.51 58.67 210.31 59.36 208.50 C 59.60 207.87 62.78 206.55 66.41 205.56 C 74.16 203.46 72.37 202.52 86.50 216.12 C 92.00 221.41 98.83 227.71 101.68 230.12 C 104.53 232.53 107.18 235.40 107.57 236.50 C 109.20 241.09 117.19 257.18 122.40 266.38 C 125.48 271.81 128.00 276.39 128.00 276.54 C 128.00 276.70 126.01 277.94 123.59 279.30 L 119.17 281.76 L 114.84 279.20 Z M 277.50 249.35 C 275.85 247.91 272.74 245.15 270.59 243.22 L 266.68 239.71 L 271.86 219.11 C 274.71 207.77 277.03 197.92 277.02 197.21 C 277.01 196.50 277.94 194.92 279.08 193.71 C 283.82 188.69 290.30 179.23 296.67 168.07 L 303.43 156.20 L 307.72 159.15 C 311.85 161.99 312.00 162.29 312.00 167.36 C 312.00 182.11 307.25 204.41 300.92 219.39 C 297.30 227.97 288.15 243.38 283.72 248.36 L 280.50 251.98 L 277.50 249.35 Z M 193.00 216.32 C 182.94 214.68 150.55 208.90 146.46 208.01 L 141.42 206.93 L 138.80 199.71 C 130.66 177.34 125.00 161.08 125.00 160.06 C 125.00 156.53 146.59 128.59 157.84 117.57 L 164.92 110.63 L 177.21 112.40 C 203.23 116.12 216.53 119.25 218.00 122.00 C 219.66 125.11 232.46 159.71 235.47 169.24 L 238.23 177.99 L 231.69 184.74 C 223.54 193.17 217.87 199.34 209.25 209.22 C 202.10 217.39 201.42 217.69 193.00 216.32 Z M 55.09 195.80 C 49.49 169.60 51.81 143.64 62.00 118.50 C 65.39 110.11 65.84 109.50 68.50 109.50 C 71.28 109.50 71.40 109.71 72.63 117.00 C 73.33 121.12 75.69 131.44 77.88 139.93 C 81.38 153.48 81.71 155.67 80.57 157.93 C 77.95 163.11 74.02 185.94 74.01 196.03 L 74.00 201.56 L 66.75 203.52 C 62.76 204.60 59.00 205.62 58.40 205.79 C 57.74 205.97 56.41 201.93 55.09 195.80 Z M 265.00 187.75 C 259.77 184.91 251.90 181.12 247.50 179.33 C 242.27 177.21 239.37 175.46 239.14 174.29 C 238.54 171.34 225.45 134.94 222.04 126.76 L 218.88 119.16 L 220.93 115.33 C 222.06 113.22 224.45 109.16 226.24 106.30 C 228.03 103.44 231.45 97.95 233.83 94.11 C 236.21 90.26 238.69 86.69 239.33 86.17 C 240.94 84.88 256.54 88.87 266.00 92.99 C 277.86 98.16 283.72 102.34 285.97 107.24 C 288.41 112.56 295.85 133.62 299.42 145.32 L 302.11 154.14 L 296.95 163.82 C 290.22 176.45 278.43 193.01 276.20 192.96 C 275.27 192.94 270.23 190.60 265.00 187.75 Z M 111.00 156.46 C 105.78 155.75 97.39 154.85 92.36 154.47 L 83.21 153.78 L 79.16 137.14 C 76.94 127.99 74.64 117.85 74.06 114.60 L 73.01 108.70 L 77.76 103.01 C 87.37 91.47 93.36 84.36 98.00 79.00 C 100.61 75.97 103.82 72.26 105.13 70.74 C 108.25 67.11 116.43 65.57 128.50 66.35 C 137.51 66.93 152.90 69.62 154.19 70.85 C 155.14 71.75 158.38 84.34 161.09 97.67 L 163.37 108.85 L 154.87 117.78 C 144.28 128.91 134.29 141.29 128.27 150.75 C 125.54 155.04 123.01 157.95 122.08 157.88 C 121.21 157.81 116.22 157.18 111.00 156.46 Z M 281.45 99.07 C 277.18 94.91 253.07 85.39 244.12 84.33 C 240.16 83.86 238.19 82.83 233.38 78.71 C 226.72 73.00 209.52 59.18 206.00 56.71 L 203.68 55.09 L 205.73 48.29 C 207.76 41.54 207.80 41.50 211.14 41.78 C 220.69 42.58 245.65 53.94 258.34 63.25 C 267.36 69.89 284.49 86.81 285.55 90.15 C 286.22 92.28 284.26 100.00 283.04 100.00 C 282.69 100.00 281.97 99.58 281.45 99.07 Z M 151.26 67.97 C 145.98 65.85 126.39 63.77 117.75 64.42 C 109.47 65.04 109.00 64.97 109.00 63.09 C 109.00 57.40 136.72 44.41 157.13 40.54 C 169.77 38.14 184.20 37.55 195.79 38.97 C 201.40 39.66 206.00 40.51 206.00 40.86 C 206.00 41.21 204.95 44.41 203.66 47.97 L 201.33 54.44 L 190.92 57.29 C 185.19 58.86 174.59 62.14 167.37 64.57 C 160.15 67.01 154.07 68.97 153.87 68.94 C 153.67 68.90 152.49 68.47 151.26 67.97 Z" fill="#0a2e18" fill-rule="evenodd"/></g><rect x="170" y="352" width="136" height="18" rx="9" fill="#a3e635" opacity=".6"/></svg>'''

# النسخة المقنّعة: أندرويد يقصّها دائريًا، فتملأ الحافة ويصغر المحتوى
ICON_MASKABLE_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a3e635"/><stop offset="1" stop-color="#16a34a"/></linearGradient></defs><rect width="512" height="512" fill="url(#g)"/><g transform="translate(256 256) scale(0.7600) translate(-256 -256)"><rect x="108" y="92" width="296" height="328" rx="30" fill="#0f3d22"/><rect x="352" y="92" width="52" height="328" fill="#06210f" opacity=".45"/><rect x="352" y="92" width="9" height="328" fill="#06210f" opacity=".20"/><rect x="108" y="116" width="14" height="280" rx="7" fill="#ffffff" opacity=".10"/><g transform="translate(238.000 236.000) scale(0.71483) translate(-181.00 -167.50)"><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z" fill="#ffffff"/><path d="M 206.25 297.38 C 230.74 292.78 256.48 279.18 274.45 261.33 C 294.87 241.04 307.48 216.04 312.06 186.74 C 313.99 174.43 312.73 147.76 309.69 136.50 C 298.99 96.90 274.82 67.10 239.50 49.98 C 219.17 40.13 204.43 36.67 182.50 36.61 C 166.62 36.57 157.85 37.82 143.50 42.16 C 113.99 51.10 88.66 70.05 71.59 95.97 C 56.98 118.14 49.06 147.04 50.32 173.50 C 53.14 232.70 94.25 282.46 151.61 296.08 C 168.62 300.12 189.04 300.61 206.25 297.38 Z M 188.66 293.16 L 184.91 289.33 L 193.71 281.74 C 198.54 277.57 206.32 270.56 211.00 266.15 C 219.05 258.57 220.01 257.98 229.00 255.09 C 234.22 253.42 244.55 249.59 251.94 246.59 L 265.38 241.13 L 271.04 246.04 C 280.65 254.36 280.66 253.20 270.99 262.18 C 252.53 279.34 229.90 290.91 205.89 295.46 C 194.05 297.71 192.95 297.56 188.66 293.16 Z M 154.92 282.28 L 130.33 276.78 L 124.23 265.64 C 116.23 251.03 110.00 238.02 110.00 235.92 C 110.00 235.00 111.46 233.10 113.25 231.72 C 115.04 230.34 117.40 228.36 118.50 227.33 C 120.51 225.45 136.04 212.55 139.19 210.14 C 140.59 209.08 143.07 209.29 153.69 211.40 C 167.93 214.23 187.57 217.53 196.04 218.53 L 201.58 219.18 L 203.94 225.34 C 205.23 228.73 208.96 237.12 212.22 244.00 L 218.15 256.50 L 207.50 266.70 C 193.53 280.07 183.73 288.03 181.39 287.89 C 180.35 287.83 168.44 285.30 154.92 282.28 Z M 114.84 279.20 C 97.50 268.98 80.45 251.50 69.14 232.38 C 64.48 224.51 58.67 210.31 59.36 208.50 C 59.60 207.87 62.78 206.55 66.41 205.56 C 74.16 203.46 72.37 202.52 86.50 216.12 C 92.00 221.41 98.83 227.71 101.68 230.12 C 104.53 232.53 107.18 235.40 107.57 236.50 C 109.20 241.09 117.19 257.18 122.40 266.38 C 125.48 271.81 128.00 276.39 128.00 276.54 C 128.00 276.70 126.01 277.94 123.59 279.30 L 119.17 281.76 L 114.84 279.20 Z M 277.50 249.35 C 275.85 247.91 272.74 245.15 270.59 243.22 L 266.68 239.71 L 271.86 219.11 C 274.71 207.77 277.03 197.92 277.02 197.21 C 277.01 196.50 277.94 194.92 279.08 193.71 C 283.82 188.69 290.30 179.23 296.67 168.07 L 303.43 156.20 L 307.72 159.15 C 311.85 161.99 312.00 162.29 312.00 167.36 C 312.00 182.11 307.25 204.41 300.92 219.39 C 297.30 227.97 288.15 243.38 283.72 248.36 L 280.50 251.98 L 277.50 249.35 Z M 193.00 216.32 C 182.94 214.68 150.55 208.90 146.46 208.01 L 141.42 206.93 L 138.80 199.71 C 130.66 177.34 125.00 161.08 125.00 160.06 C 125.00 156.53 146.59 128.59 157.84 117.57 L 164.92 110.63 L 177.21 112.40 C 203.23 116.12 216.53 119.25 218.00 122.00 C 219.66 125.11 232.46 159.71 235.47 169.24 L 238.23 177.99 L 231.69 184.74 C 223.54 193.17 217.87 199.34 209.25 209.22 C 202.10 217.39 201.42 217.69 193.00 216.32 Z M 55.09 195.80 C 49.49 169.60 51.81 143.64 62.00 118.50 C 65.39 110.11 65.84 109.50 68.50 109.50 C 71.28 109.50 71.40 109.71 72.63 117.00 C 73.33 121.12 75.69 131.44 77.88 139.93 C 81.38 153.48 81.71 155.67 80.57 157.93 C 77.95 163.11 74.02 185.94 74.01 196.03 L 74.00 201.56 L 66.75 203.52 C 62.76 204.60 59.00 205.62 58.40 205.79 C 57.74 205.97 56.41 201.93 55.09 195.80 Z M 265.00 187.75 C 259.77 184.91 251.90 181.12 247.50 179.33 C 242.27 177.21 239.37 175.46 239.14 174.29 C 238.54 171.34 225.45 134.94 222.04 126.76 L 218.88 119.16 L 220.93 115.33 C 222.06 113.22 224.45 109.16 226.24 106.30 C 228.03 103.44 231.45 97.95 233.83 94.11 C 236.21 90.26 238.69 86.69 239.33 86.17 C 240.94 84.88 256.54 88.87 266.00 92.99 C 277.86 98.16 283.72 102.34 285.97 107.24 C 288.41 112.56 295.85 133.62 299.42 145.32 L 302.11 154.14 L 296.95 163.82 C 290.22 176.45 278.43 193.01 276.20 192.96 C 275.27 192.94 270.23 190.60 265.00 187.75 Z M 111.00 156.46 C 105.78 155.75 97.39 154.85 92.36 154.47 L 83.21 153.78 L 79.16 137.14 C 76.94 127.99 74.64 117.85 74.06 114.60 L 73.01 108.70 L 77.76 103.01 C 87.37 91.47 93.36 84.36 98.00 79.00 C 100.61 75.97 103.82 72.26 105.13 70.74 C 108.25 67.11 116.43 65.57 128.50 66.35 C 137.51 66.93 152.90 69.62 154.19 70.85 C 155.14 71.75 158.38 84.34 161.09 97.67 L 163.37 108.85 L 154.87 117.78 C 144.28 128.91 134.29 141.29 128.27 150.75 C 125.54 155.04 123.01 157.95 122.08 157.88 C 121.21 157.81 116.22 157.18 111.00 156.46 Z M 281.45 99.07 C 277.18 94.91 253.07 85.39 244.12 84.33 C 240.16 83.86 238.19 82.83 233.38 78.71 C 226.72 73.00 209.52 59.18 206.00 56.71 L 203.68 55.09 L 205.73 48.29 C 207.76 41.54 207.80 41.50 211.14 41.78 C 220.69 42.58 245.65 53.94 258.34 63.25 C 267.36 69.89 284.49 86.81 285.55 90.15 C 286.22 92.28 284.26 100.00 283.04 100.00 C 282.69 100.00 281.97 99.58 281.45 99.07 Z M 151.26 67.97 C 145.98 65.85 126.39 63.77 117.75 64.42 C 109.47 65.04 109.00 64.97 109.00 63.09 C 109.00 57.40 136.72 44.41 157.13 40.54 C 169.77 38.14 184.20 37.55 195.79 38.97 C 201.40 39.66 206.00 40.51 206.00 40.86 C 206.00 41.21 204.95 44.41 203.66 47.97 L 201.33 54.44 L 190.92 57.29 C 185.19 58.86 174.59 62.14 167.37 64.57 C 160.15 67.01 154.07 68.97 153.87 68.94 C 153.67 68.90 152.49 68.47 151.26 67.97 Z" fill="#0a2e18" fill-rule="evenodd"/></g><rect x="170" y="352" width="136" height="18" rx="9" fill="#a3e635" opacity=".6"/></g></svg>'''

SW_JS = r'''const CACHE="lotg-v5";
const SHELL=["/","/icon.svg","/icon-maskable.svg","/manifest.webmanifest"];
self.addEventListener("install",e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).catch(()=>{}));
});
self.addEventListener("activate",e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener("push",e=>{
  let d={};
  try{ d=e.data?e.data.json():{}; }catch(err){ d={body:e.data?e.data.text():""}; }
  const title=d.title||"قوانين اللعبة";
  e.waitUntil(self.registration.showNotification(title,{
    body:d.body||"سؤال اليوم بانتظارك.",
    icon:"/icon.svg", badge:"/icon.svg", dir:"rtl", lang:"ar",
    tag:d.tag||"daily", renotify:true,
    data:{url:d.url||"/"}
  }));
});
self.addEventListener("notificationclick",e=>{
  e.notification.close();
  const url=new URL((e.notification.data&&e.notification.data.url)||"/",self.location.origin).href;
  e.waitUntil(clients.matchAll({type:"window",includeUncontrolled:true}).then(ws=>{
    for(const w of ws){ if(w.url.startsWith(self.location.origin)&&"focus" in w) return w.focus(); }
    return clients.openWindow(url);
  }));
});
self.addEventListener("fetch",e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.origin!==location.origin) return;
  if(u.pathname.startsWith("/api/")) return;              // البيانات دائمًا من الشبكة
  e.respondWith(
    fetch(e.request).then(r=>{
      const copy=r.clone();
      caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
      return r;
    }).catch(()=>caches.match(e.request).then(r=>r||caches.match("/")))
  );
});'''

INDEX_HTML = (HTML.replace('__CSS__', CSS)
              .replace('__JS__', JS.replace('__MARK__', json.dumps(MARK_SVG, ensure_ascii=False))))
