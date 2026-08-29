# -*- coding: utf-8 -*-
"""컷 시트 — 컷별 한국어 설명과 영문 프롬프트. 어느 화든 인자로 받는다.

저장소 데이터(episodes/<ep>/prompts/*.json)에서 직접 읽어 site/dist/ 에 HTML을 만든다.
    python3 site/build.py            # 세 페이지 전부
    python3 site/make_sheet.py
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import bible          # 캐릭터 바이블은 40화 공용 (bible/)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
PROMPTS = ROOT / "episodes" / EP / "prompts"
DIST = HERE / "dist"
DIST.mkdir(parents=True, exist_ok=True)

CHARS = json.loads(bible.chars_path(PROMPTS).read_text(encoding="utf-8"))
SHOTS = json.loads((PROMPTS / "shots_v2.json").read_text(encoding="utf-8"))
ORDER = ["쿵쿵", "루카", "후안", "미미", "티니", "루비", "노을"]

data = {
  "sections": SHOTS["sections"],
  "negative": bible.negative(CHARS, SHOTS),
  "sheets": CHARS["master_sheet_prompts"],
  "heights": {n: c.get("height") for n, c in CHARS["characters"].items()},
  "shots": [{"id": s["id"], "sec": s["section"], "shot": s["shot"], "shotko": s["shot_ko"],
      "dur": s["duration"], "who": s.get("speaker", ""), "line": s.get("dialogue", ""),
      "ko": s["ko"], "komo": s["ko_motion"], "cast": s["cast"],
      "link": s.get("link", ""), "linkko": s.get("link_ko", ""),
      "img": s["image_ref"], "mo": s.get("motion_ref") or s["motion"]} for s in SHOTS["shots"]],
}

HTML = '''<title>쿵쿵이 __NO__ 컷 시트</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F6F8F6; --surface:#FFFFFF; --surface-2:#EFF3F0;
  --ink:#141E1B; --muted:#5D6D68; --faint:#8B9B95;
  --accent:#218A6E; --accent-soft:#DCEFE7; --peach:#C4693B;--warn-soft:#FBF1E7;--warn-line:#E8CDB2;--warn-ink:#8A4A21; --peach-soft:#F7E7DC;
  --line:#DDE4E0; --line-strong:#C6D2CC;
  --done:#9BAAA4;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926;
    --ink:#E4EDE9; --muted:#8FA39D; --faint:#6C807A;
    --accent:#4FCBA4; --accent-soft:#17322A; --peach:#E5946A;--warn-soft:#241A13;--warn-line:#4A3524;--warn-ink:#E5A46A; --peach-soft:#33231A;
    --line:#25322E; --line-strong:#33433E;
    --done:#5A6A65;
  }
}
:root[data-theme="dark"]{
  --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926;
  --ink:#E4EDE9; --muted:#8FA39D; --faint:#6C807A;
  --accent:#4FCBA4; --accent-soft:#17322A; --peach:#E5946A;--warn-soft:#241A13;--warn-line:#4A3524;--warn-ink:#E5A46A; --peach-soft:#33231A;
  --line:#25322E; --line-strong:#33433E;
  --done:#5A6A65;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans KR",system-ui,-apple-system,sans-serif;
  font-size:15px; line-height:1.65;
}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px 96px}

/* ---------- 머리말 ---------- */
header.top{padding:56px 0 28px;border-bottom:1px solid var(--line)}
h1{
  font-family:"Gowun Batang",serif; font-weight:700;
  font-size:clamp(30px,4.2vw,44px); line-height:1.25; margin:0 0 10px;
  text-wrap:balance; letter-spacing:-.01em;
}
.sub{color:var(--muted);margin:0;max-width:62ch}
.eyebrow{
  font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);font-weight:600;margin:0 0 14px;
}

/* ---------- 안내 카드 ---------- */
.guide{
  margin:32px 0 0;background:var(--surface);border:1px solid var(--line);
  border-radius:10px;padding:22px 24px;
}
.guide h2{font-family:"Gowun Batang",serif;font-size:19px;margin:0 0 14px;font-weight:700}
.guide ol{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:9px}
.guide li::marker{color:var(--accent);font-weight:600}
.script{
  margin-top:16px;padding:14px 18px;border-radius:12px;
  background:var(--surface-2);border:1px solid var(--line);
}
.script summary{
  cursor:pointer;list-style:none;font-weight:700;font-size:14.5px;color:var(--ink);
  display:inline-flex;align-items:center;gap:6px;
}
.script summary::-webkit-details-marker{display:none}
.script summary::before{content:"▸";color:var(--accent);transition:transform .15s}
.script[open] summary::before{transform:rotate(90deg)}
.scriptnote{margin:10px 0 0;font-size:13px;line-height:1.7;color:var(--muted)}
.script ol{margin:12px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:2px}
.script li{
  display:grid;grid-template-columns:64px 78px 1fr;gap:10px;align-items:baseline;
  padding:7px 0;border-top:1px solid var(--line);font-size:14px;line-height:1.6;
}
.script li .c{
  font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--faint);
  font-variant-numeric:tabular-nums;
}
.script li .w{font-size:12px;font-weight:700;color:var(--peach)}
.script li.narr .w{color:var(--accent)}
@media (max-width:560px){
  .script li{grid-template-columns:60px 1fr;gap:4px 10px}
  .script li .t{grid-column:1 / -1}
}
.guide code{
  font-family:"IBM Plex Mono",monospace;font-size:13px;
  background:var(--surface-2);padding:1px 6px;border-radius:4px;
}
.neg{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
.neg .label{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);font-weight:600}

/* ---------- 조작 바 ---------- */
.bar{
  position:sticky;top:0;z-index:10;background:var(--ground);
  border-bottom:1px solid var(--line);padding:14px 0;margin-top:36px;
  display:flex;gap:18px;align-items:center;flex-wrap:wrap;
}
.progress{display:flex;align-items:center;gap:11px;min-width:210px}
.track{flex:1;height:6px;background:var(--surface-2);border-radius:99px;overflow:hidden}
.fill{height:100%;width:0;background:var(--accent);border-radius:99px;transition:width .3s ease}
.count{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.filters{display:flex;gap:6px}
.filters button{
  font-family:inherit;font-size:13px;padding:5px 13px;border-radius:99px;cursor:pointer;
  border:1px solid var(--line-strong);background:transparent;color:var(--muted);transition:.15s;
}
.filters button:hover{border-color:var(--accent);color:var(--accent)}
.filters button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.filters button:focus-visible,.copy:focus-visible,.chk:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

/* ---------- 섹션 ---------- */
section{margin-top:44px}
section > h2{
  font-family:"Gowun Batang",serif;font-size:22px;font-weight:700;margin:0 0 4px;
  display:flex;align-items:baseline;gap:12px;
}
section > h2 .n{
  font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--faint);
  font-weight:400;font-variant-numeric:tabular-nums;
}
.rule{height:1px;background:var(--line);margin:14px 0 20px}

/* ---------- 컷 ---------- */
.shot{
  background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:16px 18px;margin-bottom:12px;display:grid;
  grid-template-columns:104px 1fr;gap:18px;transition:opacity .2s,border-color .2s;
}
.shot[data-done="1"]{opacity:.45}
.shot[data-done="1"] .id{color:var(--done);border-color:var(--line)}
.rail{display:flex;flex-direction:column;gap:9px;align-items:flex-start}
.id{
  font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:13px;
  color:var(--accent);border:1px solid var(--accent-soft);background:var(--accent-soft);
  padding:2px 9px;border-radius:5px;
}
.meta{font-size:12px;color:var(--faint);font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.cast{display:flex;flex-wrap:wrap;gap:4px;margin-top:7px}
.cast .c{
  font-size:11px;padding:2px 7px;border-radius:999px;font-weight:600;
  background:var(--accent-soft);color:var(--accent);border:1px solid transparent;
}
.cast .bg{
  font-size:11px;padding:2px 7px;border-radius:999px;font-weight:500;
  background:var(--surface-2);color:var(--faint);border:1px solid var(--line);
}
.step0{
  margin-top:16px;padding:16px 18px;border-radius:12px;
  background:var(--warn-soft);border:1px solid var(--warn-line);
}
.step0 h3{
  font-family:"Gowun Batang",serif;font-size:16px;margin:0 0 8px;font-weight:700;color:var(--warn-ink);
}
.step0 p{margin:0 0 10px;font-size:13.5px;line-height:1.7;color:var(--muted)}
.step0 .pair{display:flex;flex-direction:column;gap:10px;margin-top:12px}
.chk{display:flex;align-items:center;gap:7px;cursor:pointer;font-size:12px;color:var(--muted);
     background:none;border:none;padding:0;font-family:inherit}
.box{width:15px;height:15px;border:1.5px solid var(--line-strong);border-radius:4px;display:grid;place-items:center;flex:0 0 auto}
.shot[data-done="1"] .box{background:var(--accent);border-color:var(--accent)}
.box svg{width:10px;height:10px;opacity:0;stroke:var(--surface);stroke-width:2.5;fill:none}
.shot[data-done="1"] .box svg{opacity:1}
.body{min-width:0;display:flex;flex-direction:column;gap:12px}
.line.narr{background:var(--accent-soft);border-left-color:var(--accent)}
.line.none{
  background:transparent;border-left-color:var(--line);color:var(--faint);
  font-size:13px;font-style:normal;
}
.line .who{
  display:inline-block;margin-right:8px;padding:1px 7px;border-radius:999px;
  font-size:11.5px;font-weight:700;vertical-align:1px;
  background:var(--peach-soft);color:var(--peach);
}
.line.narr .who{background:var(--accent);color:var(--surface)}
.line.narr .who{color:var(--accent)}
.line{
  background:var(--peach-soft);border-left:2px solid var(--peach);
  padding:8px 13px;border-radius:0 6px 6px 0;font-size:14px;
}
.line .who{color:var(--peach);font-weight:600;font-size:12px;letter-spacing:.04em}
.block .label{
  font-size:12px;letter-spacing:.02em;color:var(--faint);
  font-weight:600;display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:6px;
}
.block .label .tools{display:flex;gap:6px;flex:0 0 auto}
.ko{font-size:14.5px;line-height:1.7;color:var(--ink);margin:0}
.link{display:flex;gap:9px;align-items:flex-start;padding:9px 12px;border-radius:9px;
  background:var(--sunk);border-left:3px solid var(--line-strong);margin:0 0 12px}
.link .tag{flex:none;font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:700;
  padding:1px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}
.link .txt{font-size:13.5px;line-height:1.65;color:var(--muted);margin:0}
.link.연속{border-left-color:var(--accent)} .link.연속 .tag{color:var(--accent)}
.link.전환{border-left-color:var(--peach)} .link.전환 .tag{color:var(--peach)}
.link.컷 .tag{color:var(--faint)}
.en{margin-top:8px}
.en summary{
  list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:5px;
  font-size:11.5px;color:var(--faint);font-weight:500;padding:2px 0;
}
.en summary::-webkit-details-marker{display:none}
.en summary::before{content:"▸";font-size:10px;transition:transform .15s}
.en[open] summary::before{transform:rotate(90deg)}
.en summary:hover{color:var(--accent)}
.en pre{margin-top:6px}
.copy{
  font-family:inherit;font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;
  color:var(--accent);background:none;border:1px solid var(--line-strong);
  padding:3px 10px;border-radius:99px;cursor:pointer;transition:.15s;
}
.copy:hover{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.copy[data-ok="1"]{background:var(--accent);border-color:var(--accent);color:var(--surface)}
pre{
  font-family:"IBM Plex Mono",monospace;font-size:12.5px;line-height:1.6;
  background:var(--surface-2);border-radius:7px;padding:11px 13px;margin:0;
  white-space:pre-wrap;word-break:break-word;color:var(--ink);max-height:none;
}
footer{margin-top:56px;padding-top:22px;border-top:1px solid var(--line);color:var(--faint);font-size:13px}
@media (max-width:680px){
  .wrap{padding:0 16px 64px}
  .shot{grid-template-columns:1fr;gap:12px}
  .rail{flex-direction:row;align-items:center;gap:12px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">
<header class="top">
  <p class="eyebrow">쿵쿵이와 친구들 · 시즌 __SEASON__</p>
  <h1>__NO__ 「__TITLE__」 컷 시트</h1>
  <p class="sub">대본을 __CUTS__컷으로 분해한 작업 시트입니다. 컷 내용은 한국어로 읽고, 붙여넣을 영문 프롬프트는 버튼 한 번으로 복사하세요. 완료한 컷을 체크해 두면 진행 상황이 이 브라우저에 저장됩니다.</p>

  <div class="guide">
    <h2>OpenArt 작업 순서</h2>
    <div class="step0">
      <h3>캐릭터는 등록한 이름으로 부르세요</h3>
      <p>
        컷마다 얼굴이 달라진 건 글로만 생성했기 때문입니다. 같은 문장을 넣어도 모델은 매번 그 설명에 맞는
        <strong>새 캐릭터를 새로 디자인</strong>합니다. 눈 간격도 뿔 두께도 문장에 없으니까요.
        seed로도 막히지 않습니다 &mdash; seed는 프롬프트가 완전히 같을 때만 같은 그림을 냅니다.
      </p>
      <p>
        <strong>OpenArt에 등록해 두신 캐릭터를 프롬프트에서 이름으로 부르고 있습니다.</strong>
        한글 이름 그대로 등록하셨으니 아래 프롬프트에도 <code>쿵쿵</code> <code>루카</code>처럼
        그 이름이 들어가 있습니다. 어떤 장면·구도·조명이든 등록된 얼굴로 나옵니다.
        컷 왼쪽의 <strong>등장 캐릭터</strong> 칩이 그 컷에서 지정해야 할 캐릭터입니다.
      </p>
      <p style="margin:0">
        <strong>그리고 외모를 글로 다시 쓰지 마세요.</strong> 이름과 외모 서술이 함께 있으면
        서술이 이겨서 등록한 캐릭터가 밀려납니다. 아래 프롬프트는 그 원칙대로 다시 썼습니다 &mdash;
        외모 서술을 빼고 이름으로만 부르고, 동작·표정·카메라·조명만 남겼습니다.
        평균 길이가 200단어대에서 72단어로 줄어 연출 지시가 묻히지 않습니다.
      </p>
      <details class="en" style="margin-top:12px">
        <summary>등록한 캐릭터가 계속 흔들린다면 &mdash; 마스터 시트로 재등록</summary>
        <p style="margin:10px 0 0;font-size:13.5px;line-height:1.7;color:var(--muted)">
          등록에 쓴 이미지가 정면 한 장뿐이면 옆·뒷모습 컷에서 무너질 수 있습니다. 그럴 땐 캐릭터당
          <strong>다각도 시트</strong>와 <strong>표정 시트</strong>를 만들어 그 여러 장으로 다시 등록하세요 &mdash;
          등록 이미지가 많을수록 정확해집니다. 생성 프롬프트는 저장소의
          <code>characters.json</code>에도 있고, 아래에서 바로 복사할 수 있습니다.
        </p>
        <div class="pair">
          <div class="block">
            <div class="label"><span>① 다각도 시트 &mdash; 정면 · 3/4 · 옆 · 뒤</span><span class="tools"><button class="copy" data-copy="sheet-t">영문 프롬프트 복사</button></span></div>
            <pre id="sheet-t"></pre>
          </div>
          <div class="block">
            <div class="label"><span>② 표정 시트 &mdash; 무표정 · 웃음 · 놀람 · 겁먹음 · 결의 · 폭소</span><span class="tools"><button class="copy" data-copy="sheet-e">영문 프롬프트 복사</button></span></div>
            <pre id="sheet-e"></pre>
          </div>
        </div>
        <p style="margin:10px 0 0;font-size:13.5px;line-height:1.7;color:var(--muted)">
          어느 방식이든 <strong>직전 컷을 레퍼런스로 쓰지 마세요.</strong> 오차가 누적돼 20컷 뒤엔
          다른 캐릭터가 됩니다. 항상 등록된 캐릭터 또는 마스터 시트로 돌아옵니다.
        </p>
      </details>
    </div>
    <ol>
      <li><strong>화면</strong> 설명대로 키프레임 이미지를 만듭니다. 비율 <code>16:9</code>, 모델은 <strong>Nano Banana 2</strong>. 컷에 적힌 <strong>등장 캐릭터를 지정</strong>하고 <strong>영문 프롬프트 복사</strong>를 눌러 붙여넣습니다. <strong>배경</strong>이라고 적힌 18컷은 캐릭터가 없으니 그냥 만들면 됩니다.</li>
      <li>키프레임을 <strong>Image to Video</strong>에 넣고 <strong>움직임</strong> 쪽 영문 프롬프트를 붙여넣습니다. 모델은 <strong>MiniMax H3</strong>(무제한), 길이는 컷에 적힌 초.</li>
      <li>받은 mp4를 <code>SC1-01.mp4</code>처럼 <strong>컷 번호 그대로</strong> 저장합니다. 이어붙일 때 이 이름이 기준이 됩니다.</li>
      <li><strong>나레이션</strong>은 화면 밖 목소리라 립싱크가 필요 없습니다. TTS로 만들어 편집에서 얹으면 됩니다.</li>
    </ol>
    <p style="margin:14px 0 0;color:var(--muted);font-size:13.5px">
      컷 내용은 모두 한국어로 적어 두었습니다. 실제로 붙여넣는 프롬프트만 영어인데(생성 모델이 영어를 훨씬 정확하게 알아듣습니다),
      <strong>영문 프롬프트 복사</strong> 버튼을 쓰면 영어를 읽을 일이 없습니다. 확인하고 싶을 때만 <strong>영문 프롬프트 보기</strong>를 펼치세요.
    </p>
    <details class="script">
      <summary>__NO__ 대사 전체 보기 &mdash; 나레이션 __NARR__ · 캐릭터 대사 __CHAR__</summary>
      <p class="scriptnote">
        녹음용입니다. <strong>나레이션</strong>은 화면 밖 목소리라 립싱크가 필요 없고,
        <strong>캐릭터 대사</strong>만 입을 맞춰야 합니다. 컷 번호 순서 그대로 읽으면 __NO__ 전체가 됩니다.
      </p>
      <ol id="scriptlist"></ol>
    </details>
    <div class="neg">
      <div class="label" style="margin-bottom:6px">공통 네거티브 프롬프트 — 한 번만 설정해두면 됩니다</div>
      <pre id="neg"></pre>
    </div>
  </div>
</header>

<div class="bar">
  <div class="progress">
    <div class="track"><div class="fill" id="fill"></div></div>
    <span class="count" id="count">0 / 60</span>
  </div>
  <div class="filters">
    <button data-f="all" aria-pressed="true">전체</button>
    <button data-f="todo" aria-pressed="false">남은 컷</button>
    <button data-f="line" aria-pressed="false">대사 있는 컷</button>
  </div>
  <button class="copy" id="reset" style="margin-left:auto">진행 초기화</button>
</div>

<main id="list"></main>

<footer>
  총 __CUTS__컷 · __SEC__초(__MIN__분 __SS__초) · 나레이션 __NARR__ · 캐릭터 대사 __CHAR__
</footer>
</div>

<script>
const DATA = __DATA__;
const KEY = "kungkung-__EPKEY__-v2-done";

let done = {};
try { done = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { done = {}; }
function save(){ try { localStorage.setItem(KEY, JSON.stringify(done)); } catch(e){} }

document.getElementById("neg").textContent = DATA.negative;
document.getElementById("sheet-t").textContent = DATA.sheets.turnaround;
document.getElementById("sheet-e").textContent = DATA.sheets.expressions;

const list = document.getElementById("list");
const esc = s => s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

document.getElementById("scriptlist").innerHTML = DATA.shots.filter(s => s.line).map(s =>
  `<li class="${s.who === "나레이션" ? "narr" : ""}">`
  + `<span class="c">${s.id}</span><span class="w">${esc(s.who)}</span>`
  + `<span class="t">${esc(s.line)}</span></li>`).join("");

let html = "", cur = null, idx = 0;
for (const s of DATA.shots) {
  if (s.sec !== cur) {
    if (cur !== null) html += "</section>";
    cur = s.sec;
    const n = DATA.shots.filter(x => x.sec === cur).length;
    html += `<section><h2>${esc(DATA.sections[cur])}<span class="n">${n}컷</span></h2><div class="rule"></div>`;
  }
  idx++;
  const line = s.line
    ? `<div class="line${s.who === "나레이션" ? " narr" : ""}"><span class="who">${esc(s.who)}</span>${esc(s.line)}</div>`
    : `<div class="line none">대사 없음 · 화면만</div>`;
  html += `
  <article class="shot" data-id="${s.id}" data-line="${s.line ? 1 : 0}" data-done="0">
    <div class="rail">
      <span class="id">${s.id}</span>
      <span class="meta">${s.dur}초 · ${esc(s.shotko)}</span>
      <button class="chk" data-toggle="${s.id}">
        <span class="box"><svg viewBox="0 0 12 12"><path d="M2 6.2 4.6 8.8 10 3.4"/></svg></span>완료
      </button>
      <div class="cast">${s.cast.length
        ? s.cast.map(c => `<span class="c">${esc(c)}</span>`).join("")
        : `<span class="bg">배경</span>`}</div>
    </div>
    <div class="body">
      ${s.link ? `<div class="link ${s.link}"><span class="tag">${esc(s.link)}</span><p class="txt">${esc(s.linkko)}${s.link === "연속" ? " <strong>앞 컷의 마지막 프레임을 이 컷의 시작 프레임으로 넣으세요.</strong>" : ""}</p></div>` : ""}
      ${line}
      <div class="block">
        <div class="label"><span>화면에 담길 것${s.cast.length ? ` <span style="color:var(--peach);font-weight:600">· 캐릭터 ${s.cast.length}명 지정</span>` : ""}</span><span class="tools"><button class="copy" data-copy="i${idx}">영문 프롬프트 복사</button></span></div>
        <p class="ko">${esc(s.ko)}</p>
        <details class="en"><summary>영문 프롬프트 보기</summary><pre id="i${idx}">${esc(s.img)}</pre></details>
      </div>
      <div class="block">
        <div class="label"><span>카메라 · 움직임</span><span class="tools"><button class="copy" data-copy="m${idx}">영문 프롬프트 복사</button></span></div>
        <p class="ko">${esc(s.komo)}</p>
        <details class="en"><summary>영문 프롬프트 보기</summary><pre id="m${idx}">${esc(s.mo)}</pre></details>
      </div>
    </div>
  </article>`;
}
html += "</section>";
list.innerHTML = html;

const shots = [...document.querySelectorAll(".shot")];
function render(){
  let n = 0;
  for (const el of shots) {
    const d = done[el.dataset.id] ? 1 : 0;
    el.dataset.done = d; n += d;
  }
  document.getElementById("count").textContent = `${n} / ${shots.length}`;
  document.getElementById("fill").style.width = (n / shots.length * 100) + "%";
  applyFilter();
}
let filter = "all";
function applyFilter(){
  for (const el of shots) {
    const hide = (filter === "todo" && el.dataset.done === "1")
              || (filter === "line" && el.dataset.line === "0");
    el.style.display = hide ? "none" : "";
  }
  for (const sec of document.querySelectorAll("section")) {
    const any = [...sec.querySelectorAll(".shot")].some(el => el.style.display !== "none");
    sec.style.display = any ? "" : "none";
  }
}

document.addEventListener("click", async e => {
  const t = e.target.closest("[data-toggle], [data-copy], [data-f], #reset");
  if (!t) return;
  if (t.dataset.toggle) {
    done[t.dataset.toggle] = !done[t.dataset.toggle];
    if (!done[t.dataset.toggle]) delete done[t.dataset.toggle];
    save(); render();
  } else if (t.dataset.copy) {
    const text = document.getElementById(t.dataset.copy).textContent;
    try { await navigator.clipboard.writeText(text); }
    catch (err) {
      const ta = document.createElement("textarea");
      ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch (e2) {}
      ta.remove();
    }
    const prev = t.textContent;
    t.textContent = "복사됐습니다"; t.dataset.ok = "1";
    setTimeout(() => { t.textContent = prev; delete t.dataset.ok; }, 1400);
  } else if (t.dataset.f) {
    filter = t.dataset.f;
    for (const b of document.querySelectorAll("[data-f]")) b.setAttribute("aria-pressed", b === t);
    applyFilter();
  } else if (t.id === "reset") {
    done = {}; save(); render();
  }
});
render();
</script>
'''

EPMETA = json.loads((ROOT / "episodes" / EP / "episode.json").read_text(encoding="utf-8"))
_n = int(EP[2:]) if EP[2:].isdigit() else 1
_narr = sum(1 for s in SHOTS["shots"] if s["dialogue"] and s["speaker"] == "나레이션")
_char = sum(1 for s in SHOTS["shots"] if s["dialogue"] and s["speaker"] != "나레이션")
_sec = sum(s["duration"] for s in SHOTS["shots"])
page = HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False))
for token, value in (("__NO__", EPMETA["no"]), ("__TITLE__", EPMETA["title"]),
                     ("__SEASON__", str((_n - 1) // 10 + 1)),
                     ("__CUTS__", str(len(SHOTS["shots"]))), ("__EPKEY__", EP),
                     ("__SEC__", str(_sec)), ("__MIN__", str(_sec // 60)),
                     ("__SS__", "%02d" % (_sec % 60)),
                     ("__NARR__", str(_narr)), ("__CHAR__", str(_char))):
    page = page.replace(token, value)

out = DIST / ("kungkung_%s_sheet.html" % EP)
out.write_text(page, encoding='utf-8')
print("작성:", out, out.stat().st_size // 1024, "KB")
