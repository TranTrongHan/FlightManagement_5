from random import choice
from flask_mail import Message
from flask import session

from sqlalchemy import func, case, distinct

from sqlalchemy.sql import extract
from datetime import datetime, timedelta
from app import dao, db, app, mail
from app.models import Ticket, Flight, Customer, Seat, FareClass, Plane, Route,User


def get_seat_by_quantity(quantity, flightid, fareclassid=None):
    if quantity:
        selected_seats = []
        seatinfo = {}
        for index in range(quantity):
            seats = Seat.query.filter(Seat.status == False, Seat.flight_id == flightid,
                                      Seat.fareclass_id == fareclassid).all()
            if seats:
                rand_seat = choice(seats)
                rand_seat.status = True
                selected_seats.append(rand_seat)
                seatinfo[int(rand_seat.id)] = {
                    "id": int(rand_seat.id),
                    "name": str(rand_seat.name),
                    "flightid": int(rand_seat.flight_id)
                }
                db.session.commit()
            elif not seats:
                return selected_seats
        session['seats'] = seatinfo
        return selected_seats



def add_ticket(ticket_info):
    selected_seats = session.get('seats')
    flightid = ticket_info.get('flightid')
    flight_obj = dao.get_flight_by_id(id=flightid)

    customerid  = ticket_info.get('customerid')
    customer_obj = dao.get_user_by_id(id=customerid)


    existing_customer = db.session.query(Customer).filter_by(user_id=customerid).first()
    existing_flight = db.session.query(Flight).filter_by(id=flightid).first()

    # Sử dụng đối tượng đã tồn tại
    customer_obj = existing_customer
    flight_obj = existing_flight


    for seat in selected_seats.values():
        seat_obj = dao.get_seat_by_id(id=seat['id'])
        ticket = Ticket(customer=customer_obj, flight=flight_obj, seat=seat_obj, created_date=datetime.now())
        db.session.add(ticket)


    db.session.commit()


def check_valid_date(depart_time=None, return_time=None):
    departure_date = datetime.strptime(depart_time, '%Y-%m-%d')
    return_date = datetime.strptime(return_time, '%Y-%m-%d')
    if return_date <= departure_date:
        return False
    return True


def check_pending_flighttime(flightid=None, customerid=None):
    cus_tickets = dao.get_tickets(customerid=customerid)
    pending_flight = dao.get_flight_by_id(id=flightid)
    for cus_ticket in cus_tickets:
        booked_flight = dao.get_flight_by_id(id=cus_ticket.flight_id)
        if booked_flight.take_of_time <= pending_flight.take_of_time and booked_flight.landing_time >= pending_flight.landing_time:
            return booked_flight.id
    return None


def check_booking_exists(flightid=None, userid=None):
    flight = dao.get_flight_by_id(id=flightid)

    booked_flight = None
    # lấy thời gian bay vé đã đặt của khách hàng đó
    tickets = dao.get_tickets(userid=userid)
    for ticket in tickets:
        if ticket.flight_id == flight.id:
           return True
    return False


