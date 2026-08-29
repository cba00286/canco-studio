#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""컷 리스트에 소리를 배정한다 — 환경음 · BGM · 효과음 · 능력 시그니처.

    python3 scripts/build_audio.py --episode ep1
    python3 scripts/build_audio.py --all

bible/audio.json 에 등록된 것만 쓴다. 배정 결과는 shots_v2.json 에
`audio_sections`(장면별 환경음·BGM)와 컷별 `sfx`/`sig` 로 들어가고,
대본집과 컷 시트가 그대로 읽어 간다.

배정 규칙은 bible/audio.json 의 rules 를 따른다. 특히
- 환경음은 장면 단위로만 바뀐다 (컷마다 바꾸면 이어 붙인 티가 난다)
- 말이 있는 컷에는 효과음을 하나만 넣는다
- 쿵쿵의 «지켜줄게» 한마디 컷과 타이틀 카드에는 아무것도 안 넣는다
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = json.loads((ROOT / "bible" / "audio.json").read_text(encoding="utf-8"))
_OV = ROOT / "bible" / "audio_overrides.json"
OVERRIDES = json.loads(_OV.read_text(encoding="utf-8")) if _OV.exists() else {}

# ── 환경음: 장면의 한국어 설명에서 장소와 날씨를 읽는다 ────────────────
# 장소와 날씨는 다른 겹이다. 숲에 비가 오면 «숲» 위에 «비»를 얹는다.
PLACE = [
    ("남극|빙하|얼음 벌판", "눈밭"),
    ("동굴|창고 안|굴 안", "동굴"),
    ("얼음 연못|얼어붙은 연못|언 연못", "얼음연못"),
    ("폭포", "폭포"),
    ("계곡", "계곡"),
    ("개울|올챙이", "개울"),
    ("강가|강 상류|강물|강을|불어난 강|둑", "강가"),
    ("눈밭|눈사람|첫눈|눈 덮인|서리가|겨울잠|고슴도치", "눈밭"),
    ("바람 언덕|바람언덕", "바람언덕"),
    ("참나무|낙엽|도토리|타임캡슐", "참나무숲"),
    ("꽃밭|화단|엉겅퀴|씨앗", "꽃밭"),
    ("산길|산봉우리|비탈|중턱", "산길"),
    ("정상|봉우리", "정상"),
    ("운동장|운동회|줄다리기", "운동장"),
    ("밤하늘|별똥별|밤 언덕|언덕 위 밤", "밤하늘_언덕"),
    ("광장|놀이터|장터|벤치|화단|고목", "마을_광장"),
    ("방 |집 안|곳간|작업실|창가|정자|집 앞", "실내_집"),
    ("마을", "마을_광장"),
    ("모래사장|모래 트랙|모래밭", "모래사장"),
    ("골짜기|절벽", "골짜기"),
    ("과수원", "과수원"),
    ("세면대|욕실|부엌", "실내_집"),
    ("마당", "마당"),
    ("벌통", "꽃밭"),
    ("언덕길|언덕을|언덕 위|언덕", "산길"),
    ("숲", "숲_낮"),
]
NIGHT = re.compile(r"밤|한밤|새벽|초저녁|달빛|별빛|잠들|어둠|캄캄|검다|등불|해가 지|해 질|반딧불")
STORM = re.compile(r"폭풍우|집중호우|장대비|둑이 터|사흘째 비|굵은 비|비바람")
# «루비가»의 «비가»에 걸리지 않게 앞이 한글이면 제외한다
RAIN = re.compile(r"(?<![가-힣])(비가 |비를 |비 오는|비 내리)|빗줄기|빗방울|소나기")


def ambience_for(title: str, cuts: list[dict], whole: bool = False) -> tuple[str | None, str | None]:
    """장소를 못 찾으면 None 을 준다 — 부르는 쪽에서 앞 장면을 이어받는다."""
    head = title + " " + " ".join(c["ko"] for c in (cuts if whole else cuts[:5]))
    body = title + " " + " ".join(c["ko"] for c in cuts)
    # 장면 제목과 앞부분만 본다. 못 찾으면 None 이고, 부르는 쪽이 앞 장면을
    # 이어받는다 — 이야기가 이어지는 중이라는 뜻이다.
    place = None
    for pat, key in PLACE:
        if re.search(pat, head):
            place = key
            break
    if place == "숲_낮" and NIGHT.search(head):
        place = "숲_밤"
    elif place == "마을_광장" and NIGHT.search(head):
        place = "마을_밤"
    weather = "폭우" if STORM.search(body) else ("비" if RAIN.search(body) else None)
    return place, weather


