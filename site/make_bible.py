# -*- coding: utf-8 -*-
"""캐릭터 바이블 — 성격·MBTI·목소리·꿈·두려움과 집.

저장소 데이터에서 직접 읽어 site/dist/ 에 HTML을 만든다.
    python3 site/build.py       # 세 페이지 전부
    python3 site/make_bible.py
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

FULL = {n: ("쿵쿵이" if n == "쿵쿵" else n) for n in ORDER}
EN = {"쿵쿵":"Kung-Kung","루카":"Luca","후안":"Juan","미미":"Mimi","티니":"Tini","루비":"Ruby","노을":"Noeul"}
ONE = {"쿵쿵":"생각보다 몸이 먼저 나가는, 힘을 모르는 아기",
 "루카":"제일 먼저 나서고 혼자 곱씹는 맏이","후안":"말은 없고 제일 먼저 만져보는 막내",
 "미미":"확인한 다음에 말하는 관찰자","티니":"혼자 신나는 게 아니라 옆까지 신나게 만드는 아이",
 "루비":"마음을 먼저 읽는, 이야기의 감정 엔진",
 "노을":"무리 밖에 서서, 아무도 못 본 것을 한마디로 짚는 아이"}
VOICE = {"쿵쿵":("5~6세","높고 허스키","보통","배에서 울림이 있다"),
 "루카":("8~9세","가장 낮음","보통","문장을 끝까지 맺는다"),
 "후안":("5세","작고 몽글","느림","대사보다 감탄사"),
 "미미":("7세","낮음","가장 느림","말 앞에 뜸을 들인다"),
 "티니":("5~6세","가장 높음","가장 빠름","늘 숨이 차 있다"),
 "루비":("6~7세","높음","보통","감정 폭이 가장 크다"),
 "노을":("8~9세","낮고 건조","가장 느림","한 문장을 넘기지 않는다")}
from collections import Counter
_lines = Counter(s["speaker"] for s in SHOTS["shots"] if s["dialogue"])
_cast = Counter(n for s in SHOTS["shots"] for n in s["cast"])
data = {"chars": [], "voice": [], "lines": [], "narr": _lines.get("나레이션", 0),
  "homeCommon": ("여섯 집 모두 안쪽 구조가 같습니다 — 작업 공방 · 식량 저장고 · 아늑한 침대 · 탐험가의 기록실. "
    "겉모습은 캐릭터마다 완전히 다른데 사는 방식은 같다는 뜻이고, 실내 컷의 레이아웃을 공유할 수 있습니다.")}
for n in ORDER:
    c = CHARS["characters"][n]; p = c["profile"]
    data["chars"].append({"key": n, "ko": FULL[n], "en": EN[n], "role": c["role"], "h": c["height"],
        "mbti": p["mbti"], "mbtiko": p["mbti_ko"], "energy": p["energy"], "one": ONE[n],
        "home": c["home"],
        "fields": [["성격", p["personality"]], ["목소리", p["voice"]], ["꿈", p["dream"]],
                   ["무서워하는 것", p["fear"]], ["좋아하는 것", p["likes"]],
                   ["싫어하는 것", p["dislikes"]], ["버릇 · 시그니처", p["habit"]],
                   ["시리즈에서의 역할", p["arc"]]]})
    a, r, sp, ft = VOICE[n]
    data["voice"].append({"key": n, "ko": FULL[n], "age": a, "range": r, "speed": sp, "feat": ft})
    data["lines"].append({"key": n, "ko": FULL[n], "n": _lines.get(n, 0), "cuts": _cast.get(n, 0)})

HTML = r'''<title>쿵쿵이와 친구들 캐릭터 바이블</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
:root{
  --ground:#F6F8F6; --surface:#FFFFFF; --surface-2:#EFF3F0;
  --ink:#141E1B; --muted:#54645F; --faint:#8B9B95;
  --accent:#218A6E; --line:#DDE4E0; --line-strong:#C6D2CC;
  --c-kung:#3E9E6E; --c-luca:#C4652C; --c-juan:#3A579B; --c-mimi:#7A5AA6; --c-tini:#A9772A; --c-ruby:#C25F8B;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926;
    --ink:#E4EDE9; --muted:#9BAEA8; --faint:#6C807A;
    --accent:#4FCBA4; --line:#25322E; --line-strong:#33433E;
    --c-kung:#6ED9A4; --c-luca:#EE9A5E; --c-juan:#7B9BE0; --c-mimi:#B392E0; --c-tini:#E0B364; --c-ruby:#EE94BC;
  }
}
:root[data-theme="dark"]{
  --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926;
  --ink:#E4EDE9; --muted:#9BAEA8; --faint:#6C807A;
  --accent:#4FCBA4; --line:#25322E; --line-strong:#33433E;
  --c-kung:#6ED9A4; --c-luca:#EE9A5E; --c-juan:#7B9BE0; --c-mimi:#B392E0; --c-tini:#E0B364; --c-ruby:#EE94BC;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans KR",system-ui,sans-serif; font-size:16px; line-height:1.75;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:860px; margin:0 auto; padding:56px 24px 96px; display:flex; flex-direction:column; gap:44px}
.eyebrow{
  font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.14em;
  color:var(--accent); font-weight:600; margin:0 0 10px;
}
h1{
  font-family:"Gowun Batang",serif; font-weight:700; font-size:clamp(30px,5.4vw,44px);
  line-height:1.25; margin:0 0 14px; text-wrap:balance; letter-spacing:-.01em;
}
.lede{margin:0; color:var(--muted); font-size:16.5px; max-width:62ch}
.lede strong{color:var(--ink); font-weight:600}
h2{
  font-family:"Gowun Batang",serif; font-weight:700; font-size:21px; margin:0 0 4px;
  display:flex; align-items:baseline; gap:10px; flex-wrap:wrap;
}
h2 .en{font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--faint); font-weight:500; letter-spacing:.04em}
.tablewrap{overflow-x:auto; border:1px solid var(--line); border-radius:12px; background:var(--surface)}
table{border-collapse:collapse; width:100%; min-width:520px; font-size:14.5px}
th,td{padding:11px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:baseline}
thead th{
  font-size:11.5px; letter-spacing:.09em; color:var(--faint); font-weight:600;
  background:var(--surface-2); white-space:nowrap;
}
tbody tr:last-child td{border-bottom:none}
td.num{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; white-space:nowrap}
td .nm{font-weight:700}
.mono{font-family:"IBM Plex Mono",monospace; font-size:12.5px; font-weight:600; letter-spacing:.02em}
.card{
  background:var(--surface); border:1px solid var(--line); border-radius:14px;
  border-left:5px solid var(--hue); padding:24px 26px; display:flex; flex-direction:column; gap:18px;
}
.card h2{color:var(--hue); margin:0}
.meta{
  display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center;
  font-size:13px; color:var(--muted); margin-top:2px;
}
.chip{
  font-family:"IBM Plex Mono",monospace; font-size:11.5px; font-weight:600;
  padding:2px 8px; border-radius:999px; border:1px solid var(--line-strong); color:var(--muted);
}
.chip.hue{border-color:var(--hue); color:var(--hue)}
.one{
  margin:0; font-family:"Gowun Batang",serif; font-size:17.5px; line-height:1.6;
  color:var(--ink); text-wrap:balance;
}
dl{margin:0; display:grid; grid-template-columns:118px 1fr; gap:1px 20px}
dl>div{display:contents}
dt{
  font-size:12.5px; font-weight:600; color:var(--faint); padding:9px 0 0;
  border-top:1px solid var(--line);
}
dd{margin:0; padding:9px 0 12px; border-top:1px solid var(--line); font-size:15px; line-height:1.75; color:var(--ink)}
dd.soft{color:var(--muted)}
.note{
  background:var(--surface-2); border:1px solid var(--line); border-radius:12px;
  padding:18px 22px; font-size:14.5px; line-height:1.75; color:var(--muted);
}
.note strong{color:var(--ink); font-weight:600}
.note p{margin:0}
.note p + p{margin-top:10px}
.zero{color:var(--c-luca); font-weight:700}
.home{
  margin-top:2px; padding:16px 18px; border-radius:11px;
  background:var(--surface-2); border:1px solid var(--line); display:flex; flex-direction:column; gap:9px;
}
.home .hd{display:flex; align-items:baseline; gap:9px; flex-wrap:wrap}
.home .hn{font-family:"Gowun Batang",serif; font-size:16.5px; font-weight:700; color:var(--hue)}
.home .hs{font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--faint); font-variant-numeric:tabular-nums}
.home p{margin:0; font-size:14.5px; line-height:1.75; color:var(--ink)}
.home .tie{
  padding-left:12px; border-left:2px solid var(--hue); color:var(--muted); font-size:14px;
}
footer{
  border-top:1px solid var(--line); padding-top:18px; color:var(--faint); font-size:13px;
}
@media (max-width:560px){
  .wrap{padding:40px 16px 72px; gap:34px}
  .card{padding:20px 18px}
  dl{grid-template-columns:1fr; gap:0}
  dt{border-top:1px solid var(--line); padding-top:11px}
  dd{border-top:none; padding-top:2px}
}
@media (prefers-reduced-motion:no-preference){
  .card{transition:border-color .15s}
}
</style>

<div class="wrap">
<header>
  <p class="eyebrow">쿵쿵이와 친구들 · 시즌 1</p>
  <h1>캐릭터 바이블</h1>
  <p class="lede">
    여섯 캐릭터의 성격과 목소리, 꿈과 두려움을 정리했습니다.
    <strong>대사를 쓸 때와 성우를 고를 때의 기준</strong>입니다.
    외모는 등록된 3D 모델이 담당하니, 이 문서는 그 안에 무엇이 들어 있는지를 다룹니다.
    각자의 집도 함께 넣었습니다 &mdash; 집은 성격이 밖으로 나온 결과입니다.
  </p>
</header>

<section>
  <h2>여섯 명</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>캐릭터</th><th>키</th><th>MBTI</th><th>성향</th><th>한 줄</th></tr></thead>
    <tbody id="roster"></tbody>
  </table></div>
</section>

<section>
  <h2>목소리 대비표</h2>
  <p class="lede" style="margin:0 0 14px">
    여섯이 모두 높은 아이 목소리면 한 화면에 다 나올 때 누가 말하는지 구분이 안 됩니다.
    나이감·음역·속도를 서로 겹치지 않게 배정했습니다.
  </p>
  <div class="tablewrap"><table>
    <thead><tr><th>캐릭터</th><th>나이감</th><th>음역</th><th>속도</th><th>특징</th></tr></thead>
    <tbody id="voice"></tbody>
  </table></div>
</section>

<section>
  <h2>집 &mdash; 최고의 안식처</h2>
  <p class="lede" id="homecommon"></p>
</section>

<div id="cards" style="display:flex;flex-direction:column;gap:24px"></div>

<section>
  <h2>1화 대사 배분</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>화자</th><th>등장 컷</th><th>대사</th></tr></thead>
    <tbody id="lines"></tbody>
  </table></div>
  <div class="note" style="margin-top:16px">
    <p>
      <strong>후안은 18개 컷에 나오면서 1화 내내 한 마디도 하지 않습니다.</strong>
      대본이 그렇게 되어 있습니다.
    </p>
    <p>
      이걸 «말이 늦게 트이는 아이»라는 설정으로 살릴지, 1화에 한 줄을 넣을지 결정이 필요합니다.
      살린다면 나중에 나올 첫 대사에 무게가 크게 실립니다. 넣는다면 후안이 얼음에 뺨을 붙였다
      물러나는 SC2-09가 자리로 맞습니다 — 바로 다음 컷에서 루비가 «알이 추워 보여»로 받으니
      흐름이 이어집니다.
    </p>
  </div>
</section>

<footer>
  전문과 구조화된 값은 저장소에 있습니다 — <span class="mono">canco-studio</span> ·
  <span class="mono">episodes/ep1/docs/08_캐릭터_바이블.md</span> ·
  <span class="mono">prompts/characters.json</span>의 <span class="mono">profile</span>
</footer>
</div>

<script>
const DATA = __DATA__;
const HUE = {쿵쿵:"--c-kung", 루카:"--c-luca", 후안:"--c-juan", 미미:"--c-mimi", 티니:"--c-tini", 루비:"--c-ruby"};
const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

document.getElementById("roster").innerHTML = DATA.chars.map(c => `
  <tr>
    <td><span class="nm" style="color:var(${HUE[c.key]})">${esc(c.ko)}</span></td>
    <td class="num">${c.h}cm</td>
    <td class="num">${esc(c.mbti)}</td>
    <td>${esc(c.energy.split(" — ")[0])}</td>
    <td>${esc(c.one)}</td>
  </tr>`).join("");

document.getElementById("voice").innerHTML = DATA.voice.map(v => `
  <tr>
    <td><span class="nm" style="color:var(${HUE[v.key]})">${esc(v.ko)}</span></td>
    <td class="num">${esc(v.age)}</td><td>${esc(v.range)}</td>
    <td>${esc(v.speed)}</td><td>${esc(v.feat)}</td>
  </tr>`).join("");

document.getElementById("lines").innerHTML =
  `<tr><td><span class="nm">나레이션</span></td><td class="num">—</td><td class="num">${DATA.narr}줄</td></tr>`
  + DATA.lines.slice().sort((a,b) => b.n - a.n).map(l => `
  <tr>
    <td><span class="nm" style="color:var(${HUE[l.key]})">${esc(l.ko)}</span></td>
    <td class="num">${l.cuts}컷</td>
    <td class="num${l.n === 0 ? " zero" : ""}">${l.n}줄</td>
  </tr>`).join("");

document.getElementById("homecommon").textContent = DATA.homeCommon;
document.getElementById("cards").innerHTML = DATA.chars.map(c => `
  <article class="card" style="--hue:var(${HUE[c.key]})">
    <div>
      <h2>${esc(c.ko)}<span class="en">${esc(c.en)}</span></h2>
      <div class="meta">
        <span class="chip hue">${esc(c.mbti)}</span>
        <span class="chip">${esc(c.mbtiko)}</span>
        <span class="chip">${c.h}cm</span>
        <span>${esc(c.role)}</span>
      </div>
    </div>
    <p class="one">${esc(c.one)}</p>
    <dl>${c.fields.map(([k, v]) =>
      `<div><dt>${esc(k)}</dt><dd${k === "시리즈에서의 역할" ? ' class="soft"' : ""}>${esc(v)}</dd></div>`
    ).join("")}</dl>
    <div class="home">
      <div class="hd"><span class="hn">${esc(c.home.name)}</span>
        <span class="hs">${esc(c.home.en)} · ${esc(c.home.size)}</span></div>
      <p>${esc(c.home.desc)}</p>
      <p class="tie">${esc(c.home.tie)}</p>
    </div>
  </article>`).join("");
</script>
'''

out = DIST / "kungkung_bible.html"
out.write_text(HTML.replace('__DATA__', json.dumps(data, ensure_ascii=False)), encoding='utf-8')
print('작성:', out, out.stat().st_size // 1024, 'KB')
