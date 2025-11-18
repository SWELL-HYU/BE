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
│   └── 4.4 좋아요한 코디 목록 조회
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

## 다음 엔드포인트 추가 예정

- 3.1 개인화 추천 코디 조회
- ... (계속 추가)

