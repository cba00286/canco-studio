# -*- coding: utf-8 -*-
"""제작 자료실 — 캐릭터·집·에피소드. 편집 권한이 있으면 페이지에서 바로 고친다.

저장소 데이터에서 직접 읽어 site/dist/ 에 HTML을 만든다.
    python3 site/build.py       # 세 페이지 전부
    python3 site/make_hub.py
"""
import html, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import refs

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
PROMPTS = ROOT / "episodes" / EP / "prompts"
DIST = HERE / "dist"
DIST.mkdir(parents=True, exist_ok=True)

CHARS = json.loads((PROMPTS / "characters.json").read_text(encoding="utf-8"))
SHOTS = json.loads((PROMPTS / "shots_v2.json").read_text(encoding="utf-8"))
ORDER = ["쿵쿵", "루카", "후안", "미미", "티니", "루비"]

FULL = {n: ("쿵쿵이" if n == "쿵쿵" else n) for n in ORDER}
EN = {"쿵쿵":"Kung-Kung","루카":"Luca","후안":"Juan","미미":"Mimi","티니":"Tini","루비":"Ruby"}
LOOK = json.loads((PROMPTS / "looks.json").read_text(encoding="utf-8"))
chars = []
for n in ORDER:
    c = CHARS["characters"][n]; p = c["profile"]; h = c["home"]
    chars.append({"key": n, "ko": FULL[n], "en": EN[n], "role": c["role"], "h": c["height"],
        "mbti": p["mbti"], "mbtiko": p["mbti_ko"], "look": LOOK[n],
        "personality": p["personality"], "voice": p["voice"], "dream": p["dream"],
        "fear": p["fear"], "likes": p["likes"], "dislikes": p["dislikes"],
        "habit": p["habit"], "arc": p["arc"], "home": h})
SHEETS = ROOT / "episodes" / EP / "reference" / "sheets"
HOMES = ROOT / "episodes" / EP / "reference" / "homes"
_bytes = 0
for c in chars:
    for slot, folder in (("sheetimg", SHEETS), ("homeimg", HOMES)):
        f = refs.find(folder, c["key"])
        if f:
            uri, n = refs.data_uri(f)
            c[slot] = uri; _bytes += n
        else:
            c[slot] = ""
_chart = refs.find_chart(SHEETS)
CHART = ""
if _chart:
    CHART, n = refs.data_uri(_chart, max_w=1800); _bytes += n
_n, _rep = refs.report(SHEETS, HOMES, ORDER)
print("레퍼런스 이미지 %d장 / 13장  %.1fMB" % (_n, _bytes / 1e6), file=sys.stderr)
if _n < 13:
    print(_rep, file=sys.stderr)

EPMETA = json.loads((ROOT / "episodes" / EP / "episode.json").read_text(encoding="utf-8"))
D = {"chars": chars,
  "lines": [{"id": s["id"], "who": s["speaker"], "text": s["dialogue"]} for s in SHOTS["shots"] if s["dialogue"]],
  "secs": [{"key": k, "title": v, "n": sum(1 for s in SHOTS["shots"] if s["section"] == k),
            "sec": sum(s["duration"] for s in SHOTS["shots"] if s["section"] == k)}
           for k, v in SHOTS["sections"].items()],
  "ep1": dict(EPMETA, cuts=len(SHOTS["shots"]))}

e = lambda s: html.escape(str(s), quote=True)
HUE = {'쿵쿵':'kung','루카':'luca','후안':'juan','미미':'mimi','티니':'tini','루비':'ruby'}

def img(uri, alt):
    """레퍼런스 이미지. 없으면 아무것도 넣지 않는다 — 빈 자리를 만들지 않는다."""
    if not uri:
        return ""
    return ('<figure class="ref"><img src="%s" alt="%s" loading="lazy">'
            '<figcaption>%s</figcaption></figure>' % (uri, e(alt), e(alt)))


def field(label, key, value):
    return ('<div class="f"><div class="fl">%s</div>'
            '<div class="fv ed" data-field="%s" contenteditable="plaintext-only">%s</div></div>'
            % (e(label), e(key), e(value)))

