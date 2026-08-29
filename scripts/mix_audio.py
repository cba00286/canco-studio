#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배정된 소리를 실제 오디오 트랙으로 합친다.

    python3 scripts/mix_audio.py --episode ep12 --list        # 받아야 할 파일 목록
    python3 scripts/mix_audio.py --episode ep12 --check       # 폴더에 뭐가 없는지
    python3 scripts/mix_audio.py --episode ep12 --out ep12_audio.m4a

소리 파일은 이렇게 두면 된다. 이름은 bible/audio.json 의 키와 같아야 한다.

    sound/amb/숲_낮.mp3        환경음  (짧아도 된다. 반복해서 늘린다)
    sound/bgm/일상_밝음.mp3     BGM     (반복해서 늘린다)
    sound/sfx/발소리_풀.wav     효과음  (한 번 나는 소리)
    sound/sig/쿵쿵_파워.wav     능력 소리

없는 파일은 그 자리를 비우고 계속 간다 — 다 모으기 전에도 들어 볼 수 있어야 한다.

말소리(나레이션·대사)를 따로 녹음해 두었으면 --voice 로 넣는다. 그러면
그 소리에 맞춰 BGM 이 자동으로 눌린다(덕킹). 없으면 덕킹 없이 만든다.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = json.loads((ROOT / "bible" / "audio.json").read_text(encoding="utf-8"))

