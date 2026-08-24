#!/usr/bin/env python3
"""shots_v2.json 의 대사에서 자막 파일을 만든다.

  .ass  화면에 굽는 용도. 테두리 색/두께, 폰트, 위치를 전부 지정할 수 있다.
  .srt  유튜브 업로드용. 시청자가 켜고 끌 수 있다.

컷 길이는 기본적으로 shots_v2.json 의 duration 을 쓴다. 실제 생성된 클립의
길이가 규격과 다를 수 있으므로, render_episode.py 가 측정한 실측 길이 파일을
--durations 로 넘기면 그쪽을 우선한다. 60컷이면 컷당 0.2초 오차만 나도
마지막에 12초가 밀린다.

  python3 scripts/build_subtitles.py --episode episodes/ep1
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ass_color(hex_rgb, alpha=0):
    """#RRGGBB -> &HAABBGGRR&  (ASS 는 BGR 순서, alpha 는 0=불투명)"""
    h = hex_rgb.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def wrap_ko(text, max_chars, max_lines):
    """한국어 자막 줄바꿈. 어절 단위로 끊고, 한 어절이 너무 길면 강제로 자른다."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    # 어절 하나가 max_chars 를 넘으면 잘라준다
    out = []
    for ln in lines:
        while len(ln) > max_chars:
            out.append(ln[:max_chars])
            ln = ln[max_chars:]
        out.append(ln)

    if len(out) > max_lines:
        # 줄 수를 넘으면 최대한 균등하게 다시 나눈다
        joined = " ".join(out)
        per = max(1, -(-len(joined) // max_lines))
        out = [joined[i:i + per] for i in range(0, len(joined), per)][:max_lines]
    return out


def ts_ass(sec):
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def ts_srt(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def escape_ass(text):
    # ASS 는 { } 를 오버라이드 태그로 읽는다
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def style_line(name, s):
    """ASS V4+ Style 한 줄. 필드 순서는 ASS 규격 고정."""
    return ",".join(str(x) for x in [
        f"Style: {name}",
        s["font"],
        s["size"],
        ass_color(s["fill"]),
        ass_color(s["fill"]),                                   # Secondary (카라오케용, 안 씀)
        ass_color(s["outline"]),                                # ← 테두리 색
        ass_color(s.get("shadow_color", "#000000"), s.get("shadow_alpha", 128)),
        -1 if s.get("bold") else 0,
        -1 if s.get("italic") else 0,
        0, 0,                                                   # Underline, StrikeOut
        100, 100, 0, 0,                                         # ScaleX, ScaleY, Spacing, Angle
        1,                                                      # BorderStyle 1 = 외곽선+그림자
        s["outline_width"],                                     # ← 테두리 두께
        s.get("shadow", 0),
        s.get("align", 2),
        s.get("margin_h", 100), s.get("margin_h", 100),
        s.get("margin_v", 70),
        1,                                                      # Encoding
    ])


def build(episode_dir, durations=None, out_dir=None, style_path=None):
    ep = Path(episode_dir)
    shots = json.loads((ep / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))["shots"]
    cfg = json.loads((style_path or (ROOT / "subtitle_style.json")).read_text(encoding="utf-8"))
    styles = cfg["styles"]
    timing = cfg.get("timing", {})
    lead_in = timing.get("lead_in_sec", 0.0)
    lead_out = timing.get("lead_out_sec", 0.0)
    min_dur = timing.get("min_duration_sec", 0.8)
    label_on = cfg.get("speaker_label", {}).get("enabled", False)

    measured = {}
    if durations:
        measured = json.loads(Path(durations).read_text(encoding="utf-8"))

    events, srt, t = [], [], 0.0
    n = 0
    for sh in shots:
        dur = float(measured.get(sh["id"], sh.get("duration", 0)))
        line = (sh.get("dialogue") or "").strip()
        speaker = (sh.get("speaker") or "").strip()
        if line:
            st = t + lead_in
            en = max(st + min_dur, t + dur - lead_out)
            key = "나레이션" if speaker == "나레이션" else "대사"
            s = styles[key]
            text = line
            if label_on and speaker and speaker != "나레이션":
                text = f"{speaker}: {line}"
            wrapped = wrap_ko(text, s["max_chars_per_line"], s["max_lines"])
            events.append(
                f"Dialogue: 0,{ts_ass(st)},{ts_ass(en)},{key},{speaker},0,0,0,,"
                + escape_ass("\\N".join(wrapped)).replace("\\\\N", "\\N")
            )
            n += 1
            srt.append(f"{n}\n{ts_srt(st)} --> {ts_srt(en)}\n" + "\n".join(wrapped) + "\n")
        t += dur

    W, H = cfg["video"]["width"], cfg["video"]["height"]
    ass = "\n".join([
        "[Script Info]",
        "; 쿵쿵이와 친구들 — scripts/build_subtitles.py 가 생성함. 직접 고치지 말 것.",
        "ScriptType: v4.00+", "WrapStyle: 2", "ScaledBorderAndShadow: yes",
        f"PlayResX: {W}", f"PlayResY: {H}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        *[style_line(k, v) for k, v in styles.items()], "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        *events, "",
    ])

    od = Path(out_dir) if out_dir else ep / "subtitles"
    od.mkdir(parents=True, exist_ok=True)
    name = ep.name
    (od / f"{name}.ass").write_text(ass, encoding="utf-8")
    (od / f"{name}.srt").write_text("\n".join(srt), encoding="utf-8")
    return od / f"{name}.ass", od / f"{name}.srt", n, t


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episode", required=True)
    p.add_argument("--durations", help="render_episode.py 가 만든 실측 길이 JSON")
    p.add_argument("--out")
    p.add_argument("--style")
    a = p.parse_args()
    ass, srt, n, total = build(a.episode, a.durations, a.out, Path(a.style) if a.style else None)
    src = "실측" if a.durations else "규격(duration)"
    print(f"자막 {n}줄 · 전체 {total:.1f}초 ({int(total//60)}분 {total%60:.0f}초) · 길이 기준: {src}")
    print(f"  {ass}")
    print(f"  {srt}")


if __name__ == "__main__":
    sys.exit(main())
