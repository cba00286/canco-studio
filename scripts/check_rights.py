#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""권리 관련해서 비어 있는 곳을 찾는다. 공개 전에 한 번은 돌린다.

여기서 걸리는 것들은 «나중에 하면 되는 일»이 아니다. 유튜브에 올린 뒤에
음원 클레임이 들어오거나 생성 도구 약관이 상업 이용을 막고 있으면,
40화를 다 만든 다음에 알게 된다.

    python3 scripts/check_rights.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    r = json.loads((ROOT / "bible" / "rights.json").read_text(encoding="utf-8"))
    audio = json.loads((ROOT / "bible" / "audio.json").read_text(encoding="utf-8"))

    문제, 경고 = [], []

    if "<" in r.get("권리자", ""):
        문제.append("권리자명이 비어 있습니다 — bible/rights.json 의 «권리자». "
                  "엔딩 표기와 출원서에 들어갈 이름입니다")

    자산 = r.get("자산", {})
    for 갈래, 항목들 in 자산.items():
        if 갈래.startswith("_"):
            continue
        for 이름, v in 항목들.items():
            if 이름.startswith("_") or not isinstance(v, dict):
                continue
            if v.get("상업이용") is None:
                문제.append("%s / %s — 상업적 이용 가능 여부가 확인되지 않았습니다%s"
                          % (갈래, 이름, ": " + v["확인필요"] if v.get("확인필요") else ""))
            elif v.get("상업이용") is False:
                문제.append("%s / %s — 상업적 이용이 **불가**로 적혀 있습니다. 교체하세요"
                          % (갈래, 이름))
            if v.get("라이선스") in (None, "", "미확인"):
                경고.append("%s / %s — 라이선스가 적혀 있지 않습니다" % (갈래, 이름))

    # 쓰고 있는 효과음 중 출처가 없는 것
    쓰는효과음 = {k for k in audio.get("sfx", {}) if not k.startswith("_")}
    기록된 = {k for k in 자산.get("효과음", {}) if not k.startswith("_")}
    빠진 = sorted(쓰는효과음 - 기록된)
    if 빠진:
        경고.append("효과음 %d종의 출처가 기록되지 않았습니다. 음원을 받을 때마다 "
                  "bible/rights.json 의 자산.효과음 에 적으세요 — 유튜브 Content ID "
                  "클레임이 실제로 자주 들어옵니다.\n     %s"
                  % (len(빠진), ", ".join(빠진[:12]) + (" …" if len(빠진) > 12 else "")))

    for p in ("ip/창작이력_증빙.pdf", "docs/19_지식재산_보호.md", "ip/해야_할_일.md"):
        if not (ROOT / p).exists():
            경고.append("%s 가 없습니다" % p)

    원화 = list((ROOT / "ip" / "원화").glob("*/01_스케치*")) if (ROOT / "ip" / "원화").exists() else []
    if not 원화:
        경고.append("손으로 그린 원화가 아직 없습니다. 그림 쪽 권리는 이것 말고 방법이 "
                  "없습니다 — docs/20_원화_작업.md, 쿵쿵이 한 장이면 됩니다")

    for m in 문제:
        print("✗ %s" % m)
    for m in 경고:
        print("! %s" % m)
    if not 문제 and not 경고:
        print("권리 점검 이상 없음")
        return 0
    print("\n문제 %d건 · 경고 %d건 — ip/해야_할_일.md 를 보세요" % (len(문제), len(경고)))
    return 1 if 문제 else 0


if __name__ == "__main__":
    sys.exit(main())
