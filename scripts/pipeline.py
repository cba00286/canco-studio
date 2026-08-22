#!/usr/bin/env python3
"""「쿵쿵이와 친구들」 1화 AI 영상 제작 파이프라인.

Hugging Face Space(Gradio) API를 호출해 캐릭터 레퍼런스 → 씬 키프레임 →
이미지→영상 클립까지 생성하고, ffmpeg로 한 편으로 이어붙인다.

사용 예:
    export HF_TOKEN=hf_xxxx
    python3 scripts/pipeline.py all
    python3 scripts/pipeline.py scenes --only S5 S6
    python3 scripts/pipeline.py chars --dry-run          # 네트워크 없이 프롬프트만 확인
    python3 scripts/pipeline.py all --episode ep2        # 다른 화 작업
    python3 scripts/pipeline.py all --shots shots.json   # 정식 1화 전체(128컷)

Space의 Gradio 파라미터명은 업데이트로 바뀔 수 있으므로, 이 스크립트는 호출 직전
view_api()로 실제 엔드포인트/파라미터를 읽어 존재하는 인자만 전달한다.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EPISODE = "ep1"


def set_episode(episode: str) -> None:
    """작업 대상 화(episode)를 정하고 입출력 경로를 그에 맞춘다.

    한 저장소에서 여러 화를 제작하므로 프롬프트와 결과물은 episodes/<화>/ 아래에 두고,
    파이프라인 스크립트만 저장소 최상단에서 공유한다.
    """
    global EPISODE, EP_ROOT, PROMPTS, OUT, CHAR_DIR, SCENE_DIR, VIDEO_DIR, MANIFEST
    EPISODE = episode
    EP_ROOT = ROOT / "episodes" / episode
    PROMPTS = EP_ROOT / "prompts"
    OUT = EP_ROOT / "outputs"
    CHAR_DIR = OUT / "characters"
    SCENE_DIR = OUT / "scenes"
    VIDEO_DIR = OUT / "videos"
    MANIFEST = OUT / "manifest.json"


set_episode(DEFAULT_EPISODE)

# 용도별 Space. --image-space / --video-space 로 교체 가능.
SPACE_IMAGE_FAST = "mcp-tools/Qwen-Image-Fast"
SPACE_IMAGE_HQ = "mcp-tools/Qwen-Image"
SPACE_IMAGE_ALT = "evalstate/flux1_schnell"
SPACE_VIDEO = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"

MAX_RETRIES = 4
BACKOFF = [2, 4, 8, 16]


# ---------------------------------------------------------------- 프롬프트 조립

def load_prompts(shots_file: str = "scenes.json") -> tuple[dict, dict]:
    """캐릭터 묘사와 컷 목록을 읽는다.

    컷 목록은 두 종류다. scenes.json은 12컷짜리 요약본(프로토타입·티저용),
    shots.json은 확정 대본을 4~5초 단위로 분해한 128컷 정식 1화 분량이다.
    두 파일의 항목 구조가 조금 달라 여기서 하나로 맞춘다.
    """
    chars = json.loads((PROMPTS / "characters.json").read_text(encoding="utf-8"))
    data = json.loads((PROMPTS / shots_file).read_text(encoding="utf-8"))

    if "shots" in data:
        sections = data.get("sections", {})
        scenes = {"scenes": [
            {
                "id": shot["id"],
                "title": f'{sections.get(shot.get("section"), "")} {shot.get("shot", "")}'.strip(),
                "seed": shot["seed"],
                "duration": shot["duration"],
                "image": shot["image"],
                "image_ref": shot.get("image_ref", ""),
                "cast": shot.get("cast", []),
                "motion": shot["motion"],
                "dialogue": shot.get("dialogue", ""),
            }
            for shot in data["shots"]
        ]}
    else:
        scenes = data
    return chars, scenes


def expand(template: str, chars: dict) -> str:
    """{루카}는 전체 묘사(desc), [루카]는 축약 묘사(desc_short)로 치환한다.

    등장인물이 많은 씬에서 전체 묘사를 6번 반복하면 프롬프트가 200단어를 넘어
    핵심 연출이 희석된다. 주인공만 전체 묘사, 나머지는 축약 묘사를 쓴다.

    캐릭터가 아닌 이름은 fragments에서 찾는다({쿵쿵_파워}처럼 여러 씬에
    동일하게 등장해야 하는 연출 조각을 한 곳에서 관리한다).
    """
    def lookup(name: str, key: str) -> str:
        entry = chars["characters"].get(name)
        if entry is not None:
            return entry.get(key) or entry["desc"]
        # 캐릭터가 아니면 공용 묘사 조각(fragments)에서 찾는다.
        # 능력 발동 연출처럼 여러 씬에 똑같이 나와야 하는 표현을 한 곳에서 관리하기 위함이다.
        fragment = chars.get("fragments", {}).get(name)
        if fragment is None:
            raise KeyError(f"characters.json의 characters/fragments 어디에도 없는 이름: {name}")
        return fragment

    template = re.sub(r"\{([^{}]+)\}", lambda m: lookup(m.group(1), "desc"), template)
    return re.sub(r"\[([^\[\]]+)\]", lambda m: lookup(m.group(1), "desc_short"), template)


def character_prompt(chars: dict, name: str) -> str:
    entry = chars["characters"][name]
    return f'{chars["style_tag"]}, {entry["ref_prompt"]}, {entry["desc"]}'


def scene_prompt(chars: dict, scene: dict, use_ref: bool = True) -> str:
    """컷 프롬프트를 만든다.

    기본은 레퍼런스 모드다. 캐릭터 마스터 시트를 첨부해 생성하는 것을 전제로,
    외모 서술을 빼고 이름으로만 부르는 image_ref를 쓴다. 레퍼런스를 붙였는데
    외모를 글로 또 쓰면 모델이 글을 따라 캐릭터를 새로 그려 버리기 때문이다.
    (docs/07_캐릭터_일관성_가이드.md)

    --no-ref 로 끄면 외모 서술을 펼친 구 프롬프트를 쓴다. 레퍼런스 첨부가
    불가능한 환경의 폴백이며, 이때 얼굴 일관성은 보장되지 않는다.
    """
    if use_ref and scene.get("image_ref"):
        return scene["image_ref"]
    return f'{chars["style_tag"]}, {expand(scene["image"], chars)}'


def cast_sheets(chars: dict, scene: dict) -> list[Path]:
    """이 컷에 첨부할 캐릭터 마스터 시트 경로. 없는 파일은 걸러낸다."""
    sheets = []
    for name in scene.get("cast", []):
        entry = chars["characters"].get(name, {})
        rel = entry.get("sheet")
        if rel and (EP_ROOT / rel).exists():
            sheets.append(EP_ROOT / rel)
    return sheets


# ------------------------------------------------------------ Gradio 호출 유틸

def make_client(space: str):
    from gradio_client import Client
    import inspect

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        print("  · HF_TOKEN이 없어 익명으로 접속한다. ZeroGPU 대기열이 길어질 수 있다.")
    # 토큰 인자 이름이 gradio_client 버전에 따라 다르다(구버전 hf_token, 신버전 token).
    kwargs = {}
    if token:
        params = inspect.signature(Client.__init__).parameters
        kwargs["token" if "token" in params else "hf_token"] = token
    return Client(space, **kwargs)


def resolve_endpoint(client, keywords: tuple[str, ...]) -> tuple[str, set[str]]:
    """(api_name, 허용 파라미터명 집합)을 반환. 파라미터명 변경에 대한 방어."""
    api = client.view_api(return_format="dict", print_info=False)
    named = api.get("named_endpoints", {}) or {}
    if not named:
        raise RuntimeError("named endpoint가 없는 Space다. view_api() 출력을 직접 확인할 것.")

    chosen = None
    for name in named:
        low = name.lower()
        if any(k in low for k in keywords):
            chosen = name
            break
    if chosen is None:
        chosen = next(iter(named))

    params = {p.get("parameter_name") for p in named[chosen].get("parameters", [])}
    params.discard(None)
    return chosen, params


def call_with_retry(client, api_name: str, allowed: set[str], kwargs: dict):
    payload = {k: v for k, v in kwargs.items() if not allowed or k in allowed}
    dropped = sorted(set(kwargs) - set(payload))
    if dropped:
        print(f"    · Space가 받지 않는 인자 제외: {', '.join(dropped)}")

    last = None
    for attempt in range(MAX_RETRIES):
        try:
            return client.predict(api_name=api_name, **payload)
        except Exception as exc:  # 큐/쿼터/네트워크 오류 모두 재시도
            last = exc
            wait = BACKOFF[min(attempt, len(BACKOFF) - 1)]
            print(f"    ! 실패({attempt + 1}/{MAX_RETRIES}): {exc}\n      {wait}초 후 재시도")
            time.sleep(wait)
    raise RuntimeError(f"{MAX_RETRIES}회 재시도 후에도 실패") from last


def first_file(result) -> tuple[str, int | None]:
    """(파일경로, seed)를 결과에서 뽑아낸다. Space마다 반환 형태가 달라 방어적으로 처리."""
    seed = None
    if isinstance(result, (list, tuple)):
        items = list(result)
        for item in items:
            if isinstance(item, (int, float)) and seed is None:
                seed = int(item)
        for item in items:
            path = first_path(item)
            if path:
                return path, seed
        raise RuntimeError(f"결과에서 파일을 찾지 못했다: {result!r}")
    path = first_path(result)
    if not path:
        raise RuntimeError(f"결과에서 파일을 찾지 못했다: {result!r}")
    return path, seed


def first_path(item):
    if isinstance(item, str) and os.path.exists(item):
        return item
    if isinstance(item, dict):
        for key in ("path", "video", "url", "name"):
            val = item.get(key)
            path = first_path(val) if not isinstance(val, str) else (val if os.path.exists(val) else None)
            if path:
                return path
    if isinstance(item, (list, tuple)):
        for sub in item:
            path = first_path(sub)
            if path:
                return path
    return None


# ------------------------------------------------------------------- 매니페스트

def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"characters": {}, "scenes": {}, "videos": {}}


def save_manifest(man: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------- 실행 단계

def step_chars(args, chars, scenes):
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    man = load_manifest()
    targets = args.only or list(chars["characters"])

    client = None if args.dry_run else make_client(args.image_space)
    api_name, allowed = (None, set()) if args.dry_run else resolve_endpoint(client, ("generate", "image", "predict", "infer"))
    if api_name:
        print(f"[캐릭터] {args.image_space} → {api_name}")

    for name in targets:
        entry = chars["characters"][name]
        dest = CHAR_DIR / f'{entry["id"]}.png'
        if dest.exists() and not args.force:
            print(f"  = {name}: 이미 존재, 건너뜀 ({dest.name})")
            continue
        prompt = character_prompt(chars, name)
        print(f"  → {name} ({entry['id']}) seed={entry['seed']}")
        if args.dry_run:
            print(f"     {prompt}\n")
            continue
        result = call_with_retry(client, api_name, allowed, {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "negative_prompt": chars["negative_prompt"],
            "seed": entry["seed"],
            "randomize_seed": False,
            "num_inference_steps": args.steps,
        })
        src, seed = first_file(result)
        shutil.copy(src, dest)
        man["characters"][entry["id"]] = {
            "name": name, "file": str(dest.relative_to(EP_ROOT)),
            "space": args.image_space, "seed": seed if seed is not None else entry["seed"],
            "prompt": prompt,
        }
        save_manifest(man)
        print(f"     저장: {dest.relative_to(EP_ROOT)}")


def step_scenes(args, chars, scenes):
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    man = load_manifest()
    targets = [s for s in scenes["scenes"] if not args.only or s["id"] in args.only]

    client = None if args.dry_run else make_client(args.image_space)
    api_name, allowed = (None, set()) if args.dry_run else resolve_endpoint(client, ("generate", "image", "predict", "infer"))
    if api_name:
        print(f"[씬] {args.image_space} → {api_name}")

    for scene in targets:
        dest = SCENE_DIR / f'{scene["id"]}.png'
        if dest.exists() and not args.force:
            print(f"  = {scene['id']}: 이미 존재, 건너뜀")
            continue
        prompt = scene_prompt(chars, scene, use_ref=not args.no_ref)
        sheets = cast_sheets(chars, scene)
        cast = scene.get("cast", [])
        # 트리거 워드가 있으면 플랫폼이 캐릭터를 고정하므로 시트 첨부가 필요 없다.
        by_trigger = bool(cast) and all(chars["characters"].get(n, {}).get("trigger") for n in cast)
        missing = [] if (sheets or by_trigger or not cast) else cast
        label = f"cast={','.join(cast)}" if cast else "배경"
        print(f"  → {scene['id']} {scene['title']} seed={scene['seed']} {label}")
        if cast and missing:
            print(f"     ! 마스터 시트가 없어 레퍼런스 없이 생성됩니다 — 얼굴이 컷마다 달라집니다."
                  f" reference/sheets/ 를 먼저 채우세요 (docs/07 참고)")
        elif by_trigger:
            print(f"     트리거 워드로 지정: {', '.join(chars['characters'][n]['trigger'] for n in cast)}")
        elif sheets:
            print(f"     레퍼런스 {len(sheets)}장: {', '.join(s.name for s in sheets)}")
        if args.dry_run:
            print(f"     {prompt}\n")
            continue
        result = call_with_retry(client, api_name, allowed, {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "negative_prompt": chars["negative_prompt"],
            "seed": scene["seed"],
            "randomize_seed": False,
            "num_inference_steps": args.steps,
        })
        src, seed = first_file(result)
        shutil.copy(src, dest)
        man["scenes"][scene["id"]] = {
            "title": scene["title"], "file": str(dest.relative_to(EP_ROOT)),
            "space": args.image_space, "seed": seed if seed is not None else scene["seed"],
            "prompt": prompt,
        }
        save_manifest(man)
        print(f"     저장: {dest.relative_to(EP_ROOT)}")


def step_videos(args, chars, scenes):
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    man = load_manifest()
    targets = [s for s in scenes["scenes"] if not args.only or s["id"] in args.only]

    client = None if args.dry_run else make_client(args.video_space)
    api_name, allowed = (None, set()) if args.dry_run else resolve_endpoint(client, ("video", "generate", "predict"))
    if api_name:
        print(f"[영상] {args.video_space} → {api_name}")

    for scene in targets:
        keyframe = SCENE_DIR / f'{scene["id"]}.png'
        dest = VIDEO_DIR / f'{scene["id"]}.mp4'
        if dest.exists() and not args.force:
            print(f"  = {scene['id']}: 이미 존재, 건너뜀")
            continue
        motion = scene["motion"]
        print(f"  → {scene['id']} {scene['duration']}초")
        if args.dry_run:
            print(f"     {motion}\n")
            continue
        if not keyframe.exists():
            print(f"     ! 키프레임 없음({keyframe.name}) — scenes 단계를 먼저 실행할 것")
            continue
        from gradio_client import handle_file

        result = call_with_retry(client, api_name, allowed, {
            "input_image": handle_file(str(keyframe)),
            "prompt": motion,
            "negative_prompt": chars["negative_prompt"],
            "duration_seconds": scene["duration"],
            "steps": args.video_steps,
            "seed": scene["seed"],
            "randomize_seed": False,
        })
        src, seed = first_file(result)
        shutil.copy(src, dest)
        man["videos"][scene["id"]] = {
            "file": str(dest.relative_to(EP_ROOT)), "space": args.video_space,
            "seed": seed if seed is not None else scene["seed"],
            "duration": scene["duration"], "prompt": motion,
        }
        save_manifest(man)
        print(f"     저장: {dest.relative_to(EP_ROOT)}")


def find_ffmpeg() -> str | None:
    """시스템 ffmpeg를 먼저 쓰고, 없으면 pip 패키지에 동봉된 정적 바이너리를 쓴다."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def step_assemble(args, chars, scenes):
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("ffmpeg가 없다. `pip install imageio-ffmpeg` 또는 시스템 패키지로 설치할 것.")
        return 1

    order = [s["id"] for s in scenes["scenes"] if not args.only or s["id"] in args.only]
    clips = [VIDEO_DIR / f"{sid}.mp4" for sid in order]
    missing = [c.name for c in clips if not c.exists()]
    if missing:
        print(f"클립 누락: {', '.join(missing)} — videos 단계를 먼저 실행할 것")
        return 1

    listfile = OUT / "filelist.txt"
    listfile.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")

    raw = OUT / "episode1_raw.mp4"
    # 클립마다 인코딩 파라미터가 다를 수 있어 -c copy 대신 재인코딩으로 안전하게 붙인다.
    subprocess.run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", str(raw),
    ], check=True)
    print(f"이어붙이기 완료: {raw.relative_to(EP_ROOT)}")

    theme = Path(args.theme) if args.theme else EP_ROOT / "assets" / "theme_song.mp3"
    if theme.exists():
        final = OUT / "episode1_final.mp4"
        subprocess.run([
            ffmpeg, "-y", "-i", str(raw), "-i", str(theme),
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(final),
        ], check=True)
        print(f"배경음악 합성 완료: {final.relative_to(EP_ROOT)}")
    else:
        print(f"테마곡({theme})이 없어 무음 상태로 둔다. Suno로 생성 후 이 경로에 두고 assemble을 다시 실행할 것.")
    return 0


