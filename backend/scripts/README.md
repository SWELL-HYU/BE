# 배치 스크립트

데이터 일괄 삽입 및 관리 작업을 위한 스크립트 디렉토리입니다.

## 사용법

### 아이템 데이터 삽입

```bash
# backend 디렉토리에서 실행
python scripts/load_items.py data/items.json

# 또는 Python 모듈로 실행
python -m scripts.load_items data/items.json
```

### 코디 데이터 삽입

```bash
# backend 디렉토리에서 실행
python scripts/load_coordis.py data/coordis_sample.json

# 또는 Python 모듈로 실행
python -m scripts.load_coordis data/coordis.json
```

### 태그 데이터 삽입

```bash
# backend 디렉토리에서 실행
python scripts/load_tags.py data/tags_sample.json
```

**데이터 파일 위치:**
- 모든 데이터 파일은 `backend/data/` 디렉토리에 저장합니다.
- 예: `backend/data/items.json`, `backend/data/coordis.json` 등

## 데이터 파일 형식

### items.json 예시

```json
[
  {
    "category": "top",
    "brand": "유니클로",
    "name": "린넨 반팔 셔츠",
    "price": 39000,
    "imageUrl": "/images/items/item_001.png",
    "purchaseUrl": "https://www.uniqlo.com/kr/..."
  }
]
```

### coordis.json 예시

```json
[
  {
    "outfit_id": "1438474944176932480",
    "gender": "FEMALE",
    "detail_url": "https://www.musinsa.com/snap/1438474944176932480",
    "image_url": "https://image.msscdn.net/thumbnails/images/goods_img/20251014/5590956/",
    "items": [
      {
        "item_id": "5590956",
        "category": "아우터",
        "brand": "프리버07",
        "name": "High neck fleece point half jumper",
        "price": 234000,
        "image_url": "https://image.msscdn.net/...",
        "purchase_url": "https://www.musinsa.com/app/goods/5590956",
        "position": 1
      }
    ],
    "season": "겨울",
    "style": "캐주얼",
    "description": "포근한 텍스처와 화사한 컬러 조합..."
  }
]
```

## 주의사항

- 스크립트 실행 전 데이터베이스가 실행 중인지 확인하세요.
- `.env` 파일에 올바른 `DATABASE_URL`이 설정되어 있어야 합니다.
- 대량 데이터 삽입 시 시간이 걸릴 수 있습니다.
- **코디 스크립트의 특징:**
  - `outfit_id`와 `item_id`를 직접 지정하여 삽입합니다.
  - 이미 존재하는 아이템이나 코디는 건너뛰거나 업데이트합니다.
  - 한국어 카테고리/시즌/스타일은 자동으로 영어로 변환됩니다.
    - 카테고리: "아우터" → "outer", "상의" → "top", "바지" → "bottom"
    - 시즌: "봄" → "spring", "여름" → "summer", "가을" → "fall", "겨울" → "winter"
    - 스타일: "캐주얼" → "casual", "스트리트" → "street", "스포티" → "sporty", "미니멀" → "minimal"

