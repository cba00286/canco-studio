# -*- coding: utf-8 -*-
"""D03 프리비즈 — 블렌더에서 실행한다.

블렌더 → Scripting 탭 → 이 파일을 열고 ▶ Run Script.
한 타임라인에 7컷이 순서대로 깔리고, 컷마다 카메라가 마커로 묶인다.
스페이스바를 누르면 30.0초짜리 프리비즈가 통째로 재생된다.

고치는 법
  · 구도가 마음에 안 드는 컷 → 타임라인에서 그 컷으로 가서 카메라를 움직인다.
    (N 패널에서 렌즈 mm 도 바꾼다)
  · 인물 위치 → 해당 컷 프레임에서 인물을 옮기고 I → Location 으로 키를 덮는다.
  · 컷 길이 → shots_v2.json 의 duration 을 고치고 build_previz.py 를 다시 돌린다.

이 스크립트는 아무것도 렌더하지 않고 아무것도 생성하지 않는다. 장면만 만든다.
"""
import bpy, json, math

SPEC = json.loads(r'''{"_comment": "scripts/build_previz.py 가 만든다. 손으로 고치지 말고 블렌더에서 고친 뒤 그 값을 여기 적거나, shots_v2.json 을 고치고 다시 돌린다.", "화": "D03", "fps": 30, "해상도": [1080, 1920], "비율": "9:16", "총_프레임": 900, "총_초": 30.0, "컷_수": 7, "장면": {"SH": "쇼츠 · 쿵쿵이의 오늘 한마디 · 9화"}, "환경": {"SH": "꽃밭"}, "컷": [{"id": "D03-01", "section": "SH", "샷": "CU", "샷_ko": "클로즈업", "초": 4, "시작_프레임": 1, "끝_프레임": 120, "연결": "전환", "화자": "", "대사": "", "설명": "쿵쿵이가 화면 아래에서 쏙 올라와 정면을 본다. 배경은 단순한 한 색이다.", "움직임_설명": "아기 공룡이 프레임 아래에서 위로 올라와 카메라를 본다.", "인물": [{"이름": "쿵쿵", "키_m": 1.4, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 85, "거리_m": 1.16, "타깃": [0.0, 0.0, 1.26], "움직임": "상승", "밀림": 1.35, "시작": {"위치": [0.0, -1.218, 0.58], "회전_deg": [119.174, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.16, 1.288], "회전_deg": [88.617, 0.0, 0.0]}}, "움직임_후보": ["상승"]}, {"id": "D03-02", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 4, "시작_프레임": 121, "끝_프레임": 240, "연결": "전환", "화자": "", "대사": "", "설명": "미미가 손가락 세 개를 펴 보이고, 루카가 가슴을 두드리며 자신 있게 웃는다.", "움직임_설명": "코알라가 손가락 셋을 펴 보이고 호랑이가 가슴을 툭툭 친다.", "인물": [{"이름": "티니", "키_m": 1.1, "위치": [-0.367, 0.092, 0.0], "방향_deg": 12.0, "말한다": false}, {"이름": "루카", "키_m": 1.6, "위치": [-0.165, 0.892, 0.0], "방향_deg": 0.0, "말한다": true}, {"이름": "미미", "키_m": 1.05, "위치": [0.367, 0.092, 0.0], "방향_deg": -12.0, "말한다": false}, {"이름": "루비", "키_m": 1.2, "위치": [0.715, 1.03, 0.0], "방향_deg": -12.0, "말한다": false}], "카메라": {"렌즈_mm": 50, "거리_m": 4.722, "타깃": [0.0, 0.526, 1.152], "움직임": "정지", "밀림": 3.43, "시작": {"위치": [0.0, -4.267, 1.36], "회전_deg": [87.515, 0.0, 0.0]}, "끝": {"위치": [0.0, -4.196, 1.36], "회전_deg": [87.478, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "D03-03", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 4, "시작_프레임": 241, "끝_프레임": 360, "연결": "컷", "화자": "", "대사": "", "설명": "루카가 침대에 엎드려 만화책에 빠져 있다. 창밖 빛이 하얀색에서 주황색으로 물든다.", "움직임_설명": "페이지가 빠르게 넘어가고 창으로 드는 빛이 점점 붉어진다.", "인물": [{"이름": "루카", "키_m": 1.6, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 50, "거리_m": 1.86, "타깃": [0.0, 0.0, 1.152], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.888, 1.36], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.86, 1.36], "회전_deg": [83.619, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "D03-04", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 4, "시작_프레임": 361, "끝_프레임": 480, "연결": "컷", "화자": "", "대사": "", "설명": "텅 빈 꽃밭. 풀밭에 눌린 자국 세 개만 남아 있고 노을이 붉다.", "움직임_설명": "빈 꽃밭 위로 꽃잎이 날리고 눌린 풀 자국 위에 내려앉는다.", "인물": [], "카메라": {"렌즈_mm": 50, "거리_m": 1.86, "타깃": [0.0, 0.0, 1.152], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.888, 1.36], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.86, 1.36], "회전_deg": [83.619, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "D03-05", "section": "SH", "샷": "WS", "샷_ko": "풀샷", "초": 5, "시작_프레임": 481, "끝_프레임": 630, "연결": "컷", "화자": "", "대사": "", "설명": "다음 날 오후. 루카가 돗자리에 혼자 먼저 앉아 길을 지켜보고, 셋이 언덕을 넘어온다.", "움직임_설명": "호랑이가 돗자리에서 벌떡 일어나 두 팔을 흔들고 셋이 언덕 위로 올라온다.", "인물": [{"이름": "티니", "키_m": 1.1, "위치": [-0.367, 0.092, 0.0], "방향_deg": 12.0, "말한다": false}, {"이름": "루카", "키_m": 1.6, "위치": [-0.165, 0.892, 0.0], "방향_deg": 0.0, "말한다": true}, {"이름": "미미", "키_m": 1.05, "위치": [0.367, 0.092, 0.0], "방향_deg": -12.0, "말한다": false}, {"이름": "루비", "키_m": 1.2, "위치": [0.715, 1.03, 0.0], "방향_deg": -12.0, "말한다": false}], "카메라": {"렌즈_mm": 24, "거리_m": 4.32, "타깃": [0.0, 0.526, 0.88], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -3.858, 1.248], "회전_deg": [85.202, 0.0, 0.0]}, "끝": {"위치": [0.0, -3.794, 1.248], "회전_deg": [85.131, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "D03-06", "section": "SH", "샷": "MS", "샷_ko": "미디엄샷", "초": 5, "시작_프레임": 631, "끝_프레임": 780, "연결": "전환", "화자": "쿵쿵", "대사": "시간 약속은 친구 사이의 가장 소중한 신뢰야!", "설명": "쿵쿵이가 정면을 보고 두 앞발을 허리에 얹은 시그니처 포즈를 취한다. 하단에 자막 자리를 비운다.", "움직임_설명": "아기 공룡이 자세를 잡고 가슴을 펴며 카메라를 향해 환하게 웃는다.", "인물": [{"이름": "쿵쿵", "키_m": 1.4, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 50, "거리_m": 1.628, "타깃": [0.0, 0.0, 1.008], "움직임": "정지", "밀림": 1.35, "시작": {"위치": [0.0, -1.652, 1.19], "회전_deg": [83.713, 0.0, 0.0]}, "끝": {"위치": [0.0, -1.628, 1.19], "회전_deg": [83.621, 0.0, 0.0]}}, "움직임_후보": []}, {"id": "D03-07", "section": "SH", "샷": "타이틀", "샷_ko": "타이틀", "초": 4, "시작_프레임": 781, "끝_프레임": 900, "연결": "컷", "화자": "", "대사": "", "설명": "엔드 카드. 쿵쿵이가 손을 흔든다. 하단에 채널 이름을 넣을 여백.", "움직임_설명": "아기 공룡이 앞발을 흔들고 화면이 아주 느리게 물러난다.", "인물": [{"이름": "쿵쿵", "키_m": 1.4, "위치": [0.0, 0.0, 0.0], "방향_deg": 0.0, "말한다": true}], "카메라": {"렌즈_mm": 35, "거리_m": 4.043, "타깃": [0.0, 0.0, 0.84], "움직임": "후진", "밀림": 1.35, "시작": {"위치": [0.0, -4.043, 1.12], "회전_deg": [86.038, 0.0, 0.0]}, "끝": {"위치": [0.0, -5.255, 1.12], "회전_deg": [86.95, 0.0, 0.0]}}, "움직임_후보": ["후진"]}], "키": {"쿵쿵": 1.4, "루카": 1.6, "후안": 1.0, "미미": 1.05, "티니": 1.1, "루비": 1.2, "노을": 1.3}, "색": {"쿵쿵": [0.55, 0.85, 0.7], "루카": [0.55, 0.65, 0.9], "후안": [0.95, 0.75, 0.45], "미미": [0.9, 0.6, 0.8], "티니": [0.95, 0.9, 0.5], "루비": [0.95, 0.65, 0.72], "노을": [0.95, 0.55, 0.35]}}''')
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
