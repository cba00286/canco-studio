#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사이트 전체를 다시 만든다.

    python3 site/build.py           # ep1
    python3 site/build.py ep2       # 다른 에피소드

저장소의 JSON이 유일한 원본이다. 페이지를 고치려면 JSON이나 템플릿을 고치고
이 스크립트를 다시 돌린 뒤, 산출물을 Artifact로 배포한다. 자세한 절차는 CLAUDE.md.
"""
import subprocess, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
PAGES = [("make_hub.py", "제작 자료실"), ("make_bible.py", "캐릭터 바이블"), ("make_sheet.py", "컷 시트")]

fail = 0
for script, label in PAGES:
    r = subprocess.run([sys.executable, str(HERE / script), EP], capture_output=True, text=True)
    if r.returncode:
        fail += 1
        print("✗ %s\n%s" % (label, r.stderr.strip()))
    else:
        print("✓ %-12s %s" % (label, r.stdout.strip().split(": ", 1)[-1]))
sys.exit(1 if fail else 0)
