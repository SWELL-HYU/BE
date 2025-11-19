# API 테스트 가이드 (Postman)

이 문서는 Postman을 사용한 API 테스트 가이드를 제공합니다.

## 환경 설정

### Postman Environment Variables

다음 환경 변수를 설정하세요:

| 변수명 | 설명 | 예시 값 |
|--------|------|---------|
| `base_url` | API 기본 URL | `http://localhost:8000` |
| `api_base` | API 기본 경로 | `{{base_url}}/api` |
| `token` | JWT 인증 토큰 | (로그인 후 자동 설정) |

### Postman Collection 구조

```
HCI Fashion API
├── 1. 인증 (Authentication)
│   ├── 1.1 회원가입
│   ├── 1.2 로그인
│   ├── 1.3 로그아웃
│   └── 1.4 내 정보 조회
├── 2. 사용자 (Users)
│   ├── 2.1 사용자 선호도 설정 옵션 제공
│   ├── 2.2 사용자 선호도 설정
│   ├── 2.3 프로필 사진 업로드
│   └── 2.4 프로필 사진 삭제
├── 3. 추천 (Recommendations)
│   └── 3.1 개인화 추천 코디 조회
├── 4. 코디 (Outfits)
│   ├── 4.1 코디 목록 조회
│   ├── 4.2 코디 좋아요 추가
│   ├── 4.3 코디 좋아요 취소
│   ├── 4.4 좋아요한 코디 목록 조회
│   └── 4.5 본 코디 스킵 기록
├── 5. 옷장 (Closet)
│   ├── 5.1 옷장에 아이템 저장
│   ├── 5.2 옷장 아이템 목록 조회
│   └── 5.3 옷장에서 아이템 삭제
└── 6. 가상 피팅 (Virtual Fitting)
    ├── 6.1 가상 피팅 시작
    ├── 6.2 가상 피팅 상태 조회
    └── 6.3 가상 피팅 이력 조회
```

---

## 1. 인증 (Authentication)

### 1.1 회원가입

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/auth/signup`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "email": "test@example.com",
    "password": "password123",
    "name": "홍길동",
    "gender": "male"
  }
  ```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "test@example.com",
      "name": "홍길동",
      "gender": "male",
      "profileImageUrl": null,
      "preferredTags": null,
      "preferredCoordis": null,
      "hasCompletedOnboarding": false,
      "createdAt": "2025-11-16T10:00:00Z"
    }
  }
}
```

**Test Cases:**

1. **성공 케이스**
   - 이메일: `test1@example.com`
   - 비밀번호: `password123`
   - 이름: `홍길동`
   - 성별: `male`

2. **이메일 중복 (409 Conflict)**
   - 동일한 이메일로 두 번 요청
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "EMAIL_EXISTS",
         "message": "이미 가입된 이메일입니다"
       }
     }
     ```

3. **비밀번호 길이 부족 (400 Bad Request)**
   - 비밀번호: `pass123` (7자)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "비밀번호가 8자 이상이여야합니다"
       }
     }
     ```

4. **성별 미입력 (400 Bad Request)**
   - Body에서 `gender` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "성별을 선택해주세요"
       }
     }
     ```

5. **이메일 형식 오류 (400 Bad Request)**
   - 이메일: `invalid-email`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "유효하지 않은 이메일 형식입니다"
       }
     }
     ```

---

### 1.2 로그인

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/auth/login`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "email": "test@example.com",
    "password": "password123"
  }
  ```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "test@example.com",
      "name": "홍길동",
      "gender": "male",
      "profileImageUrl": null,
      "preferredTags": null,
      "preferredCoordis": null,
      "hasCompletedOnboarding": true,
      "createdAt": "2025-11-16T10:00:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Test Cases:**

1. **성공 케이스**
   - 이메일: `test@example.com` (회원가입한 계정)
   - 비밀번호: `password123`
   - Expected: 200 OK, user 객체와 token 반환

2. **인증 실패 - 잘못된 이메일 (401 Unauthorized)**
   - 이메일: `wrong@example.com`
   - 비밀번호: `password123`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_CREDENTIALS",
         "message": "이메일 또는 비밀번호가 올바르지 않습니다"
       }
     }
     ```

3. **인증 실패 - 잘못된 비밀번호 (401 Unauthorized)**
   - 이메일: `test@example.com`
   - 비밀번호: `wrongpassword`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_CREDENTIALS",
         "message": "이메일 또는 비밀번호가 올바르지 않습니다"
       }
     }
     ```

4. **이메일 형식 오류 (400 Bad Request)**
   - 이메일: `invalid-email`
   - 비밀번호: `password123`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "유효하지 않은 이메일 형식입니다"
       }
     }
     ```

5. **비밀번호 길이 부족 (400 Bad Request)**
   - 이메일: `test@example.com`
   - 비밀번호: `pass123` (7자)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "비밀번호가 8자 이상이여야합니다"
       }
     }
     ```

6. **이메일 필수값 누락 (400 Bad Request)**
   - Body에서 `email` 필드 제거
   - 비밀번호: `password123`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "이메일을 입력해주세요"
       }
     }
     ```

7. **비밀번호 필수값 누락 (400 Bad Request)**
   - 이메일: `test@example.com`
   - Body에서 `password` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "비밀번호를 입력해주세요"
       }
     }
     ```

---

### 1.3 로그아웃

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/auth/logout`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "로그아웃되었습니다"
}
```

**Test Cases:**

1. **성공 케이스**
   - 유효한 토큰으로 요청
   - Expected: 200 OK, success와 message 반환

2. **토큰 없음 (401 Unauthorized)**
   - Headers에서 `Authorization` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "인증이 필요합니다."
       }
     }
     ```

3. **토큰 형식 오류 (401 Unauthorized)**
   - Authorization: `InvalidFormat token123`
   - 또는 Authorization: `token123` (Bearer 없음)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "유효하지 않은 토큰 형식입니다"
       }
     }
     ```

4. **토큰 만료 (401 Unauthorized)**
   - 만료된 토큰 사용
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "토큰이 만료되었습니다"
       }
     }
     ```

