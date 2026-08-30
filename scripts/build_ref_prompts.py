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
import bible

ROOT = Path(__file__).resolve().parent.parent
FIVE = ["루카", "후안", "미미", "티니", "루비"]
SIX = ["쿵쿵"] + FIVE
# 노을은 11화에 합류한다. 1~10화에는 없다 — 10화 엔딩의 실루엣은 이름을 쓰지 않는다.
SEVEN = SIX + ["노을"]
ALL = SEVEN


def name_of(chars: dict, key: str, mode: str = "auto") -> str:
    """캐릭터를 프롬프트에서 부르는 이름.

    trigger 는 OpenArt Characters 에 등록한 트리거 워드다. 다른 도구에서는
    아무 의미가 없으므로, OpenArt 밖에서 만들 때는 mode="sheet" 로 ref_tag 를
    쓰고 마스터 시트를 레퍼런스 이미지로 첨부한다.
    """
    entry = chars["characters"][key]
    if mode == "sheet":
        return entry["ref_tag"]
    return entry.get("trigger") or entry["ref_tag"]


def cast_of(shot: dict, episode_cast: list[str] | None = None) -> list[str]:
    text = shot["image"] + " " + shot["motion"]
    names = [n for n in re.findall(r"[{\[]([^}\]]+)[}\]]", text) if n in ALL]
    if "쿵쿵_" in text:                           # 능력 연출 조각은 모두 쿵쿵이 주어다
        names.append("쿵쿵")
    low = text.lower()
    if "seven friends" in low:
        names += SEVEN
    elif "six friends" in low or "five friends behind him" in low:
        names += SIX
    elif "five friends" in low:
        names += FIVE
    elif "the friends" in low:                    # 인원수가 안 적힌 그룹 컷
        # 화마다 나오는 인원이 다르다. shots_v2.json의 episode_cast를 쓰고,
        # 없으면 1화 기준(후반부는 여섯 전원)으로 되돌아간다.
        names += episode_cast or (SIX if shot["section"] in ("SC4", "EN") else FIVE)
    return [n for n in ALL if n in names]         # 항상 같은 순서로


def ref_prompt(chars: dict, shot: dict, cast: list[str],
               mode: str = "auto", style_key: str = "style_tag") -> str:
    text = shot["image"]
    # 조각을 먼저 펼친다. 조각 안에 {쿵쿵} 같은 이름 자리가 들어 있으므로
    # 이름 치환은 그다음이어야 한다.
    used_power = False
    for frag, value in chars.get("fragments", {}).items():
        if frag != "_comment":
            if ("{%s}" % frag) in text or ("[%s]" % frag) in text:
                used_power = used_power or frag.startswith("쿵쿵_")
            text = text.replace("{%s}" % frag, value).replace("[%s]" % frag, value)
    if used_power and chars.get("horn_lock"):
        text = text.rstrip(" .") + ". " + chars["horn_lock"].rstrip(" .")
    for key in ALL:
        called = name_of(chars, key, mode)
        text = text.replace("{%s}" % key, called).replace("[%s]" % key, called)
    # 그룹 지칭은 전원의 이름으로 펼친다. 이름이 있어야 등록된 캐릭터가 적용된다.
    # "the five/six friends"를 먼저 바꾼 뒤 남은 "the friends"를 cast 기준으로 처리한다.
    for group, members in (("the five friends", FIVE), ("the six friends", SIX),
                           ("the seven friends", SEVEN)):
        text = text.replace(group, ", ".join(name_of(chars, m, mode) for m in members))
    if "the friends" in text and cast:
        text = text.replace("the friends", ", ".join(name_of(chars, m, mode) for m in cast))
    out = chars.get(style_key, chars["style_tag"]) + ", " + text
    if not cast:
        return out
    # 등록된 캐릭터를 부르는 경우와 시트를 첨부하는 경우는 고정 지시문이 다르다.
    if mode == "sheet":
        key = "consistency_tag_sheet"
    elif mode == "trigger":
        key = "consistency_tag_trigger"
    else:
        key = "consistency_tag_trigger" if chars["characters"][cast[0]].get("trigger") else "consistency_tag_sheet"
    out += ". " + chars[key]
    # 소품을 더하는 컷은 "의상 그대로" 지시와 부딪히므로 예외를 명시한다.
    if shot.get("image_suffix"):
        out += " " + shot["image_suffix"]
    return out


