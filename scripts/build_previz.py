#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""컷 리스트에서 블렌더 프리비즈를 만든다.

생성 순서가 바뀌었다. 예전에는 컷 설명을 곧장 생성기에 넣었지만, 이제는

    대본 → 프리비즈(블렌더) → 편집 → 확정 프레임 → 매핑 → 힉스필드 생성

이 순서로 간다. 구도·카메라·타이밍은 블렌더가 잡고, 생성기는 그 구도 위에
그림을 입히는 일만 한다. 그래서 컷마다 다시 뽑아도 구도가 흔들리지 않는다.

이 스크립트가 내는 것 (episodes/<ep>/previz/)

  previz.json        컷마다 카메라(렌즈·거리·높이·움직임)와 인물 배치, 프레임 구간
  블렌더_<ep>.py     블렌더 텍스트 편집기에 붙여 넣고 실행하면 한 타임라인에
                     전 컷이 카메라 마커로 깔린다
  프리비즈_작업지.md  컷마다 무엇을 보고 무엇을 고칠지

카메라는 계산으로 잡는다. 샷 크기(WS/MS/CU)가 «주인공 키의 몇 배를 화면에
담을지»를 정하고, 거기서 렌즈와 거리가 나온다. 사람이 손으로 옮겨 고치라고
만든 출발점이지 정답이 아니다 — 블렌더에서 옮긴 값이 최종이다.

    python3 scripts/build_previz.py --episode ep1
    python3 scripts/build_previz.py --all
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import bible

ROOT = Path(__file__).resolve().parent.parent
# 블렌더 센서는 기본 36mm 이고, sensor_fit=AUTO 는 «긴 쪽» 에 36mm 를 준다.
# 그래서 가로(16:9) 영상의 세로 센서는 20.25mm, 세로(9:16) 쇼츠는 36mm 다.
SENSOR_H_가로 = 36.0 * 9.0 / 16.0                 # 20.25mm
SENSOR_H_세로 = 36.0


def load(name: str) -> dict:
    return json.loads((ROOT / "bible" / name).read_text(encoding="utf-8"))


def move_of(shot: dict, spec: dict) -> str:
    """ko_motion 에서 카메라 움직임을 읽는다.

    «카메라»·«앵글»·«화면이» 가 들어간 문장만 본다. 대본이 카메라를 말하지 않은
    컷은 정지로 둔다 — 인물이 «다가간다», 불티가 «스쳐 간다» 같은 말을 카메라
    움직임으로 잘못 읽으면 전 화가 흔들린다. 움직임은 블렌더에서 사람이 넣는다.
    """
    import re as _re
    text = shot.get("ko_motion", "")
    said = " ".join(x for x in _re.split(r"(?<=[.!?])\s+", text)
                    if any(w in x for w in ("카메라", "앵글", "화면이 ")))
    if not said:
        return "정지"
    hits = [k for k, w in spec["움직임_말머리"].items()
            if not k.startswith("_") and any(x in said for x in w)]
    return hits[0] if hits else "정지"


def moves_of(shot: dict, spec: dict) -> list[str]:
    """맞은 움직임을 모두 돌려준다. 둘 이상이면 사람이 골라야 한다는 표시다."""
    import re as _re
    said = " ".join(x for x in _re.split(r"(?<=[.!?])\s+", shot.get("ko_motion", ""))
                    if any(w in x for w in ("카메라", "앵글", "화면이 ")))
    return [k for k, w in spec["움직임_말머리"].items()
            if not k.startswith("_") and any(x in said for x in w)]


