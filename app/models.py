

from app import db, app
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, values, false
from sqlalchemy.orm import relationship, backref
from enum import Enum as RoleEnum
import hashlib
from datetime import datetime, date, time
from flask_login import UserMixin


class UserRoleEnum(RoleEnum):
    CUSTOMER = 1
    STAFF = 2
    ADMIN = 3


class AirportRole(RoleEnum):
    DEPARTURE = 1
    ARRIVAL = 2
    INTERMEDIATE = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # last_name = Column(String(50), nullable=False)
    # first_name = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(UserRoleEnum), nullable=False)
    joined_date = Column(DateTime, default=datetime.now())
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    staff_id = relationship("Staff", uselist=False)
    admin_id = relationship("Admin", uselist=False)
    customer_id = relationship("Customer", uselist=False)

    def __str__(self):
        return self.name



    #####################################
class Customer(db.Model):
    # id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False, unique=True)
    ticket = relationship("Ticket", backref="customer", lazy=True)

    def to_dict(self):
        return {
            # 'id': self.id,
            'user_id': self.user_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            # id=data['id'],
            user_id=data['user_id'],
        )

#####################################
class Staff(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    flight_schedules = relationship("FlightSchedule", backref="Staff", lazy=True)

    # user = relationship("User",uselist=False)

#####################################
class Admin(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)

#####################################
class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flights = relationship("Flight", backref="plane", lazy=True)
    def __str__(self):
        return self.name

#####################################
class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    take_off_airport = relationship("Route", foreign_keys="Route.take_off_airport_id", backref="takeoff_airport")
    landing_airport = relationship("Route", foreign_keys="Route.landing_airport_id", backref="landing_airport_ref")
    flights = relationship("MidAirport", backref="airport", lazy=True)

    def __str__(self):
        return self.name

#####################################
class Route(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flights = relationship("Flight", backref="route", lazy=True)
    take_off_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    landing_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)

    def __str__(self):
        return self.name

#####################################
class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    take_of_time = Column(DateTime, nullable=True)
    landing_time = Column(DateTime, nullable=True)
    num_of_1st_seat = Column(Integer, nullable=False)
    num_of_2st_seat = Column(Integer, nullable=False)
    mid_airports = relationship("MidAirport", backref="flight", lazy=True)
    ticket = relationship("Ticket", backref="flight", lazy=True)
    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=False)
    route_id = Column(Integer, ForeignKey(Route.id), nullable=False)
    flight_schedule_id = relationship("FlightSchedule", uselist=False)
    seats =  relationship("Seat",backref = "flight",lazy=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
        )

#####################################
class MidAirport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    stop_time = Column(Float(), nullable=False)
    note = Column(String(255), nullable=True)
    mid_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False, primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, primary_key=True)

class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    value = Column(Float, nullable=False)

#####################################
class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey(Staff.id), nullable=False)
    # flight_details = relationship("FlightDetails",backref="FlightSchedule",lazy=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, unique=True)

#####################################
class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    tickets = relationship("Ticket", backref="fareclass", lazy=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
        )

#####################################
class Seat(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    status = Column(Boolean, nullable=False)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable = False)
    ticket_id = relationship("Ticket", backref='seat', uselist=False)

    def __str__(self):
        return self.name

