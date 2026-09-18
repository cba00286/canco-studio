# -*- coding: utf-8 -*-
"""T09 프리비즈 — 블렌더에서 실행한다.

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

SPEC = json.loads(r'''{"_comment": "scripts/build_previz.py 가 만든다. 손으로 고치지 말고 블렌더에서 고친 뒤 그 값을 여기 적거나, shots_v2.json 을 고치고 다시 돌린다.", "화": "T09", "fps": 30, "해상도": [1080, 1920], "비율": "9:16", "총_프레임": 690, "총_초": 23.0, "컷_수": 5, "장면": {"SH": "쇼츠 · 9화 예고 — 약속을 지켜요"}, "환경": {"SH": "꽃밭"}, "컷": [{"id": "T09-01", "section": "SH", "샷": "CU", "샷_ko": "클로즈업", "초": 4, "시작_프레임": 1, "끝_프레임": 120, "연결": "전환", "화자": "", "대사": "", "설명": "풀밭에 눌린 자국 세 개만 남아 있다. 꽃잎이 그 위로 떨어진다.", "움직임_설명": "카메라가 눌린 풀 자국 위를 천천히 지나가고 꽃잎이 내려앉는다.", "인물": [], "카메라": {"렌즈_mm": 85, "거리_m": 1.326, "타깃": [0.0, 0.0, 1.44], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.346, 1.472], "회전_deg": [88.638, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.326, 1.472], "회전_deg": [88.618, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T09-02", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 4, "시작_프레임": 121, "끝_프레임": 240, "연결": "연속", "화자": "", "대사": "", "설명": "루카가 언덕 꼭대기에서 숨이 턱에 찬 채 멈춰 선다. 빈 꽃밭 위로 노을이 붉다.", "움직임_설명": "호랑이가 헐떡이며 멈춰 서고 붉은 노을이 빈 꽃밭을 물들인다.", "인물": [{"이름": "루카", "키_m": 1.6, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 50, "거리_m": 1.86, "타깃": [0.0, 0.0, 1.152], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.888, 1.36], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.86, 1.36], "회전_deg": [83.619, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T09-03", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 5, "시작_프레임": 241, "끝_프레임": 390, "연결": "컷", "화자": "", "대사": "", "설명": "언덕 아래 마을 길로 친구들의 실루엣이 멀어진다. 루카는 그 자리에 무릎을 꿇는다.", "움직임_설명": "세 실루엣이 점점 작아지고 호랑이가 천천히 무릎을 꿇는다.", "인물": [{"이름": "루카", "키_m": 1.6, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 50, "거리_m": 1.86, "타깃": [0.0, 0.0, 1.152], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.888, 1.36], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.86, 1.36], "회전_deg": [83.619, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T09-04", "section": "SH", "샷": "WS", "샷_ko": "풀샷", "초": 5, "시작_프레임": 391, "끝_프레임": 540, "연결": "컷", "화자": "", "대사": "", "설명": "새벽. 루카가 미미의 집 앞에 혼자 서서 접힌 종이 세 장을 만지작거린다.", "움직임_설명": "호랑이가 문 앞에서 종이를 손에서 이리저리 돌리며 기다린다.", "인물": [{"이름": "루카", "키_m": 1.6, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 24, "거리_m": 4.32, "타깃": [0.0, 0.0, 0.88], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -4.385, 1.248], "회전_deg": [85.203, 0.0, 0.0]}, "끝": {"위치": [0.0, -4.32, 1.248], "회전_deg": [85.131, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "T09-05", "section": "SH", "샷": "타이틀", "샷_ko": "타이틀", "초": 5, "시작_프레임": 541, "끝_프레임": 690, "연결": "컷", "화자": "", "대사": "", "설명": "제목 카드. 꽃잎이 날리는 언덕 위 돗자리와 그 위에 덮인 채 놓인 만화책 한 권. 하단에 제목 자리가 비어 있다.", "움직임_설명": "제목이 천천히 떠오르고 화면이 아주 느리게 물러난다.", "인물": [], "카메라": {"렌즈_mm": 35, "거리_m": 4.62, "타깃": [0.0, 0.0, 0.96], "움직임": "상승", "밀림": 1.35, "시작": {"위치": [0.0, -4.851, 0.576], "회전_deg": [94.526, 0.0, 0.0]}, "끝": {"위치": [0.0, -4.62, 1.28], "회전_deg": [86.038, 0.0, 0.0]}}, "움직임_후보": ["상승", "후진"]}], "키": {"쿵쿵": 1.4, "루카": 1.6, "후안": 1.0, "미미": 1.05, "티니": 1.1, "루비": 1.2, "노을": 1.3}, "색": {"쿵쿵": [0.55, 0.85, 0.7], "루카": [0.55, 0.65, 0.9], "후안": [0.95, 0.75, 0.45], "미미": [0.9, 0.6, 0.8], "티니": [0.95, 0.9, 0.5], "루비": [0.95, 0.65, 0.72], "노을": [0.95, 0.55, 0.35]}}''')
FLOOR = json.loads(r'''{"기본": [0.5, 0.5, 0.5]}''')

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
