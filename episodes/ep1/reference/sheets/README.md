# 캐릭터 마스터 시트

캐릭터당 2장. 60컷 전부가 이 파일들을 레퍼런스로 물고 생성된다. 자세한 절차는
`docs/07_캐릭터_일관성_가이드.md`.

| 캐릭터 | 다각도 | 표정 |
|---|---|---|
| 쿵쿵 | `kungkung_turnaround.png` | `kungkung_expressions.png` |
| 루카 | `luca_turnaround.png` | `luca_expressions.png` |
| 후안 | `juan_turnaround.png` | `juan_expressions.png` |
| 미미 | `mimi_turnaround.png` | `mimi_expressions.png` |
| 티니 | `tini_turnaround.png` | `tini_expressions.png` |
| 루비 | `ruby_turnaround.png` | `ruby_expressions.png` |

아직 비어 있다. OpenArt Characters에 캐릭터를 등록했다면(방법 A) 이 폴더는 비워 둬도 된다. 등록하지 않았거나
재등록이 필요할 때만 기존 공식 3D 시트를 레퍼런스로 Nano Banana 2에서 생성해 여기에 넣는다.
원본과 조금이라도 다르면 채택하지 말 것 — 이 12장이 어긋나면 60컷 전부가 어긋난다.

## 캐릭터 종합 시트 (공식 3D 마스터 시트)

캐릭터 6종 + 키 도감 1장, 모두 7장.

## 파일 이름은 자유입니다

**한글 이름 그대로 올리셔도 됩니다.** 파일 이름에 캐릭터 이름만 들어 있으면 빌더가 찾습니다.
띄어쓰기·괄호·번호·버전이 붙어 있어도 상관없습니다.

```
쿵쿵이 3D 모델링 마스터 시트.png     → 쿵쿵
루카(Luca) 종합 시트 v2.jpg          → 루카
후안 - 펭귄 마스터시트.png           → 후안
쿵쿵이와 친구들 캐릭터 키 도감.png   → 키 도감
```

영어 이름(`kungkung`, `luca`, `juan`, `mimi`, `tini`, `ruby`)도 인식합니다.
확장자는 `png` `jpg` `jpeg` `webp` 중 아무거나.

올린 뒤 `python3 site/build.py ep1` 을 돌리면 페이지에 들어갑니다.
몇 장을 찾았고 무엇이 빠졌는지 알려줍니다.
