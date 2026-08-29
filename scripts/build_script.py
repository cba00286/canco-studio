#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""컷 리스트에서 대본집을 만든다. 이것 하나로 한 화를 만들 수 있게.

컷마다 화면 설명 · 대사 · 카메라 · 컷 연결 · 영문 프롬프트(이미지/영상)가
다 들어간다. 화 끝에는 대사만 모은 녹음용 표가 붙는다.

    python3 scripts/build_script.py                 # 1~10화, 프롬프트 포함
    python3 scripts/build_script.py --no-prompts    # 읽기용(대사와 설명만)
    python3 scripts/build_script.py ep2 ep3         # 골라서
"""
import argparse
import json
import sys
from pathlib import Path

import bible

ROOT = Path(__file__).resolve().parent.parent


def load(ep):
    d = ROOT / "episodes" / ep
    return (json.loads((d / "episode.json").read_text(encoding="utf-8")),
            json.loads((d / "prompts" / "shots_v2.json").read_text(encoding="utf-8")))


def mmss(sec):
    return "%d분 %02d초" % (int(sec) // 60, int(sec) % 60)


def episode_block(meta, doc, morals, prompts):
    S = doc["shots"]
    total = sum(x["duration"] for x in S)
    cast = doc.get("episode_cast") or sorted({c for x in S for c in x["cast"]})
    narr = sum(1 for x in S if x["dialogue"] and x["speaker"] == "나레이션")
    char = sum(1 for x in S if x["dialogue"] and x["speaker"] != "나레이션")

    o = ["\n\n---\n\n# %s %s\n" % (meta["no"], meta["title"]),
         "> %s\n" % meta["logline"]]
    if meta.get("note"):
        o.append("*%s*\n" % meta["note"])
    o += ["| | |", "|---|---|",
          "| 러닝타임 | %s (%d초) |" % (mmss(total), total),
          "| 컷 | %d컷 |" % len(S),
          "| 등장 | %s |" % ", ".join(cast)]
    if morals.get(meta["no"]):
        o.append("| 교훈 | %s |" % morals[meta["no"]])
    o.append("| 대사 | 나레이션 %d줄 · 캐릭터 %d줄 |" % (narr, char))
    if prompts:
        o.append("| 네거티브 | %s |" % ("공통 + 실외전용" if "실외전용" in (doc.get("negative_extras") or [])
                                        else "공통만 (실내 컷이 있어 실외전용을 붙이지 마세요)"))
    o.append("")

    cur = None
    for x in S:
        if x["section"] != cur:
            cur = x["section"]
            o.append("\n## %s\n" % doc["sections"][cur])
            au = (doc.get("audio_sections") or {}).get(cur)
            if au:
                w = (" + %s" % au["weather"]) if au.get("weather") else ""
                o.append("`소리` **환경음** %s%s &nbsp;·&nbsp; **BGM** %s\n"
                         % (au["amb"], w, au["bgm"]))
        who = ", ".join(x["cast"]) if x["cast"] else "배경"
        o.append("**%s**  `%d초 · %s · %s · %s · seed %d`\n"
                 % (x["id"], x["duration"], x["shot_ko"], x.get("link", ""), who, x["seed"]))
        if x.get("link_ko"):
            note = x["link_ko"]
            if x.get("link") == "연속":
                note += " **앞 컷 영상의 마지막 프레임을 이 컷의 시작 프레임으로 넣으세요.**"
            o.append("*연결 — %s*\n" % note)
        o.append("%s\n" % x["ko"])
        o.append("*카메라 — %s*\n" % x["ko_motion"])
        if x["dialogue"]:
            o.append("> **%s**  %s\n" % (x["speaker"], x["dialogue"]))
        bits = []
        if x.get("sig"):
            bits.append("**능력 소리 %s**" % x["sig"])
        if x.get("sfx"):
            bits.append("효과음 " + " · ".join(x["sfx"]))
        if bits:
            o.append("*소리 — %s*\n" % " / ".join(bits))
        elif x["shot_ko"] == "타이틀":
            o.append("*소리 — 엔딩 타이틀 음악만. 환경음도 효과음도 넣지 마세요.*\n")
        if x.get("transition"):
            t = x["transition"]
            o.append("*전환 효과 — `%s` %s초. %s*\n" % (t["type"], t["sec"], t.get("why", "")))
        if prompts:
            o.append("<details><summary>영문 프롬프트</summary>\n")
            o.append("**이미지**\n")
            o.append("```\n%s\n```\n" % x["image_ref"])
            o.append("**영상**\n")
            o.append("```\n%s\n```\n" % (x.get("motion_ref") or x["motion"]))
            o.append("</details>\n")

    o.append("\n### %s 대사 전체 — 녹음용\n" % meta["no"])
    o.append("나레이션은 화면 밖 목소리라 립싱크가 필요 없고, 캐릭터 대사만 입을 맞춥니다. "
             "순서대로 읽으면 이 화 전체가 됩니다.\n")
    o += ["| 컷 | 화자 | 대사 |", "|---|---|---|"]
    for x in S:
        if x["dialogue"]:
            o.append("| `%s` | %s | %s |" % (x["id"], x["speaker"], x["dialogue"]))
    return "\n".join(o)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("episodes", nargs="*")
    p.add_argument("--out", default="docs/대본_시즌1.md")
    p.add_argument("--no-prompts", action="store_true",
                   help="영문 프롬프트를 빼고 읽기용으로만 만든다")
    a = p.parse_args()

    eps = a.episodes or ["ep%d" % i for i in range(1, 11)]
    eps = [e for e in eps if (ROOT / "episodes" / e / "prompts" / "shots_v2.json").exists()]
    if not eps:
        sys.exit("만들 에피소드가 없습니다.")

    chars = json.loads((ROOT / "bible" / "characters.json").read_text(encoding="utf-8"))
    all_eps = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))["episodes"]
    morals = {"%d화" % e["no"]: e.get("moral", "") for e in all_eps}

    blocks, rows, grand, cuts = [], [], 0, 0
    for e in eps:
        meta, doc = load(e)
        total = sum(x["duration"] for x in doc["shots"])
        grand += total
        cuts += len(doc["shots"])
        lines = sum(1 for x in doc["shots"] if x["dialogue"])
        rows.append("| %s | %s | %s | %d컷 | %d줄 | %s |"
                    % (meta["no"], meta["title"], mmss(total), len(doc["shots"]), lines,
                       ", ".join(doc.get("episode_cast") or [])))
        blocks.append(episode_block(meta, doc, morals, not a.no_prompts))

    nos = sorted(int(e[2:]) for e in eps)
    season = (nos[0] - 1) // 10 + 1
    head = ["# 쿵쿵이와 친구들 — 시즌 %d 대본집" % season, "",
            "%d화부터 %d화까지, 컷마다 화면에 담길 내용과 대사를 그대로 옮긴 것입니다." % (nos[0], nos[-1]),
            "전체 **%s** · %d화 · %d컷." % (mmss(grand), len(eps), cuts), ""]
    if not a.no_prompts:
        head += ["컷마다 «영문 프롬프트»를 펼치면 이미지·영상 프롬프트가 그대로 나옵니다. "
                 "그것만 복사해 생성기에 붙여 넣으면 됩니다.", ""]
    head += ["화마다 끝에 **대사만 모은 표**가 있습니다. 녹음할 때 그 표만 보시면 됩니다.", "",
             "이 문서는 `scripts/build_script.py` 가 컷 리스트에서 자동으로 만듭니다. "
             "여기를 고치지 마시고 컷 리스트를 고친 뒤 다시 돌리세요 — 안 그러면 어긋납니다.", ""]
    if not a.no_prompts:
        head += [
            "## 만들기 전에", "",
            "**캐릭터는 트리거 워드로 고정됩니다.** 프롬프트 안의 한글 이름(쿵쿵 · 루카 · 미미 · "
            "티니 · 후안 · 루비 · 노을)이 OpenArt Characters 에 등록한 트리거 워드입니다. "
            "**외모를 따로 적지 마세요** — 적는 순간 등록된 얼굴을 덮어씁니다.", "",
            "**화면비는 프롬프트가 아니라 생성 화면의 설정입니다.** 본편은 16:9 로 맞춰 두세요. "
            "프롬프트에 적힌 `16:9 cinematic composition` 은 구도 힌트일 뿐 캔버스 크기를 바꾸지 않습니다.", "",
            "**「연속」 이라고 표시된 컷**은 앞 컷 영상의 마지막 프레임을 시작 프레임으로 넣으면 "
            "이음매가 사라집니다. `scripts/chain_frames.py` 가 그 프레임을 뽑아 줍니다. "
            "얼굴 레퍼런스와 혼동하지 마세요 — 얼굴은 언제나 트리거 워드로 잡습니다.", "",
            "**클립은 4~5초를 넘기지 마세요.** image2video 는 그 이상에서 얼굴이 무너집니다.", "",
            "**소리는 네 겹입니다.** 장면마다 «환경음»과 «BGM»이 적혀 있고, 컷마다 «효과음»이 "
            "적혀 있습니다. 환경음은 장면 내내 끊지 마세요 — 컷마다 끊으면 이어 붙인 티가 "
            "가장 크게 납니다. 무엇을 어디서 구하는지는 `bible/audio.json` 과 "
            "`docs/17_소리.md` 에 있습니다.", "",
            "**네거티브 프롬프트** — 아래가 전 화 공통입니다. 한 번 복사해서 계속 쓰세요.", "",
            "```", chars["negative_prompt"], "```", "",
            "밖에서만 벌어지는 화에는 아래를 **뒤에 이어 붙이세요.** 실내가 나오는 화에는 붙이면 안 됩니다 "
            "— 붙이면 그 화의 실내 컷과 싸웁니다. 어느 화에 붙이는지는 화마다 머리에 적어 두었습니다.", "",
            "```", chars.get("negative_prompt_extras", {}).get("실외전용", ""), "```", ""]
    head += ["| 화 | 제목 | 길이 | 컷 | 대사 | 등장 |", "|---|---|---|---|---|---|", *rows, ""]

    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(head) + "".join(blocks) + "\n", encoding="utf-8")
    print("작성: %s  %d KB · %d화 · %d컷 · 전체 %s"
          % (out, out.stat().st_size // 1024, len(eps), cuts, mmss(grand)))


if __name__ == "__main__":
    sys.exit(main())