#####################################
class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey(Customer.user_id), nullable=False, primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, primary_key=True)
    fareclass_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)
    seat_id = Column(Integer, ForeignKey(Seat.id), nullable=True, unique=True)
    created_date = Column(DateTime,nullable=False)

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        rule1 = Rule(name='num_of_1st_class_seat', value=10)
        rule2 = Rule(name='num_of_2st_class_seat', value=10)
        rule3 = Rule(name='thời gian dừng tối thiểu', value='20')
        rule4 = Rule(name='1st_seat_price', value=1500000)
        rule5 = Rule(name='2st_seat_price', value=1000000)
        user1 = User(name='Nguyen An', phone='0123456789', address='123 Street A', email='an.nguyen@example.com',
                     user_role=UserRoleEnum.ADMIN, username='admin1',
                     password=str(hashlib.md5('admin1'.encode('utf-8')).hexdigest()))
        user2 = User(name='Tran Binh', phone='0123456790', address='456 Street B', email='binh.tran@example.com',
                     user_role=UserRoleEnum.ADMIN, username='admin2',
                     password=str(hashlib.md5('admin2'.encode('utf-8')).hexdigest()))
        user3 = User(name='Le Cuc', phone='0123456791', address='789 Street C', email='cuc.le@example.com',
                     user_role=UserRoleEnum.STAFF, username='staff1',
                     password=str(hashlib.md5('staff1'.encode('utf-8')).hexdigest()))
        user4 = User(name='Pham Duong', phone='0123456792', address='101 Street D', email='duong.pham@example.com',
                     user_role=UserRoleEnum.STAFF, username='staff2',
                     password=str(hashlib.md5('staff2'.encode('utf-8')).hexdigest()))
        user5 = User(name='Nguyen Minh', phone='0123456793', address='202 Street W',
                     email='minh.nguyen@example.com', user_role=UserRoleEnum.CUSTOMER, username='customer1',
                     password=str(hashlib.md5('customer1'.encode('utf-8')).hexdigest()))
        user6 = User(name='Hoang Tu', phone='0123456723', address='202 Street B', email='tu.hoang@example.com',
                     user_role=UserRoleEnum.CUSTOMER, username='customer2',
                     password=str(hashlib.md5('customer2'.encode('utf-8')).hexdigest()))

        db.session.add_all([user1, user2, user3, user4, user5, user6])
        db.session.commit()

        admin1 = Admin(user_id='1')
        admin2 = Admin(user_id='2')
        db.session.add_all([admin1, admin2])
        db.session.commit()

        staff1 = Staff(user_id='3')
        staff2 = Staff(user_id='4')
        db.session.add_all([staff1])
        db.session.commit()

        customer1 = Customer(user_id='5')
        customer2 = Customer(user_id='6')
        db.session.add_all([customer1, customer2])
        db.session.commit()

        plane1 = Plane(name='VietNam Airlines')
        plane2 = Plane(name='Vietjet Air')
        plane3 = Plane(name='Jetstar Pacific')
        plane4 = Plane(name='Bamboo Airways')
        plane5 = Plane(name='Japan Airlines')
        db.session.add_all([plane1, plane2, plane3, plane4, plane5])
        db.session.commit()

        airport1 = Airport(name='Nội Bài')
        airport2 = Airport(name='Tân Sơn Nhất')
        airport3 = Airport(name='Cần Thơ')
        airport4 = Airport(name='Đà Nẵng')
        airport5 = Airport(name='Cà Mau')
        airport6 = Airport(name='Phú Quốc')
        airport7 = Airport(name='Điện Biên Phủ')
        airport8 = Airport(name='Thọ Xuân')
        airport9 = Airport(name='Phú Bài')
        airport10 = Airport(name='Pleiku')
        airport11 = Airport(name='Rạch Giá')
        airport12 = Airport(name='Buôn Ma Thuột')
        airport13 = Airport(name='Liên Khương')
        airport14 = Airport(name='Côn Đảo')
        airport15 = Airport(name='TP Vinh')

        db.session.add_all(
            [airport1, airport2, airport3, airport4, airport5, airport6, airport7, airport8, airport9, airport10,
             airport11, airport12, airport13, airport14, airport15])
        db.session.commit()

        route1 = Route(name='Hà Nội - TP HCM', take_off_airport_id="1", landing_airport_id="2")
        route2 = Route(name='Cần Thơ - TP HCM', take_off_airport_id="3", landing_airport_id="2")
        route3 = Route(name='Đà Nẵng - TP HCM', take_off_airport_id="4", landing_airport_id="2")
        route4 = Route(name='Cà Mau - Phu Quoc', take_off_airport_id="5", landing_airport_id="6")
        route5 = Route(name='Cần Thơ - Hà Nội', take_off_airport_id="3", landing_airport_id="1")
        route6 = Route(name='Phú Quốc - Thọ Xuân', take_off_airport_id="6", landing_airport_id="8")
        route7 = Route(name='Điện Biên Phủ - Thọ Xuân', take_off_airport_id="7", landing_airport_id="8")
        route8 = Route(name='Thọ Xuân - Cần Thơ', take_off_airport_id="8", landing_airport_id="3")
        route9 = Route(name='Hà Nội - Phú Bài', take_off_airport_id="1", landing_airport_id="9")
        route10 = Route(name='Thọ Xuân - TP HCM', take_off_airport_id="8", landing_airport_id="2")
        route11 = Route(name='Rạch Giá - Cần Thơ', take_off_airport_id="11", landing_airport_id="3")
        route12 = Route(name='Buôn Ma Thuột - TP HCM', take_off_airport_id="12", landing_airport_id="2")
        route13 = Route(name='Rạch Giá - Liên Khương', take_off_airport_id="11", landing_airport_id="13")
        route14 = Route(name='Côn Đảo - Phú Quốc', take_off_airport_id="14", landing_airport_id="6")
        route15 = Route(name='TP Vinh - Thọ Xuân', take_off_airport_id="15", landing_airport_id="8")
        route16 = Route(name='Liên Khương - Cần Thơ', take_off_airport_id="13", landing_airport_id="3")
        db.session.add_all([route1, route2, route3, route4, route5,
                            route6, route7, route8, route9, route10,
                            route11, route12, route13, route14, route15,
                            route16])
        db.session.commit()

        db.session.add_all([rule1, rule2])
        db.session.commit()
        flight1 = Flight(name='VN001', take_of_time=datetime(2024, 12, 11, 11, 00, 00),
                         landing_time=datetime(2024, 12, 13, 12, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='1', route_id='1')
        flight2 = Flight(name='VN002', take_of_time=datetime(2024, 12, 11, 7, 00, 00),
                         landing_time=datetime(2024, 12, 14, 15, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='2', route_id='1')
        flight3 = Flight(name='VN003', take_of_time=datetime(2024, 12, 11, 9, 00, 00),
                         landing_time=datetime(2024, 12, 14, 9, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='4', route_id='1')
        flight4 = Flight(name='VN004', take_of_time=datetime(2024, 12, 12, 10, 00, 00),
                         landing_time=datetime(2024, 12, 13, 12, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='2', route_id='2')
        flight5 = Flight(name='VN005', take_of_time=datetime(2024, 12, 12, 9, 00, 00),
                         landing_time=datetime(2024, 12, 14, 11, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='1', route_id='2')
        flight6 = Flight(name='VN006', take_of_time=datetime(2024, 11, 12, 8, 00, 00),
                         landing_time=datetime(2024, 12, 15, 10, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='1', route_id='3')
        flight7 = Flight(name='VN007', take_of_time=datetime(2024, 12, 13, 22, 00, 00),
                         landing_time=datetime(2024, 12, 15, 22, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='2', route_id='3')
        flight8 = Flight(name='VN008', take_of_time=datetime(2024, 12, 13, 23, 00, 00),
                         landing_time=datetime(2024, 12, 15, 23, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='5', route_id='3')
        flight9 = Flight(name='VN009', take_of_time=datetime(2024, 12, 13, 2, 00, 00),
                         landing_time=datetime(2024, 12, 15, 4, 00, 00), num_of_1st_seat=rule1.value,
                         num_of_2st_seat=rule2.value, plane_id='3', route_id='3')
        flight10 = Flight(name='VN010', take_of_time=datetime(2024, 12, 13, 11, 00, 00),
                          landing_time=datetime(2024, 12, 15, 23, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='3', route_id='3')
        flight11 = Flight(name='VN011', take_of_time=datetime(2024, 12, 14, 10, 00, 00),
                          landing_time=datetime(2024, 12, 15, 12, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='1', route_id='4')
        flight12 = Flight(name='VN012', take_of_time=datetime(2024, 12, 14, 12, 00, 00),
                          landing_time=datetime(2024, 12, 16, 14, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='2', route_id='5')
        flight13 = Flight(name='VN013', take_of_time=datetime(2024, 12, 14, 14, 00, 00),
                          landing_time=datetime(2024, 12, 17, 16, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='6')
        flight14 = Flight(name='VN014', take_of_time=datetime(2024, 10, 9, 11, 00, 00),
                          landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='7')
        flight15 = Flight(name='VN015', take_of_time=datetime(2024, 10, 15, 11, 00, 00),
                          landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='3', route_id='9')
        flight16 = Flight(name='VN016', take_of_time=datetime(2024, 12, 15, 3, 00, 00),
                          landing_time=datetime(2024, 12, 16, 5, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='2', route_id='9')
        flight17 = Flight(name='VN017', take_of_time=datetime(2024, 12, 15, 5, 00, 00),
                          landing_time=datetime(2024, 12, 17, 7, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='1', route_id='10')
        flight18 = Flight(name='VN018', take_of_time=datetime(2024, 12, 15, 7, 00, 00),
                          landing_time=datetime(2024, 12, 18, 9, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='10')
        flight19 = Flight(name='VN019', take_of_time=datetime(2024, 12, 25, 3, 00, 00),
                          landing_time=datetime(2024, 12, 26, 14, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='3', route_id='11')
        flight20 = Flight(name='VN020', take_of_time=datetime(2024, 12, 25, 3, 00, 00),
                          landing_time=datetime(2024, 12, 27, 2, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='5', route_id='12')
        flight21 = Flight(name='VN020', take_of_time=datetime(2024, 12, 25, 4, 00, 00),
                          landing_time=datetime(2024, 12, 28, 5, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight22 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 10, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='1', route_id='12')
        flight23 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 9, 00, 00),
                          landing_time=datetime(2024, 12, 29, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='2', route_id='12')
        flight24 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 13, 00, 00),
                          landing_time=datetime(2024, 12, 28, 14, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight25 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='5', route_id='1')
        flight26 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 11, 00, 00),
                          landing_time=datetime(2024, 12, 28, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='1')
        flight27 = Flight(name='VN020', take_of_time=datetime(2024, 12, 26, 11, 00, 00),
                          landing_time=datetime(2024, 12, 28, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='1')
        flight28 = Flight(name='VN020', take_of_time=datetime(2024, 11, 1, 11, 00, 00),
                          landing_time=datetime(2024, 11, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight29 = Flight(name='VN020', take_of_time=datetime(2024, 11, 2, 11, 00, 00),
                          landing_time=datetime(2024, 11, 3, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight30 = Flight(name='VN020', take_of_time=datetime(2024, 11, 3, 11, 00, 00),
                          landing_time=datetime(2024, 11, 5, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight31 = Flight(name='VN020', take_of_time=datetime(2024, 11, 4, 11, 00, 00),
                          landing_time=datetime(2024, 11, 6, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        flight32 = Flight(name='VN020', take_of_time=datetime(2024, 11, 5, 11, 00, 00),
                          landing_time=datetime(2024, 11, 7, 11, 00, 00), num_of_1st_seat=rule1.value,
                          num_of_2st_seat=rule2.value, plane_id='4', route_id='12')

        db.session.add_all([flight1, flight2, flight3, flight4, flight5,
                            flight6, flight7, flight8, flight9, flight10,
                            flight11, flight12, flight13, flight14, flight15,
                            flight16, flight17, flight18, flight19, flight20,
                            flight21, flight22, flight23, flight24, flight25,
                            flight26, flight27, flight28, flight29, flight30,
                            flight31, flight32])
        db.session.commit()

        db.session.add(rule3)
        db.session.commit()

        mid_airport1 = MidAirport(stop_time=rule3.value, note='Dừng x giờ', mid_airport_id='5', flight_id='1')
        mid_airport2 = MidAirport(stop_time=rule3.value, note='Dừng x giờ', mid_airport_id='6', flight_id='2')
        db.session.add_all([mid_airport1, mid_airport2])
        db.session.commit()

        flight_schedule1 = FlightSchedule(staff_id='1', flight_id='2')
        flight_schedule2 = FlightSchedule(staff_id='1', flight_id='3')
        flight_schedule3 = FlightSchedule(staff_id='1', flight_id='4')
        flight_schedule4 = FlightSchedule(staff_id='1', flight_id='5')
        flight_schedule5 = FlightSchedule(staff_id='1', flight_id='6')
        db.session.add_all(
            [flight_schedule1, flight_schedule2, flight_schedule3, flight_schedule4, flight_schedule5])
        db.session.commit()

        db.session.add_all([rule4, rule5])
        db.session.commit()

        fareclass1 = FareClass(name='Ghế Hạng 1', price=rule4.value)
        fareclass2 = FareClass(name='Ghế Hạng 2', price=rule5.value)
        db.session.add_all([fareclass1, fareclass2])
        db.session.commit()

        # TRUE = BOOKED, FALSE = EMPTY
        # ROUTE = 1(NB_TSN), PLANE =1,2,4
        # ROUTE = 2(CT_TSN), PLANE =2,1
        # EMPY SEAT
        # FLIGHT1
        f1_seat1 = Seat(name='Seat01', status=False, flight_id='1')
        f1_seat2 = Seat(name='Seat02', status=False, flight_id='1')
        f1_seat3 = Seat(name='Seat03', status=False, flight_id='1')
        f1_seat4 = Seat(name='Seat04', status=False, flight_id='1')
        f1_seat5 = Seat(name='Seat05', status=False, flight_id='1')
        f1_seat6= Seat(name='Seat06', status=False, flight_id='1')
        f1_seat7= Seat(name='Seat07', status=False, flight_id='1')
        f1_seat8 = Seat(name='Seat08', status=False, flight_id='1')
        f1_seat9 = Seat(name='Seat09', status=False, flight_id='1')
        f1_seat10 = Seat(name='Seat10', status=False, flight_id='1')
        # f1_seat11 = Seat(name='Seat11', status=False, flight_id='1')
        # f1_seat12 = Seat(name='Seat12', status=False, flight_id='1')
        # f1_seat13 = Seat(name='Seat13', status=False, flight_id='1')
        # f1_seat14 = Seat(name='Seat14', status=False, flight_id='1')
        # f1_seat15 = Seat(name='Seat15', status=False, flight_id='1')
        # f1_seat16 = Seat(name='Seat16', status=False, flight_id='1')
        # f1_seat17 = Seat(name='Seat17', status=False, flight_id='1')
        # f1_seat18 = Seat(name='Seat18', status=False, flight_id='1')
        # f1_seat19 = Seat(name='Seat19', status=False, flight_id='1')
        # f1_seat20 = Seat(name='Seat20', status=False, flight_id='1')

        # FLIGHT2
        f2_seat1 = Seat(name='Seat01', status=False, flight_id='2')
        f2_seat2 = Seat(name='Seat02', status=False, flight_id='2')
        f2_seat3 = Seat(name='Seat03', status=False, flight_id='2')
        f2_seat4 = Seat(name='Seat04', status=False, flight_id='2')
        f2_seat5 = Seat(name='Seat05', status=False, flight_id='2')
        f2_seat6 = Seat(name='Seat06', status=False, flight_id='2')
        f2_seat7 = Seat(name='Seat07', status=False, flight_id='2')
        f2_seat8 = Seat(name='Seat08', status=False, flight_id='2')
        f2_seat9 = Seat(name='Seat09', status=False, flight_id='2')
        f2_seat10 = Seat(name='Seat10', status=False, flight_id='2')

        # FLIGHT3
        f3_seat1 = Seat(name='Seat01', status=False, flight_id='3')
        f3_seat2 = Seat(name='Seat02', status=False, flight_id='3')
        f3_seat3 = Seat(name='Seat03', status=False, flight_id='3')
        f3_seat4 = Seat(name='Seat04', status=False, flight_id='3')
        f3_seat5 = Seat(name='Seat05', status=False, flight_id='3')
        f3_seat6 = Seat(name='Seat06', status=False, flight_id='3')
        f3_seat7 = Seat(name='Seat07', status=False, flight_id='3')
        f3_seat8 = Seat(name='Seat08', status=False, flight_id='3')
        f3_seat9 = Seat(name='Seat09', status=False, flight_id='3')
        f3_seat10 = Seat(name='Seat10', status=False, flight_id='3')
        # FLIGHT4
        f4_seat1 = Seat(name='Seat01', status=False, flight_id='4')
        f4_seat2 = Seat(name='Seat02', status=False, flight_id='4')
        f4_seat3 = Seat(name='Seat03', status=False, flight_id='4')
        f4_seat4 = Seat(name='Seat04', status=False, flight_id='4')
        f4_seat5 = Seat(name='Seat05', status=False, flight_id='4')
        f4_seat6 = Seat(name='Seat06', status=False, flight_id='4')
        f4_seat7 = Seat(name='Seat07', status=False, flight_id='4')
        f4_seat8 = Seat(name='Seat08', status=False, flight_id='4')
        f4_seat9 = Seat(name='Seat09', status=False, flight_id='4')
        f4_seat10 = Seat(name='Seat10', status=False, flight_id='4')

        # FLIGHT5
        f5_seat1 = Seat(name='Seat01', status=False, flight_id='5')
        f5_seat2 = Seat(name='Seat02', status=False, flight_id='5')
        f5_seat3 = Seat(name='Seat03', status=False, flight_id='5')
        f5_seat4 = Seat(name='Seat04', status=False, flight_id='5')
        f5_seat5 = Seat(name='Seat05', status=False, flight_id='5')
        f5_seat6 = Seat(name='Seat06', status=False, flight_id='5')
        f5_seat7 = Seat(name='Seat07', status=False, flight_id='5')
        f5_seat8 = Seat(name='Seat08', status=False, flight_id='5')
        f5_seat9 = Seat(name='Seat09', status=False, flight_id='5')
        f5_seat10 = Seat(name='Seat10', status=False, flight_id='5')

        # FLIGHT6
        f6_seat1 = Seat(name='Seat01', status=False, flight_id='6')
        f6_seat2 = Seat(name='Seat02', status=False, flight_id='6')
        f6_seat3 = Seat(name='Seat03', status=False, flight_id='6')
        f6_seat4 = Seat(name='Seat04', status=False, flight_id='6')
        f6_seat5 = Seat(name='Seat05', status=False, flight_id='6')
        f6_seat6 = Seat(name='Seat06', status=False, flight_id='6')
        f6_seat7 = Seat(name='Seat07', status=False, flight_id='6')
        f6_seat8 = Seat(name='Seat08', status=False, flight_id='6')
        f6_seat9 = Seat(name='Seat09', status=False, flight_id='6')
        f6_seat10 = Seat(name='Seat10', status=False, flight_id='6')

        # FLIGHT7
        f7_seat1 = Seat(name='Seat01', status=False, flight_id='7')
        f7_seat2 = Seat(name='Seat02', status=False, flight_id='7')
        f7_seat3 = Seat(name='Seat03', status=False, flight_id='7')
        f7_seat4 = Seat(name='Seat04', status=False, flight_id='7')
        f7_seat5 = Seat(name='Seat05', status=False, flight_id='7')
        f7_seat6 = Seat(name='Seat06', status=False, flight_id='7')
        f7_seat7 = Seat(name='Seat07', status=False, flight_id='7')
        f7_seat8 = Seat(name='Seat08', status=False, flight_id='7')
        f7_seat9 = Seat(name='Seat09', status=False, flight_id='7')
        f7_seat10 = Seat(name='Seat10', status=False, flight_id='7')
        # FLIGHT20
        f20_seat1 = Seat(name='Seat01', status=False, flight_id='20')
        f20_seat2 = Seat(name='Seat02', status=False, flight_id='20')
        f20_seat3 = Seat(name='Seat03', status=False, flight_id='20')
        f20_seat4 = Seat(name='Seat04', status=False, flight_id='20')
        f20_seat5 = Seat(name='Seat05', status=False, flight_id='20')
        f20_seat6 = Seat(name='Seat06', status=False, flight_id='20')
        f20_seat7 = Seat(name='Seat07', status=False, flight_id='20')
        f20_seat8 = Seat(name='Seat08', status=False, flight_id='20')
        f20_seat9 = Seat(name='Seat09', status=False, flight_id='20')
        f20_seat10 = Seat(name='Seat10', status=False, flight_id='20')
        # FLIGHT21
        f21_seat1 = Seat(name='Seat01', status=False, flight_id='21')
        f21_seat2 = Seat(name='Seat02', status=False, flight_id='21')
        f21_seat3 = Seat(name='Seat03', status=False, flight_id='21')
        f21_seat4 = Seat(name='Seat04', status=False, flight_id='21')
        f21_seat5 = Seat(name='Seat05', status=False, flight_id='21')
        f21_seat6 = Seat(name='Seat06', status=False, flight_id='21')
        f21_seat7 = Seat(name='Seat07', status=False, flight_id='21')
        f21_seat8 = Seat(name='Seat08', status=False, flight_id='21')
        f21_seat9 = Seat(name='Seat09', status=False, flight_id='21')
        f21_seat10 = Seat(name='Seat10', status=False, flight_id='21')

        # FLIGHT24
        f24_seat1 = Seat(name='Seat01', status=False, flight_id='24')
        f24_seat2 = Seat(name='Seat02', status=False, flight_id='24')
        f24_seat3 = Seat(name='Seat03', status=False, flight_id='24')
        f24_seat4 = Seat(name='Seat04', status=False, flight_id='24')
        f24_seat5 = Seat(name='Seat05', status=False, flight_id='24')
        f24_seat6 = Seat(name='Seat06', status=False, flight_id='24')
        f24_seat7 = Seat(name='Seat07', status=False, flight_id='24')
        f24_seat8 = Seat(name='Seat08', status=False, flight_id='24')
        f24_seat9 = Seat(name='Seat09', status=False, flight_id='24')
        f24_seat10 = Seat(name='Seat10', status=False, flight_id='24')
        # FLIGHT25
        f25_seat1 = Seat(name='Seat01', status=False, flight_id='25')
        f25_seat2 = Seat(name='Seat02', status=False, flight_id='25')
        f25_seat3 = Seat(name='Seat03', status=False, flight_id='25')
        f25_seat4 = Seat(name='Seat04', status=False, flight_id='25')
        f25_seat5 = Seat(name='Seat05', status=False, flight_id='25')
        f25_seat6 = Seat(name='Seat06', status=False, flight_id='25')
        f25_seat7 = Seat(name='Seat07', status=False, flight_id='25')
        f25_seat8 = Seat(name='Seat08', status=False, flight_id='25')
        f25_seat9 = Seat(name='Seat09', status=False, flight_id='25')
        f25_seat10 = Seat(name='Seat10', status=False, flight_id='25')
        # FLIGHT26
        f26_seat1 = Seat(name='Seat01', status=False, flight_id='26')
        f26_seat2 = Seat(name='Seat02', status=False, flight_id='26')
        f26_seat3 = Seat(name='Seat03', status=False, flight_id='26')
        f26_seat4 = Seat(name='Seat04', status=False, flight_id='26')
        f26_seat5 = Seat(name='Seat05', status=False, flight_id='26')
        f26_seat6 = Seat(name='Seat06', status=False, flight_id='26')
        f26_seat7 = Seat(name='Seat07', status=False, flight_id='26')
        f26_seat8 = Seat(name='Seat08', status=False, flight_id='26')
        f26_seat9 = Seat(name='Seat09', status=False, flight_id='26')
        f26_seat10 = Seat(name='Seat10', status=False, flight_id='26')
        # FLIGHT29
        f29_seat1 = Seat(name='Seat01', status=False, flight_id='29')
        f29_seat2 = Seat(name='Seat02', status=False, flight_id='29')
        f29_seat3 = Seat(name='Seat03', status=False, flight_id='29')
        f29_seat4 = Seat(name='Seat04', status=False, flight_id='29')
        f29_seat5 = Seat(name='Seat05', status=False, flight_id='29')
        f29_seat6 = Seat(name='Seat06', status=False, flight_id='29')
        f29_seat7 = Seat(name='Seat07', status=False, flight_id='29')
        f29_seat8 = Seat(name='Seat08', status=False, flight_id='29')
        f29_seat9 = Seat(name='Seat09', status=False, flight_id='29')
        f29_seat10 = Seat(name='Seat10', status=False, flight_id='29')

        db.session.add_all([f1_seat1,f1_seat2,f1_seat3, f1_seat4, f1_seat5,
                            f1_seat6, f1_seat7, f1_seat8, f1_seat9, f1_seat10,

                            f2_seat1, f2_seat2, f2_seat3, f2_seat4, f2_seat5,
                            f2_seat6, f2_seat7, f2_seat8, f2_seat9, f2_seat10,

                            f3_seat1, f3_seat2, f3_seat3, f3_seat4, f3_seat5,
                            f3_seat6, f3_seat7, f3_seat8, f3_seat9, f3_seat10,

                            f4_seat1, f4_seat2, f4_seat3, f4_seat4, f4_seat5,
                            f4_seat6, f4_seat7, f4_seat8, f4_seat9, f4_seat10,

                            f5_seat1, f5_seat2, f5_seat3, f5_seat4, f5_seat5,
                            f5_seat6, f5_seat7, f5_seat8, f5_seat9, f5_seat10,

                            f6_seat1, f6_seat2, f6_seat3, f6_seat4, f6_seat5,
                            f6_seat6, f6_seat7, f6_seat8, f6_seat9, f6_seat10,

                            f7_seat1, f7_seat2, f7_seat3, f7_seat4, f7_seat5,
                            f7_seat6, f7_seat7, f7_seat8, f7_seat9, f7_seat10,

                            f20_seat1, f20_seat2, f20_seat3, f20_seat4, f20_seat5,
                            f20_seat6, f20_seat7, f20_seat8, f20_seat9, f20_seat10,

                            f21_seat1, f21_seat2, f21_seat3, f21_seat4, f21_seat5,
                            f21_seat6, f21_seat7, f21_seat8, f21_seat9, f21_seat10,

                            f24_seat1, f24_seat2, f24_seat3, f24_seat4, f24_seat5,
                            f24_seat6, f24_seat7, f24_seat8, f24_seat9, f24_seat10,

                            f25_seat1, f25_seat2, f25_seat3, f25_seat4, f25_seat5,
                            f25_seat6, f25_seat7, f25_seat8, f25_seat9, f25_seat10,

                            f26_seat1, f26_seat2, f26_seat3, f26_seat4, f26_seat5,
                            f26_seat6, f26_seat7, f26_seat8, f26_seat9, f26_seat10,

                            f29_seat1, f29_seat2, f29_seat3, f29_seat4, f29_seat5,
                            f29_seat6, f29_seat7, f29_seat8, f29_seat9, f29_seat10,
                            ])
        db.session.commit()
        # ticket1 = Ticket(customer_id='1',flight_id='1',fareclass_id='1',seat_id='1')
        # ticket2 = Ticket(customer_id='2',flight_id='2',fareclass_id='2',seat_id='2')
        # ticket3 = Ticket(customer_id='2',flight_id='3',fareclass_id='1',seat_id='3')
        # ticket4 = Ticket(customer_id='1',flight_id='4',fareclass_id='2',seat_id='4')
        # ticket5 = Ticket(customer_id='1',flight_id='5',fareclass_id='2',seat_id='5')
        # ticket6 = Ticket(customer_id='2',flight_id='1',fareclass_id='2',seat_id='6')
        # ticket7 = Ticket(customer_id='2',flight_id='2',fareclass_id='1',seat_id='7')
        # ticket8 = Ticket(customer_id='1',flight_id='3',fareclass_id='1',seat_id='8')
        # ticket9 = Ticket(customer_id='1',flight_id='4',fareclass_id='2',seat_id='9')
        # ticket10 = Ticket(customer_id='2',flight_id='5',fareclass_id='2',seat_id='10')
        # ticket11 = Ticket(customer_id='2',flight_id='1',fareclass_id='1',seat_id='11')
        # ticket12 = Ticket(customer_id='2',flight_id='2',fareclass_id='2',seat_id='12')
        # ticket13 = Ticket(customer_id='1',flight_id='3',fareclass_id='1',seat_id='13')
        # ticket14 = Ticket(customer_id='2',flight_id='4',fareclass_id='2',seat_id='14')
        # ticket15 = Ticket(customer_id='1',flight_id='5',fareclass_id='1',seat_id='15')
        # ticket16 = Ticket(customer_id='1',flight_id='5',fareclass_id='1',seat_id='16')
        # ticket17 = Ticket(customer_id='2',flight_id='5',fareclass_id='2',seat_id='17')
        # ticket18 = Ticket(customer_id='1',flight_id='5',fareclass_id='1',seat_id='18')
        # ticket19 = Ticket(customer_id='1',flight_id='5',fareclass_id='2',seat_id='19')
        # ticket20 = Ticket(customer_id='1',flight_id='5',fareclass_id='2',seat_id='20')
        # ticket21 = Ticket(customer_id='2',flight_id='5',fareclass_id='1',seat_id='21')
        # ticket22 = Ticket(customer_id='1',flight_id='5',fareclass_id='2',seat_id='22')
        # ticket23 = Ticket(customer_id='2',flight_id='5',fareclass_id='1',seat_id='23')
        # ticket24 = Ticket(customer_id='1',flight_id='5',fareclass_id='2',seat_id='24')
        # ticket25 = Ticket(customer_id='2',flight_id='5',fareclass_id='1',seat_id='25')
        # ticket26 = Ticket(customer_id='2',flight_id='5',fareclass_id='1',seat_id='26')
        #
        # db.session.add_all([ticket1,ticket2,ticket3,ticket4,ticket5,
        #                     ticket6,ticket7,ticket8,ticket9,ticket10,
        #                     ticket11,ticket12,ticket13,ticket14,ticket15,
        #                     ticket16,ticket17,ticket18,ticket19,ticket20,
        #                     ticket21,ticket22,ticket23,ticket24,ticket25,ticket26])
        #
        # db.session.commit()