# ---------- 캐릭터 ----------
cards = []
for c in D['chars']:
    cards.append('''
  <article class="card c-%s" data-key="%s">
    <header class="ch">
      <h3><span class="ed nm" data-field="ko" contenteditable="plaintext-only">%s</span><span class="en">%s</span></h3>
      <div class="tags">
        <span class="tag hue ed" data-field="mbti" contenteditable="plaintext-only">%s</span>
        <span class="tag ed" data-field="mbti_ko" contenteditable="plaintext-only">%s</span>
        <span class="tag ed" data-field="height" contenteditable="plaintext-only">%scm</span>
        <span class="tag ed" data-field="role" contenteditable="plaintext-only">%s</span>
      </div>
    </header>
    %s
    <div class="fields">%s%s%s%s%s%s%s%s</div>
    <div class="home">
      <div class="hh"><span class="hn ed" data-field="home.name" contenteditable="plaintext-only">%s</span>
        <span class="hs ed" data-field="home.enSize" contenteditable="plaintext-only">%s · %s</span></div>
      <p class="ed" data-field="home.desc" contenteditable="plaintext-only">%s</p>
      <p class="tie ed" data-field="home.tie" contenteditable="plaintext-only">%s</p>
      %s
    </div>
  </article>''' % (HUE[c['key']], e(c['key']), e(c['ko']), e(c['en']),
     e(c['mbti']), e(c['mbtiko']), c['h'], e(c['role']),
     img(c['sheetimg'], '%s 3D 마스터 시트' % c['ko']),
     field('모습', 'look', c['look']), field('성격', 'personality', c['personality']),
     field('목소리', 'voice', c['voice']), field('꿈', 'dream', c['dream']),
     field('무서워하는 것', 'fear', c['fear']), field('좋아하는 것', 'likes', c['likes']),
     field('싫어하는 것', 'dislikes', c['dislikes']), field('버릇 · 시그니처', 'habit', c['habit']),
     e(c['home']['name']), e(c['home']['en']), e(c['home']['size']),
     e(c['home']['desc']), e(c['home']['tie']),
     img(c['homeimg'], '%s — %s 마스터 시트' % (c['ko'], c['home']['name']))))

# ---------- 집 ----------
homes = []
for c in D['chars']:
    homes.append('''
  <tr data-key="%s">
    <td><span class="nm c-%s-t ed" contenteditable="plaintext-only">%s</span></td>
    <td><span class="ed" contenteditable="plaintext-only">%s</span></td>
    <td class="num"><span class="ed" contenteditable="plaintext-only">%s</span></td>
    <td><span class="ed" contenteditable="plaintext-only">%s</span></td>
  </tr>''' % (e(c['key']), HUE[c['key']], e(c['ko']), e(c['home']['name']),
              e(c['home']['size']), e(c['home']['desc'])))

# ---------- 대사 ----------
lines = ''.join('''
  <tr data-key="%s"><td class="num"><span class="ed" contenteditable="plaintext-only">%s</span></td>
  <td><span class="w ed" contenteditable="plaintext-only">%s</span></td>
  <td><span class="ed" contenteditable="plaintext-only">%s</span></td></tr>'''
  % (e(l['id']), e(l['id']), e(l['who']), e(l['text'])) for l in D['lines'])

secs = ''.join('''
  <tr data-key="%s"><td><span class="ed" contenteditable="plaintext-only">%s</span></td>
  <td class="num"><span class="ed" contenteditable="plaintext-only">%d컷</span></td>
  <td class="num"><span class="ed" contenteditable="plaintext-only">%d초</span></td></tr>'''
  % (e(s['key']), e(s['title']), s['n'], s['sec']) for s in D['secs'])

ep = D['ep1']

