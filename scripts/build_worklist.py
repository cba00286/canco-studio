#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한 화를 만드는 데 필요한 모든 것을 한 파일에 담는다.

생성 순서가 바뀌었다.

    대본 → 프리비즈(블렌더) → 편집 → 확정 프레임 → 매핑 → 힉스필드 생성

구도·카메라·타이밍은 블렌더가 잡는다. 생성기는 그 구도 위에 그림을 입히는
일만 한다. 그래서 어느 컷을 다시 뽑아도 앞뒤와 구도가 어긋나지 않는다.

컷마다 다 들어간다.

  · 프리비즈 — 카메라(움직임·렌즈·거리)와 인물 배치, 프레임 구간
  · 매핑     — 걸 캐릭터 마스터 시트와 넣을 프리비즈 프레임
  · 엔진     — 이 컷을 어디로 보낼지 (대사 있으면 하이루, 물·불이면 클링 …)
  · ① 키프레임 프롬프트 — 영어
  · ② 영상 프롬프트 — 엔진 언어로. 넣는 프레임이 한 장이냐 두 장이냐로 갈린다
  · 대사 · 소리 · 시드 · 앞 컷과의 연결

    python3 scripts/build_worklist.py --episode ep1
    python3 scripts/build_worklist.py --episode C01 --root shorts
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bible                                            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--episode", required=True)
    p.add_argument("--root", default="episodes")
    p.add_argument("--out")
    a = p.parse_args()

    base = ROOT / a.root / a.episode
    d = json.loads((base / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))
    chars = json.loads((ROOT / "bible" / "characters.json").read_text(encoding="utf-8"))
    meta_path = base / ("episode.json" if a.root == "episodes" else "short.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    pv_path = base / "previz" / "previz.json"
    if not pv_path.exists():
        raise SystemExit("프리비즈가 없습니다 — 먼저 "
                         "python3 scripts/build_previz.py --episode %s 를 돌리세요" % a.episode)
    pv = {c["id"]: c for c in json.loads(pv_path.read_text(encoding="utf-8"))["컷"]}
    eng_tbl = json.loads((ROOT / "bible" / "engines.json").read_text(encoding="utf-8"))

    shots = d["shots"]
    세로 = a.root == "shorts"
    neg = bible.negative(chars, d)
    _pv = json.loads(pv_path.read_text(encoding="utf-8"))
    pvfps, pvres = _pv["fps"], _pv["해상도"]
    title = meta.get("title", a.episode)
    no = meta.get("no", meta.get("id", a.episode))

    o = []
    A = o.append
    A("# %s %s — 제작 작업지" % (no, title))
    A("")
    if meta.get("logline"):
        A("> %s" % meta["logline"])
        A("")
    A("`%d컷 · 캐릭터 등장 %d컷 · 배경만 %d컷`"
      % (len(shots), sum(1 for s in shots if s["cast"]),
         sum(1 for s in shots if not s["cast"])))
    A("")
    A("## 만드는 순서")
    A("")
    A("1. **프리비즈** — `previz/블렌더_%s.py` 를 블렌더에서 실행한다" % a.episode)
    A("2. **편집** — 원하는 샷이 나올 때까지 카메라와 배치를 고친다. 여기가 진짜 연출이다")
    A("3. **프레임** — 컷마다 첫 프레임(과 끝 프레임)을 PNG 로 뽑는다 — `%s_시작.png`"
      % shots[0]["id"])
    A("4. **매핑** — 힉스필드에서 그 컷에 나오는 **캐릭터 마스터 시트**와 "
      "**프리비즈 프레임**을 건다")
    A("5. **생성** — 컷의 엔진을 고르고 ② 영상 프롬프트를 붙인다")
    A("6. 파일명을 컷 ID 로 맞춘다 — `%s.mp4`. 다 모이면 로컬에서 이어붙이기 · 자막 · 소리"
      % shots[0]["id"])
    A("")
    A("> **구도는 프리비즈가 정한다.** 프롬프트로 구도를 다시 말하지 않는다. "
      "두 번 말하면 두 번 움직인다.")
    A("")
    A("> **대사와 효과음은 ② 영상 프롬프트가 만든다.** 나레이션 · BGM · 자막은 "
      "로컬에서 얹는다. 이 구분을 헷갈리면 다시 만들어야 한다.")
    A("")
    A("## 생성 설정 — 컷마다 같다")
    A("")
    A("| | |")
    A("|---|---|")
    A("| 프리비즈 | 블렌더 · %dfps · %d×%d |" % (pvfps, pvres[0], pvres[1]))
    A("| 비율 | **%s** |" % ("9:16 세로" if 세로 else "16:9 가로"))
    A("| 기본 엔진 | %s |" % eng_tbl["엔진"][eng_tbl["기본"]]["이름"])
    A("| 네거티브 | 아래 한 줄을 매번 같이 넣는다 |")
    A("")
    A("```")
    A(neg)
    A("```")
    A("")
    A("> **비율은 프롬프트가 아니라 생성 화면의 설정이다.** 프롬프트에 «16:9» 라고 "
      "적어도 설정이 1:1 이면 1:1 로 나온다.")
    A("")
    A("> **캐릭터 마스터 시트를 빼먹지 않는다.** 프롬프트에 이름만 적고 시트를 걸지 "
      "않으면, 이름은 그냥 글자일 뿐이라 얼굴이 매번 달라진다.")
    A("")
    A("## 엔진을 고르는 법")
    A("")
    for line in eng_tbl["고르는_법"]:
        A("- %s" % line)
    A("")
    A("컷마다 아래에 **엔진**이 이미 적혀 있다. 바꾸고 싶으면 그 컷만 바꾸면 된다 — "
      "구도는 프리비즈가 들고 있으므로 앞뒤 컷은 다시 뽑지 않아도 된다.")
    A("")
    A("---")
    A("")

    aud = json.loads((ROOT / "bible" / "audio.json").read_text(encoding="utf-8"))

    def 소리(sh):
        names = [aud.get("sfx", {}).get(x, {}).get("소리", x) for x in (sh.get("sfx") or [])]
        if sh.get("sig"):
            names.append(aud.get("signature", {}).get(sh["sig"], {}).get("소리", sh["sig"]))
        return " · ".join(n for n in names if n)

    sec = None
    for i, s in enumerate(shots, 1):
        if s["section"] != sec:
            sec = s["section"]
            A("")
            A("---")
            A("")
            A("## %s" % d.get("sections", {}).get(sec, sec))
            a_ = (d.get("audio_sections") or {}).get(sec) or {}
            if a_:
                A("")
                A("`환경음 %s · BGM %s`" % (a_.get("amb", "—"), a_.get("bgm", "—")))
            A("")

        A("### %d/%d  `%s`" % (i, len(shots), s["id"]))
        A("")
        c = pv.get(s["id"], {})
        cam = c.get("카메라", {})
        bits = ["%d초" % s["duration"], s["shot_ko"]]
        if c:
            bits.append("프레임 %d–%d" % (c["시작_프레임"], c["끝_프레임"]))
        bits.append("시드 %s" % s["seed"])
        if s.get("link"):
            bits.append("앞 컷과 %s" % s["link"])
        A("`%s`" % " · ".join(bits))
        A("")
        pr = s.get("previz_ref") or {}
        if cam:
            who = " · ".join(x["이름"] + ("*" if x["말한다"] else "") for x in c["인물"])
            A("**프리비즈** — 카메라 %s · %dmm · %.1fm%s"
              % (cam["움직임"], cam["렌즈_mm"], cam["거리_m"],
                 (" · " + who) if who else " · 배경만"))
            if cam.get("밀림", 1) > 1.8:
                A("")
                A("> 인물이 다 들어가느라 카메라가 %.1f배 뒤로 밀렸다. 프리비즈에서 "
                  "배치를 앞뒤로 접거나 샷을 풀샷으로 바꾼다." % cam["밀림"])
            if len(c.get("움직임_후보") or []) > 1:
                A("")
                A("> 대본이 카메라 움직임을 둘 말했다 (%s). 블렌더에서 하나로 정한다."
                  % " · ".join(c["움직임_후보"]))
            A("")
        A("**매핑** — %s / 구도 `%s_시작.png`%s"
          % ("캐릭터 시트 " + " · ".join(s["cast"]) if s["cast"] else "캐릭터 시트 없음 (배경만)",
             s["id"], " + 끝 `%s_끝.png`" % s["id"]))
        A("")
        if pr:
            A("**엔진** — %s · %s 프롬프트" % (pr["엔진_이름"], pr["언어"]))
            A("")
        A("%s" % s["ko"])
        A("")
        if s.get("link_ko"):
            A("*연결 — %s*" % s["link_ko"])
            A("")
        if s.get("dialogue"):
            who = s.get("speaker") or ""
            if who == "나레이션":
                A("**나레이션** (자막 없음 · 편집에서 TTS) — %s" % s["dialogue"])
            else:
                A("**%s** 「%s」" % (who, s["dialogue"]))
            A("")
        if 소리(s):
            A("*소리 — %s*" % 소리(s))
            A("")
        A("**① 키프레임 프롬프트** — 영어. 프리비즈 프레임 위에 그림을 입힐 때")
        A("")
        A("```")
        A(s["image_ref"])
        A("```")
        if s.get("image_suffix"):
            A("")
            A("> 소품이 바뀌는 컷이다. 위 프롬프트 끝에 예외 지시가 붙어 있다.")
        A("")
        if pr:
            A("**② 영상 프롬프트 — 첫·끝 두 장 넣을 때** `권장` · %s" % pr["언어"])
            A("")
            A("```")
            A(pr["start_end"])
            A("```")
            A("")
            A("**② 영상 프롬프트 — 첫 장만 넣을 때** · 카메라를 문장으로 말해 준다")
            A("")
            A("```")
            A(pr["i2v"])
            A("```")
            A("")
        if s.get("link") == "연속":
            A("> **앞 컷 영상의 마지막 프레임을 이 컷의 시작 프레임으로 넣는다.** "
              "프리비즈에서도 두 컷의 카메라가 이어져 있어야 한다.")
            A("")

    A("---")
    A("")
    A("## 막힐 때")
    A("")
    A("- **얼굴이 매번 달라진다** — 캐릭터 마스터 시트를 안 걸었다. 프롬프트의 이름만으로는 안 된다")
    A("- **대사를 안 한다** — 대사 컷을 하이루 아닌 엔진으로 보냈거나, "
      "영상 프롬프트를 영어로 바꿨다. 대사 컷은 통째로 한국어여야 한다")
    A("- **카메라가 두 번 움직인다** — 첫·끝 두 장을 넣으면서 `[카메라]` 줄이 든 "
      "프롬프트를 썼다. 두 장을 넣을 때는 `권장` 쪽을 쓴다")
    A("- **구도가 프리비즈와 다르다** — `[구도]` 줄을 지웠거나 프레임을 안 걸었다")
    A("- **앞뒤 컷이 안 붙는다** — 프리비즈에서 두 컷의 카메라가 이어지는지 먼저 본다. "
      "프롬프트 문제가 아니다")
    A("- **컷 톤이 다르다** — 프롬프트를 손으로 고쳤다. 마음에 안 들면 **시드를 바꿔** 다시 뽑는다")
    A("- **소품이 중간에 생긴다** — 영상 프롬프트의 `[외형]` 줄을 지웠다")
    A("- **클립에 엉뚱한 음악이 깔린다** — `[소리]` 줄의 «배경음악 없이» 를 지웠다")
    A("")

    dia = [x for x in shots if x.get("dialogue") and x.get("speaker") != "나레이션"]
    narr = [x for x in shots if x.get("dialogue") and x.get("speaker") == "나레이션"]
    A("## 대사 전체 — %d줄" % len(dia))
    A("")
    A("생성기가 만든다. 컷마다 ② 영상 프롬프트 안에 이미 들어 있으니 따로 넣을 것은 없고, "
      "**나온 클립에서 이 대사가 들리는지 확인하는 용도**다.")
    A("")
    A("| 컷 | 화자 | 대사 |")
    A("|---|---|---|")
    for x in dia:
        A("| `%s` | %s | %s |" % (x["id"], x["speaker"], x["dialogue"]))
    A("")
    if narr:
        A("## 나레이션 %d줄 — 로컬에서 TTS" % len(narr))
        A("")
        A("화면 밖 목소리라 **자막을 넣지 않고** 편집에서 얹는다. 컷마다 생성하면 "
          "나레이터가 컷 수만큼 늘어난다.")
        A("")
        A("| 컷 | 나레이션 |")
        A("|---|---|")
        for x in narr:
            A("| `%s` | %s |" % (x["id"], x["dialogue"]))
        A("")

    out = Path(a.out) if a.out else base / "prompts" / "제작_작업지.md"
    out.write_text("\n".join(o) + "\n", encoding="utf-8")
    print("%s — %d컷 (캐릭터 %d · 배경 %d)"
          % (no, len(shots), sum(1 for s in shots if s["cast"]),
             sum(1 for s in shots if not s["cast"])))
    print("  %s" % out.relative_to(ROOT))


if __name__ == "__main__":
    sys.exit(main())
