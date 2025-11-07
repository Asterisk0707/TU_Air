# TU_Air/tu_air/mypage/__init__.py
# (!!! 새 파일 !!!)

from flask import Blueprint

# 'mypage' 블루프린트 정의
mypage_bp = Blueprint('mypage', __name__, template_folder='../templates')

# mypage_views.py 파일을 임포트해서 라우트들을 등록합니다.
from . import mypage_views