def place(cast: list[str], subject: str | None, heights: dict, spec: dict,
          세로: bool = False):
    """인물을 무대에 세운다. 말하는 사람이 가운데, 나머지가 좌우로 갈라진다.

    9:16 쇼츠는 좌우가 좁다. 셋 이상을 한 줄로 세우면 카메라가 한참 뒤로 밀려
    미디엄샷이 풀샷이 된다. 그래서 세로 화면에서는 앞뒤 두 줄로 나눠 세운다.
    """
    if not cast:
        return []
    bat = spec["배치"]
    # 말하는 사람을 가운데로 두고 나머지를 좌·우 번갈아 세운다.
    rest = [c for c in cast if c != subject]
    order: list[str] = []
    for i, c in enumerate(rest):
        (order.insert(0, c) if i % 2 else order.append(c))
    mid = len(order) // 2 if subject else len(order)
    if subject:
        order.insert(mid, subject)

    # 이웃 간격 → 중심 좌표
    xs = [0.0]
    for a, b in zip(order, order[1:]):
        gap = bat["간격_계수"] * (heights[a] + heights[b]) / 2 + bat["간격_여유_m"]
        xs.append(xs[-1] + gap)
    centre = (xs[0] + xs[-1]) / 2
    xs = [x - centre for x in xs]

    # 세로 화면 · 셋 이상 → 앞줄/뒷줄로 접는다. 뒷줄은 앞줄 사이로 보이게 반 칸 민다.
    rows = [0.0] * len(order)
    if 세로 and len(order) >= 3:
        앞 = order[0::2]
        뒤 = order[1::2]
        def 줄(names, 깊이, 밀기):
            zs = [0.0]
            for a, b in zip(names, names[1:]):
                zs.append(zs[-1] + bat["간격_계수"] * (heights[a] + heights[b]) / 2
                          + bat["간격_여유_m"])
            c = (zs[0] + zs[-1]) / 2
            return {n: (z - c + 밀기, 깊이) for n, z in zip(names, zs)}
        칸 = bat["간격_여유_m"] + 0.3
        자리 = {}
        자리.update(줄(앞, 0.0, 0.0))
        자리.update(줄(뒤, 0.85, 칸 / 2))
        xs = [자리[n][0] for n in order]
        rows = [자리[n][1] for n in order]

    out = []
    for name, x, row in zip(order, xs, rows):
        depth = row + bat["호_깊이_m"] * abs(x) / max(abs(xs[0]), abs(xs[-1]), 1e-6)
        yaw = 0.0 if name == subject else -math.copysign(bat["안쪽보기_deg"], x or 1.0)
        out.append({"이름": name, "키_m": round(heights[name], 3),
                    "위치": [round(x, 3), round(depth, 3), 0.0],
                    "방향_deg": round(yaw, 1),
                    "말한다": name == subject})
    return out


def look_at(cam: list[float], tgt: list[float]) -> list[float]:
    """카메라가 타깃을 보는 오일러 각(도). 블렌더 XYZ 순서."""
    dx, dy, dz = (tgt[0] - cam[0], tgt[1] - cam[1], tgt[2] - cam[2])
    horiz = math.hypot(dx, dy)
    rx = math.degrees(math.atan2(horiz, -dz))
    rz = math.degrees(math.atan2(dy, dx)) - 90.0
    return [round(rx, 3), 0.0, round(rz, 3)]


