# Python 3.8 기반의 이미지를 사용
FROM python:3.8-slim

# PostgreSQL 클라이언트 설치
RUN apt-get update && apt-get install -y postgresql-client

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치를 위한 requirements.txt 복사
COPY requirements.txt /app/requirements.txt

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . /app

# PostgreSQL 연결 대기 후 Flask 애플리케이션 실행 (gunicorn 사용)
CMD ["sh", "-c", "until pg_isready -h postgres -U nak -d mydb; do echo 'Waiting for postgres...'; sleep 2; done; echo 'PostgreSQL is ready!'; gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app"]
