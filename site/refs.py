# -*- coding: utf-8 -*-
"""레퍼런스 이미지 찾기 — 파일명을 강제하지 않는다.

파일 이름에 캐릭터 이름만 들어 있으면 찾는다. 한글이든 영어든 상관없고
띄어쓰기·괄호·번호가 붙어 있어도 된다.

    쿵쿵이 3D 모델링 마스터 시트.png        → 쿵쿵
    루카(Luca) 종합 시트 v2.jpg              → 루카
    후안의 비니 돔 마스터시트.png            → 후안

페이지에 넣을 때는 폭을 줄이고 JPEG로 다시 인코딩한다. 원본을 그대로 넣으면
Artifact 용량 한도(16MB)를 금방 넘긴다.
"""
import base64, io, pathlib, re

EXT = {".png", ".jpg", ".jpeg", ".webp"}
ALIAS = {
    "쿵쿵": ["쿵쿵", "kungkung", "kung-kung", "kung_kung"],
    "루카": ["루카", "luca"],
    "후안": ["후안", "juan"],
    "미미": ["미미", "mimi"],
    "티니": ["티니", "tini"],
    "루비": ["루비", "ruby"],
}
CHART = ["도감", "키 비교", "height", "chart", "scale"]


def _norm(s):
    return re.sub(r"[\s_\-()\[\]]+", "", s).lower()


def _scan(folder):
    d = pathlib.Path(folder)
    return sorted(p for p in d.iterdir() if p.suffix.lower() in EXT) if d.is_dir() else []


def find(folder, key):
    """폴더에서 캐릭터 하나의 이미지를 찾는다. 없으면 None."""
    words = [_norm(w) for w in ALIAS.get(key, [key])]
    for p in _scan(folder):
        n = _norm(p.stem)
        if any(w in n for w in words):
            return p
    return None


def find_chart(folder):
    for p in _scan(folder):
        n = _norm(p.stem)
        if any(_norm(w) in n for w in CHART):
            return p
    return None


def data_uri(path, max_w=1400, quality=78):
    """페이지에 박아 넣을 data URI. Pillow가 없으면 원본을 그대로 쓴다."""
    raw = pathlib.Path(path).read_bytes()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), len(buf.getvalue())
    except ImportError:
        mime = "image/png" if pathlib.Path(path).suffix.lower() == ".png" else "image/jpeg"
        return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode()), len(raw)


def report(sheets_dir, homes_dir, keys):
    """무엇을 찾았고 무엇이 없는지 한 줄씩 알려준다."""
    lines, found = [], 0
    for k in keys:
        s, h = find(sheets_dir, k), find(homes_dir, k)
        found += bool(s) + bool(h)
        lines.append("  %s  캐릭터 %-28s 집 %s" % (k,
            s.name if s else "(없음)", h.name if h else "(없음)"))
    c = find_chart(sheets_dir)
    found += bool(c)
    lines.append("  키 도감  %s" % (c.name if c else "(없음)"))
    return found, "\n".join(lines)