def camera_for(shot: dict, people: list[dict], subject_h: float, spec: dict,
               세로: bool = False) -> dict:
    s = spec["샷"][shot["shot"]]
    lens = s["렌즈_mm"]

    # 화면에 담을 세로 길이. 여러 명이면 좌우로 다 들어가도록 넓힌다.
    V = subject_h * s["담는높이_배"]
    if 세로:
        V *= 1.35                                    # 9:16 은 좌우가 좁아 위아래로 더 담는다

    # 둘 이상이 나란히 설 때만 좌우가 문제가 된다. 혼자면 클로즈업이 몸통 너비에
    # 끌려 뒤로 밀리면 안 된다.
    if len(people) >= 2:
        xs = [p["위치"][0] for p in people]
        어깨 = max(p["키_m"] for p in people) * 0.28
        너비 = (max(xs) - min(xs)) + 어깨
        # 화면 가로 = V × (가로:세로). 세로가 V 이상이 되려면 너비를 이 비로 나눈다.
        비 = 9.0 / 16.0 if 세로 else 16.0 / 9.0
        V = max(V, 너비 * spec["배치"]["가로여유_배"] / 비)
    d = lens * V / (SENSOR_H_세로 if 세로 else SENSOR_H_가로)

    ty = sum(p["위치"][1] for p in people) / len(people) if people else 0.0
    tgt = [0.0, round(ty, 3), round(subject_h * s["타깃_z_배"], 3)]
    cz = subject_h * s["카메라_z_배"]

    m = spec["카메라_움직임"][move_of(shot, spec)]
    label = move_of(shot, spec)

    def pose(dist_mul: float, z_mul: float, yaw_off: float):
        pos = [0.0, round(ty - d * dist_mul, 3), round(cz * z_mul, 3)]
        rot = look_at(pos, tgt)
        rot[2] = round(rot[2] + yaw_off, 3)
        return {"위치": pos, "회전_deg": rot}

    half = m["요_deg"] / 2.0
    민정도 = d / (lens * subject_h * s["담는높이_배"]
                 / (SENSOR_H_세로 if 세로 else SENSOR_H_가로))
    return {
        "렌즈_mm": lens, "거리_m": round(d, 3), "타깃": tgt, "움직임": label,
        "밀림": round(민정도, 2),
        "시작": pose(m["시작_거리_배"], m["시작_z_배"], -half),
        "끝":   pose(m["끝_거리_배"], 1.0, +half),
    }


def build(prompts: Path, spec: dict, chars: dict, 세로: bool = False) -> dict:
    data = json.loads((prompts / "shots_v2.json").read_text(encoding="utf-8"))
    ent = chars["characters"]
    heights = {k: v["height"] / 100.0 for k, v in ent.items()}
    fps = spec["fps"]
    amb = {k: v.get("amb") for k, v in (data.get("audio_sections") or {}).items()}

    cuts, frame = [], 1
    for shot in data["shots"]:
        cast = [c for c in (shot.get("cast") or []) if c in heights]
        sp = shot.get("speaker")
        subject = sp if sp in cast else (cast[0] if cast else None)
        people = place(cast, subject, heights, spec, 세로)
        subject_h = heights[subject] if subject else 1.6
        n = int(round(shot["duration"] * fps))
        cuts.append({
            "id": shot["id"], "section": shot["section"],
            "샷": shot["shot"], "샷_ko": shot.get("shot_ko"),
            "초": shot["duration"], "시작_프레임": frame, "끝_프레임": frame + n - 1,
            "연결": shot.get("link"), "화자": sp, "대사": shot.get("dialogue"),
            "설명": shot.get("ko"), "움직임_설명": shot.get("ko_motion"),
            "인물": people, "카메라": camera_for(shot, people, subject_h, spec, 세로),
            "움직임_후보": moves_of(shot, spec),
        })
        frame += n

    return {
        "_comment": "scripts/build_previz.py 가 만든다. 손으로 고치지 말고 블렌더에서 고친 뒤 "
                    "그 값을 여기 적거나, shots_v2.json 을 고치고 다시 돌린다.",
        "화": prompts.parent.name, "fps": fps,
        "해상도": spec["해상도"][::-1] if 세로 else spec["해상도"],
        "비율": "9:16" if 세로 else "16:9",
        "총_프레임": frame - 1, "총_초": round((frame - 1) / fps, 2),
        "컷_수": len(cuts), "장면": data.get("sections", {}), "환경": amb,
        "컷": cuts,
    }