STEPS = {"chars": step_chars, "scenes": step_scenes, "videos": step_videos, "assemble": step_assemble}


def main() -> int:
    ap = argparse.ArgumentParser(description="쿵쿵이와 친구들 1화 생성 파이프라인")
    ap.add_argument("step", choices=[*STEPS, "all"], help="실행할 단계")
    ap.add_argument("--only", nargs="*", default=None, help="특정 캐릭터명/씬 ID만 실행 (예: --only S5 S6)")
    ap.add_argument("--force", action="store_true", help="이미 있는 결과물도 다시 생성")
    ap.add_argument("--dry-run", action="store_true", help="네트워크 호출 없이 최종 프롬프트만 출력")
    ap.add_argument("--no-ref", action="store_true",
                    help="레퍼런스 모드를 끄고 외모 서술을 펼친 구 프롬프트를 쓴다. 얼굴 일관성은 보장되지 않는다.")
    ap.add_argument("--image-space", default=SPACE_IMAGE_FAST,
                    help=f"이미지 Space (기본 {SPACE_IMAGE_FAST}, 고품질 {SPACE_IMAGE_HQ}, 대안 {SPACE_IMAGE_ALT})")
    ap.add_argument("--video-space", default=SPACE_VIDEO, help=f"영상 Space (기본 {SPACE_VIDEO})")
    ap.add_argument("--steps", type=int, default=8, help="이미지 추론 스텝")
    ap.add_argument("--video-steps", type=int, default=6, help="영상 추론 스텝")
    ap.add_argument("--theme", default=None, help="배경음악 mp3 경로")
    ap.add_argument("--shots", default="scenes.json",
                    help="컷 목록 파일 (기본 scenes.json 12컷 요약본, 정식 1화는 shots.json 128컷)")
    ap.add_argument("--episode", default=DEFAULT_EPISODE,
                    help=f"작업할 화 (episodes/ 아래 디렉터리명, 기본 {DEFAULT_EPISODE})")
    args = ap.parse_args()

    set_episode(args.episode)
    if not PROMPTS.exists():
        print(f"{PROMPTS.relative_to(ROOT)} 가 없다. --episode 값을 확인할 것.")
        return 1
    print(f"작업 대상: episodes/{args.episode}")

    chars, scenes = load_prompts(args.shots)
    print(f"컷 목록: {args.shots} ({len(scenes['scenes'])}컷)")
    steps = ["chars", "scenes", "videos", "assemble"] if args.step == "all" else [args.step]
    for name in steps:
        print(f"\n=== {name} ===")
        rc = STEPS[name](args, chars, scenes)
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
