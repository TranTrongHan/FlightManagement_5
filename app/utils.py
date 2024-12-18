from random import choice
from flask_mail import Message
from flask import session
from sqlalchemy import func
from sqlalchemy.sql import extract
from datetime import datetime
from app import dao, db, app, mail
from app.models import Ticket, Flight, Customer, Seat, FareClass, Plane, Route


def get_seat_by_quantity(quantity,flightid):
    if quantity:
        selected_seats = []
        seatinfo = {}
        for index  in range(quantity):
            seats = Seat.query.filter(Seat.status == False, Seat.flight_id == flightid).all()
            if seats:
                rand_seat = choice(seats)
                rand_seat.status = True
                # print(f"Chỉ số hiện tại: {index}")
                # print(f"Chỗ ngồi hiện tại: {rand_seat.name}")
                print(rand_seat.status)
                selected_seats.append(rand_seat)
                seatinfo[int(rand_seat.id)]={
                    "id":int(rand_seat.id),
                    "name":str(rand_seat.name),
                    "flightid":int(rand_seat.flight_id)
                }
                db.session.commit()

            elif not seats:
                return selected_seats
        session['seats'] = seatinfo
        return selected_seats


def add_ticket(ticket_info):
    flight_dict = ticket_info.get('flightid')

    selected_seats = session.get('seats')

    flight_obj = Flight.from_dict(flight_dict)
    customer_dict = ticket_info.get('customerid')
    customer_obj = Customer.from_dict(customer_dict)
    fareclass_dict = ticket_info.get('fareclassid')
    fareclass_obj = FareClass.from_dict(fareclass_dict)
    # flight = dao.get_flight_by_id(id=ticket_info['flightid'])
    # customer = dao.get_user_by_id(id=ticket_info['customerid'])
    # fareclass = dao.get_fareclass_by_id(id=ticket_info['fareclassid'])
    # plane = dao.get_plane_by_id(id=ticket_info['planeid'])


    existing_customer = db.session.query(Customer).filter_by(user_id=customer_obj.user_id).first()
    existing_flight = db.session.query(Flight).filter_by(id = flight_obj.id).first()
    existing_fareclass = db.session.query(FareClass).filter_by(id = fareclass_obj.id).first()
    # Sử dụng đối tượng đã tồn tại
    customer_obj = existing_customer
    flight_obj = existing_flight
    fareclass_obj = existing_fareclass

    tickets = []
    for seat in selected_seats.values():
        seat_obj = dao.get_seat_by_id(id=seat['id'])
        ticket = Ticket(customer = customer_obj,flight= flight_obj,fareclass = fareclass_obj,
                        seat = seat_obj,created_date = datetime.now())
        db.session.add(ticket)
        tickets.append(ticket)
    db.session.commit()
def check_valid_date(depart_time = None,return_time=None):
    departure_date = datetime.strptime(depart_time, '%Y-%m-%d')
    return_date = datetime.strptime(return_time, '%Y-%m-%d')
    if return_date <= departure_date:
        return False
    return True
def check_time(flighid = None,customerid = None):
    cus_tickets = dao.load_tickets(userid=customerid)
    flight = dao.get_flight_by_id(id = flighid)
    cus_flights = []
    pass


def testbackup():
    pass
def checkduplicate_ticket(flightid=None,customer_id=None):
    flight = dao.get_flight_by_id(id = flightid)
    booked_flight = None
    # lấy thời gian bay vé đã đặt của khách hàng đó
    tickets = dao.load_tickets(userid=customer_id)
    for ticket in tickets:
        if ticket.flight_id == flight.id:
            booked_flight = dao.get_flight_by_id(id=ticket.flight_id)

    return booked_flight


def count_seat_of_flight(flightid=None):
    if flightid:
        avail_seats = Seat.query.filter(Seat.flight_id == flightid,Seat.status==False).count()
        return avail_seats


def send_ticket_email(ticket_info):
    subject = f"Vé {ticket_info['order_id']} của bạn đã được ghi nhận."
    msg = Message(subject, recipients=[app.config['MAIL_USERNAME']])

    # Tạo nội dung email với bảng thông tin vé
    msg.html = f"""
    <h3>Chúc mừng bạn đã đặt vé thành công!</h3>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Thông Tin</th>
            <th>Giá Trị</th>
        </tr>
        <tr>
            <td>{ticket_info.get('customername')}</td>
            <td>{ticket_info.get('customername')}</td>
        </tr>
       
    </table>
    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!</p>
    """
    # Gửi email
    mail.send(msg)

def route_stats(kw = None,from_date=None,to_date=None):
    route_stats = db.session.query(Route.id,Route.name,
                    func.sum(FareClass.price))\
                .join(Flight,Flight.route_id.__eq__(Route.id),isouter = True) \
                .join(Ticket, Ticket.flight_id.__eq__(Flight.id), isouter=True) \
                .join(FareClass,FareClass.id.__eq__(Ticket.fareclass_id), isouter=True)\
            .group_by(Route.id,Route.name)
    if kw:
        route_stats = route_stats.filter(Route.name.contains(kw))
    if from_date:
        route_stats = route_stats.filter(Ticket.created_date.__ge__(from_date))
    if to_date:
        route_stats = route_stats.filter(Ticket.created_date.__le__(to_date))
    return  route_stats.all()

def route_month_stats(year):
    return db.session.query(extract('month',Ticket.created_date)
                            ,func.sum(FareClass.price))\
                            .join(FareClass, FareClass.id.__eq__(Ticket.fareclass_id))\
                            .filter(extract('year',Ticket.created_date) == year)\
                            .group_by(extract('month',Ticket.created_date))\
                            .order_by(extract('month',Ticket.created_date)).all()