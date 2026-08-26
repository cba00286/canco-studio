#!/usr/bin/env python3
"""`link: 연속` 인 컷의 시작 프레임을 앞 컷 영상의 마지막 프레임에서 뽑아낸다.

Kling 3 Omni · Seedance 2.0/2.5 · Wan 2.7 · PixVerse V6 는 시작 프레임을 받는다.
앞 컷의 끝 프레임을 그대로 다음 컷의 시작 프레임으로 넣으면 이음매가 사라진다.

    python3 scripts/chain_frames.py --episode episodes/ep1 --clips ~/쿵쿵이/1화클립

캐릭터 레퍼런스 체이닝과 혼동하지 말 것. 얼굴은 언제나 등록된 트리거 워드로
잡는다 — 앞 컷 결과물을 얼굴 레퍼런스로 쓰면 컷을 거듭할수록 얼굴이 변한다.
여기서 물려주는 것은 첫 프레임의 구도와 위치뿐이다. (docs/14)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from render_episode import find_ffmpeg, match_clips          # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episode", required=True)
    p.add_argument("--clips", required=True, help="이미 만든 컷 영상이 있는 폴더")
    p.add_argument("--out", help="기본값: <episode>/chain")
    p.add_argument("--trim", type=float, default=0.04,
                   help="마지막 프레임 대신 끝에서 이만큼 앞의 프레임을 쓴다(초). "
                        "맨 끝 프레임은 인코딩이 뭉개져 있는 경우가 있다")
    a = p.parse_args()

    ep = Path(a.episode)
    shots = json.loads((ep / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))["shots"]
    ffmpeg = find_ffmpeg("ffmpeg")
    out = Path(a.out) if a.out else ep / "chain"
    out.mkdir(parents=True, exist_ok=True)

    matched, _ = match_clips(shots, a.clips)
    have = dict(matched)

    need = [(shots[i - 1]["id"], s["id"])
            for i, s in enumerate(shots) if i and s.get("link") == "연속"]
    if not need:
        print("`link: 연속` 인 컷이 없습니다. docs/14 를 보고 이어붙일 자리를 정하세요.")
        return

    done, missing = 0, []
    for prev_id, this_id in need:
        src = have.get(prev_id)
        if not src:
            missing.append((prev_id, this_id))
            continue
        dst = out / f"{this_id}_시작프레임.png"
        r = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-sseof", f"-{a.trim}",
             "-i", str(src), "-frames:v", "1", "-q:v", "1", str(dst)])
        if r.returncode:
            missing.append((prev_id, this_id))
            continue
        print(f"  {this_id:<9} ← {prev_id} 의 끝 프레임   {dst.name}")
        done += 1

    print(f"\n연속 컷 {len(need)}개 중 {done}개 준비됨 → {out}")
    if missing:
        print("  앞 컷 영상이 아직 없어 못 뽑은 것: "
              + ", ".join(f"{b}(←{a_})" for a_, b in missing))
    if done:
        print("\n이 파일들을 OpenArt 에서 해당 컷의 **시작 프레임**으로 올리세요.")
        print("캐릭터 얼굴은 그대로 트리거 워드로 잡습니다 — 얼굴 레퍼런스로 쓰지 마세요.")


if __name__ == "__main__":
    sys.exit(main())
