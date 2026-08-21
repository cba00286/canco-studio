# -*- coding: utf-8 -*-
"""「쿵쿵이와 친구들」 1화 생성기 — 파일 하나로 끝나는 버전.

윈도우 명령 프롬프트에서:

    pip install gradio_client imageio-ffmpeg
    set HF_TOKEN=여기에_토큰            (토큰 없어도 동작하지만 대기열이 깁니다)
    python kungkung_generator.py all

    scenes    씬 그림 12장  (실제로 영상이 될 장면들)
    videos    씬별 4~5초 영상 클립  (scenes 먼저 실행)
    assemble  클립을 순서대로 이어붙여 한 편으로 (episode1.mp4)
    all       scenes → videos → assemble 을 한 번에

    chars     캐릭터 설정화 6장 (참고용. 공식 아트가 있으면 안 돌려도 됩니다)

뒤에 이름을 붙이면 그것만 만듭니다. 무료 쿼터가 적을 때 유용합니다.

    python kungkung_generator.py scenes S5 S0        (두 장면만)
    python kungkung_generator.py videos S5           (한 클립만)

무료 쿼터가 부족하면 더 가벼운 이미지 Space로 바꿔볼 수 있습니다.

    set IMAGE_SPACE=evalstate/flux1_schnell
    python kungkung_generator.py scenes S5

결과물은 이 파일 옆에 만들어지는 kungkung_outputs 폴더에 저장됩니다.
같은 이름의 파일이 이미 있으면 건너뜁니다. 다시 뽑고 싶으면 그 파일을 지우세요.
"""

import os
import shutil
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent / "kungkung_outputs"

# 이미지 Space는 환경변수로 바꿀 수 있다. 무료 쿼터가 빠듯할 때 더 가벼운 Space를 쓰기 위함이다.
#   set IMAGE_SPACE=evalstate/flux1_schnell
SPACE_IMAGE = os.environ.get("IMAGE_SPACE") or "mcp-tools/Qwen-Image-Fast"
SPACE_VIDEO = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"

MAX_RETRIES = 4
BACKOFF = [5, 10, 20, 40]


STYLE = '3D Pixar/DreamWorks style animated film still, soft studio lighting, high detail fur and scale texture, warm color grading, family animation movie quality, 16:9 cinematic composition'

NEGATIVE = 'text, watermark, signature, copyright, blurry, low resolution, deformed, extra limbs, scary, photorealistic human'

FRAGMENTS = {
    '쿵쿵_파워': 'his three horns and neck frill flaring with faint golden-teal meteor light while a visible shockwave ripple spreads outward from where his front paws strike the ground',
    '유성빛': 'faint golden-teal meteor light, the same hue as the aurora',
}

CHARACTERS = {
    '쿵쿵': {
        'id': 'kungkung',
        'seed': 12001,
        'desc': 'a baby triceratops named Kung-Kung, soft pastel mint-green scaly skin with a cream-colored belly and muzzle, three small peach-colored horns (two above the eyes, one on the snout), a low beige neck frill with softly rounded scallops, very large sparkling green-hazel eyes with bright catchlights, blush pink cheeks, an ivory bandana scarf with a colorful tropical floral pattern tied around the neck, chubby rounded body, short stubby legs, cheerful open smile',
        'desc_short': 'Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, standing in a confident signature pose with both front paws on hips, three-quarter front view',
    },
    '루카': {
        'id': 'luca',
        'seed': 12002,
        'desc': 'a baby tiger cub named Luca, bright orange fur with dark brown stripes, cream-colored face and belly, brown aviator goggles pushed up on the forehead, blue denim overalls, energetic wide grin',
        'desc_short': 'Luca the orange baby tiger cub in denim overalls with aviator goggles on his forehead',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, standing with one paw waving, three-quarter front view',
    },
    '몽이': {
        'id': 'mongi',
        'seed': 12003,
        'desc': 'a baby penguin named Mong-i, glossy black and white feathers, a red beanie hat with a small propeller, tiny flippers, dreamy wide eyes',
        'desc_short': 'Mong-i the baby penguin in a red beanie hat',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, standing with flippers slightly spread, three-quarter front view',
    },
    '소미': {
        'id': 'somi',
        'seed': 12004,
        'desc': 'a baby rabbit named Somi, pale pink fur, long soft ears, a tiny pink neckerchief, holding a small sparkly trinket wand, gentle shy expression',
        'desc_short': 'Somi the pale pink baby rabbit with long ears holding a sparkly trinket',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, standing while holding the sparkly trinket, three-quarter front view',
    },
    '두리': {
        'id': 'duri',
        'seed': 12005,
        'desc': 'a baby koala named Duri, soft gray fur with a cream chest, round wire glasses, a small satchel over one shoulder, calm composed expression',
        'desc_short': 'Duri the gray baby koala with round glasses',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, standing calmly adjusting the glasses, three-quarter front view',
    },
    '초코': {
        'id': 'choco',
        'seed': 12006,
        'desc': 'a baby golden retriever puppy named Choco, golden-tan fluffy fur, wearing a small brown bandana, floppy ears, cheerful sniffing pose with wagging tail',
        'desc_short': 'Choco the golden-tan baby retriever puppy in a brown bandana',
        'ref_prompt': 'full-body character reference sheet on a soft neutral pastel background, cheerful sniffing pose, three-quarter front view',
    },
}

