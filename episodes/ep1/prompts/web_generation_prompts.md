# 「쿵쿵이와 친구들」 1화 — 키프레임 웹 생성용 프롬프트 (60컷)

> MCP 경유 생성(`nano-banana-2-lite` text2image)은 컷마다 캐릭터 디자인이 흔들리고, 의도치 않은 다른 동물/캐릭터가 섞여 나오는 문제가 있었다.
> 이 문서는 그 문제를 프롬프트 차원에서 최대한 보정한 버전이다 (캐릭터별 '이 캐릭터만 등장, 다른 동물/공룡/캐릭터 없음' 배제 문구 추가). 그래도 완벽한 일관성을 원하면 아래 0단계(레퍼런스/Character 만들기)를 꼭 거치고 시작할 것.

## 0단계 — 캐릭터 레퍼런스 먼저 만들기 (일관성의 핵심)

OpenArt 웹 UI에서 **Character(캐릭터 저장)** 기능으로 6명을 먼저 고정해두고, 이후 모든 컷 생성 시 해당 Character를 레퍼런스로 붙여서 생성한다. 텍스트 설명만으로는 컷마다 얼굴이 달라진다 — 이게 이번에 터진 문제의 원인이다.

| 캐릭터 | 레퍼런스 만드는 법 |
|---|---|
| **쿵쿵** | 이미 있음 — episodes/ep1/reference/kungkung_official_reference.png 를 웹 UI에 레퍼런스 이미지로 업로드해서 Character로 저장 |
| **루카** | 3D Pixar/DreamWorks style character reference sheet on a soft neutral pastel background — Luca, an energetic baby tiger cub with bright orange fur and dark brown stripes, a cream-colored muzzle, chest and belly, brown aviator goggles pushed up on his forehead, blue denim overalls with metal buttons, a long striped tail, standing in a confident three-quarter front view, cheerful open smile, no text |
| **후안** | 3D Pixar/DreamWorks style character reference sheet on a soft neutral pastel background — Juan, a cheerful baby penguin with a navy-blue back and flippers and a soft white face and belly, a red knitted beanie with a white pompom, an orange bandana with a small pattern tied at his neck, a small orange beak and orange webbed feet, round dark eyes with bright catchlights, blush cheeks, standing in a confident three-quarter front view, cheerful open smile, no text |
| **미미** | 3D Pixar/DreamWorks style character reference sheet on a soft neutral pastel background — Mimi, a curious baby koala with soft gray fur and a pale cream chest, large fluffy round ears with pink inner fur, a big dark nose, round gold wire-rimmed glasses, a violet-purple vest and a floral-patterned neckerchief, big gray-green eyes, standing in a confident three-quarter front view, cheerful open smile, no text |
| **티니** | 3D Pixar/DreamWorks style character reference sheet on a soft neutral pastel background — Tini, a small golden retriever puppy with fluffy golden-tan fur, a cream muzzle and chest, long floppy ears, a dark button nose, warm brown eyes, and a floral-patterned bandana tied at his neck, standing in a confident three-quarter front view, cheerful open smile, no text |
| **루비** | 3D Pixar/DreamWorks style character reference sheet on a soft neutral pastel background — Ruby, a cheerful baby rabbit with pale pink fluffy fur, long upright ears with a small pink ribbon bow on one ear, a pink bow tie at her neck, large violet eyes with bright catchlights, rosy blush cheeks, holding a small wooden wand topped with a sparkling star, standing in a confident three-quarter front view, cheerful open smile, no text |

순서: (1) 위 프롬프트로 이미지 생성 → 마음에 드는 1장 선택 → (2) OpenArt에서 그 이미지를 **Character로 저장** → (3) 아래 컷 생성 시 등장 캐릭터의 Character를 레퍼런스로 첨부.

## 1단계 — 컷별 생성

