# Python 3.11 슬림 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 어댑터, OpenCV/Mediapipe 지원 등)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Cloud Run은 기본적으로 8080 포트를 사용합니다
ENV PORT=8080

# uvicorn 실행
# Cloud Run은 $PORT 환경변수를 주입하므로 그에 맞춰 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