SCENES = [
    {
        'id': 'S0',
        'title': '프롤로그 — 남극의 밤, 떨어지는 유성',
        'seed': 20001,
        'duration': 4,
        'image': 'a vast moonlit Antarctic ice field under a swirling green aurora, a brilliant meteor streaking down through the night sky trailing golden-teal fire and sparks, the last moment before impact, epic wide establishing shot, cold blue palette pierced by warm meteor light',
        'motion': 'The meteor streaks across the sky trailing sparks, the aurora ripples overhead, the camera slowly tilts down following it toward the ice field, fine snow crystals drifting through the air',
    },
    {
        'id': 'S0B',
        'title': '크레이터 속의 알 — 생명이 깨어나다',
        'seed': 20002,
        'duration': 5,
        'image': 'a huge crater blasted into the Antarctic ice, steam rising from glowing meteor fragments at the bottom, embedded in the translucent crater wall a large pale egg with {유성빛} seeping into it and pulsing inside like a slow heartbeat, hushed and awe-inspiring, medium wide shot, cold blue ice against a warm glowing core',
        'motion': 'Steam drifts up from the glowing fragments, waves of golden-teal light ripple outward through the ice and sink into the egg, the egg answers with a slow pulse of light like a first heartbeat, camera pushes in slowly',
    },
    {
        'id': 'S0C',
        'title': '표류 — 바다를 건너',
        'seed': 20003,
        'duration': 5,
        'image': 'a massive block of ice carrying the faintly glowing egg breaking away from a melting Antarctic ice cliff and drifting out into a starlit ocean, distant aurora on the horizon, the ice block tiny against the vast sea, lonely epic long shot, moonlight scattered on the water',
        'motion': "The ice cliff cracks and the block calves into the sea with a great splash, then drifts away across the moonlit water, long swells rolling past, the egg's glow pulsing faintly within, camera pulls back to reveal the vast ocean",
    },
    {
        'id': 'S1',
        'title': '숲속 공터',
        'seed': 21001,
        'duration': 4,
        'image': 'five baby forest animal friends playing tag in a sunny forest clearing — [루카], [소미], [두리], [초코], and [몽이] — warm afternoon sunlight, lush green grass, wildflowers, joyful motion, cinematic wide shot',
        'motion': 'Camera slowly pans right following the animals as they run and laugh, gentle bouncing character motion, leaves rustling in the wind, soft natural lighting',
    },
    {
        'id': 'S2',
        'title': '강물 위 거대한 얼음덩어리',
        'seed': 21002,
        'duration': 5,
        'image': 'dark storm clouds rolling in over a forest river, heavy rain, a massive ice block glowing faintly from within carried up the swollen river from the distant sea, a dramatic lightning flash in the background, five baby animal friends — [루카], [소미], [두리], [초코], and [몽이] — pointing in surprise from the riverbank, cinematic dramatic lighting',
        'motion': 'Camera pushes in slowly toward the ice block as it drifts closer, rain falling continuously, a distant lightning flash illuminates the scene, water ripples and splashes, tense atmospheric motion',
    },
    {
        'id': 'S3',
        'title': '얼음 속에서 발견한 알',
        'seed': 21003,
        'duration': 4,
        'image': 'close-up of a large egg glowing with {유성빛} inside a translucent ice block lodged against riverbank rocks, five baby animal friends — [루카], [소미], [두리], [초코], and [몽이] — gathered around looking amazed, rain still falling lightly, warm hopeful light against the dark storm',
        'motion': 'Slow dolly-in toward the ice block, a subtle pulsing glow from within the egg synced with a faint heartbeat rhythm, the characters lean in closer with wonder',
    },
    {
        'id': 'S4',
        'title': '몸으로 얼음을 녹여주는 밤',
        'seed': 21004,
        'duration': 5,
        'image': 'five baby animal friends — [루카], [소미], [두리], [초코], and [몽이] — curled up together embracing a large ice block under a big tree at night, gentle moonlight, rain lightly falling, peaceful sleeping poses, warm emotional tone, soft blue-and-gold night lighting',
        'motion': "Very slow time-lapse style motion, the ice block subtly melting with dripping water, the characters' breathing motion while asleep, moonlight flickering through the clouds",
    },
    {
        'id': 'S5',
        'title': '새벽, 알이 깨어나는 순간 (하이라이트)',
        'seed': 21005,
        'duration': 5,
        'image': 'dramatic sunrise breaking through storm clouds, a cracking egg shell bursting open, {쿵쿵} emerging with mouth open in a joyful first cry, {유성빛} flickering briefly across his horns, golden sunrise backlight creating a glowing rim-light silhouette, five baby animal friends watching in awe with tears of joy, epic emotional composition, wide shot',
        'motion': "The egg shell cracks and bursts open in slow motion, the baby triceratops' head emerges and looks up at the sunrise, a brief teal shimmer runs across his horns, camera slowly cranes upward revealing the full triumphant moment, golden light rays sweep across the frame",
    },
    {
        'id': 'S6',
        'title': '첫 걸음, 그리고 이름 — "쿵쿵!"',
        'seed': 21006,
        'duration': 4,
        'image': "{쿵쿵} taking his very first step in front of [루카] and the friends, his foot landing with a heavy thump that puffs a small ring of dust and leaves outward, {쿵쿵_파워}, the friends' eyes wide with surprise and delight, morning sunlight, cheerful group shot, tender friendship moment",
        'motion': 'The baby triceratops wobbles, plants one foot down with a heavy thump that sends a ring of dust puffing outward and shakes the leaves overhead, the friends jump in surprise then burst out laughing, the tiger cub claps and cheers, warm morning light flickers through the branches',
    },
    {
        'id': 'S7',
        'title': '아직 서툰 힘 — 숲속 소동',
        'seed': 21007,
        'duration': 4,
        'image': '{쿵쿵} tripping over a tree root on a sunlit forest path, the tumble sending a thump through the ground that shakes the trees and rains berries and leaves down over [초코] and [몽이], [루카] and [소미] laughing while [두리] watches and takes notes, dappled sunlight, comedic mid-shot',
        'motion': 'The baby triceratops trips and tumbles, the ground thumps and the trees shake, berries and leaves rain down burying the puppy and the penguin, everyone laughs, the koala scribbles a note, dappled sunlight drifting across the frame',
    },
    {
        'id': 'S8',
        'title': '개울가 구조 — 처음으로 힘이 누군가를 지키다',
        'seed': 21008,
        'duration': 5,
        'image': '{쿵쿵} slamming both front paws down on a rocky stream bank, {쿵쿵_파워}, a fallen log toppling across the rushing water to block the current as [소미] is swept toward it and grabs on safely, spray flying, brave determined expression, dynamic action composition, warm daytime lighting',
        'motion': 'The baby triceratops charges to the bank and slams both paws down, a shockwave ripples out and topples the log across the stream, the rabbit is swept against it and grabs on, water sprays up catching the sunlight, the other friends rush in cheering',
    },
    {
        'id': 'ENDING',
        'title': '노을 지는 언덕',
        'seed': 21009,
        'duration': 5,
        'image': 'six baby animal friends sitting together on a hilltop watching a warm orange sunset — [루카], [소미], [두리], [초코], [몽이] and {쿵쿵} — silhouette composition, the baby triceratops standing with front paws on hips in a signature confident pose, heartwarming finale shot',
        'motion': 'Camera slowly pulls back to reveal the full group silhouetted against the sunset, gentle wind moves the grass and fur, the triceratops strikes his signature pose, warm glowing light',
    },
]