모델: **Nano Banana 2 Lite** (웹 UI, 무제한 무료) · 비율: **16:9** · 컷당 이미지 2장 추천.
각 컷 프롬프트를 그대로 복사해서 붙여넣고, `등장 캐릭터` 줄에 있는 이름들의 Character를 레퍼런스로 첨부한다 (없으면 첨부 없이 생성).

### Act 1 · SC#1 남극의 밤 — 유성 낙하와 얼음 속 알

#### `SC1-01` (WS)
- 대사: **나레이션** — 아득히 먼 북쪽 얼음의 땅,
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a vast frozen wasteland at night, endless blue-white ice cliffs meeting a black sea, a silver-green aurora rippling across the whole sky, utterly still and immense, epic wide establishing shot, no characters, no animals, no creatures, no text
```

#### `SC1-02` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the aurora sky above the frozen land suddenly split by a brilliant meteor streaking down, trailing golden-teal fire and sparks, the ice below lit up by its glow, wide shot, no characters, no animals, no creatures, no text
```

#### `SC1-03` (CU)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — extreme close-up of the meteor core burning golden-teal as it falls, jagged glowing fragments breaking away, sparks streaming past camera, close-up shot, no characters, no animals, no creatures, no text
```

#### `SC1-04` (WS)
- 대사: **나레이션** — 하늘에서 떨어진 신비한 유성 빛을 머금고
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the meteor striking the ice sheet, a blinding golden-teal shockwave blasting outward across the frozen plain, ice shards and snow thrown into the air, dramatic impact, wide shot, no characters, no animals, no creatures, no text
```

#### `SC1-05` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a huge crater carved into the ice, glowing meteor fragments scattered across its floor giving off wisps of steam, golden-teal light seeping through the surrounding ice walls, wide shot, no characters, no animals, no creatures, no text
```

#### `SC1-06` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a colossal pale egg embedded deep in the translucent blue ice of the crater wall, golden-teal aurora light flowing through the ice and soaking into its shell, medium shot, no characters, no animals, no creatures, no text
```

#### `SC1-07` (CU)
- 대사: **나레이션** — 하나의 거대한 알이 숨을 쉬기 시작했어요.
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — extreme close-up of the egg's surface glowing from within, faint veins of golden-teal light spreading across the shell like a slow heartbeat, close-up shot, no characters, no animals, no creatures, no text
```

#### `SC1-08` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the ice crater seen from high above at night under the aurora, a single point of warm light glowing deep in the ice, tiny against the enormous frozen land, wide shot, no characters, no animals, no creatures, no text
```

### Act 1 · SC#2 숲속 강가 — 얼음 알 발견

#### `SC2-01` (WS)
- 대사: **나레이션** — 거센 폭풍우가 지나간 날 아침,
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a lush green forest riverbank the morning after a storm, wet leaves and puddles glittering in fresh sunlight, the river running high and brown, torn branches on the banks, wide shot, no characters, no animals, no creatures, no text
```

#### `SC2-02` (WS)
- 등장 캐릭터: 루비, 루카, 미미, 티니, 후안

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Luca the orange baby tiger cub in blue denim overalls with aviator goggles on his forehead, Juan the navy baby penguin in a red pompom beanie and orange bandana, Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand, Mimi the gray baby koala in round gold glasses and a purple vest and Tini the fluffy golden retriever puppy in a floral bandana walking out of the treeline onto the sunlit riverbank together, splashing through puddles, cheerful morning mood, wide shot, only Tini, Luca, Mimi, Juan, Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-03` (MS)
- 등장 캐릭터: 티니

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Tini the fluffy golden retriever puppy in a floral bandana bounding ahead along the riverbank with his nose to the ground, tail wagging hard, sniffing at the debris, medium shot, only Tini appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-04` (WS)
- 대사: **나레이션** — 강가로 나온 친구들의 눈 앞에 신기한 광경이 펼쳐졌답니다.
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a huge block of ice lodged against the rocks at the river's edge, sunlight blazing through it, something enormous and pale visible deep inside, the friends small beside it, wide shot, no characters, no animals, no creatures, no text
```

