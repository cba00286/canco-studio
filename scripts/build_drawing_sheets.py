#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""손으로 그릴 원화 작업지를 만든다. A4로 인쇄해서 그 위에 직접 그린다.

**왜 손으로 그리나.** AI가 뽑은 그림은 저작물로 보호받지 못한다 — 사람의
창작적 선택이 표현에 드러나지 않았기 때문이다. 사람이 직접 그린 원화가 한 장
있으면 «이 캐릭터의 형상은 내가 정했고 AI 는 채색 도구였다» 는 근거가 선다.
상표의 도형 출원에도 그대로 쓴다.

**베끼면 안 된다.** AI 그림을 그대로 옮겨 그리는 것은 원본의 표현을 복제한
것이라 새 저작권이 생기지 않는다. 비율·표정·소품을 **본인 판단으로 바꿔야**
그 바뀐 부분이 본인 것이 된다. 그래서 이 작업지는 밑그림을 깔아 주지 않고
빈 칸과 비율 안내선만 준다.

    python3 scripts/build_drawing_sheets.py             # 7종 전부
    python3 scripts/build_drawing_sheets.py 쿵쿵         # 한 명만
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ip" / "원화작업지"
FONT = ROOT / "fonts" / "NanumGothicBold.ttf"
ORDER = ["쿵쿵", "루카", "후안", "미미", "티니", "루비", "노을"]

# 그리면서 정해야 하는 것들. 빈칸으로 두면 아무도 안 채우므로 질문으로 적는다.
결정거리 = [
    "머리와 몸의 비율을 몇 대 몇으로 할까 — 더 아기 같게? 더 씩씩하게?",
    "눈 크기와 간격은 — 눈이 크면 어리고 순해 보인다",
    "소품을 그대로 둘까, 위치나 모양을 바꿀까",
    "옆모습에서 주둥이가 얼마나 나올까",
    "서 있는 자세의 무게중심 — 어느 발에 실을까",
]

TURN = ["정면", "3/4 앞", "옆", "뒤"]
EXPR = ["무표정", "환한 웃음", "놀람", "겁먹음", "결의", "폭소"]


