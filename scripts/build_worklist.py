#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""한 화를 만드는 데 필요한 모든 것을 한 파일에 담는다.

컷 시트(site/dist/*.html)는 브라우저에서 버튼으로 복사하는 용도이고, 이건
**한 파일로 죽 늘어놓은 것**이다. 화면을 오가지 않고 위에서부터 훑으며
작업할 때, 그리고 내려받아 보관할 때 쓴다.

컷마다 다 들어간다.

  · 지정할 캐릭터 — OpenArt Characters 에서 고른다. **이걸 빼면 얼굴이 매번 바뀐다**
  · ① 이미지 프롬프트 — **영어**. 캐릭터는 트리거 워드로만 부르고 외형은 적지 않는다
  · ② 영상 프롬프트 — **한국어**. 통째로. 영어로 바꾸면 그 컷의 대사를 건너뛴다
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

    shots = d["shots"]
    세로 = a.root == "shorts"
    neg = bible.negative(chars, d)
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
    A("1. **① 이미지 프롬프트**로 키프레임을 뽑는다 (Nano Banana 2)")
    A("2. 그 이미지를 **Image to Video** 에 넣고 **② 영상 프롬프트**를 붙인다 (MiniMax H3)")
    A("3. 파일명을 컷 ID 로 맞춘다 — `%s.png` / `%s.mp4`" % (shots[0]["id"], shots[0]["id"]))
    A("4. 다 모이면 로컬에서 이어붙이기 · 자막 · 소리 믹싱")
    A("")
    A("> **대사와 효과음은 ② 영상 프롬프트가 만든다.** 나레이션 · BGM · 자막은 "
      "로컬에서 얹는다. 이 구분을 헷갈리면 다시 만들어야 한다.")
    A("")
    A("## 생성 설정 — 컷마다 같다")
    A("")
    A("| | |")
    A("|---|---|")
    A("| 모델 | **Nano Banana 2** (image) |")
    A("| 비율 | **%s** |" % ("9:16 세로" if 세로 else "16:9 가로"))
    A("| 네거티브 | 아래 한 줄을 매번 같이 넣는다 |")
    A("")
    A("```")
    A(neg)
    A("```")
    A("")
    A("> **비율은 프롬프트가 아니라 생성 화면의 설정이다.** 프롬프트에 «16:9» 라고 "
      "적어도 설정이 1:1 이면 1:1 로 나온다.")
    A("")
    A("> **캐릭터 지정을 빼먹지 않는다.** 프롬프트에 이름만 적고 OpenArt 에서 캐릭터를 "
      "고르지 않으면, 이름은 그냥 글자일 뿐이라 얼굴이 매번 달라진다.")
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
        bits = ["%d초" % s["duration"], s["shot_ko"], "시드 %s" % s["seed"]]
        if s.get("link"):
            bits.append("앞 컷과 %s" % s["link"])
        A("`%s`" % " · ".join(bits))
        A("")
        if s["cast"]:
            A("**캐릭터 지정 — %s**" % " · ".join(s["cast"]))
        else:
            A("캐릭터 지정 없음 (배경만)")
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
        A("**① 이미지 프롬프트** — 영어. Nano Banana 2")
        A("")
        A("```")
        A(s["image_ref"])
        A("```")
        if s.get("image_suffix"):
            A("")
            A("> 소품이 바뀌는 컷이다. 위 프롬프트 끝에 예외 지시가 붙어 있다.")
        A("")
        A("**② 영상 프롬프트** — 한국어. 통째로 붙여 넣는다")
        A("")
        A("```")
        A(s["motion_ref"])
        A("```")
        if s.get("link") == "연속":
            A("")
            A("> **앞 컷 영상의 마지막 프레임을 이 컷의 시작 프레임으로 넣는다.**")
        A("")

    A("---")
    A("")
    A("## 막힐 때")
    A("")
    A("- **얼굴이 매번 달라진다** — 캐릭터 지정을 빼먹었다. 프롬프트의 이름만으로는 안 된다")
    A("- **대사를 안 한다** — 영상 프롬프트를 영어로 바꿨다. 통째로 한국어여야 한다")
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
