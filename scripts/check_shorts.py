#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""쇼츠가 규격(shorts_format.json)을 지키는지 검사한다.

    python3 scripts/check_shorts.py          # 전체
    python3 scripts/check_shorts.py C01      # 하나만
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FMT = json.loads((ROOT / "shorts_format.json").read_text(encoding="utf-8"))
LINKS = ("연속", "컷", "전환")

want = sys.argv[1:]
dirs = sorted(d for d in (ROOT / "shorts").iterdir()
              if d.is_dir() and (d / "prompts" / "shots_v2.json").exists())
if want:
    dirs = [d for d in dirs if d.name in want]

fails = []
print("\n%-5s %-4s %-4s %-24s %s" % ("ID", "초", "컷", "제목", "확인"))
print("─" * 74)
for d in dirs:
    D = json.loads((d / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))
    S = D["shots"]
    total = sum(x["duration"] for x in S)
    bad = []
    if not FMT["runtime_sec"]["min"] <= total <= FMT["runtime_sec"]["max"]:
        bad.append("길이 %d초" % total)
    if not FMT["cuts"]["min"] <= len(S) <= FMT["cuts"]["max"]:
        bad.append("컷 %d개" % len(S))
    off = [x["id"] for x in S
           if not FMT["clip_sec"]["min"] <= x["duration"] <= FMT["clip_sec"]["max"]]
    if off:
        bad.append("클립 길이 " + ",".join(off))
    if any(x.get("link") not in LINKS for x in S):
        bad.append("link 누락")
    if S and S[0].get("link") != "전환":
        bad.append("첫 컷이 전환이 아님")
    lines = sum(1 for x in S if x["dialogue"])
    if lines > FMT["dialogue"]["max_lines"]:
        bad.append("대사 %d줄" % lines)
    # 9:16 로 만들어졌는지
    if S and "9:16" not in S[0]["image_ref"]:
        bad.append("세로 화면비가 아님")
    print("%-5s %-4d %-4d %-24s %s" % (d.name, total, len(S), D.get("title", "")[:24],
                                       "✓" if not bad else "✗ " + " · ".join(bad)))
    if bad:
        fails.append(d.name)

print("─" * 74)
if fails:
    print("규격 위반 %d편: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("쇼츠 %d편 전부 규격 통과" % len(dirs))
