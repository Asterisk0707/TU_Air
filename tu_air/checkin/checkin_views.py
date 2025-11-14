# TU_Air/tu_air/checkin/checkin_views.py
# (!!! 새 파일 !!!)

from . import checkin_bp
from ..extensions import db
from ..models import Booking, Passenger, Boarding_Pass
from flask import render_template, request, flash, redirect, url_for, session
import datetime

@checkin_bp.route('/', methods=['GET', 'POST'])
def index():
    """ R2: 체크인 1단계: 예약 번호 조회 """
    if request.method == 'POST':
        booking_id = request.form.get('booking_id', '').strip().upper()
        
        if not booking_id:
            flash('예약 번호를 입력해 주세요.')
            return redirect(url_for('checkin.index'))

        booking = Booking.query.get(booking_id)
        
        if not booking or booking.Status != 'Reserved':
            flash('일치하는 예약 정보를 찾을 수 없습니다.')
            return redirect(url_for('checkin.index'))
            
        # [!!!] (R2) (수정) '2시간 전' 마감 체크 [!!!]
        # (가는 편/오는 편 둘 중 하나라도 체크인 가능하면 통과)
        now = datetime.datetime.now()
        outbound_time_left = (booking.outbound_flight.Departure_Time - now).total_seconds()
        inbound_time_left = -1
        if booking.return_flight:
            inbound_time_left = (booking.return_flight.Departure_Time - now).total_seconds()

        if outbound_time_left < 7200 and (not booking.return_flight or inbound_time_left < 7200):
            flash('체크인 가능한 항공편이 없습니다. (출발 2시간 전 마감)')
            return redirect(url_for('checkin.index'))

        # [!!!] (R4) (수정) 2단계 '여정 선택' 페이지로 이동 [!!!]
        return redirect(url_for('checkin.select_journey', booking_id=booking.Booking_ID))

    return render_template('checkin_index.html')

# [!!!] (R4) (신규) 2단계: 여정 선택 [!!!]
@checkin_bp.route('/<string:booking_id>/journey', methods=['GET'])
def select_journey(booking_id):
    """ (R4) 체크인 2단계: 가는 편 / 오는 편 여정 선택 """
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.Status != 'Reserved':
        flash('체크인이 불가능한 예약입니다.')
        return redirect(url_for('checkin.index'))
        
    now = datetime.datetime.now()
    
    # (가는 편 체크인 가능 여부 확인)
    outbound_time_ok = (booking.outbound_flight.Departure_Time - now).total_seconds() > 7200
    pax_out_sample = Passenger.query.filter_by(
        Booking_ID=booking_id, Flight_ID=booking.Outbound_Flight_ID
    ).first()
    outbound_checked_in = Boarding_Pass.query.filter_by(
        Booking_ID=booking_id, Flight_ID=pax_out_sample.Flight_ID, Seat_ID=pax_out_sample.Seat_ID
    ).first() is not None
    
    # (오는 편 체크인 가능 여부 확인)
    inbound_time_ok = False
    inbound_checked_in = False
    if booking.return_flight:
        inbound_time_ok = (booking.return_flight.Departure_Time - now).total_seconds() > 7200
        pax_in_sample = Passenger.query.filter_by(
            Booking_ID=booking_id, Flight_ID=booking.Return_Flight_ID
        ).first()
        if pax_in_sample:
            inbound_checked_in = Boarding_Pass.query.filter_by(
                Booking_ID=booking_id, Flight_ID=pax_in_sample.Flight_ID, Seat_ID=pax_in_sample.Seat_ID
            ).first() is not None

    return render_template('checkin_journey.html',
                           booking=booking,
                           outbound_time_ok=outbound_time_ok,
                           outbound_checked_in=outbound_checked_in,
                           inbound_time_ok=inbound_time_ok,
                           inbound_checked_in=inbound_checked_in)