5. **유효하지 않은 토큰 (401 Unauthorized)**
   - 잘못된 서명의 토큰 사용
   - 또는 임의의 문자열 사용 (예: `Bearer invalidtoken123`)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "유효하지 않은 토큰입니다"
       }
     }
     ```

---

### 1.4 내 정보 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/auth/me`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "홍길동",
      "gender": "male",
      "profileImageUrl": "/uploads/users/user_001_photo.jpg",
      "preferredTags": [
        { "id": 1, "name": "#캐주얼" },
        { "id": 2, "name": "#미니멀" },
        { "id": 3, "name": "#편안한" }
      ],
      "preferredCoordis": [
        {
          "id": 10,
          "style": "casual",
          "season": "spring",
          "gender": "male",
          "description": "봄 캐주얼 코디",
          "mainImageUrl": "/uploads/coordis/coordi_010_main.jpg",
          "preferredAt": "2025-11-16T10:30:00Z"
        },
        {
          "id": 15,
          "style": "minimal",
          "season": "fall",
          "gender": "male",
          "description": "가을 미니멀 코디",
          "mainImageUrl": "/uploads/coordis/coordi_015_main.jpg",
          "preferredAt": "2025-11-15T14:20:00Z"
        }
      ],
      "hasCompletedOnboarding": true,
      "createdAt": "2025-11-16T10:00:00Z"
    }
  }
}
```

**Test Cases:**

1. **성공 케이스**
   - 유효한 토큰으로 요청
   - Expected: 200 OK, user 객체 반환 (preferredTags, preferredCoordis 포함)

2. **토큰 없음 (401 Unauthorized)**
   - Headers에서 `Authorization` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "인증이 필요합니다"
       }
     }
     ```

3. **토큰 형식 오류 (401 Unauthorized)**
   - Authorization: `InvalidFormat token123`
   - 또는 Authorization: `token123` (Bearer 없음)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "유효하지 않은 토큰 형식입니다"
       }
     }
     ```

4. **토큰 만료 (401 Unauthorized)**
   - 만료된 토큰 사용
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "토큰이 만료되었습니다"
       }
     }
     ```

5. **유효하지 않은 토큰 (401 Unauthorized)**
   - 잘못된 서명의 토큰 사용
   - 또는 임의의 문자열 사용 (예: `Bearer invalidtoken123`)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "UNAUTHORIZED",
         "message": "유효하지 않은 토큰입니다"
       }
     }
     ```

---

## 2. 사용자 (Users)

### 2.1 사용자 선호도 설정 옵션 제공

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/users/preferences/options`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "hashtags": [
      {
        "id": 1,
        "name": "#캐주얼"
      },
      {
        "id": 2,
        "name": "#미니멀"
      },
      {
        "id": 3,
        "name": "#스트리트"
      },
      {
        "id": 4,
        "name": "#스포티"
      },
      {
        "id": 5,
        "name": "#편안한"
      },
      {
        "id": 6,
        "name": "#데일리룩"
      },
      {
        "id": 7,
        "name": "#오피스룩"
      },
      {
        "id": 8,
        "name": "#데이트룩"
      }
    ],
    "sampleOutfits": [
      {
        "id": 1438474944176932480,
        "imageUrl": "https://image.msscdn.net/...",
        "style": "casual",
        "season": "winter"
      },
      {
        "id": 1438291847265123456,
        "imageUrl": "https://image.msscdn.net/...",
        "style": "minimal",
        "season": "fall"
      }
    ]
  }
}
```

**Test Cases:**

1. **성공 케이스**
   - 유효한 토큰으로 요청
   - Expected: 200 OK, hashtags 배열과 sampleOutfits 배열 반환
   - hashtags는 모든 태그를 포함 (ID 순으로 정렬)
   - sampleOutfits는 최대 20개의 예시 코디를 포함 (ID 순으로 정렬)
---

### 2.2 사용자 선호도 설정

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/users/preferences`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "hashtagIds": [1, 2, 3],
    "sampleOutfitIds": [1438474944176932480, 1438291847265123456, 1438108750352345678, 1437925653440567890, 1437742556523789012]
  }
  ```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "선호도가 저장되었습니다",
    "user": {
      "id": 1,
      "hasCompletedOnboarding": true
    }
  }
}
```

**Test Cases:**

1. **성공 케이스**
   - 유효한 토큰으로 요청
   - hashtagIds: 3-10개 (예: [1, 2, 3])
   - sampleOutfitIds: 정확히 5개 (예: [1, 2, 3, 4, 5])
   - Expected: 200 OK, success와 message, user 객체 반환
   - hasCompletedOnboarding이 true로 변경됨

2. **해시태그 부족 (400 Bad Request)**
   - hashtagIds: [1, 2] (2개만)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INSUFFICIENT_HASHTAGS",
         "message": "최소 3개의 해시태그를 선택해야 합니다"
       }
     }
     ```

3. **해시태그 초과 (400 Bad Request)**
   - hashtagIds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] (11개)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "TOO_MANY_HASHTAGS",
         "message": "최대 10개의 해시태그만 선택할 수 있습니다"
       }
     }
     ```

4. **코디 개수 부족 (400 Bad Request)**
   - sampleOutfitIds: [1, 2, 3, 4] (4개만)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INSUFFICIENT_OUTFITS",
         "message": "정확히 5개의 코디를 선택해야 합니다"
       }
     }
     ```

5. **코디 개수 초과 (400 Bad Request)**
   - sampleOutfitIds: [1, 2, 3, 4, 5, 6] (6개)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "TOO_MANY_OUTFITS",
         "message": "정확히 5개의 코디를 선택해야 합니다"
       }
     }
     ```

6. **유효하지 않은 해시태그 ID (400 Bad Request)**
   - hashtagIds: [1, 2, 99999] (존재하지 않는 ID 포함)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_HASHTAG_ID",
         "message": "유효하지 않은 해시태그 ID가 포함되어 있습니다"
       }
     }
     ```

7. **유효하지 않은 코디 ID (400 Bad Request)**
   - sampleOutfitIds: [1, 2, 3, 4, 99999] (존재하지 않는 ID 포함)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_OUTFIT_ID",
         "message": "유효하지 않은 코디 ID가 포함되어 있습니다"
       }
     }
     ```

8. **중복된 해시태그 ID (400 Bad Request)**
   - hashtagIds: [1, 2, 2] (중복 포함)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "DUPLICATE_ID",
         "message": "중복된 ID가 포함되어 있습니다"
       }
     }
     ```

9. **중복된 코디 ID (400 Bad Request)**
   - sampleOutfitIds: [1, 2, 3, 4, 4] (중복 포함)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "DUPLICATE_ID",
         "message": "중복된 ID가 포함되어 있습니다"
       }
     }
     ```
