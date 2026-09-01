#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""창작 이력 증빙 팩을 만든다 — 저작권 등록 신청서에 첨부할 자료.

저작권은 만든 순간 자동으로 생긴다. 등록은 권리를 만드는 절차가 아니라
**«내가 언제 무엇을 만들었는지»를 다투게 됐을 때 쓰는 증거**를 미리 확보하는
절차다. 그래서 이 문서의 핵심은 예쁜 설명이 아니라 **날짜와 해시**다.

이 저장소는 커밋마다 GitHub 서버가 시각을 찍어 두었으므로, 제3자가 보관하는
시계열 기록이 이미 있다. 여기서 그걸 사람이 읽을 수 있는 표로 뽑아낸다.

**AI 생성 부분을 반드시 구분해서 적는다.** 한국 저작권법은 인간의 창작적
기여가 있어야 저작물로 본다. 프롬프트만 넣어서 나온 그림은 등록해도 그 부분이
제외되므로, 처음부터 «사람이 쓴 것»과 «생성기가 뽑은 것»을 갈라 두어야
등록이 반려되지 않고 분쟁에서도 다툴 자리가 분명해진다.

    python3 scripts/build_ip_pack.py            # ip/ 에 md + html
    python3 scripts/build_ip_pack.py --pdf      # PDF 까지 (libreoffice 필요)
