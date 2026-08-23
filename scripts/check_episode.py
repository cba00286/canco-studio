#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""에피소드가 시리즈 규격(format.json)을 지키는지 검사한다.

    python3 scripts/check_episode.py            # ep1
    python3 scripts/check_episode.py ep2

컷을 다 짠 뒤 반드시 한 번 돌린다. 규격을 벗어난 채로 생성에 들어가면
60컷을 다시 뽑아야 한다.
"""
import json, pathlib, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
FMT = json.loads((ROOT / "format.json").read_text(encoding="utf-8"))
SHOTS = json.loads((ROOT / "episodes" / EP / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))
S = SHOTS["shots"]

fails, warns = [], []

def check(label, value, lo, hi, unit=""):
    ok = lo <= value <= hi
    (fails if not ok else []).append("%s %s%s — 규격 %s~%s%s" % (label, value, unit, lo, hi, unit)) if not ok else None
    print("  %s %-14s %s%s   (%s~%s%s)" % ("✓" if ok else "✗", label, value, unit, lo, hi, unit))
    return ok

total = sum(s["duration"] for s in S)
print("\n[%s] %d컷 / %d초 (%d분 %02d초)\n" % (EP, len(S), total, total // 60, total % 60))

print("러닝타임 · 분량")
check("러닝타임", total, FMT["runtime_sec"]["min"], FMT["runtime_sec"]["max"], "초")
check("컷 수", len(S), FMT["cuts"]["min"], FMT["cuts"]["max"], "컷")
bad = [s["id"] for s in S if not (FMT["clip_sec"]["min"] <= s["duration"] <= FMT["clip_sec"]["max"])]
print("  %s 클립 길이       %s" % ("✓" if not bad else "✗",
      "전 컷 %d~%d초" % (FMT["clip_sec"]["min"], FMT["clip_sec"]["max"]) if not bad else "규격 밖: " + ", ".join(bad)))
if bad:
    fails.append("클립 길이 규격 밖: " + ", ".join(bad))

print("\n샷 배분")
mix = Counter(s["shot_ko"] for s in S)
for name, rng in FMT["shot_mix_pct"].items():
    pct = round(mix.get(name, 0) * 100 / len(S))
    check(name, pct, rng["min"], rng["max"], "%")

print("\n대사")
lines = Counter(s["speaker"] for s in S if s["dialogue"])
check("나레이션", lines.get("나레이션", 0), FMT["dialogue"]["narration"]["min"], FMT["dialogue"]["narration"]["max"], "줄")
chars = sum(v for k, v in lines.items() if k != "나레이션")
check("캐릭터 대사", chars, FMT["dialogue"]["character"]["min"], FMT["dialogue"]["character"]["max"], "줄")

if FMT["dialogue"]["silent_character_warn"]:
    cast = Counter(n for s in S for n in s["cast"])
    silent = [n for n in cast if lines.get(n, 0) == 0]
    if silent:
        warns.append("등장하는데 대사가 없는 캐릭터: " + ", ".join("%s(%d컷)" % (n, cast[n]) for n in silent))

print("\n구성")
title = sum(1 for s in S if s["shot_ko"] == "타이틀")
print("  %s 타이틀 카드     %d컷" % ("✓" if title == FMT["structure"]["title_card"] else "✗", title))
if title != FMT["structure"]["title_card"]:
    fails.append("타이틀 카드가 %d컷 (규격 %d컷)" % (title, FMT["structure"]["title_card"]))
secs = list(SHOTS["sections"])
end_n = sum(1 for s in S if s["section"] == secs[-1])
print("  %s 엔딩 분량       %d컷 (최대 %d)" % ("✓" if end_n <= FMT["structure"]["ending_cuts_max"] else "✗",
      end_n, FMT["structure"]["ending_cuts_max"]))
if end_n > FMT["structure"]["ending_cuts_max"]:
    fails.append("엔딩이 %d컷 (최대 %d)" % (end_n, FMT["structure"]["ending_cuts_max"]))

print()
for w in warns:
    print("! %s" % w)
if fails:
    print("\n규격 위반 %d건" % len(fails))
    for f in fails:
        print("  - %s" % f)
    sys.exit(1)
print("규격 통과%s" % ("  (경고 %d건)" % len(warns) if warns else ""))
