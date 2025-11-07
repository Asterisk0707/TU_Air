# TU_Air/tu_air/booking/__init__.py
# (!!! 새 파일 !!!)

from flask import Blueprint

# 'booking' 블루프린트 정의
booking_bp = Blueprint('booking', __name__, template_folder='../templates')

# booking_views.py 파일을 임포트해서 라우트들을 등록합니다.
from . import booking_views