# ── BGM: 장면의 성격에서 고른다 ────────────────────────────────────────
CRISIS = re.compile(r"위험|무너|터지|터진|쏟아지|갇히|사고|다치|삐끗|폭풍|넘어질|휩쓸|넘치려|대피|구조")
# «신비»는 남발하면 값이 떨어진다. 정말 설명이 안 되는 장면에만 쓴다.
WONDER = re.compile(r"반딧불|야광 버섯|별똥별|무지개가|무지개 다리|내려오는 빛|유성|초록빛이 켜")
FUNNY = re.compile(r"우당탕|엉망|미끄러져|쏟아진|소동|또 넘어")
SAD = re.compile(r"혼자 |아무도 없|포기|안 할래|못 하겠|사라졌|텅 비")


# 쇼츠는 장면이 하나뿐이라 종류로 정한다
SHORTS_BGM = {"캐릭터 소개": "일상_밝음", "파워": "벅찬_감동",
              "예고편": "호기심_탐험", "오늘 한마디": "잔잔한_엔딩"}


def bgm_for(key: str, title: str, cuts: list[dict], has_power: bool, has_react: bool,
            kind: str | None = None, wonder: bool = False) -> str:
    if kind:
        return "벅찬_감동" if has_power else SHORTS_BGM.get(kind, "일상_밝음")
    body = title + " " + " ".join(c["ko"] for c in cuts)
    moves = " ".join(c["ko_motion"] for c in cuts)
    if key == "EN":
        return "잔잔한_엔딩"
    if has_react or wonder:
        return "신비_경이"
    if key == "SC1":
        return "위기_긴박" if CRISIS.search(body) else "일상_밝음"
    if key == "SC2":
        if CRISIS.search(body):
            return "위기_긴박"
        if SAD.search(body):
            return "조용한_슬픔"
        if FUNNY.search(body + moves):
            return "익살_소동"
        return "걱정_긴장"
    if key == "SC3":
        if has_power:
            return "벅찬_감동"
        if CRISIS.search(body):
            return "위기_긴박"
        if SAD.search(body):
            return "조용한_슬픔"
        return "호기심_탐험"
    if key == "SC4":
        return "따뜻한_해결"
    return "일상_밝음"


# ── 효과음: 영문 프롬프트의 낱말로 찾는다 ──────────────────────────────
SFX = {k: v for k, v in AUDIO["sfx"].items() if not k.startswith("_")}
# 낱말 «앞머리»로만 찾는다. 가운데를 찾으면 voice 의 ice, window glass 의 glass 에 붙는다.
SFX_RE = {k: re.compile(r"\b(" + "|".join(re.escape(w) for w in v["match"]) + r")")
          for k, v in SFX.items() if v["match"]}
SIG = {k: v for k, v in AUDIO["signature"].items() if not k.startswith("_")}
FRAGMENTS = ("쿵쿵_파워", "쿵쿵_온기", "쿵쿵_바람", "쿵쿵_자장가", "쿵쿵_방어막")
PLEDGE = re.compile(r"지켜줄게, 쿵쿵!$")


# 바닥은 장면의 환경음이 알려 준다. 동굴에서 풀밭 발소리가 나면 바로 티가 난다.
FLOOR = {
    "동굴": "발소리_돌", "마을_광장": "발소리_돌", "마을_밤": "발소리_돌",
    "실내_집": "발소리_나무마루", "운동장": "발소리_흙", "산길": "발소리_자갈",
    "눈밭": "발소리_눈", "얼음연못": "발소리_얼음", "참나무숲": "발소리_낙엽",
    "강가": "발소리_자갈", "개울": "발소리_자갈", "계곡": "발소리_자갈", "폭포": "발소리_자갈",
}


def sfx_for(shot: dict, limit: int) -> list[str]:
    text = (shot["image"] + " " + shot["motion"]).lower()
    hits = [name for name, rx in SFX_RE.items() if rx.search(text)]
    # 발소리는 한 종류만 — 눈 > 자갈 > 풀 순으로 구체적인 것을 남긴다
    for a, b in (("발소리_눈", "발소리_풀"), ("발소리_자갈", "발소리_풀"),
                 ("발소리_눈", "발소리_자갈")):
        if a in hits and b in hits:
            hits.remove(b)
    return hits[:limit]


def retread(hits: list[str], amb: str) -> list[str]:
    """발소리를 그 장면의 바닥에 맞게 바꾼다."""
    floor = FLOOR.get(amb)
    if not floor:
        return hits
    return [floor if h.startswith("발소리_") else h for h in hits]