#### `SC2-05` (MS)
- 등장 캐릭터: 루카

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — the five friends stopping dead and staring up at the ice block, mouths open, Luca the orange baby tiger cub in blue denim overalls with aviator goggles on his forehead holding out an arm to keep the others back, medium shot, only Luca appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-06` (CU)
- 대사: **루카** — 우와! 이것 좀 봐! 얼음 안에 진짜 커다란 알이 있어!
- 등장 캐릭터: 루카

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — close-up of Luca the orange baby tiger cub in blue denim overalls with aviator goggles on his forehead pulling his aviator goggles down over his eyes and leaning in toward the ice, thrilled and amazed, close-up shot, only Luca appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-07` (CU)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — extreme close-up through the sunlit ice revealing the curved surface of the enormous pale egg, shimmering golden-teal aurora light still faintly moving within it, close-up shot, only appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-08` (MS)
- 대사: **미미** — 이상해... 얼음 속에서 따뜻한 오로라 빛이 흘러나오고 있어.
- 등장 캐릭터: 미미

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Mimi the gray baby koala in round gold glasses and a purple vest adjusting her round glasses as she studies the ice closely, the teal glow reflecting in her lenses, thoughtful and fascinated, medium shot, only Mimi appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-09` (MS)
- 등장 캐릭터: 후안

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Juan the navy baby penguin in a red pompom beanie and orange bandana waddling right up to the ice and pressing both flippers and his cheek against it, then flinching back from the cold, medium shot, only Juan appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-10` (MS)
- 대사: **루비** — 알이 추워 보여. 우리가 꼭 안아줘서 녹여주자!
- 등장 캐릭터: 루비

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand standing close to the ice with both paws pressed against it, her star wand tucked under one arm, warm concern on her face, medium shot, only Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC2-11` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the five friends looking at each other around the ice block, nodding one by one, a decision passing between them, medium shot, no characters, no animals, no creatures, no text
```

#### `SC2-12` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the five friends moving in and pressing themselves against the huge ice block from every side, arms and flippers spread wide across it, sunlight warm on their backs, wide shot, no characters, no animals, no creatures, no text
```

### Act 2 · SC#3 강가 공터 새벽 — 부화, 첫 파워, 이름

#### `SC3-01` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the riverbank at night, the five friends curled asleep in a ring around the shrinking ice block, moonlight and drifting mist, peaceful and tender, wide shot, no characters, no animals, no creatures, no text
```

#### `SC3-02` (WS)
- 대사: **나레이션** — 친구들의 따뜻한 마음이 전해진 걸까요?
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the first light of dawn spilling gold across the river valley, the sky shifting from deep blue to warm amber above the sleeping friends, wide shot, no characters, no animals, no creatures, no text
```

#### `SC3-03` (CU)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — extreme close-up of a crack racing across the melting ice, fissures branching fast, meltwater streaming down, close-up shot, no characters, no animals, no creatures, no text
```

#### `SC3-04` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the last of the ice splitting apart and falling away in glittering shards, revealing the enormous pale egg standing free in the dawn light, medium shot, no characters, no animals, no creatures, no text
```

#### `SC3-05` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the five friends jolting awake in the dawn light, heads snapping up, scrambling to their feet, medium shot, no characters, no animals, no creatures, no text
```

#### `SC3-06` (CU)
- 대사: **나레이션** — 동이 트는 새벽, 마침내 알이 깨어났어요!
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — extreme close-up of the eggshell cracking open with golden-teal light spilling from the fracture lines, close-up shot, no characters, no animals, no creatures, no text
```

