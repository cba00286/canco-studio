#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OST 폴더에 무엇이 들어왔는지 확인한다.

    python3 scripts/check_ost.py            # ep1
    python3 scripts/check_ost.py ep2

파일 이름은 강제하지 않는다. ost.json 의 slug 또는 제목이 이름에 들어 있으면 찾는다.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EP = sys.argv[1] if len(sys.argv) > 1 else "ep1"
OST = ROOT / "episodes" / EP / "assets" / "ost"
EXT = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def norm(s):
    return re.sub(r"[\s_\-()\[\]!?.,·]+", "", s).lower()


def main():
    meta = json.loads((OST / "ost.json").read_text(encoding="utf-8"))
    files = sorted(p for p in OST.iterdir() if p.suffix.lower() in EXT) if OST.is_dir() else []
    used, missing, dupes = set(), [], []

    print("\n[%s] OST — 음원 %d개\n" % (EP, len(files)))
    for t in meta["tracks"]:
        words = [norm(t["slug"]), norm(t["title"])]
        hits = [p for p in files if any(w and w in norm(p.stem) for w in words)]
        if hits:
            used.update(hits)
            mb = hits[0].stat().st_size / 1e6
            print("  ✓ %-14s %-34s %.1fMB" % (t["slug"], hits[0].name, mb))
            if len(hits) > 1:
                dupes.append((t["slug"], hits))
        else:
            missing.append(t)
            print("  · %-14s %-34s %s" % (t["slug"], "(없음)", t["status"]))

    for slug, hits in dupes:
        print("\n  ! %s 후보가 %d개입니다 — 위의 첫 번째를 씁니다:" % (slug, len(hits)))
        for p in hits:
            print("      %s" % p.name)
        print("    쓰지 않을 파일은 이름에서 곡 제목을 빼거나 폴더 밖으로 옮기세요.")

    extra = [p for p in files if p not in used]
    if extra:
        print("\n  ! 어느 곡인지 못 맞춘 파일:")
        for p in extra:
            print("      %s" % p.name)
        print("    ost.json 의 slug 나 제목을 파일 이름에 넣거나, ost.json 에 트랙을 추가하세요.")

    print("\n%d / %d 확보" % (len(meta["tracks"]) - len(missing), len(meta["tracks"])))
    if missing:
        print("남은 곡: %s" % ", ".join(t["title"] for t in missing))


if __name__ == "__main__":
    main()
