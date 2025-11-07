# TU_Air/tu_air/booking/booking_views.py
# (!!! 새 파일 !!!)

from . import booking_bp
from ..extensions import db
from ..models import Flight # (향후 Flight 정보 조회용)
from flask import render_template, request, flash, redirect, url_for, session, g

@booking_bp.route('/select', methods=['POST'])
def select_flights():
    """
    search_results.html 폼에서 요금을 선택한 후 호출됩니다.
    선택 정보를 세션에 저장하고, 로그인 상태에 따라 분기합니다.
    """
    
    # 1. 폼에서 데이터 받기
    passenger_count = int(request.form.get('passenger_count', 1))
    seat_class = request.form.get('seat_class')
    action = request.form.get('action') # (proceed, guest, member_login)
    
    outbound_data = request.form.get('outbound_flight') # (예: "FL001|150000.0")
    inbound_data = request.form.get('inbound_flight')   # (예: "FL002|160000.0" 또는 None)

    # 2. 세션에 저장할 'pending_booking'(임시 예약) 객체 생성
    # (세션은 항상 비우고 시작)
    session.pop('pending_booking', None) 
    
    if not outbound_data:
        flash('가는 편 항공권을 선택해야 합니다.')
        # (TODO: 원래 검색 결과 페이지로 돌아가야 하나, 지금은 홈으로)
        return redirect(url_for('main.home')) 
        
    out_flight_id, out_price = outbound_data.split('|')
    
    pending_booking = {
        "passenger_count": passenger_count,
        "seat_class": seat_class,
        "outbound_flight_id": out_flight_id,
        "outbound_price": float(out_price),
        "inbound_flight_id": None,
        "inbound_price": 0.0,
        "total_price": 0.0
    }

    total_price = float(out_price)

    if inbound_data:
        in_flight_id, in_price = inbound_data.split('|')
        pending_booking["inbound_flight_id"] = in_flight_id
        pending_booking["inbound_price"] = float(in_price)
        total_price += float(in_price)

    pending_booking["total_price"] = total_price * passenger_count

    # 3. 세션에 임시 예약 정보 저장
    session['pending_booking'] = pending_booking
    
    # 4. 로그인 상태에 따라 분기
    
    # (1) 이미 로그인되어 있음 ('탑승객 정보 입력' 클릭)
    if g.user:
        # (TODO: 다음 단계인 '탑승객 정보' 페이지로 리다이렉트)
        flash(f"총 금액 {pending_booking['total_price']}원. 탑승객 정보를 입력하세요. (구현 필요)")
        return redirect(url_for('main.home')) # (임시로 홈으로)

    # (2) 로그인 안 됨
    else:
        # (2a) '비회원으로 진행' 클릭
        if action == 'guest':
            session['is_guest'] = True # (게스트임을 표시)
            # (TODO: 다음 단계인 '탑승객 정보' 페이지로 리다이렉트)
            flash(f"총 금액 {pending_booking['total_price']}원. (게스트) 탑승객 정보를 입력하세요. (구현 필요)")
            return redirect(url_for('main.home')) # (임시로 홈으로)
        
        # (2b) '회원으로 진행' 클릭
        elif action == 'member_login':
            session['is_guest'] = False
            # (예약 정보를 세션에 들고, 로그인 페이지로 보냄)
            flash('로그인 후 예약을 계속 진행해 주세요.')
            return redirect(url_for('auth.login'))

    return redirect(url_for('main.home'))