# ── 블렌더 스크립트 ────────────────────────────────────────────────────────────
BLENDER = '''# -*- coding: utf-8 -*-
"""%(title)s 프리비즈 — 블렌더에서 실행한다.

블렌더 → Scripting 탭 → 이 파일을 열고 ▶ Run Script.
한 타임라인에 %(cuts)d컷이 순서대로 깔리고, 컷마다 카메라가 마커로 묶인다.
스페이스바를 누르면 %(secs).1f초짜리 프리비즈가 통째로 재생된다.

고치는 법
  · 구도가 마음에 안 드는 컷 → 타임라인에서 그 컷으로 가서 카메라를 움직인다.
    (N 패널에서 렌즈 mm 도 바꾼다)
  · 인물 위치 → 해당 컷 프레임에서 인물을 옮기고 I → Location 으로 키를 덮는다.
  · 컷 길이 → shots_v2.json 의 duration 을 고치고 build_previz.py 를 다시 돌린다.

이 스크립트는 아무것도 렌더하지 않고 아무것도 생성하지 않는다. 장면만 만든다.
"""
import bpy, json, math

SPEC = json.loads(r\'\'\'%(spec)s\'\'\')
FLOOR = json.loads(r\'\'\'%(floor)s\'\'\')

fps = SPEC["fps"]
W, H = SPEC["해상도"]

# ── 판을 비운다 ───────────────────────────────────────────────────────────────
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)

sc = bpy.context.scene
sc.render.fps = fps
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = 50          # 프리비즈는 절반 해상도로 충분하다
sc.frame_start, sc.frame_end = 1, SPEC["총_프레임"]
sc.render.engine = "%(engine)s"
for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)


def collection(name):
    c = bpy.data.collections.new(name)
    sc.collection.children.link(c)
    return c

COL_CH = collection("인물")
COL_CAM = collection("카메라")
COL_SET = collection("무대")


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = False
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    return m


def key_vis(ob, frame, shown):
    ob.hide_viewport = ob.hide_render = not shown
    ob.keyframe_insert("hide_viewport", frame=frame)
    ob.keyframe_insert("hide_render", frame=frame)


def constant(ob):
    ad = ob.animation_data
    if not ad or not ad.action:
        return
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


# ── 바닥 — 장면마다 한 장씩, 보이고 숨기고를 키로 잡는다 ───────────────────────
grounds = {}
for sec, rgb in FLOOR.items():
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 6, 0))
    g = bpy.context.object
    g.name = "바닥_" + sec
    g.data.materials.append(mat("바닥_" + sec, rgb))
    for c in g.users_collection:
        c.objects.unlink(g)
    COL_SET.objects.link(g)
    grounds[sec] = g

# ── 인물 대역 ─────────────────────────────────────────────────────────────────
people = {}
for name, h in SPEC["키"].items():
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.25
    COL_CH.objects.link(root)

    bpy.ops.mesh.primitive_cylinder_add(radius=h * 0.16, depth=h * 0.62,
                                        location=(0, 0, h * 0.31))
    body = bpy.context.object; body.name = name + "_몸"
    bpy.ops.mesh.primitive_uv_sphere_add(radius=h * 0.19, location=(0, 0, h * 0.80))
    head = bpy.context.object; head.name = name + "_머리"
    bpy.ops.mesh.primitive_cone_add(radius1=h * 0.05, depth=h * 0.12,
                                    rotation=(math.radians(-90), 0, 0),
                                    location=(0, -h * 0.20, h * 0.80))
    nose = bpy.context.object; nose.name = name + "_코"   # 어느 쪽을 보는지 표시

    col = mat(name + "_색", SPEC["색"][name])
    for part in (body, head, nose):
        part.data.materials.append(col)
        for c in part.users_collection:
            c.objects.unlink(part)
        COL_CH.objects.link(part)
        part.parent = root
    people[name] = root

# ── 컷 ────────────────────────────────────────────────────────────────────────
for cut in SPEC["컷"]:
    f0, f1 = cut["시작_프레임"], cut["끝_프레임"]

    cam_d = bpy.data.cameras.new("CAM_" + cut["id"])
    cam_d.lens = cut["카메라"]["렌즈_mm"]
    cam = bpy.data.objects.new("CAM_" + cut["id"], cam_d)
    COL_CAM.objects.link(cam)
    for when, frame in ((cut["카메라"]["시작"], f0), (cut["카메라"]["끝"], f1)):
        cam.location = when["위치"]
        cam.rotation_euler = [math.radians(a) for a in when["회전_deg"]]
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)

    mk = sc.timeline_markers.new("%%s %%s" %% (cut["id"], cut["샷_ko"] or ""), frame=f0)
    mk.camera = cam

    here = {p["이름"]: p for p in cut["인물"]}
    for name, root in people.items():
        p = here.get(name)
        key_vis(root, f0, p is not None)
        if p:
            root.location = p["위치"]
            root.rotation_euler = (0, 0, math.radians(p["방향_deg"]))
            root.keyframe_insert("location", frame=f0)
            root.keyframe_insert("rotation_euler", frame=f0)

    sec_amb = SPEC["환경"].get(cut["section"]) or "기본"
    for key, g in grounds.items():
        key_vis(g, f0, key == sec_amb or (key == "기본" and sec_amb not in grounds))

for ob in list(people.values()) + list(grounds.values()):
    constant(ob)

sc.frame_set(1)
print("프리비즈 완성 — %%d컷 / %%d프레임 / %%.1f초"
      %% (len(SPEC["컷"]), SPEC["총_프레임"], SPEC["총_프레임"] / fps))
'''