# ------------------------------------------------------------------ 프롬프트 조립

def expand(template):
    """{이름}은 전체 묘사, [이름]은 축약 묘사, 캐릭터가 아니면 FRAGMENTS에서 찾는다."""
    import re

    def lookup(name, key):
        entry = CHARACTERS.get(name)
        if entry is not None:
            return entry.get(key) or entry["desc"]
        fragment = FRAGMENTS.get(name)
        if fragment is None:
            raise KeyError("알 수 없는 이름: " + name)
        return fragment

    template = re.sub(r"\{([^{}]+)\}", lambda m: lookup(m.group(1), "desc"), template)
    return re.sub(r"\[([^\[\]]+)\]", lambda m: lookup(m.group(1), "desc_short"), template)


# ------------------------------------------------------------------ Space 호출

def make_client(space):
    from gradio_client import Client
    import inspect

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        print("  * HF_TOKEN이 없어 익명으로 접속합니다. 대기열이 길 수 있습니다.")
    print("  * 접속 중: " + space)
    # 토큰 인자 이름이 gradio_client 버전에 따라 token / hf_token으로 다르다.
    kwargs = {}
    if token:
        params = inspect.signature(Client.__init__).parameters
        kwargs["token" if "token" in params else "hf_token"] = token
    return Client(space, **kwargs)