def sheets(pdf, name, ent, look):
    """캐릭터 한 명분 3쪽."""
    H = ent.get("height")

    def header(title, sub):
        pdf.set_font("nanum", size=15)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 9, f"{name} — {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("nanum", size=8.5)
        pdf.set_text_color(90, 90, 90)
        pdf.multi_cell(0, 4.6, sub)
        pdf.set_text_color(20, 20, 20)
        pdf.ln(1)

    def footer_signature():
        """서명란. 이 종이가 나중에 «내가 언제 그렸다» 는 물증이 된다."""
        y = pdf.h - 24
        pdf.set_y(y)
        pdf.set_draw_color(150, 150, 150)
        pdf.set_font("nanum", size=8)
        pdf.set_text_color(110, 110, 110)
        w = (pdf.w - pdf.l_margin - pdf.r_margin) / 3
        for label in ("그린 사람", "그린 날짜", "서명"):
            x = pdf.get_x()
            pdf.cell(w, 5, label, new_x="LEFT", new_y="NEXT")
            pdf.line(x + 1, pdf.get_y() + 4, x + w - 6, pdf.get_y() + 4)
            pdf.set_y(y)
            pdf.set_x(x + w)
        pdf.set_y(pdf.h - 12)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("nanum", size=7)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(0, 4, "쿵쿵이와 친구들 · 원화 작업지 · 이 종이는 버리지 말고 스캔해서 저장소에 남긴다")
        pdf.set_text_color(20, 20, 20)

    def box(x, y, w, h, label, guides=0):
        pdf.set_draw_color(60, 60, 60)
        pdf.set_line_width(0.4)
        pdf.rect(x, y, w, h)
        # 머리 높이 기준선. 비율을 눈대중으로 잡지 않게 한다.
        if guides:
            pdf.set_draw_color(205, 205, 205)
            pdf.set_line_width(0.2)
            for i in range(1, guides):
                yy = y + h * i / guides
                pdf.line(x + 2, yy, x + w - 2, yy)
            pdf.set_draw_color(225, 210, 170)      # 중심선
            pdf.line(x + w / 2, y + 2, x + w / 2, y + h - 2)
        pdf.set_xy(x + 2, y + h - 6)
        pdf.set_font("nanum", size=8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(w - 4, 5, label)
        pdf.set_text_color(20, 20, 20)
        pdf.set_line_width(0.4)

    L, R = pdf.l_margin, pdf.w - pdf.r_margin
    W = R - L

    # ── 1쪽 턴어라운드 ──────────────────────────────────────────────
    pdf.add_page()
    header("턴어라운드", 
           f"키 {H}cm · {look}\n"
           "네 방향이 같은 캐릭터로 보여야 한다. 가로 안내선은 머리 높이 기준이니 "
           "네 칸에서 눈·어깨·허리가 같은 선에 오게 그린다.")
    bw, bh = (W - 6) / 4, 96
    y = pdf.get_y() + 2
    for i, t in enumerate(TURN):
        box(L + i * (bw + 2), y, bw, bh, t, guides=6)
    y += bh + 6

    pdf.set_xy(L, y)
    pdf.set_font("nanum", size=9.5)
    pdf.cell(0, 6, "그리면서 정할 것 — 하나라도 원본과 다르게 정해야 내 그림이 된다",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("nanum", size=8.5)
    pdf.set_text_color(70, 70, 70)
    for q in 결정거리:
        pdf.set_x(L + 2)
        pdf.multi_cell(W - 4, 5, "□  " + q)
    pdf.set_text_color(20, 20, 20)
    footer_signature()

    # ── 2쪽 표정 ────────────────────────────────────────────────────
    pdf.add_page()
    header("표정 여섯",
           "얼굴과 어깨까지. 여섯 칸에서 같은 얼굴이어야 하고 감정만 달라야 한다.\n"
           "이 여섯 장이 40화 내내 쓰이므로, 가장 많이 나올 «환한 웃음» 부터 그린다.")
    bw, bh = (W - 8) / 3, 62
    y = pdf.get_y() + 2
    for i, t in enumerate(EXPR):
        box(L + (i % 3) * (bw + 4), y + (i // 3) * (bh + 6), bw, bh, t, guides=4)
    y += bh * 2 + 14

    pdf.set_xy(L, y)
    pdf.set_font("nanum", size=9.5)
    pdf.cell(0, 6, "이 캐릭터의 목소리 — 표정을 그릴 때 소리를 떠올린다",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("nanum", size=8.5)
    pdf.set_text_color(70, 70, 70)
    pdf.set_x(L + 2)
    pdf.multi_cell(W - 4, 5, (ent.get("profile") or {}).get("voice", "")[:220])
    pdf.set_text_color(20, 20, 20)
    footer_signature()

    # ── 3쪽 소품과 자유 스케치 ──────────────────────────────────────
    pdf.add_page()
    header("소품 · 자유 스케치",
           f"소품: {ent.get('props_ko','')}\n"
           "소품은 40화 내내 똑같이 나와야 하므로 여기서 형태를 확정한다. "
           "아래 큰 칸에는 이 캐릭터다운 자세를 자유롭게 그린다.")
    y = pdf.get_y() + 2
    bw = (W - 8) / 3
    for i in range(3):
        box(L + i * (bw + 4), y, bw, 44, "소품 %d" % (i + 1))
    y += 50
    box(L, y, W, 108, "자유 스케치 — 시그니처 포즈")
    footer_signature()


def main():
    try:
        from fpdf import FPDF
    except Exception as e:
        sys.exit("fpdf2 가 필요합니다: pip install fpdf2  [%s]" % type(e).__name__)
    if not FONT.exists():
        sys.exit("fonts/NanumGothicBold.ttf 가 없습니다.")

    chars = json.loads((ROOT / "bible" / "characters.json").read_text(encoding="utf-8"))
    looks = json.loads((ROOT / "bible" / "looks.json").read_text(encoding="utf-8"))
    want = [a for a in sys.argv[1:] if not a.startswith("-")] or ORDER
    bad = [w for w in want if w not in chars["characters"]]
    if bad:
        sys.exit("모르는 캐릭터: %s" % ", ".join(bad))

    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name in want:
        pdf = FPDF(format="A4")
        pdf.set_margins(14, 13, 14)
        pdf.set_auto_page_break(False)
        for style in ("", "B", "I", "BI"):
            pdf.add_font("nanum", style, str(FONT))
        pdf.set_title("%s 원화 작업지" % name)
        sheets(pdf, name, chars["characters"][name], looks.get(name, ""))
        p = OUT / ("%s_원화작업지.pdf" % name)
        pdf.output(str(p))
        made.append(p)

    print("원화 작업지 %d명분 (각 3쪽) — %s" % (len(made), date.today().isoformat()))
    for p in made:
        print("  %s  (%d KB)" % (p.relative_to(ROOT), p.stat().st_size // 1024))
    print()
    print("A4 로 인쇄해서 그 위에 직접 그립니다. 다 그리면 스캔해서")
    print("ip/원화/<이름>/ 에 넣고 커밋하세요 — 커밋 날짜가 창작 시점의 증거가 됩니다.")


if __name__ == "__main__":
    sys.exit(main())