CSS = r'''
:root{
  --ground:#F6F8F6; --surface:#FFFFFF; --surface-2:#EFF3F0; --sunk:#E7EDE9;
  --ink:#141E1B; --muted:#54645F; --faint:#8B9B95;
  --accent:#218A6E; --accent-soft:#DCEFE7; --peach:#C4693B; --peach-soft:#F7E7DC;
  --line:#DDE4E0; --line-strong:#C6D2CC;
  --kung:#3E9E6E; --luca:#C4652C; --juan:#3A579B; --mimi:#7A5AA6; --tini:#A9772A; --ruby:#C25F8B;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926; --sunk:#111A18;
  --ink:#E4EDE9; --muted:#9BAEA8; --faint:#6C807A;
  --accent:#4FCBA4; --accent-soft:#17322A; --peach:#E5946A; --peach-soft:#33231A;
  --line:#25322E; --line-strong:#33433E;
  --kung:#6ED9A4; --luca:#EE9A5E; --juan:#7B9BE0; --mimi:#B392E0; --tini:#E0B364; --ruby:#EE94BC;
}}
:root[data-theme="dark"]{
  --ground:#0E1513; --surface:#16201D; --surface-2:#1D2926; --sunk:#111A18;
  --ink:#E4EDE9; --muted:#9BAEA8; --faint:#6C807A;
  --accent:#4FCBA4; --accent-soft:#17322A; --peach:#E5946A; --peach-soft:#33231A;
  --line:#25322E; --line-strong:#33433E;
  --kung:#6ED9A4; --luca:#EE9A5E; --juan:#7B9BE0; --mimi:#B392E0; --tini:#E0B364; --ruby:#EE94BC;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans KR",system-ui,sans-serif;font-size:16px;line-height:1.75;-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding:44px 22px 90px;display:flex;flex-direction:column;gap:26px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.14em;color:var(--accent);font-weight:600;margin:0 0 9px}
h1{font-family:"Gowun Batang",serif;font-weight:700;font-size:clamp(27px,5vw,40px);line-height:1.25;margin:0 0 12px;text-wrap:balance}
.lede{margin:0;color:var(--muted);font-size:15.5px;max-width:64ch}
h2{font-family:"Gowun Batang",serif;font-weight:700;font-size:20px;margin:0 0 12px}
.bar{position:sticky;top:0;z-index:20;background:var(--ground);padding:10px 0;
  border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tab,.btn{font:inherit;font-size:13.5px;font-weight:600;padding:7px 14px;border-radius:999px;
  border:1px solid var(--line-strong);background:var(--surface);color:var(--muted);cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.tab:focus-visible,.btn:focus-visible,.ed:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.btn.edit[aria-pressed="true"]{background:var(--peach);border-color:var(--peach);color:var(--surface)}
.spacer{flex:1}
.state{font-size:12.5px;color:var(--faint);font-family:"IBM Plex Mono",monospace}
.panel{display:none;flex-direction:column;gap:20px}
body[data-local-tab="chars"] #p-chars,
body[data-local-tab="homes"] #p-homes,
body[data-local-tab="eps"]   #p-eps{display:flex}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  border-left:5px solid var(--hue,var(--line-strong));padding:22px 24px;display:flex;flex-direction:column;gap:16px}
.c-kung{--hue:var(--kung)} .c-luca{--hue:var(--luca)} .c-juan{--hue:var(--juan)}
.c-mimi{--hue:var(--mimi)} .c-tini{--hue:var(--tini)} .c-ruby{--hue:var(--ruby)}
.c-kung-t{color:var(--kung)} .c-luca-t{color:var(--luca)} .c-juan-t{color:var(--juan)}
.c-mimi-t{color:var(--mimi)} .c-tini-t{color:var(--tini)} .c-ruby-t{color:var(--ruby)}
.ch h3{font-family:"Gowun Batang",serif;font-size:21px;margin:0 0 8px;display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;color:var(--hue)}
.ch .en{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--faint);font-weight:500}
.tags{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.tag{font-family:"IBM Plex Mono",monospace;font-size:11.5px;font-weight:600;padding:2px 9px;
  border-radius:999px;border:1px solid var(--line-strong);color:var(--muted)}
.tag.hue{border-color:var(--hue);color:var(--hue)}
.fields{display:flex;flex-direction:column}
.f{display:grid;grid-template-columns:118px 1fr;gap:0 20px;border-top:1px solid var(--line)}
.fl{font-size:12.5px;font-weight:600;color:var(--faint);padding:9px 0 0}
.fv{padding:9px 0 12px;font-size:15px;line-height:1.75}
.home{background:var(--surface-2);border:1px solid var(--line);border-radius:11px;padding:15px 17px;display:flex;flex-direction:column;gap:8px}
.hh{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.hn{font-family:"Gowun Batang",serif;font-size:16px;font-weight:700;color:var(--hue)}
.hs{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--faint)}
.home p{margin:0;font-size:14.5px;line-height:1.75}
.home .tie{padding-left:11px;border-left:2px solid var(--hue);color:var(--muted);font-size:14px}
.ref{margin:0;display:flex;flex-direction:column;gap:7px}
.ref img{width:100%;height:auto;display:block;border-radius:10px;border:1px solid var(--line);background:var(--surface-2)}
.ref figcaption{font-size:12px;color:var(--faint);font-family:"IBM Plex Mono",monospace}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:520px;font-size:14.5px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:baseline}
thead th{font-size:11.5px;letter-spacing:.09em;color:var(--faint);font-weight:600;background:var(--surface-2);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.num{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;white-space:nowrap}
td .nm{font-weight:700}
td .w{font-weight:700;color:var(--peach)}
.epi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 24px;display:flex;flex-direction:column;gap:14px}
.epi h3{font-family:"Gowun Batang",serif;font-size:22px;margin:0;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.epi .no{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--accent);font-weight:600}
.log{margin:0;font-size:15px;line-height:1.8;color:var(--ink)}
.stats{display:flex;flex-wrap:wrap;gap:6px}
.ed{border-radius:4px}
body[data-local-mode="edit"] .ed{
  outline:1px dashed var(--line-strong); outline-offset:3px; background:var(--sunk);
}
body[data-local-mode="edit"] .ed:hover{outline-color:var(--peach)}
body[data-local-mode="edit"] .ed:focus{outline:2px solid var(--accent);outline-offset:3px;background:var(--surface)}
body:not([data-local-mode="edit"]) .ed{caret-color:transparent;cursor:default}
[artifact-sync-state="off"]{opacity:.96}
.ro{background:var(--peach-soft);border:1px solid var(--peach);color:var(--peach);
  border-radius:10px;padding:11px 15px;font-size:13.5px;font-weight:600}
.hint{font-size:13px;color:var(--faint);margin:0}
.tpl{display:none}
footer{border-top:1px solid var(--line);padding-top:16px;color:var(--faint);font-size:13px}
@media (max-width:560px){
  .wrap{padding:32px 14px 70px}
  .card,.epi{padding:18px 16px}
  .f{grid-template-columns:1fr;gap:0}
  .fl{padding-top:11px} .fv{padding-top:2px}
}
'''

