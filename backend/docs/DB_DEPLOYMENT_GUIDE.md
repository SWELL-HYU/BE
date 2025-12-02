Google Cloud Console에서 Cloud SQL (PostgreSQL + pgvector) 설정 가이드입니다.

## Google Cloud SQL (PostgreSQL + pgvector) 설정 가이드

### 사전 준비사항

1. Google Cloud 계정 생성
   - https://cloud.google.com 접속
   - Google 계정으로 로그인
   - 무료 체험 계정 활성화 (필요 시)

2. 프로젝트 생성
   - Google Cloud Console 접속: https://console.cloud.google.com
   - 상단 프로젝트 선택 → 새 프로젝트 클릭
   - 프로젝트 이름 입력 (예: `hci-fashion-project`)
   - 조직 선택 (없으면 건너뛰기)
   - 만들기 클릭
   - 프로젝트 선택 후 대시보드 확인

3. 결제 계정 연결 (필수)
   - 좌측 메뉴 → 결제
   - 결제 계정 연결
   - 신용카드 정보 입력 (무료 체험 시에도 필요)

---

### 1단계: Cloud SQL 인스턴스 생성

#### 1-1. Cloud SQL 메뉴 접근
1. 좌측 메뉴 → SQL (또는 검색창에 "Cloud SQL" 입력)
2. 인스턴스 만들기 클릭

#### 1-2. 데이터베이스 엔진 선택
- PostgreSQL 선택
- 다음 클릭

#### 1-3. 인스턴스 ID 및 비밀번호 설정
- 인스턴스 ID: `hci-postgres` (원하는 이름)
- 루트 비밀번호: 강력한 비밀번호 설정 (저장 필수)
  - 예: `YourSecurePassword123!@#`
  - 확인 비밀번호: 동일하게 입력
- 다음 클릭

#### 1-4. 인스턴스 구성 선택
- 환경: 프로덕션 또는 개발/테스트
- 머신 유형:
  - 개발/테스트: 공유 코어 → db-f1-micro (무료 티어)
  - 프로덕션: 전용 코어 → db-n1-standard-1 이상
- 스토리지:
  - SSD 권장
  - 용량: 최소 20GB (필요에 따라 조정)
- 다음 클릭

#### 1-5. 연결 설정
- 연결:
  - 공개 IP: 활성화
  - 전용 IP: 선택 사항 (프로덕션 권장)
- 승인된 네트워크:
  - 네트워크 추가 → IP 주소 추가
  - 개발: `0.0.0.0/0` (모든 IP 허용, 보안상 권장하지 않음)
  - 프로덕션: 특정 IP 주소만 추가
    - 예: `123.456.789.0/32` (애플리케이션 서버 IP)
- 다음 클릭

#### 1-6. 데이터베이스 플래그 설정 (중요: pgvector 활성화)
- 데이터베이스 플래그 섹션
- 플래그 추가 클릭
- 플래그 이름: `cloudsql.enable_pgvector`
- 값: `on`
- 저장
- 다음 클릭

#### 1-7. 백업 설정
- 자동 백업: 활성화 권장
- 백업 시작 시간: 유지보수 시간대 선택
- 백업 보존 기간: 7일 (기본값)
- 다음 클릭

#### 1-8. 유지보수 설정
- 유지보수 기간: 원하는 시간대 선택
- 다음 클릭

#### 1-9. 최종 확인 및 생성
- 설정 요약 확인
- 만들기 클릭
- 인스턴스 생성 시작 (5-10분 소요)
- 완료되면 인스턴스 목록에 표시

---

### 2단계: 데이터베이스 및 사용자 생성

#### 2-1. 인스턴스 연결
1. 인스턴스 목록에서 `hci-postgres` 클릭
2. 연결 탭 클릭
3. Cloud Shell에서 연결 클릭 (또는 로컬 클라이언트 사용)

#### 2-2. Cloud Shell 사용 (권장)
1. Cloud Shell 아이콘 클릭 (상단 터미널 아이콘)
2. 다음 명령어 실행:

