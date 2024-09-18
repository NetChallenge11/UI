# Python 3.9 이미지를 베이스로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Flask 환경 변수를 설정
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV="development"

# 컨테이너의 포트 5000번을 열어줌
EXPOSE 5000

# 애플리케이션을 시작
CMD ["flask", "run"]