#### `SC3-07` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — the eggshell bursting open as Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — pushes his head out into the dawn light for the very first time, damp and blinking and brand new, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-08` (CU)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — extreme close-up of Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his huge green eyes opening fully for the first time, the golden sunrise reflected in them, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-09` (WS)
- 대사: **쿵쿵** — 우와아아아!! 나 일어났다!
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — standing in the broken shell with his head thrown back and mouth wide open in a joyful first cry, golden sunrise rimming him with light, the five friends watching in awe, wide shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-10` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — trying to push himself upright out of the shell, legs trembling and splaying under him, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-11` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — losing his balance and slamming both front paws down hard onto the wet ground to catch himself, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-12` (CU)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — extreme close-up of Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his three horns as golden-teal aurora light surges along them, brilliant and alive, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-13` (WS)
- 대사: **나레이션** — 쿵쿵이가 땅을 딛는 순간, 뿔에서 시작된 신비한 오로라 파장이
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — a visible ring of golden-teal light bursting outward across the ground from Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his front paws, sweeping over grass and stones and past the astonished friends, wide shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-14` (WS)
- 대사: **나레이션** — 온 숲을 따뜻하게 울렸답니다.
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the shockwave ring of light spreading out through the whole forest, leaves and branches shivering as it passes, birds lifting from the canopy, dawn sky above, wide shot, no characters, no animals, no creatures, no text
```

#### `SC3-15` (MS)
- 대사: **티니** — 쿵! 하고 땅이 울렸어! 멍멍!
- 등장 캐릭터: 미미, 티니, 후안

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Tini the fluffy golden retriever puppy in a floral bandana tumbled onto his back on the grass with all four paws in the air, delighted rather than hurt, Juan the navy baby penguin in a red pompom beanie and orange bandana and Mimi the gray baby koala in round gold glasses and a purple vest steadying themselves behind him, medium shot, only Tini, Juan, Mimi appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-16` (MS)
- 대사: **루카** — 너는 오늘부터 '쿵쿵이'야!
- 등장 캐릭터: 루카, 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Luca the orange baby tiger cub in blue denim overalls with aviator goggles on his forehead stepping forward with his goggles pushed back up and one paw raised, beaming at Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs, morning light between them, medium shot, only Luca, Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-17` (CU)
- 대사: **쿵쿵** — 좋아! 나는 쿵쿵이야!
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — close-up of Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — lighting up with the biggest joyful smile of his life, hearing his own name for the first time, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC3-18` (WS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — the six friends together on the sunlit riverbank cheering around Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs, broken shell pieces scattered at their feet, warm morning light, wide shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

### Act 3 · SC#4 불어난 개울가 — 루비 구조

#### `SC4-01` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — a swollen forest stream running fast and muddy after the storm, water churning over rocks, soft earth crumbling at the banks, wide shot, no characters, no animals, no creatures, no text
```

