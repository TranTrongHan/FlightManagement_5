from datetime import datetime, timedelta
from random import choice

from flask import session
from flask_login import current_user
from app import dao,db
from app.models import Ticket, Flight, Customer, Seat, FareClass,Plane


def get_seat_by_quantity(quantity,planeid):
    if quantity:
        selected_seats = []
        for _ in range(quantity):
            seats = Seat.query.filter(Seat.status == False, Seat.plane_id == planeid).all()
            rand_seat = choice(seats)
            rand_seat.status = True
            selected_seats.append(rand_seat)
        db.session.commit()
        return selected_seats
    return []

def create_ticket(ticket_info):
    selected_seats = get_seat_by_quantity(quantity=ticket_info['quantity'],planeid=ticket_info['planeid'])
    flight = dao.get_flight_by_id(id=ticket_info['flightid'])
    customer = dao.get_user_by_id(id=ticket_info['customerid'])
    fareclass = dao.get_fareclass_by_id(id=ticket_info['fareclassid'])
    if ticket_info:
        for seat in selected_seats:
            ticket = Ticket(customer =customer ,flight=flight,fareclass=fareclass,seat = seat.__getattribute__('id'),created_date=datetime.now())
            db.session.add(ticket)

        db.session.commit()

def add_ticket(ticket_info):
    selected_seats = get_seat_by_quantity(quantity=ticket_info['quantity'],planeid=ticket_info['planeid'])

    # flight = dao.get_flight_by_id(id=ticket_info['flightid'])
    # customer = dao.get_user_by_id(id=ticket_info['customerid'])
    # fareclass = dao.get_fareclass_by_id(id=ticket_info['fareclassid'])
    # plane = dao.get_plane_by_id(id=ticket_info['planeid'])

    flight_dict = ticket_info.get('flightid')
    flight_obj = Flight.from_dict(flight_dict)
    customer_dict = ticket_info.get('customerid')
    customer_obj = Customer.from_dict(customer_dict)
    fareclass_dict = ticket_info.get('fareclassid')
    fareclass_obj = FareClass.from_dict(fareclass_dict)

    existing_customer = db.session.query(Customer).filter_by(user_id=customer_obj.user_id).first()
    existing_flight = db.session.query(Flight).filter_by(id = flight_obj.id).first()
    existing_fareclass = db.session.query(FareClass).filter_by(id = fareclass_obj.id).first()
    # Sử dụng đối tượng đã tồn tại
    customer_obj = existing_customer
    flight_obj = existing_flight
    fareclass_obj = existing_fareclass

    tickets = []
    for seat in selected_seats:
        ticket = Ticket(customer = customer_obj,flight= flight_obj,fareclass = fareclass_obj,
                        seat = seat,created_date=datetime.now())
        db.session.add(ticket)
        tickets.append(ticket)
    db.session.commit()
def check_valid_date(depart_time = None,return_time=None):
    departure_date = datetime.strptime(depart_time, '%Y-%m-%d')
    return_date = datetime.strptime(return_time, '%Y-%m-%d')
    if return_date <= departure_date:
        return False
    return True
# def check_book_flight(takeoff_time = None):
#     if takeoff_time:
#         takeoff_time = datetime.strptime(takeoff_time, '%Y-%m-%d')
#         twelve_hours_before = takeoff_time - timedelta(hours=12)
#         current_time = datetime.now()
#         if current_time <= twelve_hours_before:
#             return True
#     return False