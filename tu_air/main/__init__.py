# TU_Air/tu_air/main/__init__.py
# (수정)

from flask import Blueprint

# 1. 'main' 블루프린트를 정의
main_bp = Blueprint('main', __name__, 
                    template_folder='../templates', 
                    static_folder='../static')

# 2. 뷰 파일을 임포트 (파일명 변경)
from . import main_views