#### `SC4-02` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — the six friends playing along the stream bank in bright daylight, Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — in the middle still walking unsteadily, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-03` (MS)
- 등장 캐릭터: 루비

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand standing near the water's edge waving her star wand, unaware the soft earth beneath her is giving way, medium shot, only Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-04` (CU)
- 대사: **나레이션** — 그때, 약해진 흙더미가 무너지며
- 등장 캐릭터: 루비

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — close-up of the muddy bank collapsing away under Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand, her feet, clods of earth dropping into the rushing water, close-up shot, only Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-05` (MS)
- 대사: **루비** — 꺄악! 도와줘! 물살이 너무 세!
- 등장 캐릭터: 루비

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand swept into the fast brown current and carried downstream, ears streaming back, one paw reaching up, panic on her face, medium shot, only Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-06` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the friends on the bank frozen in shock for a heartbeat, then breaking into panic and running along the water, medium shot, no characters, no animals, no creatures, no text
```

#### `SC4-07` (CU)
- 대사: **쿵쿵** — 루비야, 기다려!
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — close-up of Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his face hardening from fear into fierce determination, eyes locked on the water, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-08` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — charging down the bank on unsteady legs, faster than he has ever moved, mud flying behind him, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-09` (MS)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — skidding to a stop at the water's edge and slamming both front paws down onto the ground with everything he has, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-10` (CU)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — extreme close-up of Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his horns erupting with brilliant golden-teal aurora light, brighter than before, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-11` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — golden-teal aurora light surging along his three horns while a visible shockwave ring of the same light spreads outward across the ground from where his front paws struck, the ring of light racing across the ground and into a fallen log at the water's edge, wide shot, only appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-12` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the massive fallen log rolling into the rushing stream and wedging across it, water piling up against it, forming a safe barrier, wide shot, no characters, no animals, no creatures, no text
```

#### `SC4-13` (MS)
- 등장 캐릭터: 루비

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand sweeping downstream into the log and catching hold of it with both paws, hauling herself against it, safe, medium shot, only Ruby appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `SC4-14` (MS)
- 대사: **루비** — 고마워 쿵쿵아! 네 뿔에서 예쁜 빛이 났어!
- 등장 캐릭터: 루비, 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Ruby the pale pink baby rabbit with a ribbon on her ear and a little star wand soaked and safe on the bank holding Kung-Kung the mint-green baby triceratops with three peach horns and a floral ivory bandana, his paw with both of hers, looking up at his horns with wonder, the others crowding around, medium shot, only Ruby, Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

### 엔딩 · 따뜻한 첫 만남 + 유성 복선

#### `EN-01` (CU)
- 대사: **쿵쿵** — 헤헤, 내가 친구들을 지켜줄게, 쿵쿵!
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — close-up of Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — ducking his head bashfully with pink cheeks, then breaking into a proud smile, warm afternoon light, close-up shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `EN-02` (MS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the six friends laughing together on the sunlit stream bank, soaked and happy, steam rising faintly from their fur, medium shot, no characters, no animals, no creatures, no text
```

#### `EN-03` (WS)
- 대사: **나레이션** — 서툴지만 용기 있는 쿵쿵이와 소중한 친구들의
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the six friends walking together along a sunlit forest path toward home, seen from behind, long warm afternoon shadows stretching ahead of them, wide shot, no characters, no animals, no creatures, no text
```

#### `EN-04` (MS)
- 대사: **쿵쿵** — 친구들을 지켜줄게, 쿵쿵!
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — stopping and turning back with both front paws planted on his hips in his signature confident pose, chest out, golden afternoon light behind him, medium shot, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```

#### `EN-05` (WS)
- 대사: **나레이션** — 멋진 모험이 이제 막 시작되었답니다.
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — wide shot of the six friends small on the forest path beneath an enormous warm afternoon sky, the whole green valley spread around them, wide shot, no characters, no animals, no creatures, no text
```

#### `EN-06` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the camera high above the forest valley, the six friends now tiny specks on the path far below, distant blue mountains along the horizon, wide shot, no characters, no animals, no creatures, no text
```

#### `EN-07` (WS)
- 등장 캐릭터: 없음 (배경/사물 컷)

```
3D Pixar/DreamWorks style animated film still, family animation movie quality, cinematic composition — the distant mountain ridge beyond the forest, and beyond it a single faint pulse of golden-teal light flickering once behind the peaks, easy to miss, wide shot, no characters, no animals, no creatures, no text
```

#### `EN-08` (타이틀)
- 등장 캐릭터: 쿵쿵

```
3D Pixar/DreamWorks style animated film still, high detail fur and scale texture, cinematic lighting, family animation movie quality, cinematic composition — an end card illustration of Kung-Kung — a chubby baby triceratops with soft pastel mint-green skin and a pale cream belly and muzzle, three peach-colored horns (two above the eyes and one on the snout), a low beige neck frill with rounded scallops, a row of small peach scutes running down his back and tail, very large sparkling green eyes with bright catchlights, blush pink cheeks, an ivory bandana with a colorful tropical floral pattern tied around his neck, short stubby legs — in his signature pose on a sunlit hilltop with the five friends behind him, warm afternoon palette, clear empty space at the bottom for a title, title card illustration, only Kung-Kung appear — no other dinosaurs, no other animals, no extra background characters, no unrelated creatures, no text
```
