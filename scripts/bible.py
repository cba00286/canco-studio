# -*- coding: utf-8 -*-
"""캐릭터 바이블은 40화가 공유한다.

캐릭터 묘사·트리거 워드·집·프로필은 화마다 달라지지 않으므로
`bible/` 하나에 두고 모든 에피소드가 같은 파일을 읽는다. 40벌을 복사해 두면
캐릭터 하나를 고칠 때 40군데를 고쳐야 하고, 반드시 어긋난다.

특정 화에서만 바이블을 갈아끼워야 하면(예: 회상 편에서 어린 시절 디자인을
쓰는 경우) 그 화의 `prompts/` 안에 같은 이름의 파일을 두면 그쪽이 우선한다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIBLE = ROOT / "bible"


def _resolve(prompts_dir, name):
    """에피소드 안에 같은 이름의 파일이 있으면 그것을, 없으면 공용 바이블을 쓴다."""
    if prompts_dir is not None:
        local = Path(prompts_dir) / name
        if local.exists():
            return local
    return BIBLE / name


def chars_path(prompts_dir=None):
    return _resolve(prompts_dir, "characters.json")


def looks_path(prompts_dir=None):
    return _resolve(prompts_dir, "looks.json")
