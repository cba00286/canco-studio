# OST

음원 파일을 이 폴더에 넣는다. **파일 이름은 자유다.**
`ost.json` 의 `slug` 나 제목이 파일 이름에 들어 있으면 찾는다.

```
쿵쿵이와 친구들 메인테마.mp3     → main-theme
쿵! 쿵! 쿵쿵이 (최종).wav        → opening
opening_v3.mp3                    → opening
```

`mp3` `wav` `m4a` `flac` `ogg` 를 인식한다.

곡 목록·가사·생성 프롬프트·사양은 `../../docs/10_OST_바이블.md`.

## 확인

```bash
python3 scripts/check_ost.py ep1
```

무엇이 들어왔고 무엇이 비었는지 알려준다.