# 조각을 안 쓰고 손으로 쓴 능력 컷도 있다(1화). 펼쳐진 영문에서 형태로 찾는다.
SIG_PHRASES = [
    ("쿵쿵_방어막", ["curving upward into a translucent dome", "translucent dome"]),
    ("쿵쿵_자장가", ["small indoor aurora"]),
    ("쿵쿵_바람", ["slow gentle spiral"]),
    ("쿵쿵_온기", ["like warm dust", "slow warm wave"]),
    ("쿵쿵_파워", ["shockwave ring", "visible shockwave"]),
]


def signature_for(shot: dict) -> str | None:
    text = shot["image"]
    for f in FRAGMENTS:
        if "{%s}" % f in text or "[%s]" % f in text:
            return f
    ref = shot.get("image_ref") or ""
    low = (text + " " + ref).lower()
    if "horns" in low and ("on its own" in low or "does not notice" in low):  # 36·40화의 «반응»
        return "뿔_반응"
    for name, phrases in SIG_PHRASES:
        if any(ph in low for ph in phrases):
            return name
    return None


def build(ep_dir: Path) -> dict:
    path = ep_dir / "prompts" / "shots_v2.json"
    D = json.loads(path.read_text(encoding="utf-8"))
    shots = D["shots"]

    # «신비»는 남발하면 값이 떨어진다. 한 화에서 가장 강하게 걸리는 두 장면만 준다.
    score = {}
    for key, title in D["sections"].items():
        cuts = [s for s in shots if s["section"] == key]
        score[key] = len(WONDER.findall(" ".join(c["ko"] for c in cuts)))
    order = list(D["sections"])
    top = {k for k, v in sorted(score.items(),
                                key=lambda kv: (-kv[1], -order.index(kv[0])))[:2] if v}

    sections, prev_place = {}, None
    for key, title in D["sections"].items():
        cuts = [s for s in shots if s["section"] == key]
        sigs = [signature_for(s) for s in cuts]
        has_power = any(x in FRAGMENTS for x in sigs)
        has_react = "뿔_반응" in sigs
        place, weather = ambience_for(title, cuts)
        if place is None:                       # 이야기가 이어지는 장면이다
            place = prev_place or ambience_for(title, cuts, whole=True)[0] or "숲_낮"
        prev_place = place
        entry = {"amb": place,
                 "bgm": bgm_for(key, title, cuts, has_power, has_react,
                                D.get("kind"), key in top)}
        if weather:
            entry["weather"] = weather
        over = dict((D.get("audio_overrides") or {}).get(key) or {})
        over.update(OVERRIDES.get("%s:%s" % (ep_dir.name, key)) or {})
        entry.update({k: v for k, v in over.items() if v})
        if over.get("weather") == "":          # 빈 문자열은 «날씨 없음»
            entry.pop("weather", None)
        sections[key] = entry

    n_sfx = 0
    for s in shots:
        sig = signature_for(s)
        s["sig"] = sig
        if s["shot_ko"] == "타이틀":                       # 규칙 6
            s["sfx"] = []
        elif PLEDGE.search(s.get("dialogue", "")):        # 규칙 5
            s["sfx"] = []
        else:
            s["sfx"] = retread(sfx_for(s, 1 if s.get("dialogue") else 3),
                               sections[s["section"]]["amb"])          # 규칙 3
        n_sfx += len(s["sfx"])

    out = {}
    for k, v in D.items():
        if k == "audio_sections":
            continue
        out[k] = v
        if k == "sections":
            out["audio_sections"] = sections
    if "audio_sections" not in out:
        out["audio_sections"] = sections
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"sections": sections, "n_sfx": n_sfx,
            "n_sig": sum(1 for s in shots if s["sig"]),
            "n_quiet": sum(1 for s in shots if not s["sfx"])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--root", default="episodes")
    a = ap.parse_args()

    base = ROOT / a.root
    if a.all:
        eps = sorted((d for d in base.glob("*") if (d / "prompts" / "shots_v2.json").exists()),
                     key=lambda d: int(re.sub(r"\D", "", d.name) or 0))
    else:
        eps = [base / (a.episode or "ep1")]

    for d in eps:
        r = build(d)
        bgms = " · ".join(sorted({v["bgm"] for v in r["sections"].values()}))
        ambs = " · ".join(sorted({v["amb"] + ("+" + v["weather"] if v.get("weather") else "")
                                  for v in r["sections"].values()}))
        print("%-6s 효과음 %3d컷 · 능력음 %d · 조용한 컷 %2d" % (d.name, r["n_sfx"], r["n_sig"], r["n_quiet"]))
        print("       환경음 %s" % ambs)
        print("       BGM   %s" % bgms)


if __name__ == "__main__":
    main()