---

### 2.3 프로필 사진 업로드

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/users/profile-photo`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: multipart/form-data
  ```
- **Body:**
  - 탭: `Body` 선택
  - 타입: `form-data` 선택
  - Key: `photo` 입력
  - Key 옆 드롭다운: `File` 선택 (기본값은 `Text`)
  - Value: `Select Files` 버튼 클릭하여 JPG 또는 PNG 파일 선택 (최대 10MB)
  
  **Postman 설정 예시:**
  ```
  Body 탭 → form-data 선택
  Key: photo [File 타입으로 변경]
  Value: [Select Files] 버튼 클릭 → 파일 선택
  ```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "photoUrl": "/uploads/users/1/profile_550e8400e29b41d4.jpg",
    "createdAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - JPG 파일**
   - 유효한 토큰으로 요청
   - photo: JPG 파일 (10MB 이하)
   - Expected: 200 OK, photoUrl과 createdAt 반환

2. **성공 케이스 - PNG 파일**
   - 유효한 토큰으로 요청
   - photo: PNG 파일 (10MB 이하)
   - Expected: 200 OK, photoUrl과 createdAt 반환

3. **기존 프로필 사진 교체**
   - 유효한 토큰으로 요청
   - 이미 프로필 사진이 있는 사용자
   - 새로운 사진 업로드
   - Expected: 200 OK, 기존 사진이 새 사진으로 교체됨

4. **파일 형식 오류 - GIF (400 Bad Request)**
   - photo: GIF 파일
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_FILE_FORMAT",
         "message": "JPG, PNG 파일만 업로드 가능합니다"
       }
     }
     ```

5. **파일 형식 오류 - PDF (400 Bad Request)**
   - photo: PDF 파일
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_FILE_FORMAT",
         "message": "JPG, PNG 파일만 업로드 가능합니다"
       }
     }
     ```

6. **파일 크기 초과 (400 Bad Request)**
   - photo: 11MB 이상의 JPG/PNG 파일
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FILE_TOO_LARGE",
         "message": "파일 크기가 10MB를 초과했습니다"
       }
     }
     ```

7. **파일 없음 (400 Bad Request)**
   - Body에서 `photo` 필드 제거
   - Expected:
     ```json
    {
        "detail": "Missing boundary in multipart."
    }
     ```
---

### 2.4 프로필 사진 삭제

**Request:**
- **Method:** `DELETE`
- **URL:** `{{api_base}}/users/profile-photo`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "사진이 삭제되었습니다",
    "deletedAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 사진이 있는 경우**
   - 유효한 토큰으로 요청
   - 프로필 사진이 있는 사용자
   - Expected: 200 OK, message와 deletedAt 반환
   - 파일 시스템과 DB에서 모두 삭제됨

2. **성공 케이스 - 사진이 없는 경우 (Idempotent)**
   - 유효한 토큰으로 요청
   - 프로필 사진이 없는 사용자
   - Expected: 200 OK, message와 deletedAt 반환
   - 사진이 없어도 성공 응답 반환 (idempotent)
---

## 3. 추천 (Recommendations)

### 3.1 개인화 추천 코디 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/recommendations?page=1&limit=20`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Query Parameters:**
  - `page` (optional): 페이지 번호 (기본값: 1, 최소: 1)
  - `limit` (optional): 페이지당 개수 (기본값: 20, 최소: 1, 최대: 50)
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "outfits": [
      {
        "id": 134314134113,
        "imageUrl": "/images/outfits/outfit_001.jpg",
        "gender": "male",
        "season": "summer",
        "style": "casual",
        "description": "편안한 여름 캐주얼",
        "isFavorited": false,
        "llmMessage": "여름 바다 놀러갈 때 딱이에요! ☀️",
        "items": [
          {
            "id": 134314314,
            "category": "top",
            "brand": "유니클로",
            "name": "린넨 반팔 셔츠",
            "price": 39000,
            "imageUrl": "/images/items/item_001.png",
            "purchaseUrl": "https://www.uniqlo.com/kr/...",
            "isSaved": false
          },
          {
            "id": 13455133,
            "category": "bottom",
            "brand": "자라",
            "name": "베이직 치노 팬츠",
            "price": 49000,
            "imageUrl": "/images/items/item_002.png",
            "purchaseUrl": "https://www.zara.com/kr/...",
            "isSaved": true
          }
        ],
        "createdAt": "2025-10-15T10:00:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 10,
      "totalItems": 95,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

**Expected Response (200 OK - 결과 없음):**
```json
{
  "success": true,
  "data": {
    "outfits": [],
    "pagination": {
      "currentPage": 1,
      "totalPages": 0,
      "totalItems": 0,
      "hasNext": false,
      "hasPrev": false
    }
  }
}
```

**Test Cases:**

1. **성공 케이스 - 기본 파라미터**
   - 유효한 토큰으로 요청
   - Query Parameters 없음 (기본값 사용: page=1, limit=20)
   - Expected: 200 OK, outfits 배열과 pagination 정보 반환
   - 사용자 성별에 맞는 코디만 반환됨

2. **성공 케이스 - 페이지 지정**
   - URL: `{{api_base}}/recommendations?page=2&limit=20`
   - Expected: 200 OK, 두 번째 페이지의 코디 반환

3. **성공 케이스 - limit 조정**
   - URL: `{{api_base}}/recommendations?page=1&limit=20`
   - Expected: 200 OK, 20개의 코디 반환

4. **성공 케이스 - 결과 없음**
   - 모든 코디를 이미 본 사용자
   - 또는 해당 성별의 코디가 없는 경우
   - Expected: 200 OK, 빈 outfits 배열과 pagination 정보 반환

5. **페이지 번호 오류 - 0 이하 (400 Bad Request)**
   - URL: `{{api_base}}/recommendations?page=0`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "페이지 번호는 1 이상이어야 합니다"
       }
     }
     ```

6. **페이지 번호 오류 - 음수 (400 Bad Request)**
   - URL: `{{api_base}}/recommendations?page=-1`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "페이지 번호는 1 이상이어야 합니다"
       }
     }
     ```

7. **limit 오류 - 0 이하 (400 Bad Request)**
   - URL: `{{api_base}}/recommendations?limit=0`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "페이지당 개수는 1 이상 50 이하여야 합니다"
       }
     }
     ```

8. **limit 오류 - 50 초과 (400 Bad Request)**
   - URL: `{{api_base}}/recommendations?limit=51`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "페이지당 개수는 1 이상 50 이하여야 합니다"
       }
     }
     ```