def check_valid_time(takeofftime=None):
    takeofftime = datetime.strptime(takeofftime, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    # lấy thời gian khởi hành của chuyến bay - 12 ra thời gian dc phép đặt vé
    rule = dao.get_rule_by_id(id='3')
    cut_off_time = takeofftime - timedelta(hours=rule.value)
    # so sánh nếu thời gian hiện tại nhỏ hơn thời gian dc phép đặt vé => ko đc đặt vé
    if current_time > cut_off_time:
        return False
    return True


def check_seat(flightid=None, quantity=None, fareclassid=None):
    fareclass_seats = Seat.query.filter(Seat.flight_id == flightid, Seat.status == False,
                                        Seat.fareclass_id == fareclassid).count()
    if quantity > fareclass_seats:
        return False
    return True


def count_seat_of_flight(flightid=None, fareclassid=None):
    if flightid and fareclassid:
        avail_seats = Seat.query.filter(Seat.flight_id == flightid, Seat.status == False,
                                        Seat.fareclass_id == fareclassid).count()
        return avail_seats


def send_ticket_email(ticket_info):
    subject = f"Vé {ticket_info['order_id']} của bạn đã được ghi nhận."
    msg = Message(subject, recipients=[app.config['MAIL_USERNAME']])

    # Tạo nội dung email với bảng thông tin vé
    msg.html = f"""
    <h3>Chúc mừng bạn đã đặt vé thành công!</h3>
    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!</p>
    """
    # Gửi email
    mail.send(msg)


def route_stats(kw=None, from_date=None, to_date=None):
    route_stats = db.session.query(Route.id, Route.name,
                                   func.coalesce(func.sum
                                                 (case((Seat.status == True, FareClass.price), else_=0)),
                                                 0).label('total_revenue')) \
        .join(Flight, Flight.route_id.__eq__(Route.id), isouter=True) \
        .join(Seat, Seat.flight_id.__eq__(Flight.id), isouter=True) \
        .join(Ticket, Ticket.seat_id.__eq__(Seat.id), isouter=True) \
        .join(FareClass, FareClass.id.__eq__(Seat.fareclass_id), isouter=True) \
        .group_by(Route.id, Route.name)

    filtered_route_stats = []
    for route in route_stats.all():
        filtered_route_stats.append({
            'id': route[0],
            'name': route[1],
            'total_revenue': float(route[2])
        })

    if kw:
        filtered_route_stats = route_stats.filter(Route.name.contains(kw))
    if from_date:
        filtered_route_stats = route_stats.filter(Ticket.created_date.__ge__(from_date))
    if to_date:
        filtered_route_stats = route_stats.filter(Ticket.created_date.__le__(to_date))

    return filtered_route_stats


def route_month_stats(year, month):
    #Subquery để lấy tổng số ghế cho từng tuyến bay
    total_seats_subquery = db.session.query(
        Flight.route_id,
        (func.sum(Flight.first_seat_quantity + Flight.second_seat_quantity)).label('total_seats')
    ).group_by(Flight.route_id).subquery()
    #
    # # Truy vấn test để lấy tên tuyến bay và tổng số ghế
    # route_seat_stats = db.session.query(
    #     Route.name.label('route_name'),  # Tên tuyến bay
    #     func.coalesce(total_seats_subquery.c.total_seats, 0).label('total_seats')  # Tổng số ghế
    # ).join(
    #     total_seats_subquery, total_seats_subquery.c.route_id == Route.id  # Kết nối với subquery
    # ).all()
    # for stat in route_seat_stats:
    #     print(f"Tuyến bay: {stat.route_name}, Tổng số ghế: {stat.total_seats}")

    # Query for total revenue, ticket count, and flight ratio
    month_stats = db.session.query(
        Route.name.label('route_name'),  # Route name
        func.sum(FareClass.price).label('total_revenue'),  # Total revenue
        func.count(distinct(Ticket.id)).label('total_ticket'), # Total tickets
        func.round((func.count(distinct(Ticket.id))/total_seats_subquery.c.total_seats)*100,2)
    ).join(
        Seat, Seat.id == Ticket.seat_id
    ).join(
        Flight, Flight.id == Seat.flight_id  # Ensure Flight is joined before Route
    ).join(
        total_seats_subquery, total_seats_subquery.c.route_id == Flight.route_id  # Join with total seats subquery
    ).join(
        FareClass, FareClass.id == Seat.fareclass_id, isouter=True
    ).join(
        Route, Route.id == Flight.route_id  # Now join Route
    ).filter(
        extract('year', Ticket.created_date) == year,  # Filter by year
        extract('month', Ticket.created_date) == month,  # Filter by month
        Seat.status == True  # Only count booked seats
    ).group_by(
        Route.name,  # Group by route name
        total_seats_subquery.c.total_seats
    )



    # route_id = 1  # Thay đổi giá trị này cho phù hợp với tuyến bay bạn muốn
    # # Truy vấn test tổng số vé cho tuyến bay cụ thể
    # total_tickets_query = db.session.query(
    #     Route.name.label('route_name'),  # Tên tuyến bay
    #     func.count(Ticket.id).label('total_tickets')  # Tổng số vé
    # ).join(
    #     Flight, Flight.route_id == Route.id  # Kiểm tra xem 'Route.id' có chính xác không
    # ).join(
    #     Ticket, Ticket.flight_id == Flight.id
    # ).filter(
    #     Route.id == route_id  # Lọc theo tuyến bay
    # ).group_by(
    #     Route.name  # Nhóm theo tên tuyến bay
    # ).first()  # Lấy kết quả đầu tiên

    # # In ra kết quả
    # if total_tickets_query:
    #     print(f"Tuyến bay: {total_tickets_query.route_name}, Tổng số vé: {total_tickets_query.total_tickets}")
    # else:
    #     print("Không có vé nào cho tuyến bay này.")


    return month_stats.all()
