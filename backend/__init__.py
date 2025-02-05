###################################################################
#flask 앱 실행 초기화 해주는 파일 
from flask import Flask, json, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import config
from .views.vrapp import eprint, eeprint, RAPP_NAME, RAPP_URL, VIAVI_MODE, LG_MODE, ENABLE_RAPP_REG, print_rApp_status, rApp_reg, Num_Cell, network_info, Data_Update, rApp_algorithm, Thread, VIAVI_Direct_Mode, SCHEDULE_PERIOD, BLOCK_NAME, HOST_ADDRESS, HOST_PORT

# SQLAlchemy 인스턴스를 한 번만 생성
db = SQLAlchemy()

def create_app():
    # Flask 애플리케이션 객체 생성
    app = Flask(__name__)

    # CORS 설정
    CORS(app, supports_credentials=True)

    # Flask 애플리케이션 설정
    app.config.from_object(config)
    
    # SQLAlchemy 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nak:1234@postgres:5432/mydb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '1005'

    # DB 초기화 (SQLAlchemy가 Flask 애플리케이션에 연결)
    db.init_app(app)

    migrate = Migrate(app,db)

    ####################################################################
    # 블루프린트 등록
    from .views.Lib_login import ap as login
    from .views.kpm_console import ap as console
    from .views.vrapp import bp as vrapp
    from .views.Lib_sme_bk import bp as sme
    from .views.agent import bp as agent
    from .views.dme import db_bp as datab
    app.register_blueprint(login)  # login.py에서 정의된 블루프린트를 등록
    app.register_blueprint(console)
    app.register_blueprint(vrapp)
    app.register_blueprint(sme)
    app.register_blueprint(agent)
    app.register_blueprint(datab)
    ####################################################################

    #db_init 처리
    with app.app_context():
        try:             
            db.create_all()  # 테이블이 없다면 생성
            print("Database connection successful.")
        except Exception as e:
            print(f"Database connection failed: {e}")

    return app

# 앱 실행
if __name__ == '__main__':
    app = create_app()

    ## 0) 환경 설정 및 초기화
    eprint(0, RAPP_NAME)
    eeprint(0, "RAPP URL = ", RAPP_URL)
    eeprint(0, "VIAVI_MODE = ", VIAVI_MODE)
    eeprint(0, "LG_MODE = ", LG_MODE)

    ## 1) rApp, 서비스 등록
    eeprint(0, "ENABLE_RAPP_REG = ", ENABLE_RAPP_REG)
    if ENABLE_RAPP_REG == "ON":
        body = print_rApp_status()
        rApp_reg(RAPP_NAME, body)

    # 네트워크 초기화
    result = network_info()

    # 초기 값 설정
    Data_Update()
    DL_rate = [0] * (Num_Cell)
    Power_rate = [0] * (Num_Cell)
    UE_rate = [0] * (Num_Cell)

    sDL_rate = [0] * (Num_Cell)
    sPower_rate = [0] * (Num_Cell)
    sUE_rate = [0] * (Num_Cell)

    ## rApp 알고리즘 병렬 처리
    thread1 = Thread(target=rApp_algorithm)
    thread1.start()

    eeprint(0, "VIAVI_Direct_Mode = ", VIAVI_Direct_Mode)
    eeprint(0, "SCHEDULE_PERIOD = ", SCHEDULE_PERIOD)

    ## 웹 서버 실행
    eeprint(0, "Non-RT RIC rApp START : ", BLOCK_NAME)

    #wsgi에서 실행하면 됨
    # app.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True, use_reloader=False)
###################################################################
