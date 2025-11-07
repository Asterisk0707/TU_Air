# tu_air/auth/__init__.py

from flask import Blueprint

# 'auth' 블루프린트 정의
# (template_folder='../templates'는 HTML 파일들이 /tu_air/templates/에 있다고 알려줍니다)
auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# auth_views.py 파일을 임포트해서 라우트들을 등록합니다.
from . import auth_views