BODY = '''<title>쿵쿵이와 친구들 제작 자료실</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>%s</style>

<div class="wrap">
<header>
  <p class="eyebrow">쿵쿵이와 친구들 · 시즌 1</p>
  <h1>제작 자료실</h1>
  <p class="lede">
    캐릭터와 집, 에피소드를 한곳에서 봅니다.
    <strong>편집</strong>을 켜면 글이 있는 곳은 어디든 고칠 수 있고, 고친 내용은 바로 저장되어 모두에게 보입니다.
  </p>
</header>

<artifact-local>
  <div class="bar">
    <button class="tab" data-tab="chars" aria-selected="true">캐릭터</button>
    <button class="tab" data-tab="homes" aria-selected="false">집</button>
    <button class="tab" data-tab="eps" aria-selected="false">에피소드</button>
    <span class="spacer"></span>
    <span class="state" id="state">읽기 전용</span>
    <button class="btn edit" id="editbtn" aria-pressed="false">편집</button>
  </div>
  <div class="ro" id="ro" hidden>
    이 페이지를 볼 수는 있지만 고칠 권한이 없습니다. 편집이 필요하면 소유자에게 편집 권한을 요청하세요.
  </div>
</artifact-local>

<section class="panel" id="p-chars">
  <h2>캐릭터 여섯</h2>
  %s
</section>

<section class="panel" id="p-homes">
  <h2>집 — 최고의 안식처</h2>
  %s
  <p class="hint">여섯 집 모두 안쪽 구성이 같습니다 — 작업 공방 · 식량 저장고 · 아늑한 침대 · 탐험가의 기록실.</p>
  <div class="tablewrap"><table>
    <thead><tr><th>캐릭터</th><th>집</th><th>크기</th><th>설명</th></tr></thead>
    <tbody artifact-sync>%s</tbody>
  </table></div>
</section>

<section class="panel" id="p-eps">
  <h2>에피소드</h2>
  <div id="eplist" style="display:flex;flex-direction:column;gap:20px">
    <article class="epi" data-key="ep1">
      <h3><span class="no ed" data-field="no" contenteditable="plaintext-only">%s</span><span class="ed" data-field="title" contenteditable="plaintext-only">%s</span></h3>
      <div class="stats">
        <span class="tag ed" data-field="runtime" contenteditable="plaintext-only">%s</span>
        <span class="tag" data-field="cuts">%d컷</span>
        <span class="tag ed" data-field="status" contenteditable="plaintext-only">%s</span>
      </div>
      <p class="log ed" data-field="logline" contenteditable="plaintext-only">%s</p>
      <div class="tablewrap"><table>
        <thead><tr><th>구성</th><th>컷</th><th>길이</th></tr></thead>
        <tbody artifact-sync>%s</tbody>
      </table></div>
      <div class="tablewrap"><table>
        <thead><tr><th>컷</th><th>화자</th><th>대사</th></tr></thead>
        <tbody artifact-sync>%s</tbody>
      </table></div>
    </article>
  </div>
  <button class="btn" id="newep">＋ 새 에피소드 만들기</button>
  <p class="hint">편집을 켜야 새 에피소드를 만들 수 있습니다. 만든 뒤 각 칸을 눌러 채우세요.</p>
  <article class="epi tpl" id="eptpl">
    <h3><span class="no ed" contenteditable="plaintext-only">0화</span><span class="ed" contenteditable="plaintext-only">제목을 입력하세요</span></h3>
    <div class="stats">
      <span class="tag ed" contenteditable="plaintext-only">0분 00초</span>
      <span class="tag ed" contenteditable="plaintext-only">0컷</span>
      <span class="tag ed" contenteditable="plaintext-only">기획</span>
    </div>
    <p class="log ed" contenteditable="plaintext-only">한 문단으로 줄거리를 적으세요. 누가 무엇을 원하고, 무엇이 막고, 어떻게 끝나는지.</p>
  </article>
</section>

<footer>
  원본 데이터는 저장소에 있습니다 — <span class="ed" contenteditable="plaintext-only">cba00286/canco-studio · episodes/ep1</span>
</footer>
</div>

<script>
(async () => {
  const body = document.body;
  const btn = document.getElementById("editbtn");
  const state = document.getElementById("state");
  const ro = document.getElementById("ro");
  let editing = false, writable = null;

  const setMode = on => {
    editing = on;
    body.setAttribute("data-local-mode", on ? "edit" : "read");
    btn.setAttribute("aria-pressed", String(on));
    btn.textContent = on ? "편집 중" : "편집";
    if (writable !== false) state.textContent = on ? "고치면 바로 저장됩니다" : "읽는 중";
  };
  setMode(false);

  // 편집 모드가 아닐 때는 입력 자체를 막는다 — 선택·복사는 그대로 된다.
  body.addEventListener("beforeinput", ev => { if (!editing) ev.preventDefault(); }, true);
  body.addEventListener("paste", ev => { if (!editing) ev.preventDefault(); }, true);

  btn.addEventListener("click", () => setMode(!editing));

  // 탭은 뷰어마다 다르다. body의 data-local-* 는 공유되지 않으므로 여기에 둔다.
  const setTab = name => {
    body.setAttribute("data-local-tab", name);
    document.querySelectorAll(".tab").forEach(x => x.setAttribute("aria-selected", String(x.dataset.tab === name)));
  };
  setTab("chars");
  document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => setTab(t.dataset.tab)));

  const tpl = document.getElementById("eptpl");
  document.getElementById("newep").addEventListener("click", () => {
    if (!editing) { setMode(true); }
    const node = tpl.cloneNode(true);
    node.classList.remove("tpl");
    node.removeAttribute("id");
    node.dataset.key = "ep-" + Date.now();
    document.getElementById("eplist").append(node);
    node.querySelector(".ed").focus();
  });

  // 쓰기 권한 확인 — 읽기 전용이면 편집 자체를 감춘다.
  const artifact = await claude.use("artifact");
  if (!artifact) { writable = false; }
  document.addEventListener("claude:sync-off", () => { writable = false; markReadOnly(); }, true);
  function markReadOnly(){
    writable = false; setMode(false);
    btn.hidden = true; ro.hidden = false; state.textContent = "읽기 전용";
  }
  if (writable === false) markReadOnly();
})();
</script>
'''

CHARTFIG = img(CHART, "쿵쿵이와 친구들 캐릭터 키 도감")
out = DIST / "kungkung_hub.html"
out.write_text(BODY % (CSS, ''.join(cards), ''.join(homes),
    CHARTFIG, e(ep['no']), e(ep['title']), e(ep['runtime']), ep['cuts'], e(ep['status']),
    e(ep['logline']), secs, lines), encoding='utf-8')
print('작성:', out, out.stat().st_size // 1024, 'KB')
