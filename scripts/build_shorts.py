#!/usr/bin/env python3
"""쇼츠 프롬프트를 만든다.

본편과 다른 점은 **화면비 하나뿐**이다. 본편은 16:9, 쇼츠는 9:16 이다.
본편 컷을 잘라 쓸 수 없다 — 16:9 로 잡은 구도를 세로로 자르면 얼굴과
시그니처 포즈가 화면 밖으로 나간다. 쇼츠는 처음부터 세로로 만든다.

캐릭터는 본편과 똑같이 OpenArt Characters 트리거 워드로 고정한다.

    python3 scripts/build_shorts.py                 # shorts/ 전체
    python3 scripts/build_shorts.py C01             # 하나만
    python3 scripts/build_shorts.py --mode sheet    # OpenArt 밖에서 만들 때
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    argv = sys.argv[1:]
    mode = "auto"
    if "--mode" in argv:
        i = argv.index("--mode")
        mode = argv[i + 1]
        del argv[i:i + 2]
    want = argv
    dirs = sorted(d for d in (ROOT / "shorts").iterdir()
                  if d.is_dir() and (d / "prompts" / "shots_v2.json").exists())
    if want:
        dirs = [d for d in dirs if d.name in want]
    if not dirs:
        sys.exit("shorts/ 아래에 만들 것이 없습니다.")
    for d in dirs:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_ref_prompts.py"),
             "--root", "shorts", "--episode", d.name,
             "--mode", mode, "--style", "style_tag_shorts"],
            capture_output=True, text=True)
        if r.returncode:
            print(f"✗ {d.name}\n{r.stderr.strip()}")
        else:
            print(f"✓ {d.name:<6} {r.stdout.strip().split('— ', 1)[-1]}")
    if mode == "sheet":
        print("\nsheet 모드입니다 — 마스터 시트를 레퍼런스 이미지로 첨부해야 얼굴이 고정됩니다.")
    else:
        print("\nOpenArt Characters 트리거 워드로 캐릭터가 고정됩니다. 본편과 같은 방식입니다.")


if __name__ == "__main__":
    sys.exit(main())
