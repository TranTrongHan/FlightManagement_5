
from random import choice
from sqlalchemy import func
from sqlalchemy.sql import extract
from datetime import datetime
from app import dao,db
from app.models import Ticket, Flight, Customer, Seat, FareClass, Plane, Route


def get_seat_by_quantity(quantity,flightid):
    if quantity:
        selected_seats = []
        for _ in range(quantity):
            seats = Seat.query.filter(Seat.status == False, Seat.flight_id == flightid).all()
            rand_seat = choice(seats)
            rand_seat.status = True
            selected_seats.append(rand_seat)
        db.session.commit()
        return selected_seats
    return []

def create_ticket(ticket_info):
    flight_dict = ticket_info.get('flightid')

    selected_seats = get_seat_by_quantity(quantity=ticket_info['quantity'], flightid=flight_dict.get('id'))

    flight_obj = Flight.from_dict(flight_dict)
    customer_dict = ticket_info.get('customerid')
    customer_obj = Customer.from_dict(customer_dict)
    fareclass_dict = ticket_info.get('fareclassid')
    fareclass_obj = FareClass.from_dict(fareclass_dict)


    existing_customer = db.session.query(Customer).filter_by(user_id=customer_obj.user_id).first()
    existing_flight = db.session.query(Flight).filter_by(id=flight_obj.id).first()
    existing_fareclass = db.session.query(FareClass).filter_by(id=fareclass_obj.id).first()
    # Sử dụng đối tượng đã tồn tại
    customer_obj = existing_customer
    flight_obj = existing_flight
    fareclass_obj = existing_fareclass

    tickets = []
    for seat in selected_seats:
        ticket = Ticket( customer=customer_obj, flight=flight_obj, fareclass=fareclass_obj,
                        seat=seat, created_date = datetime.now())
        db.session.add(ticket)
        tickets.append(ticket)
    db.session.commit()

    return tickets

def add_ticket(ticket_info):
    flight_dict = ticket_info.get('flightid')

    selected_seats = get_seat_by_quantity(quantity=ticket_info['quantity'],flightid=flight_dict.get('id'))


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
    for seat in selected_seats:
        ticket = Ticket(customer = customer_obj,flight= flight_obj,fareclass = fareclass_obj,
                        seat = seat,created_date = datetime.now() )
        db.session.add(ticket)
        tickets.append(ticket)
    db.session.commit()
def check_valid_date(depart_time = None,return_time=None):
    departure_date = datetime.strptime(depart_time, '%Y-%m-%d')
    return_date = datetime.strptime(return_time, '%Y-%m-%d')
    if return_date <= departure_date:
        return False
    return True
def check_used_to_bookticket(flightid=None):
    booked_ticket = Ticket.query.filter(Ticket.flight_id == flightid)
    if booked_ticket:
        return True
    return False
def check_unvalid_ticket(takeofftime=None,landingtime=None,flightid=None):
    has_ticket = False
    if takeofftime and landingtime:
        takeofftime = datetime.strptime(takeofftime,'%Y-%m-%d %H:%M:%S')
        takeoffday = takeofftime.day
        takeoffmonth = takeofftime.month
        landingtime = datetime.strptime(landingtime, '%Y-%m-%d %H:%M:%S')
        landingday = landingtime.day
        landingmonth = landingtime.month
        # lay ve da dat cua chuyen bay dang dat
        booked_ticket = Ticket.query.filter(Ticket.flight_id == flightid).first()
        if booked_ticket:
            # ve dang dat da trung thoi gian di cua ve truoc do
            # if landingtime < booked_ticket.depart_date:
            #     return True
            # elif takeofftime > booked_ticket.return_date:
            #     return True
            depart_date = booked_ticket.depart_date
            departday = depart_date.day
            departmonth = depart_date.month
            return_date =booked_ticket.return_date
            returnday = return_date.day
            returnmonth = return_date.month
            if takeoffday > departday:
                pass


    return has_ticket

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