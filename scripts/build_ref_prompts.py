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
from build_previz import move_of

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
    look, say, sound, style = _parts(chars, shot, cast)
    move = shot.get("ko_motion", "").rstrip(" .") + "."
    if shot.get("link") == "연속":
        move += " 마지막에 동작을 멈추고 그 자세로 화면을 마친다."
    return "\n".join([
        "[외형] " + look, "[동작] " + move, "[대사] " + say,
        "[소리] " + sound, "[화풍] " + style,
    ])


def _parts(chars: dict, shot: dict, cast: list[str]) -> tuple[str, str, str, str]:
    """[외형] [대사] [소리] [화풍] 네 조각. motion_ref 와 previz_ref 가 같이 쓴다."""
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

    return look, say, sound, chars["style_ko"].rstrip(" .") + "."


# ── 프리비즈 기준 프롬프트 ────────────────────────────────────────────────────
#
# 구도·카메라·타이밍을 블렌더가 잡고, 확정된 프리비즈 프레임을 레퍼런스로 넣는
# 방식이다. 그래서 프롬프트는 카메라를 두 번 말하면 안 된다 — 프레임 두 장이나
# 프리비즈 영상을 넣으면 카메라는 이미 거기 있고, 문장까지 주면 두 번 움직인다.
#
#   i2v        첫 프레임 한 장.  카메라를 문장으로 말해 준다.
#   start_end  첫·끝 두 장.      카메라 문장을 빼고 구도만 지킨다.

PREVIZ = json.loads((ROOT / "bible" / "previz.json").read_text(encoding="utf-8"))
ENGINES = json.loads((ROOT / "bible" / "engines.json").read_text(encoding="utf-8"))

# «카메라가 미끄러진다» 처럼 카메라가 주어인 구절만 걷어낸다. «파편이 카메라 옆으로
# 스쳐 간다» 는 카메라를 기준점으로만 쓴 연기 묘사라서 남겨야 한다.
CAM_KO = re.compile(r"(?:카메라|앵글|화면)(?:가|는|이|은|도)")
# 영어는 «카메라가 움직인다» 는 말만 걷어낸다. "sparks streaming past camera" 처럼
# 카메라를 기준점으로만 쓰는 말은 연기 묘사라서 남겨야 한다.
CAM_EN = re.compile(
    r"\bcamera\s+\w+(?:ing|s|ed)\b"
    r"|\bcamera\s+(?:slowly|slightly|gently)\b"
    r"|\b(?:push(?:es|ing)?\s+in|pull(?:s|ing)?\s+back|zoom(?:s|ing)?\s+(?:in|out)"
    r"|the\s+shot\s+wide(?:n|ns|ning)|cran(?:e|es|ing)\s+(?:up|down))\b", re.I)

# 물·불·연기처럼 물리가 무거운 컷은 대사가 없으면 클링으로 보낸다.
HEAVY = ("급류", "물살", "파도", "소용돌이", "폭포", "불", "불꽃", "연기", "먼지",
         "눈보라", "폭우", "번개", "파장", "충격파", "무너", "쏟아", "터진")


def _split_ko(text: str) -> tuple[str, str]:
    """한국어 묘사를 «인물 연기» 와 «카메라» 로 가른다.

    문장으로 한 번, 쉼표와 «~고» 로 한 번 더 자른다. 한 문장 안에서
    «다섯이 처마 밑으로 뛰어들고 카메라는 집에 머문다» 처럼 붙어 있는 일이 잦다.
    """
    parts = []
    for sent in re.split(r"(?<=[.!?])\s+", text.strip()):
        parts += [x.strip(" ,") for x in re.split(r",\s*|(?<=고)\s+", sent) if x.strip(" ,")]
    act = [x for x in parts if not CAM_KO.search(x)]
    cam = [x for x in parts if CAM_KO.search(x)]
    return " ".join(act), " ".join(cam)


def _split_en(text: str) -> str:
    """영어 묘사에서 카메라 움직임 구절만 걷어낸다. 쉼표 단위로 자른다."""
    kept = [x.strip() for x in re.split(r",\s*", text.strip())
            if x.strip() and not CAM_EN.search(x)]
    out = ", ".join(kept)
    return re.sub(r"\s+", " ", out).strip(" ,.")


