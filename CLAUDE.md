# 쿵쿵이와 친구들 — 제작 저장소

「쿵쿵이와 친구들」 3D 애니메이션(유튜브)의 대본·컷·캐릭터 설정과 사이트 소스.
**이 저장소의 JSON이 유일한 원본이다.** 문서와 웹 페이지는 전부 여기서 만들어진다.

## 지금 상태

- **40화 전부 컷 확정** — 2,402컷 · 완성본 기준 약 2시간 50분. 화당 4분 10~30초
- 노을(여우)이 11화에 합류해 40화까지 나온다. **OpenArt 트리거 워드가 아직 비어 있다** — 등록 전까지 `Noeul the fox` 로 나간다 (`docs/18`)
- 컷마다 소리가 배정돼 있다 — 환경음·BGM은 장면 단위, 효과음은 컷 단위 (`docs/17`)
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

## 소리는 어디서 만드나 — 이걸 헷갈리면 다시 만들어야 한다

| | 어디서 | 왜 |
|---|---|---|
| **화면 안 인물의 대사** | **생성기(OpenArt)** | 입모양을 맞추려면 생성 때 넣는 수밖에 없다 |
| **그 컷의 효과음** | **생성기** | 화면 동작과 프레임 단위로 맞아야 한다 |
| 나레이션 | 로컬 | 컷마다 생성하면 60컷에서 나레이터가 60명이 된다 |
| 장면 환경음 | 로컬 | 장면 내내 끊기면 안 된다. 컷마다 생성하면 컷마다 튄다 |
| **BGM** | **로컬** | 장면 단위로 깔고 말소리에 맞춰 덕킹해야 한다 |
| **자막** | **로컬** | OpenArt 자막은 테두리 색이 없고 한글 폰트가 사실상 없다 |

### 영상 프롬프트는 통째로 한국어로 쓴다

영어 설명 안에 한글 대사만 따옴표로 끼워 넣으면 **대사 지시가 묻혀서 그 컷을
통째로 건너뛴다.** 영어로만 쓰면 **영어 입모양**을 만든다. 둘 다 실측으로 확인된
사실이다. 그래서 `motion_ref` 는 다섯 줄을 전부 한국어로 낸다.

```
[외형] 회색 아기 코알라, 동그란 금테 안경, 보라색 조끼, 꽃무늬 목스카프.
       금테 안경·보라 조끼·목스카프는 처음부터 끝까지 그대로 유지된다.
[동작] 코알라가 나뭇가지로 땅바닥의 그림 끝을 짚는다.
       마지막에 동작을 멈추고 그 자세로 화면을 마친다.
[대사] 코알라가 입을 크게 벌려 또박또박 한국어로 말한다: "여기서부터는 지도에도 안 나와."
       일곱 살 여자아이 목소리, 낮고 차분하게 또박또박, 천천히.
[소리] 종이 넘기거나 찢는 소리. 배경음악 없이 목소리와 효과음만.
[화풍] 픽사 스타일 3D 애니메이션, 부드러운 서브서피스 산란과 …
```

- **[외형]은 매 컷 다시 적는다.** 1화 첫 컷에만 적었더니 루카의 고글이 중간에
  앞주머니에서 얼굴로 올라왔다. 한두 명만 나오는 컷에는 소품 고정 문장까지 붙는다.
- **영상 프롬프트에서는 트리거 워드를 쓰지 않는다.** «토끼가 …» 처럼 종으로 부르고
  얼굴은 [외형] 줄이 잡는다. 트리거 워드로 얼굴을 고정하는 건 **이미지 프롬프트** 쪽이고,
  거기서는 반대로 외형을 절대 적지 않는다 (`docs/07`). 두 규칙을 헷갈리지 말 것.
- 대사가 없는 컷에는 **«아무도 말하지 않는다»** 를 명시한다. 안 적으면 아무 말이나 시킨다.
- **«배경음악 없이»** 를 안 붙이면 생성기가 자기 음악을 깔아서 클립끼리 안 맞는다.

전부 `scripts/build_ref_prompts.py` 가 자동으로 넣는다 — 손으로 지우지 말 것.

## 절대 어기면 안 되는 것

1. **이미지 프롬프트에 캐릭터 외모를 글로 쓰지 않는다.** 등록된 캐릭터를 이름으로만 부른다.
   외모 서술과 등록 캐릭터가 함께 있으면 서술이 이겨서 얼굴이 매번 달라진다.
   → `episodes/ep1/docs/07_캐릭터_일관성_가이드.md`
   **영상 프롬프트는 정반대다** — 트리거 워드를 안 쓰고 외형을 매 컷 다시 적는다.
2. **`image_ref`를 쓴다.** `image`는 레퍼런스 없이 돌릴 때의 폴백이다.
3. **`image_ref` / `cast`를 손으로 고치지 않는다.** `scripts/build_ref_prompts.py`로 다시 만든다.
4. **직전 컷을 레퍼런스로 쓰지 않는다.** 오차가 누적돼 20컷 뒤엔 다른 캐릭터가 된다.
5. **생성 전에 `scripts/check_episode.py`를 통과시킨다.**
6. **이미지든 영상이든 프롬프트에 픽사 스타일이 들어간다.**
   이미지는 맨 앞에 `style_tag`, 영상은 마지막 `[화풍]` 줄에 `style_ko`.
   image2video 라도 다시 적어 준다 — 안 적으면 실사 쪽으로 흐르는 경우가 있다.
7. **영상 프롬프트는 통째로 한국어로 쓴다.** 영어 설명에 한글 대사만 끼워 넣으면
   그 컷의 대사를 건너뛴다. 위 «영상 프롬프트는 통째로 한국어로 쓴다» 참고.
8. **소리 배정을 먼저, 프롬프트를 나중에.** `build_audio.py` → `build_ref_prompts.py`
   순서다. 반대로 하면 영상 프롬프트에 효과음이 안 들어간다.

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
- 이어붙일 때 `render_episode.py` 가 `link` 를 보고 **전환을 자동으로 건다**. 그냥 붙이면 툭툭 끊긴다
- 장면이 요구하는 46곳에는 특수 전환을 지정해 뒀다 (빛 터짐 `fadewhite`, 밤 `fadeblack`, 꿈 `circleopen`)
- **얼굴 레퍼런스와 혼동하지 말 것.** 시작 프레임만 물려주고 캐릭터는 트리거 워드로 잡는다

자세한 것은 `docs/14`.

## 명령

```bash
python3 scripts/build_audio.py --episode ep1          # 소리 배정 (프롬프트보다 먼저)
python3 scripts/build_ref_prompts.py --episode ep1   # 프롬프트 재생성 (소리가 영상 쪽에 들어간다)
python3 scripts/mix_audio.py --episode ep1 --list     # 로컬에서 받을 BGM·환경음 목록
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

python3 scripts/build_script.py                        # 대본집 (대사 + 프롬프트) → docs/대본_시즌1.md
python3 scripts/build_script.py --no-prompts           # 읽기용 (대사와 설명만)
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