---

## 4. 코디 목록 조회 (Outfits)

### 4.1 코디 목록 조회 (필터링)

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/outfits?season=all&style=all&gender=all&page=1&limit=10`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Query Parameters:**
  - `season` (optional): 계절 필터 (기본값: "all", 허용값: "all", "spring", "summer", "fall", "winter")
  - `style` (optional): 스타일 필터 (기본값: "all", 허용값: "all", "casual", "street", "sporty", "minimal")
  - `gender` (optional): 성별 필터 (기본값: "all", 허용값: "all", "male", "female")
  - `page` (optional): 페이지 번호 (기본값: 1, 최소: 1)
  - `limit` (optional): 페이지당 개수 (기본값: 20, 최소: 1, 최대: 50)
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "outfits": [
      {
        "id": 134314134113,
        "imageUrl": "/images/outfits/outfit_001.jpg",
        "gender": "male",
        "season": "summer",
        "style": "casual",
        "description": "편안한 여름 캐주얼",
        "isFavorited": false,
        "llmMessage": null,
        "items": [
          {
            "id": 134314314,
            "category": "top",
            "brand": "유니클로",
            "name": "린넨 반팔 셔츠",
            "price": 39000,
            "imageUrl": "/images/items/item_001.png",
            "purchaseUrl": "https://www.uniqlo.com/kr/...",
            "isSaved": false
          },
          {
            "id": 13455133,
            "category": "bottom",
            "brand": "자라",
            "name": "베이직 치노 팬츠",
            "price": 49000,
            "imageUrl": "/images/items/item_002.png",
            "purchaseUrl": "https://www.zara.com/kr/...",
            "isSaved": true
          }
        ],
        "createdAt": "2025-10-15T10:00:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 10,
      "totalItems": 95,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

**Expected Response (200 OK - 결과 없음):**
```json
{
  "success": true,
  "data": {
    "outfits": [],
    "pagination": {
      "currentPage": 1,
      "totalPages": 0,
      "totalItems": 0,
      "hasNext": false,
      "hasPrev": false
    }
  }
}
```

**Test Cases:**

1. **성공 케이스 - 기본 파라미터 (모든 필터 "all")**
   - URL: `{{api_base}}/outfits`
   - Expected: 200 OK, 모든 코디 반환 (최신순)

2. **성공 케이스 - season 필터링**
   - URL: `{{api_base}}/outfits?season=summer`
   - Expected: 200 OK, summer 계절 코디만 반환

3. **성공 케이스 - style 필터링**
   - URL: `{{api_base}}/outfits?style=casual`
   - Expected: 200 OK, casual 스타일 코디만 반환

4. **성공 케이스 - gender 필터링**
   - URL: `{{api_base}}/outfits?gender=female`
   - Expected: 200 OK, female 성별 코디만 반환

5. **성공 케이스 - 복합 필터링**
   - URL: `{{api_base}}/outfits?season=summer&style=casual&gender=male`
   - Expected: 200 OK, 모든 조건을 만족하는 코디만 반환

6. **성공 케이스 - 페이지 지정**
   - URL: `{{api_base}}/outfits?page=2&limit=10`
   - Expected: 200 OK, 두 번째 페이지의 코디 반환

7. **성공 케이스 - 결과 없음**
   - URL: `{{api_base}}/outfits?season=spring&style=minimal&gender=male`
   - 조건을 만족하는 코디가 없는 경우
   - Expected: 200 OK, 빈 outfits 배열과 pagination 정보 반환

8. **season 값 오류 - 잘못된 값 (400 Bad Request)**
   - URL: `{{api_base}}/outfits?season=invalid`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "유효하지 않은 season 값입니다. (all, spring, summer, fall, winter 중 하나를 선택해주세요)"
       }
     }
     ```

9. **style 값 오류 - 잘못된 값 (400 Bad Request)**
   - URL: `{{api_base}}/outfits?style=invalid`
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "유효하지 않은 style 값입니다. (all, casual, street, sporty, minimal 중 하나를 선택해주세요)"
       }
     }
     ```

10. **gender 값 오류 - 잘못된 값 (400 Bad Request)**
    - URL: `{{api_base}}/outfits?gender=invalid`
    - Expected:
      ```json
      {
        "success": false,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "유효하지 않은 gender 값입니다. (all, male, female 중 하나를 선택해주세요)"
        }
      }
      ```

11. **페이지 번호 오류 - 0 이하 (400 Bad Request)**
    - URL: `{{api_base}}/outfits?page=0`
    - Expected:
      ```json
      {
        "success": false,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "페이지 번호는 1 이상이어야 합니다"
        }
      }
      ```

12. **limit 오류 - 50 초과 (400 Bad Request)**
    - URL: `{{api_base}}/outfits?limit=51`
    - Expected:
      ```json
      {
        "success": false,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "페이지당 개수는 1 이상 50 이하여야 합니다"
        }
      }
      ```

### 4.2 코디 좋아요 추가

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/outfits/{outfitId}/favorite`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Path Parameters:**
  - `outfitId` (required): 코디 고유 ID
  - ex: 1438903904945349989
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "outfitId": 1438903904945349989,
    "isFavorited": true,
    "favoritedAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 새로운 코디 좋아요**
   - 유효한 토큰으로 요청
   - outfitId: 존재하는 코디 ID
   - Expected: 200 OK, outfitId, isFavorited=true, favoritedAt 반환
   - `UserCoordiInteraction` 테이블에 `action_type="like"`로 기록됨

2. **성공 케이스 - skip으로 기록된 코디를 좋아요로 변경**
   - 유효한 토큰으로 요청
   - outfitId: 이미 `action_type="skip"`으로 기록된 코디 ID
   - Expected: 200 OK, 기존 skip 레코드가 like로 업데이트됨

3. **코디 없음 (404 Not Found)**
   - outfitId: 존재하지 않는 코디 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "OUTFIT_NOT_FOUND",
         "message": "코디를 찾을 수 없습니다"
       }
     }
     ```

4. **이미 좋아요한 코디 (409 Conflict)**
   - outfitId: 이미 `action_type="like"`로 기록된 코디 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "ALREADY_FAVORITED",
         "message": "이미 좋아요한 코디입니다"
       }
     }
     ```

