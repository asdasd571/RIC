from flask import Blueprint, request, jsonify
from .. import db
from ..models import DataStore
import logging
# 블루프린트 정의
db_bp = Blueprint('man', __name__,url_prefix='/man')



def db_read_one(key):
    """특정 키 데이터 읽기"""
    data = DataStore.query.filter_by(key=key).first()
    if data:
        return {key: data.value}
    return {"error": "Key not found"}, 404

def db_write_one(key, value):
    """특정 키 데이터 쓰기 (삽입 또는 업데이트)"""
    try:
        data = DataStore.query.filter_by(key=key).first()
        if data:
            data.value = value
        else:
            data = DataStore(key=key, value=value)
            db.session.add(data)
        logging.info(f"Committing data for key: {key}, value: {value}")

        db.session.commit()
        return {"message": f"Value set for {key}"}
    except Exception as e:
        db.session.rollback()  # 오류 발생 시 롤백
        return {"error": str(e)}, 500

def db_read_all():
    """모든 데이터 읽기"""
    data = DataStore.query.all()
    return {item.key: item.value for item in data}
  
def db_write_all(new_data):
    """모든 데이터 덮어쓰기"""
    DataStore.query.delete()  # 기존 데이터 삭제
    for key, value in new_data.items():
        data = DataStore(key=key, value=value)
        db.session.add(data)
    db.session.commit()
    return {"message": "All data overwritten"}


@db_bp.route('/read', methods=['GET'])
def api_db_read():
    key = request.args.get('key')
    if not key:
        return {"error": "Key is required"}, 400
    return db_read_one(key)

@db_bp.route('/write', methods=['POST'])
def api_db_write():
    try:
        data = request.json
        if not data:
            return {"error": "Invalid JSON format"}, 400
        if 'key' not in data or 'value' not in data:
            return {"error": "Key and value are required"}, 400
        return db_write_one(data['key'], data['value'])
    except Exception as e:
        return {"error": str(e)}, 500

@db_bp.route('/read-all', methods=['GET'])
def api_db_read_all():
    return db_read_all()

@db_bp.route('/write-all', methods=['POST'])
def api_db_write_all():
    data = request.json
    if not isinstance(data, dict):
        return {"error": "Data must be a dictionary"}, 400
    return db_write_all(data)