```bash
# 인스턴스 연결 (인스턴스 연결 이름 확인 필요)
gcloud sql connect hci-postgres --user=postgres
```

3. 루트 비밀번호 입력

#### 2-3. 데이터베이스 및 사용자 생성
Cloud Shell 또는 연결된 클라이언트에서 다음 SQL 실행:

```sql
-- 데이터베이스 생성
CREATE DATABASE hci_fashion_db;

-- 애플리케이션용 사용자 생성
CREATE USER app_user WITH PASSWORD 'YourAppPassword123!@#';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE hci_fashion_db TO app_user;

-- 데이터베이스 연결
\c hci_fashion_db

-- 스키마 권한 부여
GRANT ALL ON SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
```

#### 2-4. pgvector 확장 활성화 확인
```sql
-- pgvector 확장 활성화 (이미 플래그로 활성화되어 있어야 함)
CREATE EXTENSION IF NOT EXISTS vector;

-- 확장 확인
\dx vector
```

---

### 3단계: 연결 정보 확인

#### 3-1. 인스턴스 연결 정보 확인
1. Cloud Console → SQL → 인스턴스 선택
2. 개요 탭에서 확인:
   - 연결 이름: `프로젝트ID:리전:인스턴스ID` 형식
   - 공개 IP 주소: 예) `34.123.45.67`
   - 포트: `5432` (기본값)

#### 3-2. 연결 문자열 구성
```
postgresql://app_user:YourAppPassword123!@#@34.123.45.67:5432/hci_fashion_db?sslmode=require
```

---

### 4단계: 방화벽 규칙 설정

#### 4-1. 승인된 네트워크 추가/수정
1. 인스턴스 → 연결 탭
2. 승인된 네트워크 섹션
3. 네트워크 추가 클릭
4. 네트워크: `0.0.0.0/0` (개발용) 또는 특정 IP
5. 저장 클릭

#### 4-2. VPC 방화벽 규칙 (VPC 사용 시)
1. VPC 네트워크 → 방화벽 규칙
2. 방화벽 규칙 만들기
3. 설정:
   - 이름: `allow-cloud-sql-postgres`
   - 방향: 수신
   - 대상: 지정된 대상 태그
   - 대상 태그: `cloud-sql-instance`
   - 소스 IP 범위: `0.0.0.0/0` 또는 특정 IP
   - 프로토콜 및 포트: TCP, 5432
4. 만들기 클릭

---

### 5단계: 로컬 환경에서 연결 테스트

#### 5-1. SSL 인증서 다운로드 (선택 사항)
1. 인스턴스 → 연결 탭
2. SSL 인증서 섹션
3. 서버 CA 인증서 다운로드 클릭
4. `server-ca.pem` 파일 저장

#### 5-2. 로컬에서 연결 테스트
```bash
# psql이 설치되어 있는 경우
psql "host=34.123.45.67 port=5432 dbname=hci_fashion_db user=app_user password=YourAppPassword123!@# sslmode=require"

# 또는 환경 변수 사용
export PGHOST=34.123.45.67
export PGPORT=5432
export PGDATABASE=hci_fashion_db
export PGUSER=app_user
export PGPASSWORD='YourAppPassword123!@#'
export PGSSLMODE=require

psql
```

#### 5-3. Python에서 연결 테스트
```python
import psycopg2

conn = psycopg2.connect(
    host="34.123.45.67",
    port=5432,
    database="hci_fashion_db",
    user="app_user",
    password="YourAppPassword123!@#",
    sslmode="require"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
```

---

### 6단계: 애플리케이션 환경 변수 설정

#### 6-1. .env 파일 업데이트
```bash
# .env.production
DATABASE_URL=postgresql://app_user:YourAppPassword123!@#@34.123.45.67:5432/hci_fashion_db?sslmode=require
```

#### 6-2. 환경 변수 보안 관리
- Google Secret Manager 사용 권장:
  1. Secret Manager → 비밀 만들기
  2. 이름: `database-url`
  3. 비밀 값: `DATABASE_URL` 값 입력
  4. 만들기 클릭