PALETTE = {"쿵쿵": [0.55, 0.85, 0.70], "루카": [0.55, 0.65, 0.90], "후안": [0.95, 0.75, 0.45],
           "미미": [0.90, 0.60, 0.80], "티니": [0.95, 0.90, 0.50], "루비": [0.95, 0.65, 0.72],
           "노을": [0.95, 0.55, 0.35]}


def blender_script(pv: dict, spec: dict, chars: dict, title: str) -> str:
    heights = {k: v["height"] / 100.0 for k, v in chars["characters"].items()}
    payload = dict(pv)
    payload["키"] = heights
    payload["색"] = {k: PALETTE.get(k, [0.7, 0.7, 0.7]) for k in heights}
    floors = {k: v for k, v in spec["바닥색"].items() if not k.startswith("_")}
    used = {(pv["환경"].get(c["section"]) or "기본") for c in pv["컷"]}
    floors = {k: v for k, v in floors.items() if k in used or k == "기본"}
    return BLENDER % {
        "title": title, "cuts": len(pv["컷"]), "secs": pv["총_초"],
        "engine": spec["렌더"]["엔진"],
        "spec": json.dumps(payload, ensure_ascii=False),
        "floor": json.dumps(floors, ensure_ascii=False),
    }


def worksheet(pv: dict, title: str) -> str:
    L = ["# %s 프리비즈 작업지" % title, "",
         "컷 %d개 · %d프레임 · %.1f초 · %dfps." % (
             pv["컷_수"], pv["총_프레임"], pv["총_초"], pv["fps"]), "",
         "## 순서", "",
         "1. `블렌더_%s.py` 를 블렌더 Scripting 탭에서 실행한다." % pv["화"],
         "2. 스페이스바로 전체를 한 번 본다. **타이밍**부터 본다 — 구도는 그 다음이다.",
         "3. 마음에 안 드는 컷의 마커로 가서 카메라를 옮긴다. 렌즈도 바꾼다.",
         "4. 다 되면 컷마다 **첫 프레임**과 **끝 프레임**을 PNG 로 뽑는다.",
         "5. 그 PNG 를 힉스필드에 구도 레퍼런스로 걸고 생성한다 (`제작_작업지.md`).", "",
         "> 여기서 정한 카메라가 최종 카메라다. 생성기는 이 구도를 따라 그리기만 한다.", "",
         "## 컷", "",
         "| # | 컷 | 샷 | 초 | 프레임 | 카메라 | 렌즈 | 거리 | 인물 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(pv["컷"], 1):
        who = ", ".join(p["이름"] + ("*" if p["말한다"] else "") for p in c["인물"]) or "—"
        mv = c["카메라"]["움직임"]
        if c["카메라"].get("밀림", 1) > 1.8:
            mv += " ⚑좁음"
        if len(c.get("움직임_후보") or []) > 1:
            mv += " ⚠%s" % "·".join(c["움직임_후보"])
        L.append("| %d | `%s` | %s | %d | %d–%d | %s | %dmm | %.1fm | %s |" % (
            i, c["id"], c["샷_ko"], c["초"], c["시작_프레임"], c["끝_프레임"],
            mv, c["카메라"]["렌즈_mm"], c["카메라"]["거리_m"], who))
    L += ["", "`*` 는 그 컷에서 말하는 인물이다. 카메라가 이 인물을 기준으로 잡혀 있다. "
          "`⚠` 는 대본이 카메라 움직임을 둘 말한 컷이라 블렌더에서 하나로 정해야 한다는 뜻이고, "
          "`⚑좁음` 은 인물이 다 들어가느라 카메라가 한참 뒤로 밀린 컷이다 — "
          "배치를 앞뒤로 접거나 샷을 풀샷으로 바꾼다.", "",
          "## 프레임 뽑기", "",
          "블렌더 Output 에서 PNG 로 두고, 컷마다 첫·끝 프레임만 뽑는다.", "",
          "```", "# 첫 프레임만 한 번에 뽑기 (터미널)",
          "blender -b <파일>.blend -o //previz/frames/#### -F PNG -f %s" % (
              ",".join(str(c["시작_프레임"]) for c in pv["컷"][:6]) + " ..."),
          "```", "",
          "파일 이름은 컷 ID 로 바꿔 둔다 — `SC1-01_시작.png`, `SC1-01_끝.png`.", ""]
    return "\n".join(L)


def one(base: Path, ep: str, spec: dict) -> tuple[int, int]:
    세로 = base.name == "shorts"
    prompts = base / ep / "prompts"
    chars = json.loads(bible.chars_path(prompts).read_text(encoding="utf-8"))
    meta = json.loads((base / ep / "episode.json").read_text(encoding="utf-8")) \
        if (base / ep / "episode.json").exists() else {}
    title = "%s 「%s」" % (meta.get("no", ep), meta.get("title", "")) if meta else ep

    pv = build(prompts, spec, chars, 세로)
    out = base / ep / "previz"
    out.mkdir(exist_ok=True)
    (out / "previz.json").write_text(
        json.dumps(pv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / ("블렌더_%s.py" % ep)).write_text(
        blender_script(pv, spec, chars, title), encoding="utf-8")
    (out / "프리비즈_작업지.md").write_text(worksheet(pv, title), encoding="utf-8")
    return pv["컷_수"], pv["총_프레임"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode", default="ep1")
    ap.add_argument("--root", help="episodes/ 대신 볼 폴더 (예: shorts)")
    ap.add_argument("--all", action="store_true", help="전 화 + 쇼츠 한꺼번에")
    args = ap.parse_args()

    spec = load("previz.json")
    targets = []
    if args.all:
        for root in ("episodes", "shorts"):
            base = ROOT / root
            if base.exists():
                targets += [(base, p.name) for p in sorted(base.iterdir())
                            if (p / "prompts" / "shots_v2.json").exists()]
    else:
        targets = [(ROOT / (args.root or "episodes"), args.episode)]

    for base, ep in targets:
        cuts, frames = one(base, ep, spec)
        print("%-8s 프리비즈 — %2d컷 / %4d프레임 / %5.1f초"
              % (ep, cuts, frames, frames / spec["fps"]))


if __name__ == "__main__":
    main()
