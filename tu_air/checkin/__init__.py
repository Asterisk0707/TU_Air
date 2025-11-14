# TU_Air/tu_air/checkin/__init__.py
# (!!! 새 파일 !!!)

from flask import Blueprint

# 'checkin' 블루프린트 정의
checkin_bp = Blueprint('checkin', __name__, template_folder='../templates')

# checkin_views.py 파일을 임포트해서 라우트들을 등록합니다.
from . import checkin_views