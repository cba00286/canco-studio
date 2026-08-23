#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""제작 자료실 페이지에서 고친 내용을 저장소 JSON으로 되돌린다.

페이지 편집은 빠른 메모이고, 원본은 저장소 JSON이다. 페이지에서 고친 것이
JSON으로 돌아오지 않으면 다음 빌드에서 되돌아가 버린다.

    # 1. 배포된 페이지의 현재 HTML을 받는다 (Artifact 도구 action:"read")
    # 2. 파일로 저장한 뒤
    python3 scripts/sync_from_page.py 받은파일.html            # 미리보기만
    python3 scripts/sync_from_page.py 받은파일.html --write    # 실제로 반영

되돌리는 대상은 data-field 이름표가 붙은 칸뿐이다. 표(집·대사·구성)와
새로 만든 에피소드 카드는 사람이 판단해야 하므로 건드리지 않고 알려만 준다.
"""
import argparse, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELDS = ["ko", "mbti", "mbti_ko", "height", "role", "look",
          "personality", "voice", "dream", "fear", "likes", "dislikes", "habit",
          "home.name", "home.enSize", "home.desc", "home.tie"]
EP_FIELDS = ["no", "title", "runtime", "status", "logline"]
# characters.json 안에서의 위치
AT = {"mbti": ("profile", "mbti"), "mbti_ko": ("profile", "mbti_ko"), "role": (None, "role"),
      "personality": ("profile", "personality"), "voice": ("profile", "voice"),
      "dream": ("profile", "dream"), "fear": ("profile", "fear"), "likes": ("profile", "likes"),
      "dislikes": ("profile", "dislikes"), "habit": ("profile", "habit"),
      "home.name": ("home", "name"), "home.desc": ("home", "desc"), "home.tie": ("home", "tie")}

def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def cards(page):
    """캐릭터 카드마다 {필드: 값} 을 뽑는다."""
    out = {}
    for m in re.finditer(r'<article class="card [^"]*" data-key="([^"]+)">(.*?)</article>', page, re.S):
        key, body = m.group(1), m.group(2)
        out[key] = {f: strip(v) for f, v in re.findall(r'data-field="([\w.]+)"[^>]*>(.*?)</', body, re.S)}
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="배포된 페이지에서 받은 HTML 파일")
    ap.add_argument("--episode", default="ep1")
    ap.add_argument("--write", action="store_true", help="실제로 JSON에 반영한다")
    a = ap.parse_args()

    page = pathlib.Path(a.page).read_text(encoding="utf-8")
    P = ROOT / "episodes" / a.episode / "prompts"
    C = json.loads((P / "characters.json").read_text(encoding="utf-8"))
    L = json.loads((P / "looks.json").read_text(encoding="utf-8"))
    EPF = ROOT / "episodes" / a.episode / "episode.json"
    E = json.loads(EPF.read_text(encoding="utf-8"))

    changes = []
    for key, got in cards(page).items():
        if key not in C["characters"]:
            changes.append(("?", key, "저장소에 없는 캐릭터 — 무시", "", ""))
            continue
        c = C["characters"][key]
        for f, new in got.items():
            if f == "look":
                old = L.get(key, "")
                if new and new != old:
                    changes.append(("looks.json", key, f, old, new)); L[key] = new
            elif f == "height":
                old, num = c.get("height"), re.sub(r"[^\d]", "", new)
                if num and int(num) != old:
                    changes.append(("characters.json", key, f, old, int(num))); c["height"] = int(num)
            elif f in AT:
                sub, name = AT[f]
                tgt = c[sub] if sub else c
                if new and new != tgt.get(name):
                    changes.append(("characters.json", key, f, tgt.get(name), new)); tgt[name] = new
            elif f in ("ko", "home.enSize"):
                pass   # 표시용 — 되돌리지 않는다

    for f, v in re.findall(r'data-field="(no|title|runtime|status|logline)"[^>]*>(.*?)</', page, re.S):
        v = strip(v)
        if v and v != E.get(f):
            changes.append(("episode.json", a.episode, f, E.get(f), v)); E[f] = v

    extra = len(re.findall(r'class="epi" data-key="ep-\d+"', page))
    if not changes and not extra:
        print("바뀐 것 없음."); return
    for src, who, f, old, new in changes:
        print("\n[%s] %s · %s" % (src, who, f))
        print("  전: %s" % (str(old)[:90] if old else "(없음)"))
        print("  후: %s" % str(new)[:90])
    if extra:
        print("\n! 페이지에서 새로 만든 에피소드 카드 %d개는 자동 반영하지 않습니다." % extra)
        print("  episodes/<ep>/ 를 직접 만들고 episode.json 과 shots_v2.json 을 채우세요.")
    if not a.write:
        print("\n미리보기입니다. 반영하려면 --write 를 붙이세요. (%d건)" % len(changes)); return
    (P / "characters.json").write_text(json.dumps(C, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (P / "looks.json").write_text(json.dumps(L, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    EPF.write_text(json.dumps(E, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n%d건 반영했습니다. build_ref_prompts.py 와 site/build.py 를 다시 돌리세요." % len(changes))

if __name__ == "__main__":
    main()
