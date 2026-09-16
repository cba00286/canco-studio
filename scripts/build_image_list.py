#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""이미지 생성용 작업지를 만든다. 컷 순서대로 붙여 넣기만 하면 되게.

컷 시트(site/dist/*.html)는 브라우저에서 버튼으로 복사하는 용도이고, 이건
**한 파일로 죽 늘어놓은 것**이다. 화면을 오가지 않고 위에서부터 훑으며
작업할 때 쓴다.

컷마다 이 세 가지가 필요하다.

  ① 지정할 캐릭터 — OpenArt Characters 에서 고른다. **이걸 빼면 얼굴이 매번 바뀐다**
  ② 프롬프트 — 영어. 캐릭터는 트리거 워드로만 부르고 외형은 적지 않는다
  ③ 시드 — 같은 컷을 다시 뽑을 때 쓴다

    python3 scripts/build_image_list.py --episode ep2
    python3 scripts/build_image_list.py --episode C01 --root shorts --style style_tag_shorts
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
    A("# %s %s — 이미지 생성 작업지" % (no, title))
    A("")
    if meta.get("logline"):
        A("> %s" % meta["logline"])
        A("")
    A("`%d컷 · 캐릭터 등장 %d컷 · 배경만 %d컷`"
      % (len(shots), sum(1 for s in shots if s["cast"]),
         sum(1 for s in shots if not s["cast"])))
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

    sec = None
    for i, s in enumerate(shots, 1):
        if s["section"] != sec:
            sec = s["section"]
            A("")
            A("## %s" % d.get("sections", {}).get(sec, sec))
            A("")
        cast = ("**캐릭터 지정 — %s**" % " · ".join(s["cast"])) if s["cast"] \
            else "배경만 — 캐릭터 지정 없음"
        A("### %d/%d  `%s`" % (i, len(shots), s["id"]))
        A("")
        A("`%d초 · %s · 시드 %s` · %s" % (s["duration"], s["shot_ko"], s["seed"], cast))
        A("")
        A("%s" % s["ko"])
        A("")
        A("```")
        A(s["image_ref"])
        A("```")
        if s.get("image_suffix"):
            A("")
            A("> 소품이 바뀌는 컷이다. 위 프롬프트 끝에 예외 지시가 이미 붙어 있다.")
        A("")

    A("---")
    A("")
    A("## 다 뽑고 나면")
    A("")
    A("1. 파일명을 컷 ID 로 맞춘다 — `%s-01.png` 처럼. 뒤 작업이 이걸로 찾는다" % shots[0]["section"])
    A("2. 마음에 안 드는 컷은 **시드를 바꿔** 다시 뽑는다. 프롬프트를 고치면 다른 화와 톤이 어긋난다")
    A("3. 그다음 Image to Video 로 넘어간다 — 영상 프롬프트는 **한국어**이고 컷 시트에 있다")
    A("")

    out = Path(a.out) if a.out else base / "prompts" / "이미지_작업지.md"
    out.write_text("\n".join(o) + "\n", encoding="utf-8")
    print("%s — %d컷 (캐릭터 %d · 배경 %d)"
          % (no, len(shots), sum(1 for s in shots if s["cast"]),
             sum(1 for s in shots if not s["cast"])))
    print("  %s" % out.relative_to(ROOT))


if __name__ == "__main__":
    sys.exit(main())
