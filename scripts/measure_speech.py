#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""컷 클립에서 «말이 실제로 언제 시작해서 언제 끝나는지» 를 잰다.

자막 시작·끝을 컷 길이에서 눈대중으로 계산하면 반드시 어긋난다. 생성기는
컷 앞뒤에 숨 쉬는 여백을 제멋대로 남기기 때문에, 4초 컷에서 말이 0.9초에
시작해 2.8초에 끝나는 일이 흔하다. 그런 컷에 0.08초부터 3.88초까지 자막을
띄우면 말보다 1초 먼저 뜨고 1초 늦게 사라진다.

그래서 클립의 소리를 직접 재서 말 구간을 찾는다. 음성 인식까지 갈 것도 없이
ffmpeg 의 silencedetect 로 «조용하지 않은 구간» 을 뽑으면 충분하다 —
프롬프트에 «배경음악 없이» 를 넣어 두었으므로 클립에서 소리가 나는 구간은
사실상 말과 효과음뿐이다.

    python3 scripts/measure_speech.py --episode episodes/ep1 --clips ~/쿵쿵이/1화클립
    python3 scripts/build_subtitles.py --episode episodes/ep1 --speech episodes/ep1/work/speech.json

대사가 없는 컷은 재지 않는다. 소리가 아예 안 잡힌 컷은 결과에서 빠지고,
build_subtitles.py 가 그 컷만 기존 방식(컷 길이 기준)으로 되돌린다.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_episode import find_ffmpeg, match_clips, probe_duration   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def speech_span(ffmpeg, path, dur, noise_db, min_silence):
    """클립에서 소리가 나는 첫 지점과 마지막 지점을 (시작, 끝) 으로 돌려준다."""
    out = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path), "-af",
         "silencedetect=noise=%ddB:d=%.2f" % (noise_db, min_silence),
         "-f", "null", "-"], capture_output=True, text=True).stderr

    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", out)]

    # 무음 구간의 «사이» 가 소리 나는 구간이다.
    lo = ends[0] if ends and (not starts or ends[0] < starts[0]) else 0.0
    if starts and starts[0] <= 0.05 and ends:
        lo = ends[0]                       # 클립이 무음으로 시작한다
    hi = dur
    if starts and (not ends or starts[-1] > ends[-1]):
        hi = starts[-1]                    # 클립이 무음으로 끝난다
    if hi - lo < 0.3:                      # 소리를 못 찾았다 — 이 컷은 건너뛴다
        return None
    return round(lo, 3), round(hi, 3)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--episode", required=True, help="episodes/ep1 또는 shorts/C01")
    p.add_argument("--clips", required=True, help="컷 클립이 들어있는 폴더")
    p.add_argument("--out", help="기본은 <episode>/work/speech.json")
    p.add_argument("--noise-db", type=int, default=-40,
                   help="이보다 조용하면 무음으로 본다 (기본 -40dB)")
    p.add_argument("--min-silence", type=float, default=0.25,
                   help="이보다 짧은 무음은 무시한다 (기본 0.25초)")
    a = p.parse_args()

    ep = Path(a.episode)
    shots = json.loads((ep / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))["shots"]
    talking = {s["id"] for s in shots
               if (s.get("dialogue") or "").strip() and s.get("speaker") != "나레이션"}
    if not talking:
        sys.exit("이 화에는 화면 안 인물의 대사가 없습니다 — 잴 것이 없습니다.")

    ffmpeg, ffprobe = find_ffmpeg("ffmpeg"), find_ffmpeg("ffprobe")
    matched, missing = match_clips(shots, a.clips)
    spans, quiet = {}, []
    for sid, path in matched:
        if sid not in talking:
            continue
        dur = probe_duration(ffprobe, ffmpeg, path)
        span = speech_span(ffmpeg, path, dur, a.noise_db, a.min_silence)
        if span:
            spans[sid] = span
        else:
            quiet.append(sid)

    out = Path(a.out) if a.out else ep / "work" / "speech.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spans, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("대사 컷 %d개 중 %d개에서 말 구간을 찾았습니다 → %s"
          % (len(talking), len(spans), out))
    if quiet:
        print("! 소리가 잡히지 않은 컷 %d개 — 이 컷은 자막이 컷 길이 기준으로 붙습니다: %s"
              % (len(quiet), ", ".join(quiet)))
        print("  대사가 정말 안 들어갔는지 클립을 직접 들어보세요. "
              "프롬프트가 영어면 생성기가 대사를 통째로 건너뜁니다.")
    absent = sorted(talking - {s for s, _ in matched})
    if absent:
        print("! 클립이 없는 대사 컷: %s" % ", ".join(absent))


if __name__ == "__main__":
    sys.exit(main())
