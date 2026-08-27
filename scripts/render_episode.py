#!/usr/bin/env python3
"""컷 클립을 이어붙이고 자막을 굽는다. OpenArt 크레딧을 쓰지 않는다.

  1. 클립 폴더에서 컷 ID 로 파일을 찾아 shots_v2.json 순서대로 정렬
  2. ffprobe 로 각 클립의 실제 길이를 재서 durations.json 저장
  3. 그 실측 길이로 build_subtitles.py 를 돌려 .ass 재생성 (자막 밀림 방지)
  4. link 에 맞춰 전환을 걸어 이어붙이고 + 자막 굽기 + (선택) 배경음악 믹스

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


def probe_has_audio(ffprobe, ffmpeg, path):
    """소리 트랙이 있는지 본다. 하나라도 없으면 오디오 크로스페이드를 걸 수 없다."""
    if Path(ffprobe).name.startswith("ffprobe"):
        out = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        return bool(out.stdout.strip())
    out = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True)
    return "Audio:" in out.stderr


def transition_plan(shots, a):
    """컷 사이마다 (link, 초, 종류)를 정한다.

    link 는 앞 컷과의 관계다(docs/14). 그냥 붙이면 생성 영상은 컷마다 튀므로,
    관계에 맞는 길이로 섞어준다 — 연속은 거의 안 보이게, 장면 전환은 넉넉하게.
    컷에 transition 필드가 있으면 그쪽이 우선한다.
    """
    cfg = json.loads((ROOT / "transitions.json").read_text(encoding="utf-8"))["기본"]
    plan = []
    for sh in shots[1:]:                       # 첫 컷 앞에는 전환이 없다
        link = sh.get("link", "컷")
        base = cfg.get(link, cfg["컷"])
        over = sh.get("transition") or {}
        sec = float(over.get("sec", base["sec"])) * a.transition_scale
        plan.append((link, round(sec, 3), over.get("type", base["type"])))
    return plan


def build_xfade_script(plan, dur, a, has_audio):
    """xfade 체인을 만든다.

    xfade 는 두 영상을 겹쳐서 섞는다. 겹치는 만큼 전체 길이가 줄어들기 때문에
    다음 전환의 시작 지점(offset)을 그만큼 당겨서 계산해야 한다. 하나라도
    어긋나면 뒤쪽이 전부 밀린다.
    """
    W, H, F = a.width, a.height, a.fps
    norm = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"fps={F},setsar=1,format=yuv420p")
    lines = [f"[{i}:v]{norm}[v{i}];" for i in range(len(dur))]

    acc, prev = dur[0], "[v0]"
    for i, (_, sec, kind) in enumerate(plan, start=1):
        sec = max(0.04, min(sec, dur[i] - 0.1, acc - 0.1))   # 클립보다 길면 안 된다
        off = acc - sec
        label = "[vout]" if i == len(plan) else f"[x{i}]"
        lines.append(f"{prev}[v{i}]xfade=transition={kind}:duration={sec:.3f}"
                     f":offset={off:.3f}{label};")
        acc, prev = acc + dur[i] - sec, label
    if len(dur) == 1:
        lines.append("[v0]null[vout];")

    if has_audio:
        af = "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
        lines += [f"[{i}:a]{af}[a{i}];" for i in range(len(dur))]
        prev = "[a0]"
        for i, (_, sec, _k) in enumerate(plan, start=1):
            sec = max(0.04, min(sec, dur[i] - 0.1))
            label = "[aout]" if i == len(plan) else f"[y{i}]"
            lines.append(f"{prev}[a{i}]acrossfade=d={sec:.3f}:c1=tri:c2=tri{label};")
            prev = label
        if len(dur) == 1:
            lines.append("[a0]anull[aout];")
    return "\n".join(lines).rstrip(";")


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
    p.add_argument("--no-transitions", action="store_true",
                   help="전환 없이 딱 붙인다(예전 동작). 컷마다 툭툭 끊긴다")
    p.add_argument("--fade-in", type=float, default=0.6,
                   help="검은 화면에서 열리는 시간(초). 0 이면 안 넣는다")
    p.add_argument("--fade-out", type=float, default=1.0,
                   help="검은 화면으로 닫히는 시간(초). 0 이면 안 넣는다")
    p.add_argument("--transition-scale", type=float, default=1.0,
                   help="전환 길이를 한꺼번에 늘리거나 줄인다. 0.5 면 절반, 2 면 두 배")
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

    # 2) 전환을 먼저 정한다. 자막 타이밍이 여기에 딸려 있다.
    by_id = {s["id"]: s for s in shots}
    plan = transition_plan([by_id[sid] for sid, _ in matched], a)

    # 4) 전환을 걸어 이어붙인다. 그냥 붙이면(concat) 컷마다 툭툭 끊긴다.
    merged = work / "merged.mp4"
    if a.no_transitions:
        lst = work / "concat.txt"
        lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for _, p in matched), encoding="utf-8")
        vf = (f"scale={a.width}:{a.height}:force_original_aspect_ratio=decrease,"
              f"pad={a.width}:{a.height}:(ow-iw)/2:(oh-ih)/2:color=black,fps={a.fps}")
        run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-vf", vf, "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(merged)], a.dry_run)
    else:
        clips = [p for _, p in matched]
        dur = [durations[sid] for sid, _ in matched]
        has_audio = all(probe_has_audio(ffprobe, ffmpeg, c) for c in clips)
        if not has_audio:
            print("  ! 소리가 없는 클립이 있어 원본 오디오는 버립니다 (--audio 로 넣으세요)")
        script = build_xfade_script(plan, dur, a, has_audio)
        spath = work / "transitions.filter"
        spath.write_text(script, encoding="utf-8")
        cut = sum(t for _, t, _ in plan)
        special = [(ids_[i + 1], t, k) for i, (_l, t, k) in enumerate(plan)
                   if k != "fade"] if (ids_ := [sid for sid, _ in matched]) else []
        if special:
            print("  특수 전환 " + ", ".join(f"{c}={k}" for c, _t, k in special[:10])
                  + (" …" if len(special) > 10 else ""))
        print(f"전환 {len(plan)}곳 · " + " · ".join(
            f"{k} {sum(1 for l, _, _ in plan if l == k)}곳" for k in ("연속", "컷", "전환")
            if any(l == k for l, _, _ in plan)) + f" · 겹치는 만큼 {cut:.1f}초 짧아짐")
        cmd = [ffmpeg, "-y"]
        for c in clips:
            cmd += ["-i", str(c)]
        cmd += ["-filter_complex_script", str(spath), "-map", "[vout]"]
        if has_audio:
            cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
        else:
            cmd += ["-an"]
        cmd += ["-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium",
                "-pix_fmt", "yuv420p", str(merged)]
        run(cmd, a.dry_run)

    # 5) 자막은 «이어붙인 결과»를 실제로 재서 만든다.
    #    전환으로 겹치는 만큼 짧아지는데, 그 양을 미리 계산하면 프레임 반올림 때문에
    #    조금씩 어긋난다. 62컷이면 1초 가까이 벌어진다. 그래서 예측하지 않고 잰다.
    import build_subtitles
    ids = [sid for sid, _ in matched]
    adj = dict(durations)
    if not a.no_transitions:
        for i, (_link, sec, _k) in enumerate(plan):       # plan[i] 는 ids[i] 와 ids[i+1] 사이
            sec = max(0.04, min(sec, durations[ids[i + 1]] - 0.1))
            adj[ids[i]] = round(adj[ids[i]] - sec, 3)
    if not a.dry_run and merged.exists():
        real_merged = probe_duration(ffprobe, ffmpeg, merged)
        gap = real_merged - sum(adj.values())
        if abs(gap) > 0.02:                               # 남은 오차를 컷 길이에 고루 나눈다
            k = real_merged / sum(adj.values())
            adj = {i: round(v * k, 3) for i, v in adj.items()}
            print(f"  이어붙인 결과 {real_merged:.2f}초 · 계산값과 {gap:+.2f}초 차이 → 자막을 실측에 맞춤")
    sub_path = work / "durations_render.json"
    sub_path.write_text(json.dumps(adj, ensure_ascii=False, indent=2), encoding="utf-8")
    ass, srt, n, total = build_subtitles.build(ep, durations=sub_path)
    print(f"자막 {n}줄 재생성 (완성본 실측 기준, 전체 {total:.1f}초) → {ass.name}, {srt.name}")

    # 6) 자막 굽기 + 음악
    out = Path(a.out) if a.out else ep / f"{ep.name}.mp4"
    cmd = [ffmpeg, "-y", "-i", str(merged)]
    if a.audio:
        cmd += ["-stream_loop", "-1", "-i", str(a.audio)]
    tail = probe_duration(ffprobe, ffmpeg, merged) if (not a.dry_run and merged.exists()) else 0
    fx = []
    if a.fade_in > 0:
        fx.append(f"fade=t=in:st=0:d={a.fade_in}")
    if a.fade_out > 0 and tail > a.fade_out:
        fx.append(f"fade=t=out:st={tail - a.fade_out:.3f}:d={a.fade_out}")
    if a.no_burn and not fx:
        cmd += ["-c:v", "copy"]
    elif a.no_burn:
        cmd += ["-vf", ",".join(fx), "-c:v", "libx264", "-crf", str(a.crf),
                "-preset", "medium", "-pix_fmt", "yuv420p"]
    else:
        fonts = ROOT / json.loads((ROOT / "subtitle_style.json").read_text(encoding="utf-8")).get("fonts_dir", "fonts")
        # 경로의 : 와 ' 는 filtergraph 에서 이스케이프해야 한다
        esc = lambda s: str(s).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        chain = [f"subtitles='{esc(ass)}':fontsdir='{esc(fonts)}'"] + fx
        cmd += ["-vf", ",".join(chain),
                "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p"]
    if a.audio:
        af = [f"volume={a.music_volume}"]
        if a.fade_in > 0:
            af.append(f"afade=t=in:st=0:d={a.fade_in}")
        if a.fade_out > 0 and tail > a.fade_out:
            af.append(f"afade=t=out:st={tail - a.fade_out:.3f}:d={a.fade_out}")
        cmd += ["-af", ",".join(af),
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