### 4.3 코디 좋아요 취소

**Request:**
- **Method:** `DELETE`
- **URL:** `{{api_base}}/outfits/{outfitId}/favorite`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Path Parameters:**
  - `outfitId` (required): 코디 고유 ID
  - ex: 1438903904945349989
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "outfitId": 1438903904945349989,
    "isFavorited": false,
    "unfavoritedAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 좋아요 취소**
   - 유효한 토큰으로 요청
   - outfitId: 이미 좋아요한 코디 ID
   - Expected: 200 OK, outfitId, isFavorited=false, unfavoritedAt 반환
   - `UserCoordiInteraction` 테이블에서 `action_type="like"` 레코드 삭제됨

2. **코디 없음 (404 Not Found)**
   - outfitId: 존재하지 않는 코디 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "OUTFIT_NOT_FOUND",
         "message": "코디를 찾을 수 없습니다"
       }
     }
     ```

3. **좋아요 없음 (404 Not Found)**
   - outfitId: 좋아요하지 않은 코디 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FAVORITE_NOT_FOUND",
         "message": "좋아요하지 않은 코디입니다"
       }
     }
     ```
---

### 4.4 좋아요한 코디 목록 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/outfits/favorites?page=1&limit=20`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Query Parameters:**
  - `page` (optional): 페이지 번호 (기본값: 1, 최소: 1)
  - `limit` (optional): 페이지당 개수 (기본값: 20, 최소: 1, 최대: 50)
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "outfits": [
      {
        "id": 1438903904945349989,
        "imageUrl": "/images/outfits/outfit_001.jpg",
        "gender": "male",
        "season": "summer",
        "style": "casual",
        "description": "편안한 여름 캐주얼",
        "isFavorited": true,
        "llmMessage": null,
        "items": [
          {
            "id": 134314314,
            "category": "top",
            "brand": "유니클로",
            "name": "린넨 반팔 셔츠",
            "price": 39000,
            "imageUrl": "/images/items/item_001.png",
            "purchaseUrl": "https://www.uniqlo.com/kr/...",
            "isSaved": false
          },
          {
            "id": 13455133,
            "category": "bottom",
            "brand": "자라",
            "name": "베이직 치노 팬츠",
            "price": 49000,
            "imageUrl": "/images/items/item_002.png",
            "purchaseUrl": "https://www.zara.com/kr/...",
            "isSaved": true
          }
        ],
        "createdAt": "2025-10-15T10:00:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 12,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

**Expected Response (200 OK - 결과 없음):**
```json
{
  "success": true,
  "data": {
    "outfits": [],
    "pagination": {
      "currentPage": 1,
      "totalPages": 0,
      "totalItems": 0,
      "hasNext": false,
      "hasPrev": false
    }
  }
}
```

**Test Cases:**

1. **성공 케이스 - 기본 파라미터**
   - 유효한 토큰으로 요청
   - Query Parameters 없음 (기본값 사용: page=1, limit=20)
   - Expected: 200 OK, outfits 배열과 pagination 정보 반환
   - 좋아요 추가 일시 기준 최신순으로 정렬됨
   - 모든 코디의 `isFavorited`가 `true`임
   - 모든 코디의 `llmMessage`가 `null`임

2. **성공 케이스 - 페이지 지정**
   - URL: `{{api_base}}/outfits/favorites?page=2&limit=20`
   - Expected: 200 OK, 두 번째 페이지의 코디 반환
   - 좋아요 추가 일시 기준 최신순 정렬 유지

3. **성공 케이스 - limit 조정**
   - URL: `{{api_base}}/outfits/favorites?page=1&limit=12`
   - Expected: 200 OK, 12개의 코디 반환

4. **성공 케이스 - 결과 없음 (좋아요한 코디가 없는 경우)**
   - 좋아요한 코디가 없는 사용자
   - Expected: 200 OK, 빈 outfits 배열과 pagination 정보 반환
   - `totalItems: 0`, `totalPages: 0`, `hasNext: false`, `hasPrev: false`

5. **성공 케이스 - 좋아요 추가 일시 기준 정렬 확인**
   - 여러 코디에 좋아요를 추가 (시간 간격을 두고)
   - Expected: 가장 최근에 좋아요한 코디가 첫 번째로 반환됨

---

### 4.5 본 코디 스킵 기록

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/outfits/skip`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "outfitIds": [1438903904945349989, 1438908516166171660, 1438907945581406350]
  }
  ```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "3개의 코디가 스킵으로 기록되었습니다",
    "recordedCount": 3,
    "skippedCount": 0
  }
}
```

**Test Cases:**

1. **성공 케이스 - 새로운 코디 스킵**
   - 유효한 토큰으로 요청
   - outfitIds: [123456789, 987654321, 111222333] (3개)
   - Expected: 200 OK, recordedCount=3, skippedCount=0
   - `UserCoordiInteraction` 테이블에 `action_type="skip"`으로 기록됨

2. **성공 케이스 - 일부 중복 (이미 skip으로 기록된 코디 포함)**
   - 유효한 토큰으로 요청
   - outfitIds: [123456789, 987654321, 111222333]
   - 123456789는 이미 skip으로 기록됨
   - Expected: 200 OK, recordedCount=2, skippedCount=1
   - 중복된 코디는 skippedCount에 포함됨

3. **성공 케이스 - 좋아요가 있는 코디 포함**
   - 유효한 토큰으로 요청
   - outfitIds: [123456789, 987654321, 111222333]
   - 123456789는 이미 `action_type="like"`로 기록됨
   - Expected: 200 OK, recordedCount=2, skippedCount=1
   - 좋아요가 있는 코디는 skip으로 변경되지 않음 (좋아요 우선)

4. **성공 케이스 - 좋아요와 중복 모두 포함**
   - 유효한 토큰으로 요청
   - outfitIds: [123456789, 987654321, 111222333, 444555666]
   - 123456789: 이미 like로 기록됨
   - 987654321: 이미 skip으로 기록됨
   - Expected: 200 OK, recordedCount=2, skippedCount=2
   - like와 skip 모두 skippedCount에 포함됨

5. **빈 배열 오류 (400 Bad Request)**
   - outfitIds: []
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "outfitIds는 최소 1개 이상이어야 합니다"
       }
     }
     ```