---

### 7단계: 마이그레이션 실행

#### 7-1. 로컬에서 마이그레이션 실행
```bash
cd backend

# 환경 변수 설정
export DATABASE_URL="postgresql://app_user:YourAppPassword123!@#@34.123.45.67:5432/hci_fashion_db?sslmode=require"

# 마이그레이션 실행
alembic upgrade head
```

#### 7-2. 마이그레이션 확인
```sql
-- 데이터베이스에 연결 후
\dt  -- 테이블 목록 확인
\d coordis  -- coordis 테이블 구조 확인 (description_embedding 컬럼 확인)
\dx  -- 확장 목록 확인 (vector 확장 확인)
```

---

### 8단계: 데이터 로드

#### 8-1. 태그 데이터 로드
```bash
cd backend
export DATABASE_URL="postgresql://app_user:YourAppPassword123!@#@34.123.45.67:5432/hci_fashion_db?sslmode=require"

python scripts/load_tags.py data/tags_sample.json
```

#### 8-2. 코디 데이터 로드
```bash
python scripts/load_coordis.py data/final_data_complete1.json
```

---

### 9단계: 모니터링 및 관리

#### 9-1. 모니터링 설정
1. 인스턴스 → 모니터링 탭
2. 메트릭 확인:
   - CPU 사용률
   - 메모리 사용률
   - 연결 수
   - 디스크 사용률

#### 9-2. 알림 설정
1. Cloud Monitoring → 알림 정책
2. 알림 정책 만들기
3. 조건 추가:
   - 메트릭: CPU 사용률
   - 임계값: 80%
4. 알림 채널 설정 (이메일 등)

#### 9-3. 백업 확인
1. 인스턴스 → 백업 탭
2. 자동 백업 상태 확인
3. 수동 백업 생성 (필요 시)

---

### 10단계: 보안 강화 (프로덕션)

#### 10-1. SSL/TLS 강제
- 이미 `sslmode=require` 설정됨
- 추가: 클라이언트 인증서 사용 고려

#### 10-2. IP 화이트리스트 제한
- 승인된 네트워크에서 `0.0.0.0/0` 제거
- 애플리케이션 서버 IP만 추가

#### 10-3. 비밀번호 정책
- 강력한 비밀번호 사용
- 정기적 비밀번호 변경

#### 10-4. 감사 로그 활성화
1. 인스턴스 → 감사 로그 탭
2. 감사 로그 활성화
3. 로그 유형 선택 (읽기, 쓰기 등)

---

### 문제 해결

#### 연결 실패
1. 방화벽 규칙 확인
2. IP 주소가 승인된 네트워크에 포함되어 있는지 확인
3. SSL 모드 확인 (`sslmode=require`)

#### pgvector 확장 오류
1. 데이터베이스 플래그 확인: `cloudsql.enable_pgvector=on`
2. 인스턴스 재시작 (필요 시)
3. 확장 수동 활성화:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

#### 성능 이슈
1. 머신 유형 업그레이드 고려
2. 인덱스 최적화
3. 연결 풀 설정 확인

---

### 비용 최적화

1. 개발 환경: `db-f1-micro` (무료 티어)
2. 프로덕션: 필요에 따라 스케일링
3. 자동 백업 보존 기간 조정
4. 사용하지 않는 인스턴스 중지/삭제

---

### 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] 결제 계정 연결
- [ ] Cloud SQL 인스턴스 생성 (PostgreSQL 15)
- [ ] `cloudsql.enable_pgvector=on` 플래그 설정
- [ ] 데이터베이스 및 사용자 생성
- [ ] pgvector 확장 활성화 확인
- [ ] 방화벽 규칙 설정
- [ ] 연결 테스트 성공
- [ ] 환경 변수 설정
- [ ] 마이그레이션 실행
- [ ] 데이터 로드 완료
- [ ] 모니터링 설정

이 가이드를 따라 설정하면 Cloud SQL에서 PostgreSQL + pgvector를 사용할 수 있습니다. 특정 단계에서 막히면 알려주세요.