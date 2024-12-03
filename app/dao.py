from datetime import datetime
from app import db
from app.models import Flight, Route, Airport, Customer, User, Admin, UserRoleEnum, FareClass, Plane, Seat, Ticket
import hashlib
import random
def load_route(route_id = None):
    query = Route.query
    if route_id:
        query = query.filter(Route.id  == route_id)
    return query.all()

def load_specific_routes(takeoffId = None, landingairportId=None):
    if takeoffId and landingairportId:
        return Route.query.filter(Route.take_off_airport_id == takeoffId,
                                  Route.landing_airport_id == landingairportId)


def load_airport_id(airportrole =None):
    if(airportrole):
        query = Route.query.order_by('name').filter(Route.take_off_airport_id)
    else:
        query = Route.query.order_by('name').filter(Route.landing_airport_id)
    return query

def load_airport():
    return Airport.query.all()

def load_flights(flight_id=None):
    query = Flight.query
    if flight_id:
        query = query.filter(Flight.id == flight_id)
    return query.all()
def load_fareclass():
    return FareClass.query.all()
def auth_user(username,password):

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()
def check_role(username , password,role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u =  User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()
    if u.__getattribute__('user_role') == role:
        return True
    return False

def add_user(last_name,first_name, phone, address,email ,avatar ,username,password ):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    last_name = last_name.strip()
    first_name = first_name.strip()
    phone = phone.strip()
    address = address.strip()
    email = email.strip()
    username = username.strip()
    password = password.strip()
    u = User(last_name = last_name,first_name = first_name,phone = phone,address = address , email=email,
             avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg',
             user_role = UserRoleEnum.CUSTOMER,joined_date =datetime.now(),
             username = username,password = password)
    db.session.add(u)
    db.session.commit()
def check_user_existence(last_name=None, first_name=None,phone = None, email=None):
    if email:
        existing_user_email = User.query.filter_by(email=email.strip()).first()
        if existing_user_email:
            return False
    if phone:
        existing_phone = User.query.filter_by(phone = phone.strip()).first()
        if existing_phone:
            return False
    if last_name and first_name:
        existing_user_name = User.query.filter_by(last_name=last_name.strip(), first_name=first_name.strip()).first()
        if existing_user_name:
            return False
    return True

def existence_check(attribute ,value):
    return User.query.filter(getattr(User, attribute).__eq__(value)).first()

def get_user_by_id(id):
    return User.query.get(id)

def get_flight_by_id(id):
    return Flight.query.get(id)


def load_empty_seat(planeid):
    return Seat.query.filter(Seat.plane_id == planeid,Seat.status==0).all()


def get_ticket_by_seat(seatid):
    return Ticket.query.get(Ticket.seat_id == seatid).first()

def get_seat_by_id(seatid):
    return Seat.query.get(seatid)

def load_plane():
    return Plane.query.all()

def get_plane_by_id(planeid):
    return Plane.query.get(planeid)