6. **outfitIds 필드 누락 (400 Bad Request)**
   - Body에서 `outfitIds` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "outfitIds는 최소 1개 이상이어야 합니다"
       }
     }
     ```
---

## 5. 옷장 (Closet)

### 5.1 옷장에 아이템 저장

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/closet/items`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "itemId": 5562350
  }
  ```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "message": "옷장에 저장되었습니다",
    "savedAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 새로운 아이템 저장**
   - 유효한 토큰으로 요청
   - itemId: 존재하는 아이템 ID
   - Expected: 201 Created, message와 savedAt 반환
   - `UserClosetItem` 테이블에 레코드 생성됨

2. **아이템 없음 (404 Not Found)**
   - itemId: 존재하지 않는 아이템 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "ITEM_NOT_FOUND",
         "message": "상품을 찾을 수 없습니다"
       }
     }
     ```

3. **이미 저장된 아이템 (409 Conflict)**
   - itemId: 이미 옷장에 저장된 아이템 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "ALREADY_SAVED",
         "message": "이미 옷장에 저장된 아이템입니다"
       }
     }
     ```

4. **itemId 필드 누락 (400 Bad Request)**
   - Body에서 `itemId` 필드 제거
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "아이템 ID를 입력해주세요"
       }
     }
     ```

5. **itemId 형식 오류 - 문자열 (400 Bad Request)**
   - itemId: "abc" (문자열)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "유효하지 않은 아이템 ID 형식입니다"
       }
     }
     ```

6. **itemId 형식 오류 - null (400 Bad Request)**
   - itemId: null
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "아이템 ID를 입력해주세요"
       }
     }
     ```

---

### 5.2 옷장 아이템 목록 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/closet?category=all&page=1&limit=20`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Query Parameters:**
  - `category` (optional): 카테고리 필터 (기본값: "all", 허용값: "all", "top", "bottom", "outer")
  - `page` (optional): 페이지 번호 (기본값: 1, 최소: 1)
  - `limit` (optional): 페이지당 개수 (기본값: 20, 최소: 1, 최대: 50)
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 5562350,
        "category": "outer",
        "brand": "인사일런스 우먼",
        "name": "시어링 퍼 자켓 MOCHA BROWN",
        "price": 227200,
        "imageUrl": "https://image.msscdn.net/thumbnails/images/goods_img/20251001/5562350/5562350_17593827444982_500.jpg",
        "purchaseUrl": "https://www.musinsa.com/app/goods/5562350",
        "savedAt": "2025-11-15T14:30:00Z"
      },
      {
        "id": 5195037,
        "category": "outer",
        "brand": "무신사 스탠다드 우먼",
        "name": "우먼즈 아가일 라운드 넥 가디건 [브라운]",
        "price": 59390,
        "imageUrl": "https://image.msscdn.net/thumbnails/images/goods_img/20250619/5195037/5195037_17586944462519_500.jpg",
        "purchaseUrl": "https://www.musinsa.com/app/goods/5195037",
        "savedAt": "2025-11-14T09:15:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 87,
      "hasNext": true,
      "hasPrev": false
    },
    "categoryCounts": {
      "top": 32,
      "bottom": 28,
      "outer": 27
    }
  }
}
```

**Expected Response (200 OK - 결과 없음):**
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "currentPage": 1,
      "totalPages": 0,
      "totalItems": 0,
      "hasNext": false,
      "hasPrev": false
    },
    "categoryCounts": {
      "top": 0,
      "bottom": 0,
      "outer": 0
    }
  }
}
```

**Test Cases:**

1. **성공 케이스 - 기본 파라미터 (전체 카테고리)**
   - 유효한 토큰으로 요청
   - Query Parameters 없음 (기본값 사용: category=all, page=1, limit=20)
   - Expected: 200 OK, items 배열, pagination, categoryCounts 반환
   - 저장 일시 기준 최신순으로 정렬됨

2. **성공 케이스 - category 필터링 (top)**
   - URL: `{{api_base}}/closet?category=top`
   - Expected: 200 OK, top 카테고리 아이템만 반환
   - categoryCounts는 필터와 관계없이 전체 카테고리별 개수 반환

3. **성공 케이스 - category 필터링 (bottom)**
   - URL: `{{api_base}}/closet?category=bottom`
   - Expected: 200 OK, bottom 카테고리 아이템만 반환

4. **성공 케이스 - category 필터링 (outer)**
   - URL: `{{api_base}}/closet?category=outer`
   - Expected: 200 OK, outer 카테고리 아이템만 반환

5. **성공 케이스 - 페이지 지정**
   - URL: `{{api_base}}/closet?page=2&limit=20`
   - Expected: 200 OK, 두 번째 페이지의 아이템 반환

6. **성공 케이스 - limit 조정**
   - URL: `{{api_base}}/closet?page=1&limit=12`
   - Expected: 200 OK, 12개의 아이템 반환

7. **성공 케이스 - 결과 없음 (옷장에 아이템이 없는 경우)**
   - 옷장에 아이템이 없는 사용자
   - Expected: 200 OK, 빈 items 배열과 pagination, categoryCounts 반환
   - 모든 카테고리 개수가 0

8. **성공 케이스 - 저장 일시 기준 정렬 확인**
   - 여러 아이템을 저장 (시간 간격을 두고)
   - Expected: 가장 최근에 저장한 아이템이 첫 번째로 반환됨

9. **성공 케이스 - categoryCounts는 필터와 무관하게 전체 개수 반환**
   - URL: `{{api_base}}/closet?category=top`
   - Expected: top 아이템만 반환되지만, categoryCounts는 전체 카테고리별 개수 반환

10. **category 값 오류 - 잘못된 값 (400 Bad Request)**
    - URL: `{{api_base}}/closet?category=invalid`
    - Expected:
      ```json
      {
        "success": false,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "유효하지 않은 category 값입니다. (all, top, bottom, outer 중 하나를 선택해주세요)"
        }
      }
      ```
---

### 5.3 옷장에서 아이템 삭제

**Request:**
- **Method:** `DELETE`
- **URL:** `{{api_base}}/closet/items/5562350`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Path Parameters:**
  - `itemId` (integer, required): 아이템 고유 ID
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "옷장에서 삭제되었습니다",
    "deletedAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 옷장에 저장된 아이템 삭제**
   - 유효한 토큰으로 요청
   - itemId: 옷장에 저장된 아이템 ID
   - Expected: 200 OK, message와 deletedAt 반환
   - `UserClosetItem` 테이블에서 레코드 삭제됨
   - 삭제 후 GET /api/closet 호출 시 해당 아이템이 목록에서 제외됨

