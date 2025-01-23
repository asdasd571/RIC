###################################################################
#db 설정 파일 
import os

# 프로젝트 디렉토리 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# PostgreSQL 연결 URI
SQLALCHEMY_DATABASE_URI = 'postgresql://nak:1234@postgres:5432/mydb'

SQLALCHEMY_TRACK_MODIFICATIONS = False
###################################################################
