#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""컷 프롬프트를 레퍼런스 모드로 다시 생성한다.

`image`(외모 서술 포함 원본)에서 `cast`와 `image_ref`를 만든다.

캐릭터를 부르는 이름은 characters.json의 다음 순서로 정해진다.

  1. trigger — OpenArt Characters에 등록한 트리거 워드. 있으면 이걸 쓴다.
     플랫폼이 얼굴을 고정해 주므로 가장 강하다.
  2. ref_tag — 트리거 워드가 없을 때의 폴백. 마스터 시트를 레퍼런스로
     직접 첨부하는 방식에서 쓴다.

어느 쪽이든 외모 서술은 프롬프트에 넣지 않는다. 트리거 워드나 레퍼런스와
외모 서술이 함께 있으면 서술이 이겨서 캐릭터가 새로 그려진다.
(docs/07_캐릭터_일관성_가이드.md)

    python3 scripts/build_ref_prompts.py --episode ep1
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIVE = ["루카", "후안", "미미", "티니", "루비"]
SIX = ["쿵쿵"] + FIVE


def name_of(chars: dict, key: str) -> str:
    entry = chars["characters"][key]
    return entry.get("trigger") or entry["ref_tag"]


def cast_of(shot: dict) -> list[str]:
    text = shot["image"] + " " + shot["motion"]
    names = [n for n in re.findall(r"[{\[]([^}\]]+)[}\]]", text) if n in SIX]
    if "쿵쿵_파워" in text:                       # 능력 연출 조각은 쿵쿵이 주어다
        names.append("쿵쿵")
    low = text.lower()
    if "six friends" in low or "five friends behind him" in low:
        names += SIX
    elif "five friends" in low:
        names += FIVE
    elif "the friends" in low:                    # 인원수가 안 적힌 그룹 컷
        names += SIX if shot["section"] in ("SC4", "EN") else FIVE
    return [n for n in SIX if n in names]         # 항상 같은 순서로


def ref_prompt(chars: dict, shot: dict, cast: list[str]) -> str:
    text = shot["image"]
    for key in SIX:
        called = name_of(chars, key)
        text = text.replace("{%s}" % key, called).replace("[%s]" % key, called)
    for frag, value in chars.get("fragments", {}).items():
        if frag != "_comment":
            text = text.replace("{%s}" % frag, value).replace("[%s]" % frag, value)
    # 능력 조각은 "his three horns"로 시작해 주어가 없다. 쿵쿵을 명시한다.
    text = text.replace("along his three horns", "along %s's three horns" % name_of(chars, "쿵쿵"))
    # 그룹 지칭은 전원의 이름으로 펼친다. 이름이 있어야 등록된 캐릭터가 적용된다.
    # "the five/six friends"를 먼저 바꾼 뒤 남은 "the friends"를 cast 기준으로 처리한다.
    for group, members in (("the five friends", FIVE), ("the six friends", SIX)):
        text = text.replace(group, ", ".join(name_of(chars, m) for m in members))
    if "the friends" in text and cast:
        text = text.replace("the friends", ", ".join(name_of(chars, m) for m in cast))
    out = chars["style_tag"] + ", " + text
    if not cast:
        return out
    # 등록된 캐릭터를 부르는 경우와 시트를 첨부하는 경우는 고정 지시문이 다르다.
    key = "consistency_tag_trigger" if chars["characters"][cast[0]].get("trigger") else "consistency_tag_sheet"
    return out + ". " + chars[key]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode", default="ep1")
    ap.add_argument("--shots", default="shots_v2.json")
    args = ap.parse_args()

    prompts = ROOT / "episodes" / args.episode / "prompts"
    chars = json.loads((prompts / "characters.json").read_text(encoding="utf-8"))
    path = prompts / args.shots
    data = json.loads(path.read_text(encoding="utf-8"))

    triggers = {n: chars["characters"][n].get("trigger") for n in SIX}
    missing = [n for n, t in triggers.items() if not t]
    if missing:
        print("! OpenArt 트리거 워드가 비어 있는 캐릭터: %s" % ", ".join(missing))
        print("  characters.json의 trigger에 채우고 다시 실행하면 프롬프트가 트리거 워드로 바뀝니다.")
        print("  지금은 ref_tag(마스터 시트 첨부 전제)로 생성합니다.\n")

    for shot in data["shots"]:
        cast = cast_of(shot)
        shot["cast"] = cast
        shot["image_ref"] = ref_prompt(chars, shot, cast)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_cast = sum(1 for s in data["shots"] if s["cast"])
    print("%s 갱신 — 캐릭터 등장 %d컷 / 배경 %d컷"
          % (args.shots, n_cast, len(data["shots"]) - n_cast))


if __name__ == "__main__":
    main()
