from symtable import Class

from app import db, app
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum

from datetime import datetime, date, time

class UserRoleEnum(RoleEnum):
    CUSTOMER = 1
    STAFF = 2
    ADMIN = 3

class AirportRole(RoleEnum):
    DEPARTURE = 1
    ARRIVAL = 2
    INTERMEDIATE = 3

class User(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100), default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.CUSTOMER)
    joined_date = Column(DateTime, default=datetime.now())
    staff_id = relationship("Staff",uselist=False)
    admin_id = relationship("Admin", uselist=False)
    customer_id = relationship("Customer", uselist=False)
    def __str__(self):
        return self.firstname

class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    tickets = relationship("Ticket",backref="Customer",lazy=True)

class Staff(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey(User.id),nullable=False,unique=True)
    password = Column(String(20),nullable=False)
    flight_schedules = relationship("FlightSchedule",backref="Staff",lazy=True)

    # user = relationship("User",uselist=False)

class Admin(db.Model):
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey(User.id),nullable=False,unique=True)
    password = Column(String(20), nullable=False)



class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    seats = relationship("Seat",backref="Plane",lazy=True)
    flights = relationship("Flight",backref="Plane",lazy=True)
    def __str__(self):
        return self.name

class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False,unique=True)
    routes = relationship("RouteDetails",backref="Airport",lazy=True)

    def __str__(self):
        return self.name

class Route(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    flighs = relationship("Flight",backref="Route",lazy=True)
    airports = relationship("Airport",backref="Route",lazy=True)
    def __str__(self):
        return self.name

class RouteDetails(db.Model):
    # id = Column(Integer, primary_key=True, autoincrement=True)
    airport_role = Column(Enum(AirportRole),nullable=False)
    stop_time = Column(Float(),nullable=False)
    note = Column(String(255),nullable=True)
    airport_id = Column(Integer, ForeignKey(Airport.id), primary_key=True)
    routes_id = Column(Integer, ForeignKey(Route.id), primary_key=True)

class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    tickets = relationship("Ticket",backref="Flight",lazy=True)
    plane_id = Column(Integer,ForeignKey(Plane.id),nullable=False)
    route_id = Column(Integer,ForeignKey(Route.id),nullable=False)
    def __str__(self):
        return self.name

class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    price = Column(Float,nullable=False)
    tickets = relationship("Ticket",backref="FareClass",lazy=True)
    def __str__(self):
        return self.name

class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer,ForeignKey(Customer.id),nullable=False)
    fareclass_id = Column(Integer,ForeignKey(FareClass.id),nullable=False)
    seat_id  = relationship("Seat",uselist=False)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable=False)


class Seat(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    status = Column(Boolean,nullable=False)
    ticket_id = Column(Integer,ForeignKey(Ticket.id),nullable=False, unique=True)
    plane_id = Column(Integer,ForeignKey(Plane.id),nullable=False)
    def __str__(self):
        return self.name

class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer,ForeignKey(Staff.id),nullable=False)
    flight_details = relationship("FlightDetails",backref="FlightSchedule",lazy=True)

class FlightDetails(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    departure_time = Column(DateTime,nullable=False)
    flytime  = Column(Float,nullable=False)
    num_of_1st_seat = Column(Integer,nullable=False)
    num_of_2st_seat = Column(Integer,nullable=False)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable=False,unique=True)
    flight_schedule_id =Column(Integer,ForeignKey(FlightSchedule.id),nullable=False)








if __name__ == "__main__":
    with app.app_context():
        db.create_all()