2. **아이템 없음 (404 Not Found)**
   - itemId: 존재하지 않는 아이템 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "ITEM_NOT_FOUND",
         "message": "상품을 찾을 수 없습니다"
       }
     }
     ```

3. **옷장에 저장되지 않은 아이템 (404 Not Found)**
   - itemId: 존재하는 아이템이지만 옷장에 저장되지 않은 아이템 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "ITEM_NOT_IN_CLOSET",
         "message": "옷장에 저장되지 않은 상품입니다"
       }
     }
     ```

4. **다른 사용자의 옷장 아이템 삭제 시도 (404 Not Found)**
   - User A가 저장한 아이템을 User B가 삭제 시도
   - Expected: 404 Not Found, `ITEM_NOT_IN_CLOSET` 에러

---

## 6. 가상 피팅 (Virtual Fitting)

### 6.1 가상 피팅 시작

**Request:**
- **Method:** `POST`
- **URL:** `{{api_base}}/virtual-fitting`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "items": [
      {
        "itemId": 5562350,
        "category": "outer",
        "imageUrl": "https://image.msscdn.net/thumbnails/images/goods_img/20251001/5562350/5562350_17593827444982_500.jpg"
      },
      {
        "itemId": 5195037,
        "category": "top",
        "imageUrl": "https://image.msscdn.net/thumbnails/images/goods_img/20250619/5195037/5195037_17586944462519_500.jpg"
      }
    ]
  }
  ```
  
  **Note:**
  - 사용자 사진은 `UserImage` 테이블에서 자동으로 조회됩니다.
  - 사진이 업로드되지 않은 경우 `PHOTO_REQUIRED` 에러가 발생합니다.

**Expected Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "jobId": 1234,
    "status": "processing",
    "createdAt": "2025-11-16T10:00:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 가상 피팅 시작 (1개 아이템)**
   - 유효한 토큰으로 요청
   - 사용자 사진이 `UserImage` 테이블에 존재해야 함
   - items: 1개 아이템 (category: "top")
   - Expected: 202 Accepted, jobId, status="processing", createdAt 반환
   - `FittingResult` 레코드 생성됨 (status="processing")
   - `FittingResultItem` 레코드 생성됨

2. **성공 케이스 - 가상 피팅 시작 (3개 아이템)**
   - items: 3개 아이템 (top, bottom, outer 각 1개)
   - Expected: 202 Accepted, jobId 반환
   - 각 카테고리별로 1개씩만 포함

3. **사진 없음 (400 Bad Request)**
   - `UserImage` 테이블에 사용자 사진이 없는 경우
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "PHOTO_REQUIRED",
         "message": "가상 피팅을 위해 먼저 사진을 업로드해주세요"
       }
     }
     ```

4. **중복 카테고리 (400 Bad Request)**
   - items: top 카테고리 아이템 2개
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "DUPLICATE_CATEGORY",
         "message": "동일한 카테고리의 아이템이 중복되었습니다"
       }
     }
     ```

5. **아이템 개수 초과 - 전체 (400 Bad Request)**
   - items: 4개 이상의 아이템
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "TOO_MANY_ITEMS",
         "message": "최대 3개의 아이템만 선택할 수 있습니다"
       }
     }
     ```

6. **아이템 개수 초과 - 카테고리당 (400 Bad Request)**
   - items: top 카테고리 아이템 2개 (다른 카테고리와 함께)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "TOO_MANY_ITEMS",
         "message": "각 카테고리당 최대 1개씩만 선택할 수 있습니다"
       }
     }
     ```

7. **아이템 부족 (400 Bad Request)**
   - items: 빈 배열
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INSUFFICIENT_ITEMS",
         "message": "최소 1개 이상의 아이템을 선택해주세요"
       }
     }
     ```

8. **유효하지 않은 카테고리 (400 Bad Request)**
   - items[].category: "invalid"
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_CATEGORY",
         "message": "유효하지 않은 카테고리입니다. (top, bottom, outer 중 하나를 선택해주세요)"
       }
     }
     ```

9. **유효하지 않은 아이템 ID (400 Bad Request)**
   - items[].itemId: 존재하지 않는 아이템 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "INVALID_ITEM_ID",
         "message": "유효하지 않은 아이템 ID가 포함되어 있습니다"
       }
     }
     ```

10. **items 필수값 누락 (400 Bad Request)**
    - Body에서 `items` 필드 제거
    - Expected:
      ```json
      {
        "success": false,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "피팅할 아이템 목록을 입력해주세요"
        }
      }
      ```

---

### 6.2 가상 피팅 상태 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/virtual-fitting/1234`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Path Parameters:**
  - `jobId` (integer, required): 피팅 작업 고유 ID (6.1에서 반환된 jobId)

**Expected Response (200 OK):**

상태에 따라 다른 응답 구조를 반환합니다:

**1. Processing 상태:**
```json
{
  "success": true,
  "data": {
    "jobId": 1234,
    "status": "processing",
    "currentStep": "top"
  }
}
```

**2. Completed 상태:**
```json
{
  "success": true,
  "data": {
    "jobId": 1234,
    "status": "completed",
    "resultImageUrl": "/uploads/fitting/fitting_1234_20251116_100000.png",
    "llmMessage": "이 코디는 캐주얼한 스타일로 일상복으로 착용하기 좋습니다.",
    "completedAt": "2025-11-16T10:05:30Z",
    "processingTime": 330
  }
}
```

**3. Failed 상태:**
```json
{
  "success": true,
  "data": {
    "jobId": 1234,
    "status": "failed",
    "error": "상의 피팅 중 오류가 발생했습니다",
    "failedStep": "top",
    "failedAt": "2025-11-16T10:02:15Z"
  }
}
```