def engine_for(shot: dict, move: str) -> str:
    """이 컷을 어느 엔진으로 보낼지. bible/engines.json 의 «고르는_법» 그대로."""
    speaker = shot.get("speaker")
    if shot.get("dialogue") and speaker and speaker != "나레이션":
        return "hailuo"                            # 대사 컷은 선택지가 없다
    text = (shot.get("ko", "") + shot.get("ko_motion", ""))
    if any(w in text for w in HEAVY):
        return "kling"
    if move != "정지":
        return "higgsfield"
    return ENGINES["기본"]


def previz_ref(chars: dict, shot: dict, cast: list[str], move: str,
               mode: str = "auto", style: str = "style_tag") -> dict:
    """프리비즈 프레임을 레퍼런스로 넣을 때 쓰는 컷 프롬프트."""
    eng = engine_for(shot, move)
    prof = ENGINES["엔진"][eng]
    m = PREVIZ["카메라_움직임"][move]

    if prof["프롬프트_언어"] == "한국어":
        look, say, sound, st = _parts(chars, shot, cast)
        act, cam_said = _split_ko(shot.get("ko_motion", ""))
        # 컷 전체가 카메라 묘사뿐이면 연기 줄을 비워 두지 말고 중립문을 쓴다.
        # 원문으로 되돌리면 걷어낸 카메라 지시가 그대로 다시 들어온다.
        act = (act or "인물은 크게 움직이지 않는다. 숨결과 옷·풀·물처럼 "
                      "화면 안의 것들만 자연스럽게 움직인다").rstrip(" .")
        if act.endswith("고"):
            act += " 이어서 동작을 마친다"       # «~고» 로 끊긴 채 끝나지 않게
        act += "."
        if shot.get("link") == "연속":
            act += " 마지막에 동작을 멈추고 그 자세로 화면을 마친다."
        body = ["[외형] " + look, "[연기] " + act]
        tail = ["[대사] " + say, "[소리] " + sound, "[화풍] " + st]
        i2v = "\n".join(
            ["[구도] 첨부한 프리비즈 프레임의 구도를 그대로 따른다. "
             "인물의 자리와 화면 안 크기를 바꾸지 않는다."]
            + body + ["[카메라] " + (cam_said or m["문장"])] + tail)
        se = "\n".join(
            ["[구도] 첨부한 두 프레임이 첫 화면과 끝 화면이다. 그 사이만 움직인다. "
             "인물의 자리와 화면 안 크기를 바꾸지 않는다."] + body + tail)
    else:
        act = (_split_en(shot.get("motion", ""))
               or "The scene continues with gentle natural motion in the light, "
                  "air and small details")
        # 정지 이미지용 프롬프트를 영상용으로 돌린다 — «film still» 이 남으면 안 움직인다.
        scene = shot["image_ref"].replace("animated film still", "animated film")
        base = scene.rstrip(" .") + ". " + act.rstrip(" .") + "."
        keep = (" Follow the composition of the attached previz frame exactly — "
                "do not move, resize or reframe the characters. "
                "No background music; diegetic sound effects only.")
        i2v = base + " " + m["문장_en"] + keep
        se = (base + " The two attached frames are the first and last frame; "
              "all movement happens between them." + keep)

    return {"엔진": eng, "엔진_이름": prof["이름"], "카메라": move,
            "언어": prof["프롬프트_언어"], "i2v": i2v, "start_end": se}


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
        shot["previz_ref"] = previz_ref(chars, shot, cast,
                                        move_of(shot, PREVIZ), args.mode, args.style)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_cast = sum(1 for s in data["shots"] if s["cast"])
    # 영상 프롬프트는 [외형] 같은 한국어 머리표를 쓰므로 대괄호를 세지 않는다.
    left = [s["id"] for s in data["shots"]
            if re.search(r"[{\[][^}\]]+[}\]]", s["image_ref"])
            or re.search(r"\{[^}]+\}", s["motion_ref"])]
    eng = {}
    for sh in data["shots"]:
        eng[sh["previz_ref"]["엔진"]] = eng.get(sh["previz_ref"]["엔진"], 0) + 1
    print("%s 갱신 — 캐릭터 등장 %d컷 / 배경 %d컷 / 엔진 %s"
          % (args.shots, n_cast, len(data["shots"]) - n_cast,
             ", ".join("%s %d" % kv for kv in sorted(eng.items()))))
    if left:
        print("! 채워지지 않은 이름 자리가 남았습니다: %s" % ", ".join(left))


if __name__ == "__main__":
    main()
