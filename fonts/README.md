# 자막 폰트

`subtitle_style.json` 의 `font` 에는 **파일명이 아니라 패밀리 이름**을 적는다.

기본으로 들어있는 것:

| 파일 | 패밀리 이름 | 라이선스 |
|---|---|---|
| `NanumGothicBold.ttf` | `NanumGothic` | SIL Open Font License 1.1 (상업적 사용 가능) |

## 폰트 추가

`.ttf` 를 이 폴더에 넣고 패밀리 이름을 확인한다:

```bash
python3 -c "from fontTools.ttLib import TTFont; f=TTFont('fonts/폰트.ttf'); \
print([r.toUnicode() for r in f['name'].names if r.nameID==1][:1])"
```

아동 애니메이션에는 둥근 폰트가 어울린다 — 배민 주아체, Cafe24 Ssurround,
나눔손글씨 계열. **상업적 사용이 허용된 폰트인지 반드시 확인할 것.**
유튜브 수익화 채널은 상업적 사용에 해당한다.