"""
import argparse
import html
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ip"


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return r.stdout.strip()


def first_commit_touching(path):
    """그 경로가 저장소에 처음 들어온 날."""
    out = git("log", "--diff-filter=A", "--format=%ad|%H", "--date=short", "--", str(path))
    return out.splitlines()[-1].split("|") if out else ("", "")


def first_commit_mentioning(word, path="."):
    """그 낱말이 저장소에 처음 나타난 날."""
    out = git("log", "-S", word, "--format=%ad|%H", "--date=short", "--reverse", "--", path)
    return out.splitlines()[0].split("|") if out else ("", "")


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def collect():
    chars = load("bible/characters.json")
    order = ["쿵쿵", "루카", "후안", "미미", "티니", "루비", "노을"]

    d = {"생성일": date.today().isoformat()}
    d["원격"] = git("config", "--get", "remote.origin.url")
    first = git("log", "--format=%ad|%H", "--date=short", "--reverse").splitlines()
    last = git("log", "-1", "--format=%ad|%H", "--date=short")
    d["최초커밋"] = first[0].split("|") if first else ("", "")
    d["최신커밋"] = last.split("|")
    d["커밋수"] = git("rev-list", "--count", "HEAD")

    d["캐릭터"] = []
    for n in order:
        e = chars["characters"][n]
        day, h = first_commit_mentioning(n, "bible")
        if not day:                       # 바이블로 옮기기 전에 1화 폴더에 있었다
            day, h = first_commit_mentioning(n)
        d["캐릭터"].append({
            "이름": n, "역할": e.get("role", ""), "키": e.get("height"),
            "성격": (e.get("profile") or {}).get("personality", ""),
            "목소리": (e.get("profile") or {}).get("voice", ""),
            "꿈": (e.get("profile") or {}).get("dream", ""),
            "두려움": (e.get("profile") or {}).get("fear", ""),
            "mbti": (e.get("profile") or {}).get("mbti", ""),
            "집": (e.get("home") or {}).get("name", ""),
            "외형": e.get("look_ko", ""),
            "최초기록": day, "커밋": h[:10],
        })

    d["에피소드"] = []
    for i in range(1, 41):
        ep = ROOT / "episodes" / f"ep{i}"
        if not ep.exists():
            continue
        meta = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
        shots = json.loads((ep / "prompts" / "shots_v2.json").read_text(encoding="utf-8"))["shots"]
        day, h = first_commit_touching(ep)
        d["에피소드"].append({
            "번호": meta.get("no", f"{i}화"), "제목": meta.get("title", ""),
            "로그라인": meta.get("logline", ""),
            "컷": len(shots), "초": sum(s["duration"] for s in shots),
            "대사": sum(1 for s in shots if s.get("dialogue")),
            "최초기록": day, "커밋": h[:10],
        })

    d["쇼츠"] = []
    for p in sorted((ROOT / "shorts").iterdir()):
        if not (p / "short.json").exists():
            continue
        m = json.loads((p / "short.json").read_text(encoding="utf-8"))
        day, h = first_commit_touching(p)
        d["쇼츠"].append({"id": m["id"], "종류": m.get("kind", ""), "제목": m.get("title", ""),
                        "초": m.get("runtime_sec"), "컷": m.get("cuts"),
                        "최초기록": day, "커밋": h[:10]})

    d["합계"] = {
        "화": len(d["에피소드"]),
        "본편컷": sum(e["컷"] for e in d["에피소드"]),
        "본편초": sum(e["초"] for e in d["에피소드"]),
        "쇼츠": len(d["쇼츠"]),
        "쇼츠컷": sum(s["컷"] or 0 for s in d["쇼츠"]),
        "대사": sum(e["대사"] for e in d["에피소드"]),
    }
    return d


# ── AI 사용 구분 ────────────────────────────────────────────────────────
# 등록 신청서에 그대로 옮겨 적을 표다. 여기서 «사람»으로 분류한 것만이
# 등록 대상이고, «생성기»는 등록에서 빠진다.
AI표 = [
    ("캐릭터 이름·성격·MBTI·목소리·꿈·두려움·버릇", "사람", "설정을 글로 썼다. 생성기는 관여하지 않았다"),
    ("캐릭터 키 도감·집 구조·평면 치수", "사람", "숫자와 구조를 직접 정했다"),
    ("세계관(숲속마을·해변마을)과 능력 체계 5종", "사람", "규칙을 직접 설계했다"),
    ("40화 줄거리·주제·교훈", "사람", "이야기를 직접 썼다"),
    ("전 컷의 대사", "사람", "한 줄씩 직접 썼다"),
    ("컷 분할과 컷 연결 설계(연속/컷/전환)", "사람", "몇 초짜리 몇 컷으로 나눌지 직접 정했다"),
    ("장면별 소리 설계(효과음·환경음·BGM 배치)", "사람", "규칙을 정하고 배정 결과를 검수했다"),
    ("자막 스타일과 타이밍", "사람", "직접 정하고 실측으로 맞췄다"),
    ("컷 프롬프트 문안", "사람", "직접 작성했다. 다만 아래 산출물의 저작물성은 별개다"),
    ("캐릭터 마스터 시트 이미지", "생성기", "OpenArt 로 생성. 사람이 고르고 수정한 범위만 주장한다"),
    ("컷 키프레임 이미지", "생성기", "OpenArt 로 생성"),
    ("컷 영상 클립", "생성기", "OpenArt image2video 로 생성"),
    ("클립 안의 목소리·효과음", "생성기", "생성 시 함께 만들어진다"),
    ("이어붙이기·자막 굽기·소리 믹싱", "사람", "저장소의 스크립트로 직접 처리한다"),
]

등록단위 = [
    ("㉠ 캐릭터 바이블", "어문저작물",
     "7종의 이름·성격·목소리·꿈·두려움·버릇·집 구조·키 도감·세계관·능력 체계",
     "가장 강하다. 순수 저술이고 AI 산출물이 섞이지 않았다"),
    ("㉡ 40화 시나리오", "어문저작물",
     "40화 줄거리와 전 컷 대사, 쇼츠 22편",
     "강하다. 캐릭터 이름을 바꿔 베껴도 이야기 구조로 다툴 수 있다"),
    ("㉢ 컷 구성표", "편집저작물",
     "화별 컷 분할·길이·연결·구도·소리 배치",
     "소재의 선택과 배열에 창작성이 있다. 컷 시트가 그대로 증거다"),
    ("㉣ 캐릭터 마스터 시트", "미술저작물",
     "7종의 다각도·표정 시트",
     "AI 생성 부분을 표시해야 한다. 사람이 리터치한 범위만 주장한다"),
    ("㉤ 완성 영상", "영상저작물",
     "화별 완성본",
     "화마다 따로 등록한다. 공표 후 1년 안에 등록하면 추정력을 온전히 받는다"),
]

상표 = [
    ("41", "영상 제작·배급, 엔터테인먼트업, 캐릭터 라이선싱", "가장 중요하다. 유튜브 채널과 영상 사업의 본체"),
    ("9", "내려받는 영상물, 애플리케이션, 전자출판물", "디지털 판매·앱을 낼 때"),
    ("28", "인형, 완구, 피규어, 보드게임", "굿즈의 핵심 분류"),
    ("16", "그림책, 스티커, 문구, 학습지", "출판·문구"),
    ("25", "아동복, 티셔츠, 모자", "의류 굿즈"),
    ("30", "과자, 캔디, 음료", "식품 라이선싱을 볼 거면"),
]


def markdown(d):
    o = []
    A = o.append
    A("# 「쿵쿵이와 친구들」 창작 이력 증빙")
    A("")
    A("> 저작권 등록 신청 및 권리 다툼 시 첨부용. "
      "`scripts/build_ip_pack.py` 가 저장소의 커밋 이력에서 자동으로 만든다.")
    A("")
    A("| | |")
    A("|---|---|")
    A("| 작성일 | %s |" % d["생성일"])
    A("| 저장소 | `%s` |" % d["원격"])
    A("| 최초 커밋 | **%s** · `%s` |" % (d["최초커밋"][0], d["최초커밋"][1][:10]))
    A("| 최신 커밋 | **%s** · `%s` |" % (d["최신커밋"][0], d["최신커밋"][1][:10]))
    A("| 커밋 수 | %s |" % d["커밋수"])
    A("| 분량 | 본편 %d화 · %d컷 · %d초 / 쇼츠 %d편 · %d컷 / 대사 %d줄 |"
      % (d["합계"]["화"], d["합계"]["본편컷"], d["합계"]["본편초"],
         d["합계"]["쇼츠"], d["합계"]["쇼츠컷"], d["합계"]["대사"]))
    A("")
    A("**이 표의 날짜는 저작자가 적어 넣은 값이 아니다.** 각 항목이 저장소에 처음 "
      "들어온 커밋의 날짜이며, 커밋 해시와 함께 GitHub 서버에 보관되어 있다. "
      "해시는 그 시점의 저장소 내용 전체에 대한 지문이므로, 나중에 내용을 고치면 "
      "해시가 달라져 위조가 드러난다.")
    A("")

    A("## 1. AI 사용 구분 — 등록 신청서에 그대로 옮긴다")
    A("")
    A("한국 저작권법은 **인간의 창작적 기여**가 있는 부분만 저작물로 본다. "
      "프롬프트만 넣어 나온 산출물은 등록해도 그 부분이 제외되므로, 처음부터 갈라 둔다. "
      "숨기고 등록하면 나중에 등록이 뒤집힌다.")
    A("")
    A("| 항목 | 누가 만들었나 | 비고 |")
    A("|---|---|---|")
    for a, b, c in AI표:
        A("| %s | **%s** | %s |" % (a, b, c))
    A("")
    A("> **핵심.** 이 작품의 값어치는 그림이 아니라 «설정과 이야기»에 있고, 그쪽은 "
      "온전히 사람이 만들었다. 남이 민트색 아기 공룡을 그리는 것은 막기 어려워도, "
      "«뿔에서 빛을 내어 친구를 지키는 다섯 살 아기 트리케라톱스»라는 캐릭터를 "
      "가져가는 것은 위 ㉠㉡ 으로 다툴 수 있다.")
    A("")
    A("> **그림 쪽을 강하게 만들려면** 마스터 시트를 사람이 직접 리터치하거나 원화를 "
      "손으로 그려 두고, 그 파일도 저장소에 커밋해 이력을 남긴다.")
    A("")

    A("## 2. 등록 단위")
    A("")
    A("| 단위 | 종류 | 내용 | 판단 |")
    A("|---|---|---|---|")
    for a, b, c, e in 등록단위:
        A("| **%s** | %s | %s | %s |" % (a, b, c, e))
    A("")
    A("신청처는 한국저작권위원회(`www.cros.or.kr`). 등록하면 창작연월일과 저작자에 "
      "**추정력**이 생기고, 침해자의 **과실이 추정**되며, 무엇보다 **법정손해배상**을 "
      "청구할 수 있다(저작권법 제125조의2). 실손해를 증명하지 못해도 저작물당 최대 "
      "1천만원, 영리 목적 고의 침해는 5천만원까지다. "
      "**단 침해가 일어나기 전에 등록돼 있어야 한다** — 이것이 미리 등록하는 진짜 이유다.")
    A("")

    A("## 3. 캐릭터 7종 — 설정 원문과 최초 기록일")
    A("")
    for c in d["캐릭터"]:
        A("### %s — %s" % (c["이름"], c["역할"]))
        A("")
        A("`최초 기록 %s · 커밋 %s · 키 %scm · %s`"
          % (c["최초기록"], c["커밋"], c["키"], c["mbti"]))
        A("")
        A("- **외형** %s" % c["외형"])
        A("- **성격** %s" % c["성격"])
        A("- **목소리** %s" % c["목소리"])
        A("- **꿈** %s" % c["꿈"])
        A("- **두려움** %s" % c["두려움"])
        A("- **집** %s" % c["집"])
        A("")

    A("## 4. 본편 40화")
    A("")
    A("| 화 | 제목 | 로그라인 | 컷 | 초 | 대사 | 최초 기록 | 커밋 |")
    A("|---|---|---|---|---|---|---|---|")
    for e in d["에피소드"]:
        A("| %s | %s | %s | %d | %d | %d | %s | `%s` |"
          % (e["번호"], e["제목"], e["로그라인"], e["컷"], e["초"], e["대사"],
             e["최초기록"], e["커밋"]))
    A("")

    A("## 5. 쇼츠 %d편" % len(d["쇼츠"]))
    A("")
    A("| ID | 종류 | 제목 | 컷 | 초 | 최초 기록 | 커밋 |")
    A("|---|---|---|---|---|---|---|")
    for s in d["쇼츠"]:
        A("| %s | %s | %s | %s | %s | %s | `%s` |"
          % (s["id"], s["종류"], s["제목"], s["컷"], s["초"], s["최초기록"], s["커밋"]))
    A("")

    A("## 6. 상표 출원 대상")
    A("")
    A("굿즈·라이선싱·채널명 방어에는 저작권보다 **상표**가 훨씬 실효적이다. "
      "저작권은 «베낀 것»만 막지만, 상표는 **비슷하기만 해도** 막는다. "
      "출원 전에 `KIPRIS`(특허정보넷)에서 선출원을 검색한다. 출원은 특허청 `특허로`.")
    A("")
    A("**출원할 표장** — 문자와 도형을 각각 낸다. 도형을 함께 낸 것만 있으면 "
      "이름만 베껴 쓰는 것을 막기 어렵다.")
    A("")
    A("| 표장 | 형태 | 비고 |")
    A("|---|---|---|")
    A("| 쿵쿵이와 친구들 | 문자 | 작품 제목이자 브랜드 |")
    A("| 쿵쿵이 | 문자 | 주인공 단독. 굿즈에서 제일 많이 쓰인다 |")
    for c in d["캐릭터"][1:]:
        A("| %s | 문자 | 조연 캐릭터 |" % c["이름"])
    A("| (로고) | 도형 | 확정된 로고 이미지 |")
    A("| (쿵쿵이 도안) | 도형 | 마스터 시트의 정면 도안 |")
    A("")
    A("**지정상품 분류(니스 분류)**")
    A("")
    A("| 류 | 지정상품·서비스 | 왜 |")
    A("|---|---|---|")
    for a, b, c in 상표:
        A("| **%s류** | %s | %s |" % (a, b, c))
    A("")
    A("한 류당 출원료는 약 5.6만원(온라인, 20개 지정상품까지)이며 등록료가 따로 든다. "
      "예산이 빠듯하면 **41류와 28류를 먼저** 낸다 — 영상 사업의 본체와 굿즈의 핵심이다.")
    A("")

    A("## 7. 하는 순서")
    A("")
    A("1. **KIPRIS 선출원 검색** — 「쿵쿵이」가 이미 등록돼 있으면 이름부터 다시 정해야 한다. 다른 일보다 먼저 확인한다")
    A("2. **상표 출원** (41류·28류) — 먼저 낸 사람이 이긴다. 공개 전에 내는 것이 가장 안전하다")
    A("3. **저작권 등록** ㉠ 캐릭터 바이블 · ㉡ 시나리오 — 이 문서를 첨부한다")
    A("4. **공개** — 유튜브 업로드")
    A("5. **저작권 등록** ㉤ 완성 영상 — 화별로, 공표 후 1년 안에")
    A("6. **디자인권** — 인형·문구를 낼 계획이면 공개 후 **12개월 안에** 출원해야 신규성 예외를 받는다")
    A("")
    A("> 이 문서는 법률 자문이 아니다. 실제 출원 전에 변리사 확인을 받는 것을 권한다. "
      "한국저작권위원회와 발명진흥회는 무료 상담을 제공한다.")
    A("")
    return "\n".join(o)


CSS = """
@page { size: A4; margin: 18mm 15mm; }
body { font-family: 'NanumGothic','Nanum Gothic','Malgun Gothic',sans-serif;
       font-size: 10pt; line-height: 1.65; color: #1b1b1b; }
h1 { font-size: 19pt; border-bottom: 3px solid #2f6f5e; padding-bottom: 6px; }
h2 { font-size: 14pt; margin-top: 26px; border-left: 5px solid #2f6f5e;
     padding-left: 9px; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 18px; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 8.6pt; }
th, td { border: 1px solid #c9c9c9; padding: 4px 7px; text-align: left;
         vertical-align: top; }
th { background: #eef4f2; }
code { font-family: 'DejaVu Sans Mono',monospace; font-size: 8.4pt;
       background: #f2f2f2; padding: 1px 3px; }
blockquote { border-left: 4px solid #d8b25f; background: #fdf8ec;
             margin: 10px 0; padding: 7px 12px; }
blockquote p { margin: 4px 0; }
li { margin: 3px 0; }
"""


def md_to_html(md, pdf=False):
    """이 문서가 쓰는 문법만 처리한다 — 표 · 제목 · 목록 · 인용 · 굵게 · 코드.

    pdf=True 는 fpdf2 용이다. fpdf2 의 HTML 처리기는 표 칸 안에 태그가 들어가는
    것을 지원하지 않고, <code> 를 courier 로 그리는데 courier 에는 한글이 없다.
    그래서 PDF 쪽은 칸 안을 맨 글자로 두고 <code> 를 없앤다.
    """
    import re

    def inline(t, plain=False):
        t = html.escape(t)
        if plain or pdf:
            t = re.sub(r"`([^`]+)`", r"\1", t)
        else:
            t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        if plain:
            return re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
        return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)

    out, rows, quote, lst = [], [], [], []

    def flush_table():
        if not rows:
            return
        body = [r for r in rows if not set(r.replace("|", "").strip()) <= set("-: ")]
        out.append("<table>")
        for i, r in enumerate(body):
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            out.append("<tr>" + "".join(
                f"<{tag}>{inline(c, plain=pdf)}</{tag}>" for c in cells) + "</tr>")
        out.append("</table>")
        rows.clear()

    def flush_quote():
        if quote:
            body = inline(" ".join(quote))
            out.append(f"<p>{body}</p>" if pdf
                       else f"<blockquote><p>{body}</p></blockquote>")
            quote.clear()

    def flush_list():
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + "</ul>")
            lst.clear()

    def flush_all():
        flush_table(); flush_quote(); flush_list()

    for ln in md.split("\n"):
        s = ln.rstrip()
        if s.startswith("|"):
            flush_quote(); flush_list(); rows.append(s); continue
        flush_table()
        if s.startswith("> "):
            flush_list(); quote.append(s[2:]); continue
        flush_quote()
        m = re.match(r"^(\d+)\. (.*)", s)
        if s.startswith("- ") or m:
            lst.append(m.group(2) if m else s[2:]); continue
        flush_list()
        if s.startswith("### "):
            out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s:
            out.append(f"<p>{inline(s)}</p>")
    flush_all()
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<title>쿵쿵이와 친구들 창작 이력 증빙</title>"
            f"<style>{CSS}</style></head><body>" + "\n".join(out) + "</body></html>")


def to_pdf(md, out_path):
    """한글이 들어간 PDF 를 만든다.

    저장소의 나눔고딕을 문서에 박아 넣는다. 시스템 폰트에 기대면 PDF 를 여는
    컴퓨터마다 글자가 달라지고, 한글 폰트가 없는 곳에서는 아예 깨진다.
    """
    try:
        from fpdf import FPDF
    except Exception as e:
        print("! fpdf2 가 없어 PDF 는 건너뜁니다 (pip install fpdf2). "
              "HTML 을 브라우저에서 «인쇄 → PDF 로 저장» 해도 결과는 같습니다. [%s]"
              % type(e).__name__)
        return None

    font = ROOT / "fonts" / "NanumGothicBold.ttf"
    if not font.exists():
        print("! fonts/NanumGothicBold.ttf 가 없어 PDF 에서 한글이 깨집니다.")
        return None

    body = md_to_html(md, pdf=True).split("<body>", 1)[1].rsplit("</body>", 1)[0]
    f = FPDF(format="A4")
    f.set_margins(15, 16, 15)
    f.set_auto_page_break(True, 16)
    for style in ("", "B", "I", "BI"):
        f.add_font("nanum", style, str(font))
    f.set_font("nanum", size=9)
    f.add_page()
    f.write_html(body)
    f.output(str(out_path))
    return out_path


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pdf", action="store_true", help="PDF 까지 만든다 (libreoffice 필요)")
    a = p.parse_args()

    if git("status", "--porcelain"):
        print("! 커밋되지 않은 변경이 있습니다. 증빙은 커밋된 상태를 기준으로 만드는 것이 "
              "맞으므로, 먼저 커밋하고 다시 실행하는 것을 권합니다.\n")

    d = collect()
    OUT.mkdir(exist_ok=True)
    md = markdown(d)
    (OUT / "창작이력_증빙.md").write_text(md + "\n", encoding="utf-8")
    (OUT / "창작이력_증빙.html").write_text(md_to_html(md), encoding="utf-8")
    (OUT / "창작이력_증빙.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("창작 이력 증빙 — 캐릭터 %d종 · 본편 %d화(%d컷) · 쇼츠 %d편"
          % (len(d["캐릭터"]), d["합계"]["화"], d["합계"]["본편컷"], d["합계"]["쇼츠"]))
    print("  최초 커밋 %s · 최신 %s · 커밋 %s개"
          % (d["최초커밋"][0], d["최신커밋"][0], d["커밋수"]))
    for f in ("창작이력_증빙.md", "창작이력_증빙.html", "창작이력_증빙.json"):
        print("  ip/%s" % f)
    if a.pdf:
        pdf = to_pdf(md, OUT / "창작이력_증빙.pdf")
        if pdf:
            print("  ip/%s  (%d KB)" % (pdf.name, pdf.stat().st_size // 1024))


if __name__ == "__main__":
    sys.exit(main())