def resolve_endpoint(client, keywords):
    """Space가 업데이트돼도 죽지 않도록 실제 엔드포인트와 파라미터를 읽어온다."""
    api = client.view_api(return_format="dict", print_info=False)
    named = api.get("named_endpoints", {}) or {}
    if not named:
        raise RuntimeError("호출 가능한 엔드포인트가 없습니다: " + str(api)[:200])
    chosen = None
    for name in named:
        if any(k in name.lower() for k in keywords):
            chosen = name
            break
    if chosen is None:
        chosen = next(iter(named))
    params = set()
    for p in named[chosen].get("parameters", []):
        if p.get("parameter_name"):
            params.add(p["parameter_name"])
    print("  * 엔드포인트: " + chosen)
    return chosen, params


def call_with_retry(client, api_name, allowed, kwargs):
    payload = {k: v for k, v in kwargs.items() if not allowed or k in allowed}
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            return client.predict(api_name=api_name, **payload)
        except Exception as exc:
            last = exc
            message = str(exc)
            if "quota" in message.lower():
                # 쿼터 초과는 몇 초 기다린다고 풀리지 않는다. 즉시 알리고 멈춘다.
                print("\n  !! ZeroGPU 무료 쿼터를 다 쓰셨습니다.")
                print("     " + message.strip().splitlines()[0])
                print("     쿼터가 회복된 뒤 같은 명령을 다시 실행하면,")
                print("     이미 만들어진 파일은 건너뛰고 남은 것부터 이어서 진행합니다.")
                raise SystemExit(1)
            wait = BACKOFF[min(attempt, len(BACKOFF) - 1)]
            print("    ! 실패 %d/%d: %s" % (attempt + 1, MAX_RETRIES, exc))
            print("      %d초 후 다시 시도합니다" % wait)
            time.sleep(wait)
    raise RuntimeError("%d번 시도했지만 실패했습니다: %s" % (MAX_RETRIES, last))


def first_path(item):
    if isinstance(item, str):
        return item if os.path.exists(item) else None
    if isinstance(item, dict):
        for key in ("path", "video", "url", "name"):
            found = first_path(item.get(key))
            if found:
                return found
    if isinstance(item, (list, tuple)):
        for sub in item:
            found = first_path(sub)
            if found:
                return found
    return None


def take_file(result):
    path = first_path(result)
    if not path:
        raise RuntimeError("결과에서 파일을 찾지 못했습니다: " + repr(result)[:300])
    return path


# ------------------------------------------------------------------ 실행 단계

ONLY = []          # 실행할 대상만 담는다. 비어 있으면 전부.


def wanted(name):
    return not ONLY or name in ONLY


def step_chars():
    folder = OUT / "characters"
    folder.mkdir(parents=True, exist_ok=True)
    client = make_client(SPACE_IMAGE)
    api_name, allowed = resolve_endpoint(client, ("generate", "image", "predict", "infer"))

    for name, entry in CHARACTERS.items():
        if not wanted(name):
            continue
        dest = folder / (entry["id"] + ".png")
        if dest.exists():
            print("  = %s: 이미 있음, 건너뜀" % name)
            continue
        prompt = "%s, %s, %s" % (STYLE, entry["ref_prompt"], entry["desc"])
        print("  > %s 생성 중..." % name)
        result = call_with_retry(client, api_name, allowed, {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "width": 1280,
            "height": 720,
            "negative_prompt": NEGATIVE,
            "seed": entry["seed"],
            "randomize_seed": False,
            "num_inference_steps": 8,
        })
        shutil.copy(take_file(result), str(dest))
        print("    저장: %s" % dest)


