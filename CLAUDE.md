# 쿵쿵이와 친구들 — 제작 저장소

「쿵쿵이와 친구들」 3D 애니메이션(유튜브)의 대본·컷·캐릭터 설정과 사이트 소스.
**이 저장소의 JSON이 유일한 원본이다.** 문서와 웹 페이지는 전부 여기서 만들어진다.

## 지금 상태

- 1화 60컷 확정, `SC2-04`부터 생성 남음 → `episodes/ep1/PROGRESS.md`
- 캐릭터 6종 OpenArt Characters 등록 완료(한글 이름이 트리거 워드)
- 사이트 3페이지 빌드 가능

## 절대 어기면 안 되는 것

1. **이미지 프롬프트에 캐릭터 외모를 글로 쓰지 않는다.** 등록된 캐릭터를 이름으로만 부른다.
   외모 서술과 등록 캐릭터가 함께 있으면 서술이 이겨서 얼굴이 매번 달라진다.
   → `episodes/ep1/docs/07_캐릭터_일관성_가이드.md`
2. **`image_ref`를 쓴다.** `image`는 레퍼런스 없이 돌릴 때의 폴백이다.
3. **`image_ref` / `cast`를 손으로 고치지 않는다.** `scripts/build_ref_prompts.py`로 다시 만든다.
4. **직전 컷을 레퍼런스로 쓰지 않는다.** 오차가 누적돼 20컷 뒤엔 다른 캐릭터가 된다.
5. **생성 전에 `scripts/check_episode.py`를 통과시킨다.**

## 확정된 설정

| 항목 | 값 |
|---|---|
| 러닝타임 | 3~5분 (목표 4분 30초) — `format.json` |
| 키 | 루카 160 > 쿵쿵 140 > 루비 120 > 티니 110 > 미미 105 > 후안 100 |
| 루카 고글 | 상시 착용 아님. 오버올 주머니에서 꺼내는 소품. 1화는 SC2-06에서만 |
| 남극 크레이터 | 노천. 동굴 아니다 |
| 이미지 모델 | Nano Banana 2 (얼굴 중요 컷은 Pro), 16:9 |
| 영상 모델 | MiniMax H3, 컷에 적힌 초 |

## 명령

```bash
python3 scripts/build_ref_prompts.py --episode ep1   # 프롬프트 재생성
python3 scripts/check_episode.py ep1                 # 규격 검사 (생성 전 필수)
python3 site/build.py ep1                            # 사이트 3페이지 → site/dist/
python3 scripts/sync_from_page.py <page.html>        # 페이지 편집 → JSON 되돌리기
python3 scripts/pipeline.py scenes --episode ep1 --shots shots_v2.json --dry-run
```

세션이 시작되면 `.claude/hooks/session-start.sh` 가 진행 상황·규격 검사·미결정 사항을
자동으로 띄운다. 물어보지 말고 그것부터 읽으면 된다.

## 구조

```
CLAUDE.md                       이 파일 — 새 세션은 여기부터
.claude/hooks/session-start.sh  세션 시작 시 진행 상황·규격 검사·미결정 사항 출력
format.json                     시리즈 공통 에피소드 규격
scripts/
  build_ref_prompts.py          image → cast + image_ref
  check_episode.py              format.json 대조 검사
  sync_from_page.py             페이지에서 고친 내용 → JSON
  pipeline.py                   생성 파이프라인 (chars/scenes/videos/assemble)
site/
  build.py                      세 페이지 전부 빌드
  make_hub.py                   제작 자료실 (편집 가능 · artifact 기능)
  make_bible.py                 캐릭터 바이블
  make_sheet.py                 컷 시트
  dist/                         산출물 (git 제외)
episodes/ep1/
  episode.json                  화 메타 (제목·러닝타임·로그라인)
  PROGRESS.md                   어디까지 했나
  prompts/characters.json       캐릭터 — 외모·트리거·프로필·집
  prompts/looks.json            한국어 외모 서술 (사이트용, 프롬프트 아님)
  prompts/shots_v2.json         60컷
  docs/                         대본·컷리스트·가이드·바이블·포맷
```

## 사이트 배포

`site/build.py`로 만든 뒤 `site/dist/*.html`을 Artifact로 올린다. **같은 URL로 다시 올려야 한다.**

| 페이지 | URL |
|---|---|
| 제작 자료실 | https://claude.ai/code/artifact/5257d608-308c-435c-b6a1-20be020d88c9 |
| 캐릭터 바이블 | https://claude.ai/code/artifact/1c5aea83-ee12-46a0-8d12-f574dd3e4ba4 |
| 컷 시트 | https://claude.ai/code/artifact/1e318145-bd9a-4ef9-8a69-bd6a53e605e7 |

제작 자료실은 `capabilities: {"artifact": {}}`로 배포한다 — 편집 권한이 있는 사람이 페이지에서
직접 고칠 수 있다.

**페이지에서 고친 내용은 저장소로 자동으로 돌아오지 않는다.** 되돌리는 절차:

1. Artifact 도구 `action: "read"` 로 배포된 페이지의 현재 HTML을 받아 파일로 저장
2. `python3 scripts/sync_from_page.py 받은파일.html` — 무엇이 바뀌었는지 먼저 본다
3. `--write` 를 붙여 반영한 뒤 `build_ref_prompts.py` 와 `site/build.py` 를 다시 돌린다

`data-field` 이름표가 붙은 칸만 되돌아온다. 표(집·대사·구성)와 페이지에서 새로 만든
에피소드 카드는 사람이 판단해야 하므로 자동 반영하지 않고 알려만 준다.

## 아직 안 정해진 것

- **쿵쿵이 능력 규칙** — 발동 조건·한계·대가·성장 곡선. 없으면 매화 편의대로 세지고 약해진다
- **월드 지도** — 집 6채 배치, 남극과 숲의 거리
- **후안 대사** — 1화 18컷 등장에 0줄. 무언 캐릭터로 갈지 결정 필요
- 유튜브 채널 규격 · 사운드 · 아동 안전 가이드