**4. Timeout 상태:**
```json
{
  "success": true,
  "data": {
    "jobId": 1234,
    "status": "timeout",
    "error": "처리 시간을 초과했습니다 (300초)",
    "timeoutAt": "2025-11-16T10:05:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - Processing 상태 조회**
   - 유효한 토큰으로 요청
   - jobId: 6.1에서 반환된 jobId
   - 작업이 아직 진행 중인 경우
   - Expected: 200 OK, status="processing", currentStep 반환
   - currentStep은 "top", "bottom", "outer" 중 하나

2. **성공 케이스 - Completed 상태 조회**
   - 작업이 완료된 경우
   - Expected: 200 OK, status="completed", resultImageUrl, llmMessage, completedAt, processingTime 반환
   - resultImageUrl은 유효한 이미지 경로
   - llmMessage는 문자열 또는 null (null인 경우 "메시지 생성 중 오류가 발생했습니다"로 대체)
   - processingTime은 초 단위 정수

3. **성공 케이스 - Completed 상태 (llmMessage null)**
   - LLM 메시지 생성 실패한 경우
   - Expected: 200 OK, llmMessage="메시지 생성 중 오류가 발생했습니다"

4. **성공 케이스 - Failed 상태 조회**
   - 작업이 실패한 경우
   - Expected: 200 OK, status="failed", error, failedStep, failedAt 반환
   - error는 동적으로 생성된 메시지 (예: "상의 피팅 중 오류가 발생했습니다")
   - failedStep은 "top", "bottom", "outer" 중 하나

5. **성공 케이스 - Timeout 상태 조회**
   - 작업이 타임아웃된 경우
   - Expected: 200 OK, status="timeout", error, timeoutAt 반환
   - error는 "처리 시간을 초과했습니다 (300초)" 형식

6. **작업 없음 (404 Not Found)**
   - jobId: 존재하지 않는 작업 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FITTING_JOB_NOT_FOUND",
         "message": "가상 피팅 작업을 찾을 수 없습니다"
       }
     }
     ```

7. **권한 없음 (403 Forbidden)**
   - jobId: 다른 사용자의 작업 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FORBIDDEN",
         "message": "다른 사용자의 작업에 접근할 수 없습니다"
       }
     }
     ```
---

### 6.3 가상 피팅 이력 조회

**Request:**
- **Method:** `GET`
- **URL:** `{{api_base}}/virtual-fitting`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Query Parameters:**
  - `page` (integer, optional, default 1): 페이지 번호
  - `limit` (integer, optional, default 20): 페이지당 개수

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "fittings": [
      {
        "jobId": 1234,
        "status": "completed",
        "resultImageUrl": "/uploads/fitting/fitting_1234_20251116_100000.png",
        "items": [
          {
            "itemId": 1234,
            "category": "top",
            "name": "린넨 반팔 셔츠"
          },
          {
            "itemId": 1235,
            "category": "bottom",
            "name": "베이직 치노 팬츠"
          }
        ],
        "createdAt": "2025-11-09T20:00:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "totalItems": 25,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

**Expected Response (200 OK - 결과 없음):**
```json
{
  "success": true,
  "data": {
    "fittings": [],
    "pagination": {
      "currentPage": 1,
      "totalPages": 0,
      "totalItems": 0,
      "hasNext": false,
      "hasPrev": false
    }
  }
}
```

**Test Cases:**

1. **성공 케이스 - 기본 파라미터 (전체 이력)**
   - 유효한 토큰으로 요청
   - Query Parameters 없음 (기본값 사용: page=1, limit=20)
   - Expected: 200 OK, fittings 배열, pagination 반환
   - 생성 일시 기준 최신순으로 정렬됨

2. **성공 케이스 - 페이지 지정**
   - URL: `{{api_base}}/virtual-fitting?page=2&limit=20`
   - Expected: 200 OK, 두 번째 페이지의 이력 반환

3. **성공 케이스 - limit 조정**
   - URL: `{{api_base}}/virtual-fitting?page=1&limit=10`
   - Expected: 200 OK, 10개의 이력 반환

4. **성공 케이스 - 결과 없음 (이력이 없는 경우)**
   - 가상 피팅 이력이 없는 사용자
   - Expected: 200 OK, 빈 fittings 배열과 pagination 반환
   - 모든 pagination 값이 0 또는 false

5. **성공 케이스 - 생성 일시 기준 정렬 확인**
   - 여러 가상 피팅 작업 수행 (시간 간격을 두고)
   - Expected: 가장 최근에 생성한 작업이 첫 번째로 반환됨

6. **성공 케이스 - completed 상태의 resultImageUrl 포함**
   - status="completed"인 이력
   - Expected: resultImageUrl이 유효한 이미지 경로로 반환됨

7. **성공 케이스 - failed/timeout 상태의 resultImageUrl null**
   - status="failed" 또는 "timeout"인 이력
   - Expected: resultImageUrl이 null로 반환됨

8. **성공 케이스 - 아이템 정보 포함 확인**
   - 각 fitting에 items 배열이 포함됨
   - Expected: itemId, category, name이 올바르게 반환됨

---

### 6.4 가상 피팅 이력 삭제

**Request:**
- **Method:** `DELETE`
- **URL:** `{{api_base}}/virtual-fitting/1234`
- **Headers:**
  ```
  Authorization: Bearer {{token}}
  ```
- **Path Parameters:**
  - `jobId` (integer, required): 가상 피팅 작업 고유 ID
- **Body**: 없음

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "가상 피팅 이력이 삭제되었습니다",
    "deletedAt": "2025-11-19T10:30:00Z"
  }
}
```

**Test Cases:**

1. **성공 케이스 - 가상 피팅 이력 삭제**
   - 유효한 토큰으로 요청
   - jobId: 현재 사용자가 생성한 가상 피팅 작업 ID
   - Expected: 200 OK, message와 deletedAt 반환
   - `FittingResult` 테이블에서 레코드 삭제됨
   - `FittingResultItem`, `FittingResultImage` 테이블에서도 관련 레코드 삭제됨 (CASCADE)
   - 결과 이미지 파일도 파일 시스템에서 삭제됨
   - 삭제 후 GET /api/virtual-fitting 호출 시 해당 이력이 목록에서 제외됨

2. **작업 없음 (404 Not Found)**
   - jobId: 존재하지 않는 작업 ID (예: 999999999999)
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FITTING_JOB_NOT_FOUND",
         "message": "가상 피팅 작업을 찾을 수 없습니다"
       }
     }
     ```

3. **권한 없음 (403 Forbidden)**
   - jobId: 다른 사용자가 생성한 작업 ID
   - Expected:
     ```json
     {
       "success": false,
       "error": {
         "code": "FORBIDDEN",
         "message": "다른 사용자의 작업에 접근할 수 없습니다"
       }
     }
     ```

---

## 다음 엔드포인트 추가 예정

- ... (계속 추가)

