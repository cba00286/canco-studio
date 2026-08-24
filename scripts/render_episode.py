#!/usr/bin/env python3
"""컷 클립을 이어붙이고 자막을 굽는다. OpenArt 크레딧을 쓰지 않는다.

  1. 클립 폴더에서 컷 ID 로 파일을 찾아 shots_v2.json 순서대로 정렬
  2. ffprobe 로 각 클립의 실제 길이를 재서 durations.json 저장
  3. 그 실측 길이로 build_subtitles.py 를 돌려 .ass 재생성 (자막 밀림 방지)
  4. concat + 자막 굽기 + (선택) 배경음악 믹스

클립 파일명은 컷 ID 를 포함하면 된다: SC1-01.mp4, ep1_SC1-01_v2.mp4 등.

  python3 scripts/render_episode.py --episode episodes/ep1 --clips ~/쿵쿵이/1화클립
  python3 scripts/render_episode.py --episode episodes/ep1 --clips ... --audio ost.mp3 --dry-run
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


def find_ffmpeg(name="ffmpeg"):
    """ffmpeg 를 찾는다. 사용자 PC 에 설치돼 있으면 그걸 쓰고,
    없으면 pip 로 깔리는 imageio-ffmpeg 동봉 바이너리를 쓴다."""
    env = os.environ.get(name.upper())
    if env and Path(env).exists():
        return env
    found = shutil.which(name)
    if found:
        return found
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if name == "ffmpeg":
            return exe
        cand = Path(exe).parent / "ffprobe"
        if cand.exists():
            return str(cand)
        return exe          # ffprobe 가 없으면 ffmpeg 로 길이를 잰다
    except ImportError:
        pass
    sys.exit(f"{name} 를 찾을 수 없습니다.  brew install ffmpeg  또는  "
             f"pip install imageio-ffmpeg  로 설치하세요.")


def probe_duration(ffprobe, ffmpeg, path):
    if Path(ffprobe).name.startswith("ffprobe"):
        out = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return float(out.stdout.strip())
    # ffprobe 가 없을 때: ffmpeg 로그에서 Duration 을 긁는다
    out = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out.stderr)
    if not m:
        sys.exit(f"길이를 잴 수 없습니다: {path}")
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def match_clips(shots, clips_dir):
    files = [p for p in sorted(Path(clips_dir).iterdir())
             if p.suffix.lower() in VIDEO_EXT]
    matched, missing = [], []
    for sh in shots:
        hits = [p for p in files if sh["id"].lower() in p.stem.lower()]
        if not hits:
            missing.append(sh["id"])
        else:
            # 같은 컷의 파일이 여러 개면 가장 최근 것을 쓴다 (재생성본 우선)
            matched.append((sh["id"], max(hits, key=lambda p: p.stat().st_mtime)))
    return matched, missing


def run(cmd, dry):
    printable = " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd)
    if dry:
        print("  $ " + printable)
        return
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"ffmpeg 실패 (코드 {r.returncode})")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episode", required=True)
    p.add_argument("--clips", required=True, help="컷 클립이 들어있는 폴더")
    p.add_argument("--audio", help="배경음악/OST 파일 (선택)")
    p.add_argument("--music-volume", type=float, default=0.35)
    p.add_argument("--out")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--crf", type=int, default=18)
    p.add_argument("--no-burn", action="store_true", help="자막을 굽지 않고 이어붙이기만")
    p.add_argument("--allow-missing", action="store_true", help="없는 컷은 건너뛴다")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    ep = Path(a.episode)
    work = ep / "render"
    work.mkdir(parents=True, exist_ok=True)
    ffmpeg, ffprobe = find_ffmpeg("ffmpeg"), find_ffmpeg("ffprobe")
    shots = json.loads((ep / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))["shots"]

    matched, missing = match_clips(shots, a.clips)
    print(f"컷 {len(shots)}개 중 {len(matched)}개 찾음")
    if missing:
        print(f"  없는 컷 {len(missing)}개: {', '.join(missing[:12])}"
              + (" …" if len(missing) > 12 else ""))
        if not a.allow_missing:
            sys.exit("  --allow-missing 을 주면 있는 것만으로 진행합니다.")

    # 1) 실측 길이
    durations = {}
    for sid, path in matched:
        durations[sid] = round(probe_duration(ffprobe, ffmpeg, path), 3)
    dpath = work / "durations.json"
    dpath.write_text(json.dumps(durations, ensure_ascii=False, indent=2), encoding="utf-8")
    spec = sum(s.get("duration", 0) for s in shots if s["id"] in durations)
    real = sum(durations.values())
    print(f"실측 총 길이 {real:.1f}초 · 규격 {spec}초 · 차이 {real - spec:+.1f}초")

    # 2) 실측 길이로 자막 재생성
    import build_subtitles
    ass, srt, n, _ = build_subtitles.build(ep, durations=dpath)
    print(f"자막 {n}줄 재생성 (실측 기준) → {ass.name}, {srt.name}")

    # 3) 이어붙이기. 클립마다 해상도/fps 가 다를 수 있으므로 재인코딩한다.
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for _, p in matched), encoding="utf-8")
    merged = work / "merged.mp4"
    vf = (f"scale={a.width}:{a.height}:force_original_aspect_ratio=decrease,"
          f"pad={a.width}:{a.height}:(ow-iw)/2:(oh-ih)/2:color=black,fps={a.fps}")
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-vf", vf, "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(merged)], a.dry_run)

    # 4) 자막 굽기 + 음악
    out = Path(a.out) if a.out else ep / f"{ep.name}.mp4"
    cmd = [ffmpeg, "-y", "-i", str(merged)]
    if a.audio:
        cmd += ["-stream_loop", "-1", "-i", str(a.audio)]
    if a.no_burn:
        cmd += ["-c:v", "copy"]
    else:
        fonts = ROOT / json.loads((ROOT / "subtitle_style.json").read_text(encoding="utf-8")).get("fonts_dir", "fonts")
        # 경로의 : 와 ' 는 filtergraph 에서 이스케이프해야 한다
        esc = lambda s: str(s).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        cmd += ["-vf", f"subtitles='{esc(ass)}':fontsdir='{esc(fonts)}'",
                "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p"]
    if a.audio:
        cmd += ["-filter_complex" if False else "-af", f"volume={a.music_volume}",
                "-map", "0:v", "-map", "1:a", "-shortest", "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-c:a", "copy"]
    cmd += [str(out)]
    run(cmd, a.dry_run)

    if not a.dry_run:
        size = Path(out).stat().st_size / 1e6
        print(f"\n완성: {out}  ({size:.1f} MB)")
        print(f"유튜브 자막 파일: {srt}")


if __name__ == "__main__":
    sys.exit(main())