def step_scenes():
    folder = OUT / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    client = make_client(SPACE_IMAGE)
    api_name, allowed = resolve_endpoint(client, ("generate", "image", "predict", "infer"))

    for scene in SCENES:
        if not wanted(scene["id"]):
            continue
        dest = folder / (scene["id"] + ".png")
        if dest.exists():
            print("  = %s: 이미 있음, 건너뜀" % scene["id"])
            continue
        print("  > %s %s 생성 중..." % (scene["id"], scene["title"]))
        result = call_with_retry(client, api_name, allowed, {
            "prompt": "%s, %s" % (STYLE, expand(scene["image"])),
            "aspect_ratio": "16:9",
            "width": 1280,
            "height": 720,
            "negative_prompt": NEGATIVE,
            "seed": scene["seed"],
            "randomize_seed": False,
            "num_inference_steps": 8,
        })
        shutil.copy(take_file(result), str(dest))
        print("    저장: %s" % dest)


def step_videos():
    from gradio_client import handle_file

    folder = OUT / "videos"
    folder.mkdir(parents=True, exist_ok=True)
    client = make_client(SPACE_VIDEO)
    api_name, allowed = resolve_endpoint(client, ("video", "generate", "predict"))

    for scene in SCENES:
        if not wanted(scene["id"]):
            continue
        keyframe = OUT / "scenes" / (scene["id"] + ".png")
        dest = folder / (scene["id"] + ".mp4")
        if dest.exists():
            print("  = %s: 이미 있음, 건너뜀" % scene["id"])
            continue
        if not keyframe.exists():
            print("  ! %s: 키프레임이 없습니다. 먼저 scenes를 실행하세요." % scene["id"])
            continue
        print("  > %s 영상 %d초 생성 중... (몇 분 걸립니다)" % (scene["id"], scene["duration"]))
        result = call_with_retry(client, api_name, allowed, {
            "input_image": handle_file(str(keyframe)),
            "prompt": scene["motion"],
            "negative_prompt": NEGATIVE,
            "duration_seconds": scene["duration"],
            "steps": 6,
            "seed": scene["seed"],
            "randomize_seed": False,
        })
        shutil.copy(take_file(result), str(dest))
        print("    저장: %s" % dest)



# ------------------------------------------------------------------ 편집(이어붙이기)

def find_ffmpeg():
    """시스템 ffmpeg를 먼저 찾고, 없으면 pip 패키지에 동봉된 것을 쓴다."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def step_assemble():
    import subprocess

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("  ! ffmpeg가 없습니다.  pip install imageio-ffmpeg  실행 후 다시 시도하세요.")
        return

    clips = []
    missing = []
    for scene in SCENES:
        clip = OUT / "videos" / (scene["id"] + ".mp4")
        (clips if clip.exists() else missing).append(clip if clip.exists() else scene["id"])
    if missing:
        print("  ! 아직 없는 클립: %s" % ", ".join(missing))
        print("    먼저 videos를 끝까지 실행하세요.")
        if not clips:
            return
        print("  * 있는 클립 %d개만 이어붙입니다." % len(clips))

    listfile = OUT / "filelist.txt"
    with open(listfile, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write("file '%s'\n" % str(clip.resolve()).replace("\\", "/"))

    raw = OUT / "episode1.mp4"
    print("  > %d개 클립을 이어붙입니다..." % len(clips))
    # 클립마다 인코딩이 다를 수 있어 -c copy 대신 재인코딩으로 안전하게 붙인다.
    subprocess.run([
        ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(listfile), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(raw),
    ], check=True)
    print("    저장: %s" % raw)

    theme = OUT / "theme_song.mp3"
    if theme.exists():
        final = OUT / "episode1_music.mp4"
        print("  > 배경음악을 입힙니다...")
        subprocess.run([
            ffmpeg, "-y", "-loglevel", "error", "-i", str(raw), "-i", str(theme),
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(final),
        ], check=True)
        print("    저장: %s" % final)
    else:
        print("  * 배경음악 없음. %s 에 mp3를 두고 assemble을 다시 실행하면 입혀집니다." % theme)


STEPS = {
    "chars": step_chars,
    "scenes": step_scenes,
    "videos": step_videos,
    "assemble": step_assemble,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in list(STEPS) + ["all"]:
        print(__doc__)
        return 1
    try:
        import gradio_client  # noqa: F401
    except ImportError:
        print("먼저 설치가 필요합니다:  pip install gradio_client")
        return 1

    global ONLY
    ONLY = sys.argv[2:]
    if ONLY:
        print("* 지정한 대상만 실행합니다: " + ", ".join(ONLY))

    names = ["scenes", "videos", "assemble"] if sys.argv[1] == "all" else [sys.argv[1]]
    for name in names:
        print("\n=== %s ===" % name)
        STEPS[name]()
    print("\n완료. 결과물 위치: %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