AUDIO_PATH = ROOT / "bible" / "audio.json"
AUDIO = json.loads(AUDIO_PATH.read_text(encoding="utf-8")) if AUDIO_PATH.exists() else {}


def josa(word: str, pair: str) -> str:
    """받침에 맞는 조사를 붙인다. pair 는 "은는" "이가" "을를" 처럼 받침 있는 쪽 먼저."""
    ch = word.rstrip(")\"' ")[-1:]
    if not ch:
        return word + pair[1]
    if "가" <= ch <= "힣":
        return word + (pair[0] if (ord(ch) - 0xAC00) % 28 else pair[1])
    return word + pair[1]                          # 숫자·영문은 받침 없는 쪽으로


def motion_ref(chars: dict, shot: dict, cast: list[str], mode: str = "auto") -> str:
    """영상 생성 프롬프트. **통째로 한국어로 쓴다.**

    영어 설명 안에 한글 대사만 따옴표로 끼워 넣으면 대사 지시가 묻혀서 그 컷을
    통째로 건너뛴다. 실측으로 확인된 사실이다. 그래서 외형·동작·대사·소리·화풍을
    전부 한국어로 쓰고, 캐릭터는 트리거 워드 대신 종(種)으로 부른다.

    다섯 줄을 이 순서로 낸다.

      [외형] 매 컷 다시 적는다. 1화 한 번만 적으면 소품이 중간에 바뀐다
             (루카의 고글이 앞주머니에서 얼굴로 올라온 적이 있다).
      [동작] ko_motion. 연속 컷은 끝 자세를 고정해 다음 컷의 시작 프레임을 만든다.
      [대사] 화면 안 인물의 대사만. 나레이션은 로컬에서 얹으므로 여기서는 무성이다.
      [소리] 그 컷의 효과음. «배경음악 없이» 를 반드시 붙인다 —
             안 붙이면 생성기가 자기 음악을 깔아서 클립끼리 안 맞는다.
      [화풍] 픽사 스타일. 컷마다 빠짐없이 들어가야 한다.
    """
    ent = chars["characters"]

    # [외형] — 한두 명이면 전체 외형 + 소품 고정, 셋 이상이면 짧은 외형만.
    if not cast:
        look = "등장인물 없이 배경만 보인다."
    elif len(cast) <= 2:
        look = ", ".join(ent[k]["look_ko"] for k in cast) + ". "
        look += josa("·".join(ent[k]["props_ko"] for k in cast), "은는")
        look += " 처음부터 끝까지 그대로 유지된다."
    else:
        look = ", ".join(ent[k]["look_ko_short"] for k in cast) + ". "
        look += "각자의 옷과 소품은 처음부터 끝까지 그대로 유지된다."

    # [동작] — 연속 컷은 끝 자세를 멈춰야 다음 컷이 그 프레임에서 이어진다.
    move = shot.get("ko_motion", "").rstrip(" .") + "."
    if shot.get("link") == "연속":
        move += " 마지막에 동작을 멈추고 그 자세로 화면을 마친다."

    # [대사] — 화자 이름이 성경과 어긋나면 여기서 잡는다.
    speaker, line = shot.get("speaker", ""), shot.get("dialogue", "")
    if speaker and speaker != "나레이션" and speaker not in ent:
        raise SystemExit("%s: 모르는 화자 %r — bible/characters.json 의 이름과 맞춰야 합니다"
                         % (shot["id"], speaker))
    if line and speaker and speaker != "나레이션":
        e = ent[speaker]
        say = '%s 입을 크게 벌려 또박또박 한국어로 말한다: "%s"' % (
            josa(e["noun_ko"], "이가"), line)
        if e.get("voice_ko"):
            say += " " + e["voice_ko"].rstrip(" .") + "."
    else:
        say = "아무도 말하지 않는다. 입을 움직이지 않는다."

    # [소리] — 대사와 효과음은 생성기가 만든다. BGM 은 로컬에서 얹는다.
    heard = [AUDIO.get("sfx", {}).get(x, {}).get("소리") for x in (shot.get("sfx") or [])]
    if shot.get("sig"):
        heard.append(AUDIO.get("signature", {}).get(shot["sig"], {}).get("소리"))
    heard = [h for h in heard if h]
    sound = (", ".join(heard) + ". " if heard else "그 장면의 자연스러운 환경음만. ")
    sound += chars.get("sound_ko", "배경음악 없이 목소리와 효과음만") + "."

    return "\n".join([
        "[외형] " + look,
        "[동작] " + move,
        "[대사] " + say,
        "[소리] " + sound,
        "[화풍] " + chars["style_ko"].rstrip(" .") + ".",
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode", default="ep1")
    ap.add_argument("--shots", default="shots_v2.json")
    ap.add_argument("--mode", default="auto", choices=["auto", "trigger", "sheet"],
                    help="캐릭터를 어떻게 고정할지. sheet 는 마스터 시트를 첨부하는 방식으로, "
                         "OpenArt 밖에서 만들 때 쓴다 (트리거 워드는 OpenArt 전용)")
    ap.add_argument("--style", default="style_tag",
                    help="style_tag(본편 16:9) 또는 style_tag_shorts(쇼츠 9:16)")
    ap.add_argument("--root", help="episodes/ 대신 볼 폴더 (예: shorts)")
    args = ap.parse_args()

    prompts = ROOT / (args.root or "episodes") / args.episode / "prompts"
    chars = json.loads(bible.chars_path(prompts).read_text(encoding="utf-8"))
    path = prompts / args.shots
    data = json.loads(path.read_text(encoding="utf-8"))

    triggers = {n: chars["characters"][n].get("trigger") for n in ALL}
    missing = [n for n, t in triggers.items() if not t]
    if missing and args.mode != "sheet":
        print("! OpenArt 트리거 워드가 비어 있는 캐릭터: %s" % ", ".join(missing))
        print("  characters.json의 trigger에 채우고 다시 실행하면 프롬프트가 트리거 워드로 바뀝니다.")
        print("  지금은 ref_tag(마스터 시트 첨부 전제)로 생성합니다.\n")

    episode_cast = data.get("episode_cast")
    if episode_cast:
        unknown = [n for n in episode_cast if n not in ALL]
        if unknown:
            raise SystemExit("episode_cast에 모르는 이름: %s" % ", ".join(unknown))

    for shot in data["shots"]:
        cast = cast_of(shot, episode_cast)
        shot["cast"] = cast
        shot["image_ref"] = ref_prompt(chars, shot, cast, args.mode, args.style)
        shot["motion_ref"] = motion_ref(chars, shot, cast, args.mode)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_cast = sum(1 for s in data["shots"] if s["cast"])
    # 영상 프롬프트는 [외형] 같은 한국어 머리표를 쓰므로 대괄호를 세지 않는다.
    left = [s["id"] for s in data["shots"]
            if re.search(r"[{\[][^}\]]+[}\]]", s["image_ref"])
            or re.search(r"\{[^}]+\}", s["motion_ref"])]
    print("%s 갱신 — 캐릭터 등장 %d컷 / 배경 %d컷"
          % (args.shots, n_cast, len(data["shots"]) - n_cast))
    if left:
        print("! 채워지지 않은 이름 자리가 남았습니다: %s" % ", ".join(left))


if __name__ == "__main__":
    main()