# bible/audio.json 의 mix 값과 맞춘다
GAIN = {"amb": "-30dB", "bgm": "-22dB", "sfx": "-14dB", "sig": "-12dB"}
XFADE = 0.5          # 장면이 바뀔 때 환경음·BGM 크로스페이드
EXTS = (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac")


def find(sound: Path, kind: str, name: str) -> Path | None:
    d = sound / kind
    for ext in EXTS:
        f = d / (name + ext)
        if f.exists():
            return f
    return None


def plan(ep_dir: Path, durations: list[float] | None):
    """장면별 구간과 컷별 효과음 시각을 계산한다."""
    D = json.loads((ep_dir / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))
    shots = D["shots"]
    au = D.get("audio_sections") or {}
    if durations and len(durations) != len(shots):
        sys.exit("--durations 개수(%d)가 컷 수(%d)와 다릅니다." % (len(durations), len(shots)))
    dur = durations or [float(s["duration"]) for s in shots]

    at, cuts, secs = 0.0, [], []
    cur, start = None, 0.0
    for s, d in zip(shots, dur):
        if s["section"] != cur:
            if cur is not None:
                secs.append({"key": cur, "start": start, "end": at, **au.get(cur, {})})
            cur, start = s["section"], at
        cuts.append({"id": s["id"], "at": at, "dur": d,
                     "sfx": s.get("sfx") or [], "sig": s.get("sig")})
        at += d
    secs.append({"key": cur, "start": start, "end": at, **au.get(cur, {})})
    return secs, cuts, at


def needed(secs, cuts):
    want = {"amb": set(), "bgm": set(), "sfx": set(), "sig": set()}
    for s in secs:
        if s.get("amb"):
            want["amb"].add(s["amb"])
        if s.get("weather"):
            want["amb"].add(s["weather"])
        if s.get("bgm"):
            want["bgm"].add(s["bgm"])
    for c in cuts:
        want["sfx"].update(c["sfx"])
        if c["sig"]:
            want["sig"].add(c["sig"])
    return want


def describe(kind: str, name: str) -> str:
    if kind == "amb":
        e = AUDIO["ambience"].get(name, {})
        return "%s  —  %s" % (e.get("소리", ""), e.get("검색어", ""))
    if kind == "bgm":
        e = AUDIO["bgm"].get(name, {})
        return "%s / %s  —  %s" % (e.get("분위기", ""), e.get("템포", ""), e.get("검색어", ""))
    if kind == "sfx":
        e = AUDIO["sfx"].get(name, {})
        return "%s  —  %s" % (e.get("소리", ""), e.get("검색어", ""))
    e = AUDIO["signature"].get(name, {})
    return "%s  —  %s" % (e.get("구성", ""), e.get("검색어", ""))


LABEL = {"amb": "환경음", "bgm": "BGM", "sfx": "효과음", "sig": "능력 소리"}


def print_list(want, sound: Path | None):
    for kind in ("bgm", "amb", "sfx", "sig"):
        names = sorted(want[kind])
        if not names:
            continue
        print("\n[%s] %d개  → sound/%s/" % (LABEL[kind], len(names), kind))
        for n in names:
            mark = ""
            if sound is not None:
                mark = "   ✓" if find(sound, kind, n) else "   ✗ 없음"
            print("  %-16s%s" % (n, mark))
            print("      %s" % describe(kind, n))


def build_filters(secs, cuts, sound: Path, total: float, voice: Path | None):
    """ffmpeg 입력 목록과 filter_complex 를 만든다."""
    inputs, parts, mixes = [], [], []

    def add_input(path: Path, loop: bool) -> int:
        i = len(inputs)
        inputs.append((path, loop))
        return i

    # 환경음 · BGM — 장면 단위로 잘라 놓고 앞뒤로 페이드
    for kind in ("amb", "bgm"):
        for s in secs:
            names = []
            if kind == "amb":
                names = [n for n in (s.get("amb"), s.get("weather")) if n]
            elif s.get("bgm"):
                names = [s["bgm"]]
            for name in names:
                f = find(sound, kind, name)
                if not f:
                    continue
                i = add_input(f, True)
                length = s["end"] - s["start"]
                lab = "%s%d" % (kind, len(mixes))
                parts.append(
                    "[%d:a]atrim=0:%.3f,asetpts=PTS-STARTPTS,"
                    "afade=t=in:st=0:d=%.2f,afade=t=out:st=%.3f:d=%.2f,"
                    "volume=%s,adelay=%d|%d[%s]"
                    % (i, length + XFADE, XFADE, max(0.0, length - XFADE), XFADE,
                       GAIN[kind], int(s["start"] * 1000), int(s["start"] * 1000), lab))
                mixes.append(lab)

    # 효과음 · 능력 소리 — 컷이 시작하는 시각에 한 번씩
    for c in cuts:
        for kind, names in (("sfx", c["sfx"]), ("sig", [c["sig"]] if c["sig"] else [])):
            for name in names:
                f = find(sound, kind, name)
                if not f:
                    continue
                i = add_input(f, False)
                lab = "%s%d" % (kind, len(mixes))
                ms = int(c["at"] * 1000) + (0 if kind == "sig" else 120)  # 효과음은 살짝 늦게
                parts.append("[%d:a]volume=%s,adelay=%d|%d[%s]" % (i, GAIN[kind], ms, ms, lab))
                mixes.append(lab)

    if not mixes:
        return None, None, None

    parts.append("%samix=inputs=%d:normalize=0:duration=longest[bed]"
                 % ("".join("[%s]" % m for m in mixes), len(mixes)))
    last = "bed"

    if voice:
        vi = add_input(voice, False)
        # 말이 나오는 동안 BGM·환경음을 눌러 준다
        parts.append("[%d:a]volume=0dB,asplit=2[v1][vkey]" % vi)
        parts.append("[bed][vkey]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[ducked]")
        parts.append("[ducked][v1]amix=inputs=2:normalize=0:duration=longest[mixed]")
        last = "mixed"

    parts.append("[%s]atrim=0:%.3f,loudnorm=I=-14:TP=-1:LRA=11[out]" % (last, total))
    return inputs, ";".join(parts), "[out]"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episode", default="ep1")
    ap.add_argument("--root", default="episodes")
    ap.add_argument("--sound", default="sound", help="소리 파일 폴더")
    ap.add_argument("--durations", help="실측 길이 (쉼표로 구분). 없으면 대본의 길이를 쓴다")
    ap.add_argument("--voice", help="녹음한 나레이션·대사 파일 (있으면 덕킹한다)")
    ap.add_argument("--out", help="만들 오디오 파일")
    ap.add_argument("--list", action="store_true", help="받아야 할 소리 목록만 본다")
    ap.add_argument("--check", action="store_true", help="폴더에 뭐가 없는지 본다")
    ap.add_argument("--dry-run", action="store_true", help="ffmpeg 명령만 보여 준다")
    a = ap.parse_args()

    ep_dir = ROOT / a.root / a.episode
    if not (ep_dir / "prompts" / "shots_v2.json").exists():
        sys.exit("컷 리스트가 없습니다: %s" % ep_dir)
    durs = [float(x) for x in a.durations.split(",")] if a.durations else None
    secs, cuts, total = plan(ep_dir, durs)
    want = needed(secs, cuts)
    sound = ROOT / a.sound

    print("[%s] %d장면 · %d컷 · %.1f초" % (a.episode, len(secs), len(cuts), total))
    for s in secs:
        w = " + %s" % s["weather"] if s.get("weather") else ""
        print("  %-4s %6.1f~%6.1f초   환경음 %s%s   BGM %s"
              % (s["key"], s["start"], s["end"], s.get("amb", "-"), w, s.get("bgm", "-")))

    if a.list or a.check:
        print_list(want, sound if a.check else None)
        if a.check:
            miss = [(k, n) for k in want for n in sorted(want[k]) if not find(sound, k, n)]
            print("\n%d개 중 %d개가 없습니다." % (sum(len(v) for v in want.values()), len(miss)))
        return 0

    if not a.out:
        print("\n--out 을 주면 실제로 합칩니다. 먼저 --list 로 목록을 받으세요.")
        return 0

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg 를 찾을 수 없습니다.")
    inputs, fc, out_lab = build_filters(secs, cuts, sound,
                                        total, Path(a.voice) if a.voice else None)
    if not inputs:
        sys.exit("쓸 수 있는 소리 파일이 하나도 없습니다. --check 로 확인하세요.")

    cmd = [ffmpeg, "-y"]
    for path, loop in inputs:
        if loop:
            cmd += ["-stream_loop", "-1"]
        cmd += ["-i", str(path)]
    script = ROOT / "episodes" / a.episode / "render" / "audio_filter.txt"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(fc, encoding="utf-8")
    cmd += ["-filter_complex_script", str(script), "-map", out_lab,
            "-c:a", "aac", "-b:a", "192k", str(a.out)]

    print("\n입력 %d개 · 필터 %d글자" % (len(inputs), len(fc)))
    if a.dry_run:
        print(" ".join(cmd))
        return 0
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        print(r.stderr[-2500:], file=sys.stderr)
        return r.returncode
    print("작성:", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
