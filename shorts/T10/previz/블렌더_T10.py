# -*- coding: utf-8 -*-
"""T10 프리비즈 — 블렌더에서 실행한다.

블렌더 → Scripting 탭 → 이 파일을 열고 ▶ Run Script.
한 타임라인에 5컷이 순서대로 깔리고, 컷마다 카메라가 마커로 묶인다.
스페이스바를 누르면 23.0초짜리 프리비즈가 통째로 재생된다.

고치는 법
  · 구도가 마음에 안 드는 컷 → 타임라인에서 그 컷으로 가서 카메라를 움직인다.
    (N 패널에서 렌즈 mm 도 바꾼다)
  · 인물 위치 → 해당 컷 프레임에서 인물을 옮기고 I → Location 으로 키를 덮는다.
  · 컷 길이 → shots_v2.json 의 duration 을 고치고 build_previz.py 를 다시 돌린다.

이 스크립트는 아무것도 렌더하지 않고 아무것도 생성하지 않는다. 장면만 만든다.
"""
import bpy, json, math

SPEC = json.loads(r'''{"_comment": "scripts/build_previz.py 가 만든다. 손으로 고치지 말고 블렌더에서 고친 뒤 그 값을 여기 적거나, shots_v2.json 을 고치고 다시 돌린다.", "화": "T10", "fps": 30, "해상도": [1080, 1920], "비율": "9:16", "총_프레임": 690, "총_초": 23.0, "컷_수": 5, "장면": {"SH": "쇼츠 · 10화 예고 — 우리들의 첫 번째 파티"}, "환경": {"SH": "눈밭"}, "컷": [{"id": "T10-01", "section": "SH", "샷": "CU", "샷_ko": "클로즈업", "초": 4, "시작_프레임": 1, "끝_프레임": 120, "연결": "전환", "화자": "", "대사": "", "설명": "새로 얹은 나뭇잎 캐노피 모서리가 바람에 들썩이고 나무못 하나가 뽑히기 시작한다.", "움직임_설명": "캐노피 모서리가 반복해 들썩이고 못이 조금씩 밀려 나온다.", "인물": [], "카메라": {"렌즈_mm": 85, "거리_m": 1.326, "타깃": [0.0, 0.0, 1.44], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.346, 1.472], "회전_deg": [88.638, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.326, 1.472], "회전_deg": [88.618, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T10-02", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 4, "시작_프레임": 121, "끝_프레임": 240, "연결": "연속", "화자": "", "대사": "", "설명": "빗속. 쿵쿵이가 처마 밖으로 걸어 나가고 뒤에서 뻗은 손이 닿지 못한다.", "움직임_설명": "아기 공룡이 빗속으로 발을 내딛고 뒤에서 뻗은 앞발이 허공을 잡는다.", "인물": [{"이름": "쿵쿵", "키_m": 1.4, "위치": [-0.463, 0.18, 0.0], "방향_deg": 0.0, "말한다": true}, {"이름": "루카", "키_m": 1.6, "위치": [0.463, 0.18, 0.0], "방향_deg": -12.0, "말한다": false}], "카메라": {"렌즈_mm": 50, "거리_m": 4.241, "타깃": [0.0, 0.18, 1.008], "움직임": "정지", "밀림": 3.52, "시작": {"위치": [0.0, -4.124, 1.19], "회전_deg": [87.579, 0.0, 0.0]}, "끝": {"위치": [0.0, -4.061, 1.19], "회전_deg": [87.543, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T10-03", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 5, "시작_프레임": 241, "끝_프레임": 390, "연결": "컷", "화자": "", "대사": "", "설명": "빛의 돔 아래에서 쿵쿵이의 뒷다리가 떨리고 발이 진흙 속에서 밀려난다. 돔의 빛이 약해진다.", "움직임_설명": "다리가 떨리며 발이 뒤로 밀리고 돔의 빛이 깜빡이며 약해진다.", "인물": [{"이름": "쿵쿵", "키_m": 1.4, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 50, "거리_m": 1.628, "타깃": [0.0, 0.0, 1.008], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.652, 1.19], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.628, 1.19], "회전_deg": [83.621, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T10-04", "section": "SH", "샷": "WS", "샷_ko": "풀샷", "초": 5, "시작_프레임": 391, "끝_프레임": 540, "연결": "컷", "화자": "", "대사": "", "설명": "다섯이 빗속으로 달려 나와 쿵쿵이를 둘러싸고 등에 손을 얹는다.", "움직임_설명": "다섯이 차례로 손과 날개를 등에 얹고 돔의 빛이 살아난다.", "인물": [{"이름": "티니", "키_m": 1.1, "위치": [-0.807, 0.128, 0.0], "방향_deg": 12.0, "말한다": false}, {"이름": "후안", "키_m": 1.0, "위치": [-0.583, 0.943, 0.0], "방향_deg": 12.0, "말한다": false}, {"이름": "쿵쿵", "키_m": 1.4, "위치": [0.006, 0.001, 0.0], "방향_deg": 0.0, "말한다": true}, {"이름": "루카", "키_m": 1.6, "위치": [0.253, 0.89, 0.0], "방향_deg": -12.0, "말한다": false}, {"이름": "미미", "키_m": 1.05, "위치": [0.807, 0.128, 0.0], "방향_deg": -12.0, "말한다": false}, {"이름": "루비", "키_m": 1.2, "위치": [1.133, 1.03, 0.0], "방향_deg": -12.0, "말한다": false}], "카메라": {"렌즈_mm": 24, "거리_m": 3.78, "타깃": [0.0, 0.52, 0.77], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -3.317, 1.092], "회전_deg": [85.203, 0.0, 0.0]}, "끝": {"위치": [0.0, -3.26, 1.092], "회전_deg": [85.131, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T10-05", "section": "SH", "샷": "타이틀", "샷_ko": "타이틀", "초": 5, "시작_프레임": 541, "끝_프레임": 690, "연결": "컷", "화자": "", "대사": "", "설명": "제목 카드. 달빛 언덕 위 창에 불이 켜진 바위 집. 하단에 제목 자리가 비어 있다.", "움직임_설명": "제목이 천천히 떠오르고 화면이 아주 느리게 물러난다.", "인물": [], "카메라": {"렌즈_mm": 35, "거리_m": 4.62, "타깃": [0.0, 0.0, 0.96], "움직임": "상승", "밀림": 1.35, "시작": {"위치": [0.0, -4.851, 0.576], "회전_deg": [94.526, 0.0, 0.0]}, "끝": {"위치": [0.0, -4.62, 1.28], "회전_deg": [86.038, 0.0, 0.0]}}, "움직임_후보": ["상승", "후진"]}], "키": {"쿵쿵": 1.4, "루카": 1.6, "후안": 1.0, "미미": 1.05, "티니": 1.1, "루비": 1.2, "노을": 1.3}, "색": {"쿵쿵": [0.55, 0.85, 0.7], "루카": [0.55, 0.65, 0.9], "후안": [0.95, 0.75, 0.45], "미미": [0.9, 0.6, 0.8], "티니": [0.95, 0.9, 0.5], "루비": [0.95, 0.65, 0.72], "노을": [0.95, 0.55, 0.35]}}''')
FLOOR = json.loads(r'''{"눈밭": [0.86, 0.9, 0.95], "기본": [0.5, 0.5, 0.5]}''')

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
sc.render.engine = "BLENDER_WORKBENCH"
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

    mk = sc.timeline_markers.new("%s %s" % (cut["id"], cut["샷_ko"] or ""), frame=f0)
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
print("프리비즈 완성 — %d컷 / %d프레임 / %.1f초"
      % (len(SPEC["컷"]), SPEC["총_프레임"], SPEC["총_프레임"] / fps))
