#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""쇼츠 22편을 한 페이지에 모은다. OpenArt 에 복붙하는 용도다.

    python3 site/make_shorts.py
"""
import html, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = ROOT / "site" / "dist"
DIST.mkdir(parents=True, exist_ok=True)
e = lambda s: html.escape(str(s), quote=True)

FMT = json.loads((ROOT / "shorts_format.json").read_text(encoding="utf-8"))
NEG = json.loads((ROOT / "bible" / "characters.json").read_text(encoding="utf-8"))["negative_prompt"]

KINDS = [("캐릭터 소개", "23초 · 얼굴 → 그 아이를 정의하는 행동 → 무리 안에서의 자리 → 자기 집 → 이름과 한마디. "
                       "본편이 올라가기 전에 얼굴부터 각인시킨다."),
         ("예고편", "23초 · 위기 → 상황 → 막힌 순간 → 실마리 → 제목. 결말은 보여주지 않는다."),
         ("파워", "23초 · 능력만 보여주면 «그래서 뭐»가 된다. 그 힘이 무엇을 했는지까지 보여준다."),
         ("오늘 한마디", "30초 · 반복 포맷. 상황 → 문제 → 전환점 → 해결이 있어야 교훈이 들린다. "
                       "컷1·6·7 은 고정이라 한 번 뽑아 두면 계속 재사용한다.")]

shorts = []
for d in sorted(x for x in (ROOT / "shorts").iterdir()
                if x.is_dir() and (x / "prompts" / "shots_v2.json").exists()):
    D = json.loads((d / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))
    shorts.append({"id": d.name, "kind": D.get("kind", ""), "title": D.get("title", ""),
                   "hook": D.get("hook", ""), "sec": D["total_seconds"], "shots": D["shots"]})

idx = 0
groups = []
for kind, blurb in KINDS:
    items = [s for s in shorts if s["kind"] == kind]
    if not items:
        continue
    cards = []
    for s in items:
        cuts = []
        for sh in s["shots"]:
            idx += 1
            line = (f'<p class="line"><span class="who">{e(sh["speaker"])}</span>'
                    f'<span class="say">{e(sh["dialogue"])}</span></p>') if sh["dialogue"] else ""
            cuts.append(f'''
      <div class="cut">
        <div class="crail"><span class="cid">{e(sh["id"])}</span>
          <span class="cmeta">{sh["duration"]}초 · {e(sh["shot_ko"])}</span>
          <span class="lk {e(sh["link"])}">{e(sh["link"])}</span></div>
        <div class="cbody">
          <p class="lknote">{e(sh["link_ko"])}</p>
          {line}
          <p class="ko">{e(sh["ko"])}</p>
          <div class="row"><button class="copy" data-c="p{idx}">이미지 프롬프트 복사</button>
            <button class="copy" data-c="m{idx}">영상 프롬프트 복사</button></div>
          <pre id="p{idx}" hidden>{e(sh["image_ref"])}</pre>
          <pre id="m{idx}" hidden>{e(sh.get("motion_ref") or sh["motion"])}</pre>
          <p class="komo">{e(sh["ko_motion"])}</p>
        </div>
      </div>''')
        cards.append(f'''
  <article class="sh" id="{e(s["id"])}">
    <header class="shh">
      <span class="sid">{e(s["id"])}</span>
      <h3>{e(s["title"])}</h3>
      <span class="stat">{s["sec"]}초 · {len(s["shots"])}컷 · 9:16</span>
    </header>
    <p class="hook">훅 — {e(s["hook"])}</p>
    {"".join(cuts)}
  </article>''')
    groups.append(f'<section class="grp"><h2>{e(kind)} <span class="n">{len(items)}편</span></h2>'
                  f'<p class="blurb">{e(blurb)}</p>{"".join(cards)}</section>')

CSS = '''
:root{
  --ground:#F7F6FA; --surface:#FFFFFF; --surface-2:#EFEEF5; --sunk:#E6E4EF;
  --ink:#161425; --muted:#5A5670; --faint:#8E8AA6;
  --accent:#6D4AC9; --accent-soft:#E7E0FA; --peach:#C4693B;
  --line:#E0DDEA; --line-strong:#C9C4DC;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#100E18; --surface:#191622; --surface-2:#221E2E; --sunk:#141220;
  --ink:#E9E6F2; --muted:#A6A1BC; --faint:#736E8C;
  --accent:#A98CF0; --accent-soft:#241C3A; --peach:#E5946A;
  --line:#282334; --line-strong:#38324A;
}}
:root[data-theme="dark"]{
  --ground:#100E18; --surface:#191622; --surface-2:#221E2E; --sunk:#141220;
  --ink:#E9E6F2; --muted:#A6A1BC; --faint:#736E8C;
  --accent:#A98CF0; --accent-soft:#241C3A; --peach:#E5946A;
  --line:#282334; --line-strong:#38324A;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans KR",system-ui,sans-serif;font-size:16px;line-height:1.72;-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:44px 20px 90px;display:flex;flex-direction:column;gap:30px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.15em;color:var(--accent);font-weight:600;margin:0 0 9px}
h1{font-family:"Gowun Batang",serif;font-weight:700;font-size:clamp(27px,5vw,40px);line-height:1.24;margin:0 0 12px;text-wrap:balance}
.lede{margin:0;color:var(--muted);font-size:15.5px;max-width:62ch}
.note{background:var(--accent-soft);border:1px solid var(--line-strong);border-radius:12px;
  padding:15px 18px;font-size:14px;line-height:1.75;color:var(--ink)}
.note strong{color:var(--accent)}
.warn{background:var(--surface);border:2px solid var(--peach);border-radius:12px;padding:17px 20px}
.warn p{margin:0 0 10px;font-size:14.5px;line-height:1.75}
.warn p:last-child{margin-bottom:0}
.wt{font-family:"Gowun Batang",serif;font-weight:700;font-size:18px;color:var(--peach)}
.warn code{font-family:"IBM Plex Mono",monospace;font-size:13px;background:var(--sunk);
  padding:1px 6px;border-radius:5px}
.steps{margin:0 0 10px;padding-left:22px;display:flex;flex-direction:column;gap:6px}
.steps li{font-size:14.5px;line-height:1.7}
.wn{color:var(--muted);font-size:13.5px !important;border-top:1px solid var(--line);padding-top:10px}
h2{font-family:"Gowun Batang",serif;font-weight:700;font-size:23px;margin:0 0 4px;display:flex;align-items:baseline;gap:10px}
h2 .n{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--accent);font-weight:600}
.blurb{margin:0 0 18px;color:var(--muted);font-size:14.5px}
.grp{display:flex;flex-direction:column;gap:0}
.sh{background:var(--surface);border:1px solid var(--line);border-radius:15px;
  padding:20px 22px;display:flex;flex-direction:column;gap:12px;margin-bottom:18px}
.shh{display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}
.sid{font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:700;color:var(--surface);
  background:var(--accent);padding:2px 9px;border-radius:6px}
.shh h3{font-family:"Gowun Batang",serif;font-size:20px;margin:0;flex:1;min-width:200px}
.stat{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--faint);white-space:nowrap}
.hook{margin:0;font-size:14px;color:var(--peach);font-weight:600}
.cut{border-top:1px solid var(--line);padding-top:13px;display:grid;grid-template-columns:104px 1fr;gap:0 16px}
.crail{display:flex;flex-direction:column;gap:5px;align-items:flex-start}
.cid{font-family:"IBM Plex Mono",monospace;font-size:12.5px;font-weight:600}
.cmeta{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--faint)}
.lk{font-family:"IBM Plex Mono",monospace;font-size:10.5px;font-weight:700;padding:1px 7px;
  border-radius:999px;border:1px solid currentColor;color:var(--faint)}
.lk.연속{color:var(--accent)} .lk.전환{color:var(--peach)}
.cbody{display:flex;flex-direction:column;gap:7px;min-width:0}
.lknote{margin:0;font-size:12.5px;color:var(--faint);line-height:1.6}
.ko{margin:0;font-size:14.5px;line-height:1.72}
.komo{margin:0;font-size:13.5px;color:var(--muted);line-height:1.68}
.line{margin:0;display:flex;gap:9px;align-items:baseline;background:var(--sunk);
  border-radius:8px;padding:7px 11px}
.who{font-size:12px;font-weight:700;color:var(--accent);white-space:nowrap}
.say{font-size:14.5px}
.row{display:flex;gap:7px;flex-wrap:wrap;margin-top:2px}
.copy{font:inherit;font-size:12.5px;font-weight:600;padding:5px 12px;border-radius:999px;
  border:1px solid var(--line-strong);background:var(--surface-2);color:var(--muted);cursor:pointer}
.copy:hover{border-color:var(--accent);color:var(--accent)}
.copy.ok{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.copy:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
pre{margin:0;white-space:pre-wrap;word-break:break-word;font-family:"IBM Plex Mono",monospace;font-size:12.5px}
footer{border-top:1px solid var(--line);padding-top:16px;color:var(--faint);font-size:13px}
@media (max-width:600px){
  .wrap{padding:30px 13px 70px}
  .sh{padding:16px 15px}
  .cut{grid-template-columns:1fr;gap:6px}
  .crail{flex-direction:row;align-items:center;gap:8px}
}
'''

BODY = f'''<title>쿵쿵이 쇼츠 22편</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&display=swap">
<style>{CSS}</style>

<div class="wrap">
<header>
  <p class="eyebrow">쿵쿵이와 친구들 · 세로 9:16</p>
  <h1>쇼츠 22편</h1>
  <p class="lede">짧은 것은 23초 5컷, 「오늘 한마디」는 30초 7컷.
  버튼을 누르면 프롬프트가 복사됩니다. OpenArt 에 그대로 붙여 넣으세요.</p>
</header>

<div class="warn">
  <p class="wt">생성하기 전에 — 비율을 먼저 바꾸세요</p>
  <p><strong>화면비는 프롬프트로 정해지지 않습니다.</strong> 프롬프트에 <code>vertical 9:16 composition</code>
  이라고 적혀 있어도 그건 «인물을 세로로 배치하라»는 구도 힌트일 뿐입니다.
  실제 이미지 크기는 <strong>OpenArt 생성 화면의 비율(Aspect ratio) 설정</strong>이 결정합니다.</p>
  <ol class="steps">
    <li>이미지 생성 화면에서 비율을 <strong>9:16</strong>(또는 Portrait / 세로)로 바꾼다</li>
    <li>그 상태에서 아래 <strong>이미지 프롬프트</strong>를 붙여 넣고 생성한다</li>
    <li>나온 세로 이미지를 <strong>영상 생성의 시작 이미지</strong>로 넣는다 —
        image2video 는 넣은 이미지의 비율을 그대로 따라가므로, 이미지만 세로면 영상도 세로다</li>
  </ol>
  <p class="wn">이미 16:9 로 뽑은 것은 다시 뽑아야 합니다. 잘라서는 못 씁니다 —
  세로로 자르면 얼굴과 시그니처 포즈가 화면 밖으로 나갑니다.</p>
</div>

<div class="note">
  <strong>본편 컷을 잘라서 쓰지 마세요.</strong> 본편 600컷은 전부 16:9 로 구도를 잡았습니다.
  여기 22편은 처음부터 세로 구도로 짰습니다.<br><br>
  <strong>캐릭터는 트리거 워드로 고정됩니다.</strong> 프롬프트 안의 한글 이름이 OpenArt Characters 에
  등록한 트리거 워드입니다. 외모를 따로 적지 마세요 — 적으면 등록된 얼굴을 덮어씁니다.<br><br>
  <strong>「연속」 표시가 붙은 컷</strong>은 앞 컷 영상의 마지막 프레임을 시작 프레임으로 넣으면
  이음매가 사라집니다.
</div>

{"".join(groups)}

<section class="grp">
  <h2>네거티브 프롬프트</h2>
  <p class="blurb">전 컷 공통입니다. 한 번 복사해서 계속 쓰세요.</p>
  <article class="sh"><div class="cbody">
    <div class="row"><button class="copy" data-c="neg">네거티브 프롬프트 복사</button></div>
    <pre id="neg" hidden>{e(NEG)}</pre>
  </div></article>
</section>

<footer>원본 데이터는 저장소에 있습니다 — cba00286/canco-studio · shorts/</footer>
</div>

<script>
document.addEventListener("click", async ev => {{
  const b = ev.target.closest(".copy");
  if (!b) return;
  const src = document.getElementById(b.dataset.c);
  if (!src) return;
  try {{ await navigator.clipboard.writeText(src.textContent); }}
  catch {{
    const t = document.createElement("textarea");
    t.value = src.textContent; document.body.append(t); t.select();
    document.execCommand("copy"); t.remove();
  }}
  const was = b.textContent;
  b.textContent = "복사됨"; b.classList.add("ok");
  setTimeout(() => {{ b.textContent = was; b.classList.remove("ok"); }}, 1400);
}});
</script>
'''

out = DIST / "kungkung_shorts.html"
out.write_text(BODY, encoding="utf-8")
print("작성:", out, out.stat().st_size // 1024, "KB ·", len(shorts), "편")
