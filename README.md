# 캔코 스튜디오 (canco-studio)

AI로 애니메이션 영상을 제작하는 작업 저장소. 「쿵쿵이와 친구들」 시리즈의
화별 프롬프트·레퍼런스·생성 스크립트를 여기서 관리한다.

## 구조

```
canco-studio/
├── scripts/pipeline.py    # 전 화 공용 제작 파이프라인
├── requirements.txt
└── episodes/
    └── ep1/               # 1화 「안녕, 나는 쿵쿵이야!」
        ├── prompts/       # 캐릭터·씬 프롬프트 (JSON)
        ├── reference/     # 캐릭터 공식 레퍼런스 이미지
        ├── docs/          # 기획 문서
        ├── outputs/       # 생성 결과물 (미디어는 .gitignore)
        └── README.md      # 1화 상세 실행 가이드
```

## 빠른 시작

```bash
pip install -r requirements.txt
export HF_TOKEN=hf_xxxxxxxx

python3 scripts/pipeline.py all              # 1화 전체 (기본값)
python3 scripts/pipeline.py scenes --only S5 # 특정 씬만
python3 scripts/pipeline.py all --episode ep2
```

파이프라인은 네 단계다 — **chars**(캐릭터 레퍼런스) → **scenes**(씬 키프레임) →
**videos**(이미지→4~5초 클립) → **assemble**(ffmpeg 이어붙이기 + 테마곡 합성).
Hugging Face Space API를 호출하므로 `HF_TOKEN`이 필요하고, ZeroGPU 대기열 때문에
단계별로 나눠 돌리는 편이 안전하다.

각 화의 상세 내용(캐릭터 설정, 씬 목록, 확인된 Space API 스키마, 남은 작업)은
해당 화의 README를 참고할 것 — 1화는 [`episodes/ep1/README.md`](episodes/ep1/README.md).

## 화 추가하기

`episodes/<새 화>/prompts/`에 `characters.json`과 `scenes.json`을 같은 형식으로 두고
`--episode <새 화>`로 실행하면 된다. 캐릭터 묘사는 화마다 복사해 두는 것을 권장한다.
시리즈 도중 설정이 바뀌어도 이전 화를 그대로 재현할 수 있다.
