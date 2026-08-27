# 쿵쿵이와 친구들 — 제작 저장소

「쿵쿵이와 친구들」 3D 애니메이션(유튜브)의 대본·컷·캐릭터 설정과 사이트 소스.
**이 저장소의 JSON이 유일한 원본이다.** 문서와 웹 페이지는 전부 여기서 만들어진다.

## 지금 상태

- **시즌 1(1~10화) 컷 리스트 전부 확정** — 화당 60컷, 규격 전 화 통과
- 1화 `SC2-04`부터 생성 남음 → `episodes/ep1/PROGRESS.md`. 2~10화는 아직 생성 전
- 캐릭터 6종 OpenArt Characters 등록 완료(한글 이름이 트리거 워드)
- 자막·렌더는 ffmpeg 로 저장소 안에서 처리 (`docs/12`)
- 쿵쿵의 능력은 등록된 5종이 전부 (`docs/13`)
- **모든 컷에 `link` 가 있다** — 앞 컷과 어떻게 이어지는지 (`docs/14`). `연속` 인 컷은 앞 컷 영상의 마지막 프레임을 시작 프레임으로 넣는다
- 쿵쿵이는 1화 엔딩부터 9화까지 루카의 나무집에서 지낸다. 자기 집은 10화에 완성된다 (`docs/15`)
- **쇼츠 22편** 컷 확정 — 9:16 세로. 본편 컷을 잘라 쓸 수 없다 (`docs/16`)
  - 비율은 프롬프트가 아니라 **생성 화면의 설정**이다. 이미지를 9:16 으로 뽑으면 image2video 가 그 비율을 따라간다
- 사이트 3페이지 빌드 가능, 컷 시트는 화별로 나온다

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

## 편집은 OpenArt 밖에서

OpenArt는 **생성만** 쓴다. 이어붙이기·자막·음악·최종 출력은 ffmpeg 로 한다 —
크레딧 0, 워터마크 0. OpenArt 자막 기능에는 테두리 색 지정이 없고 폰트가 4개뿐이며
그중 `Inter` 는 한글 글리프가 없다. 자세한 것은 `docs/12_자막과_렌더.md`.

컷마다 자막을 굽지 말 것. 오타 하나에 컷을 재생성하게 되고 크레딧이 샌다.

## 컷은 이어져야 한다

컷 하나하나가 잘 나와도 이어붙이면 툭툭 끊긴다. 앞 컷이 어떤 상태로 끝나는지 적혀 있지 않으면 생성 모델은 앞뒤를 모른다.

- `motion` 은 **반드시 그 컷이 끝나는 자세·위치·카메라로 끝맺는다**
- 모든 컷에 `link` 를 지정한다 — `연속` / `컷` / `전환`
- `연속` 은 `scripts/chain_frames.py` 로 앞 컷 끝 프레임을 뽑아 시작 프레임으로 넣는다
- **얼굴 레퍼런스와 혼동하지 말 것.** 시작 프레임만 물려주고 캐릭터는 트리거 워드로 잡는다

자세한 것은 `docs/14`.

## 명령

```bash
python3 scripts/build_ref_prompts.py --episode ep1   # 프롬프트 재생성
python3 scripts/check_episode.py ep1                 # 규격 검사 (생성 전 필수)
python3 scripts/check_ost.py ep1                     # OST 확보 현황
python3 site/build.py ep1                            # 사이트 3페이지 → site/dist/
python3 scripts/sync_from_page.py <page.html>        # 페이지 편집 → JSON 되돌리기
python3 scripts/pipeline.py scenes --episode ep1 --shots shots_v2.json --dry-run

python3 scripts/build_subtitles.py --episode episodes/ep1              # 자막 .ass + .srt
python3 scripts/render_episode.py --episode episodes/ep1 --clips <폴더> # 이어붙이기 + 자막 굽기
python3 scripts/chain_frames.py --episode episodes/ep1 --clips <폴더>   # 연속 컷 시작 프레임 추출

python3 scripts/build_shorts.py                        # 쇼츠 프롬프트 (9:16)
python3 scripts/check_shorts.py                        # 쇼츠 규격 검사
python3 site/make_shorts.py                            # 쇼츠 복붙 페이지
```

세션이 시작되면 `.claude/hooks/session-start.sh` 가 진행 상황·규격 검사·미결정 사항을
자동으로 띄운다. 물어보지 말고 그것부터 읽으면 된다.

## 구조

`bible/` 은 40화 공용 캐릭터 설정이다. 화별 `episodes/epN/prompts/` 안에
같은 이름의 파일을 두면 그 화에서만 덮어쓴다.

```
CLAUDE.md                       이 파일 — 새 세션은 여기부터
.claude/hooks/session-start.sh  세션 시작 시 진행 상황·규격 검사·미결정 사항 출력
format.json                     시리즈 공통 에피소드 규격
scripts/
  build_ref_prompts.py          image → cast + image_ref
  check_episode.py              format.json 대조 검사
  check_ost.py                  OST 확보 현황
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
  assets/ost/                   음원 (파일명 자유) + ost.json
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

- **쿵쿵이 능력의 한계** — 능력 종류는 5종으로 등록해 잠갔지만(`docs/13`), "지치면 주저앉는다" 말고는 한계가 없다. 시즌 2 컷 짜기 전에 정해야 한다
- **월드 지도** — 집 6채 배치, 남극과 숲의 거리
- **시즌 2 신규 캐릭터 이름** — 10화 엔딩(EN-06/07)에 여우 실루엣 복선을 넣었다. 이름이 확정되기 전이라 프롬프트에 이름을 쓰지 않았다
- **후안 대사** — 1화 18컷 등장에 0줄(유일하게 남은 규격 경고). 7화에서 주연으로 7줄을 말하므로 무언 캐릭터는 아니다. 1화에 한 줄 넣을지 결정 필요
- **메인 테마 사양** — 파일을 받아야 ost.json 의 길이·조성을 채운다
- **엔딩곡 가사**
- 유튜브 채널 규격 · 아동 안전 가이드