@checkin_bp.route('/<string:booking_id>/<string:direction>', methods=['GET', 'POST'])
def details(booking_id, direction):
    """ R3, R4: 체크인 3단계: 탑승객 상세 정보 입력 """
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.Status != 'Reserved':
        flash('체크인이 불가능한 예약입니다.')
        return redirect(url_for('checkin.index'))

    # (체크인할 항공편 ID 및 객체 설정)
    if direction == 'outbound':
        current_flight_id = booking.Outbound_Flight_ID
        current_flight = booking.outbound_flight
    elif direction == 'inbound' and booking.return_flight:
        current_flight_id = booking.Return_Flight_ID
        current_flight = booking.return_flight
    else:
        flash('잘못된 여정입니다.')
        return redirect(url_for('checkin.select_journey', booking_id=booking_id))
        
    # (R2) 시간 재검사
    if (current_flight.Departure_Time - datetime.datetime.now()).total_seconds() < 7200:
        flash('체크인 마감 시간(출발 2시간 전)이 지났습니다.')
        return redirect(url_for('checkin.select_journey', booking_id=booking_id))

    # (탑승객 목록 조회)
    passengers_to_checkin = Passenger.query.filter_by(
        Booking_ID=booking_id, 
        Flight_ID=current_flight_id
    ).all()
    
    # (이미 체크인했는지 확인)
    if passengers_to_checkin and passengers_to_checkin[0].boarding_pass:
        flash(f"이미 {direction} 여정의 체크인이 완료되었습니다.")
        return redirect(url_for('checkin.select_journey', booking_id=booking_id))
    
    # (R4) 국제선 여부 확인
    is_international = (current_flight.departure_airport.Country != '대한민국' or 
                        current_flight.arrival_airport.Country != '대한민국')

    # (R5) POST: 폼 제출 시 (탑승권 발급)
    if request.method == 'POST':
        try:
            nationalities = request.form.getlist('nationality')
            phones = request.form.getlist('phone')
            passport_nos = request.form.getlist('passport_no')
            
            if len(nationalities) != len(passengers_to_checkin):
                raise Exception("폼 데이터가 올바르지 않습니다.")
            
            for i in range(len(passengers_to_checkin)):
                if not nationalities[i] or not phones[i]:
                    raise Exception(f"'인원 {i+1}'의 국적, 전화번호는 필수입니다.")
                if is_international and not passport_nos[i]:
                    raise Exception(f"'인원 {i+1}'의 여권번호는 국제선 탑승에 필수입니다.")

            # [!!!] (R1, R5) (수정) 'Booking' 상태는 변경하지 않음 [!!!]
            
            # (Passenger 정보 업데이트 및 Boarding_Pass 생성)
            for i, pax in enumerate(passengers_to_checkin):
                pax.Nationality = nationalities[i]
                pax.Phone = phones[i]
                pax.Passport_No = passport_nos[i] if is_international else None
                db.session.add(pax)
                
                new_bp = Boarding_Pass(
                    Booking_ID=booking.Booking_ID,
                    Flight_ID=pax.Flight_ID,
                    Seat_ID=pax.Seat_ID,
                    Boarding_Time=pax.flight.Departure_Time - datetime.timedelta(minutes=15)
                )
                db.session.add(new_bp)
            
            db.session.commit()
            
            # (R4) 다시 여정 선택 페이지로 돌아감
            return redirect(url_for('checkin.select_journey', booking_id=booking_id))

        except Exception as e:
            db.session.rollback()
            flash(f'체크인 중 오류가 발생했습니다: {e}')

    # GET: 폼 페이지 렌더링
    return render_template('checkin_details.html',
                           booking=booking,
                           passengers=passengers_to_checkin,
                           is_international=is_international,
                           direction=direction) # (R4)

# [!!!] (R4) (신규) 체크인 취소 (Boarding_Pass 삭제) [!!!]
@checkin_bp.route('/<string:booking_id>/cancel', methods=['POST'])
def cancel_checkin(booking_id):
    """ (R4) 체크인 취소: 이 여정의 Boarding_Pass만 삭제 """
    
    booking = Booking.query.get_or_404(booking_id)
    direction = request.form.get('direction', 'outbound')

    if direction == 'outbound':
        flight_id = booking.Outbound_Flight_ID
    else:
        flight_id = booking.Return_Flight_ID

    if not flight_id:
        flash('잘못된 여정입니다.')
        return redirect(url_for('checkin.select_journey', booking_id=booking_id))
        
    try:
        # (이 여정의 모든 탑승객)
        passengers = Passenger.query.filter_by(Booking_ID=booking_id, Flight_ID=flight_id).all()
        
        for pax in passengers:
            if pax.boarding_pass:
                db.session.delete(pax.boarding_pass)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'체크인 취소 중 오류가 발생했습니다: {e}')

    return redirect(url_for('checkin.select_journey', booking_id=booking_id))