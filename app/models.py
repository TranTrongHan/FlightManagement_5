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
    name = Column(String(100), nullable=False, unique=True)
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
    seats_quantity = Column(Integer,nullable=False)
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

        rule1 = Rule(name='Số lượng ghế ngồi',value ='5')
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

        airport1 = Airport(name='Sân bay Nội Bài (HAN)')
        airport2 = Airport(name='Sân bay Tân Sơn Nhất (SGN)')
        airport3 = Airport(name='Sân bay Cam Ranh (CXR)')
        airport4 = Airport(name='Sân bay Đà Nẵng (DAD)')
        airport5 = Airport(name='Sân bay Phù Cát (UIH)')
        airport6 = Airport(name='Sân bay Quốc tế Phú Quốc (PQH)')
        airport7 = Airport(name='Sân bay Liên Khương (DLI)')
        airport8 = Airport(name='Sân bay Cát Bi (HPH)')
        airport9 = Airport(name='Sân bay Điện Biên Phủ (DIN)')
        airport10 = Airport(name='Sân bay Côn Đảo (VCS) ')
        airport11 = Airport(name='Sân bay Tuy Hòa (UIH)')
        airport12 = Airport(name='Sân bay Rạch Giá (VKG) ')


        db.session.add_all(
            [airport1, airport2, airport3, airport4, airport5, airport6, airport7, airport8, airport9, airport10,
             airport11, airport12])
        db.session.commit()

        route1 = Route(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_off_airport_id="1", landing_airport_id="2")
        route2 = Route(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_off_airport_id="1", landing_airport_id="4")
        route3 = Route(name='Đà Nẵng(DAD) - TP HCM(SG)', take_off_airport_id="4", landing_airport_id="2")
        route4 = Route(name='Hà Nội(HAN) - Nha Trang(CXR)', take_off_airport_id="1", landing_airport_id="4")
        route5 = Route(name='TP HCM(SG)- Nha Trang(CXR)', take_off_airport_id="2", landing_airport_id="3")
        route6 = Route(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_off_airport_id="1", landing_airport_id="6")
        route7 = Route(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_off_airport_id="2", landing_airport_id="6")
        route8 = Route(name='Hà Nội(HAN) - Quy Nhơn(UIH)', take_off_airport_id="1", landing_airport_id="5")
        route9 = Route(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_off_airport_id="2", landing_airport_id="7")
        route10 = Route(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_off_airport_id="1", landing_airport_id="8")
        route11 = Route(name='Hà Nội(HAN) - Điện Biên Phủ(DIN)', take_off_airport_id="1", landing_airport_id="9")
        route12 = Route(name='Hồ Chí Minh(SGN) - Côn Đảo(VCS)', take_off_airport_id="2", landing_airport_id="10")
        route13 = Route(name='Hà Nội(HAN) - Phú Yên(UIH)', take_off_airport_id="1", landing_airport_id="11")
        # route14 = Route(name='Hồ Chí Minh(SGN) -  Phú Yên(UIH)', take_off_airport_id="2", landing_airport_id="11")
        # route15 = Route(name='Hà Nội (HAN) - Rạch Giá (VKG)', take_off_airport_id="1", landing_airport_id="12")
        db.session.add_all([route1, route2, route3, route4, route5,
                            route6, route7, route8, route9, route10,
                            route11, route12, route13])
        db.session.commit()

        db.session.add_all([rule1])
        db.session.commit()
        #         ==============================Tuyến Hà Nội(HAN) - Hồ Chí Minh(SGN) ======================================
        flight1 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                            seats_quantity = rule1.value, plane_id='1', route_id='1')
        flight2 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                         landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                         seats_quantity=rule1.value, plane_id='2', route_id='1')
        flight3 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_of_time=datetime(2024, 12, 29, 23, 00, 00),
                         landing_time=datetime(2024, 12, 1, 12, 00, 00),
                         seats_quantity=rule1.value, plane_id='3', route_id='1')
        flight4 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_of_time=datetime(2024, 12, 28, 5, 00, 00),
                         landing_time=datetime(2024, 12, 30, 10, 00, 00), 
                         seats_quantity=rule1.value, plane_id='4', route_id='1')
        #         ==============================Tuyến Hà Nội(HAN) - Đà Nẵng(DAD) ======================================
        flight5 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                         seats_quantity=rule1.value, plane_id='1', route_id='2')
        flight6 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                         landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                         seats_quantity=rule1.value, plane_id='2', route_id='2')
        flight7 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_of_time=datetime(2024, 12, 29, 23, 00, 00),
                         landing_time=datetime(2024, 12, 1, 12, 00, 00), 
                         seats_quantity=rule1.value, plane_id='3', route_id='1')
        flight8 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_of_time=datetime(2024, 12, 28, 5, 00, 00),
                         landing_time=datetime(2024, 12, 30, 10, 00, 00), 
                         seats_quantity=rule1.value, plane_id='4', route_id='2')

        #         ==============================Tuyến Hà Nội(HAN) - Nha Trang(CXR) ======================================
        flight9 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                         seats_quantity=rule1.value, plane_id='1', route_id='4')
        flight10 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                         landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                         seats_quantity=rule1.value, plane_id='2', route_id='4')
        flight11 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_of_time=datetime(2024, 12, 29, 23, 00, 00),
                         landing_time=datetime(2024, 12, 1, 12, 00, 00), 
                         seats_quantity=rule1.value, plane_id='3', route_id='4')
        flight12 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_of_time=datetime(2024, 12, 28, 5, 00, 00),
                         landing_time=datetime(2024, 12, 30, 10, 00, 00), 
                         seats_quantity=rule1.value, plane_id='4', route_id='4')

        #         ==============================Tuyến Đà Nẵng(DAD) - TP HCM(SG) ======================================
        flight13 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                         seats_quantity=rule1.value, plane_id='1', route_id='3')
        flight14 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                         landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                         seats_quantity=rule1.value, plane_id='2', route_id='3')
        flight15 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_of_time=datetime(2024, 12, 29, 23, 00, 00),
                         landing_time=datetime(2024, 12, 1, 12, 00, 00), 
                         seats_quantity=rule1.value, plane_id='3', route_id='3')
        flight16 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_of_time=datetime(2024, 12, 28, 5, 00, 00),
                         landing_time=datetime(2024, 12, 30, 10, 00, 00), 
                         seats_quantity=rule1.value, plane_id='4', route_id='3')

        #         ==============================Tuyến TP HCM(SG)- Nha Trang(CXR) ======================================
        flight17 = Flight(name='TP HCM(SG)- Nha Trang(CXR)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                         seats_quantity=rule1.value, plane_id='1', route_id='5')
        flight18 = Flight(name='TP HCM(SG)- Nha Trang(CXR)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                         landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                         seats_quantity=rule1.value, plane_id='2', route_id='5')

        #         ==============================Tuyến Hà Nội(HAN) - Phú Quốc(PQH) ======================================
        flight19 = Flight(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='6')
        flight20 = Flight(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                          landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                          seats_quantity=rule1.value, plane_id='2', route_id='6')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Phú Quốc(PQH) ======================================
        flight21 = Flight(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='7')
        flight22 = Flight(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                          landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                          seats_quantity=rule1.value, plane_id='2', route_id='7')

        #         ==============================Tuyến Hà Nội(HAN) - Quy Nhơn(UIH) ======================================
        flight23 = Flight(name='Hà Nội(HAN) - Quy Nhơn(UIH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='8')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Đà Lạt(DLI) ======================================
        flight24 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='9')
        flight25 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                          landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                          seats_quantity=rule1.value, plane_id='2', route_id='9')

        #         ==============================Tuyến Hà Nội(HAN) - Hải Phòng(HPH) ======================================
        flight26 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='10')
        flight27 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_of_time=datetime(2024, 12, 26, 12, 00, 00),
                          landing_time=datetime(2024, 12, 18, 11, 00, 00), 
                          seats_quantity=rule1.value, plane_id='2', route_id='10')

        #         ==============================Tuyến Hà Nội(HAN) - Điện Biên Phủ(DIN) ======================================
        flight28 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='11')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Côn Đảo(VCS) ======================================
        flight29 = Flight(name='Hồ Chí Minh(SGN) - Côn Đảo(VCS)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='12')

        #         ==============================Tuyến Hà Nội(HAN) - Phú Yên(UIH) ======================================
        flight30 = Flight(name='Hà Nội(HAN) - Phú Yên(UIH)', take_of_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='13')


        #         ==============================Các chuyến bay đã qua lịch hiện tại ======================================
        flight31 = Flight(name='Hà Nội(HAN) - Phú Yên(UIH)', take_of_time=datetime(2024, 12, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='13')
        flight32 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_of_time=datetime(2024, 11, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='9')
        flight33 = Flight(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 10, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='7')
        flight34 = Flight(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_of_time=datetime(2024, 8, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='6')
        flight35 = Flight(name='TP HCM(SG)- Nha Trang(CXR)', take_of_time=datetime(2024, 9, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='5')
        flight36 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_of_time=datetime(2024, 10, 15, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00), 
                          seats_quantity=rule1.value, plane_id='1', route_id='1')

        db.session.add_all([flight1, flight2, flight3, flight4, flight5,
                            flight6, flight7, flight8, flight9, flight10,
                            flight11, flight12, flight13, flight14, flight15,
                            flight16, flight17, flight18, flight19, flight20,
                            flight21, flight22, flight23, flight24, flight25,
                            flight26, flight27, flight28, flight29, flight30,
                            flight31, flight32, flight33, flight34, flight35,flight36])
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
        # EMPY SEAT
        seat1 = Seat(name='Seat01', status=False, flight_id='1')
        seat2 = Seat(name='Seat02', status=False, flight_id='1')
        seat3 = Seat(name='Seat03', status=False, flight_id='1')
        seat4 = Seat(name='Seat04', status=False, flight_id='1')
        seat5 = Seat(name='Seat05', status=False, flight_id='1')

        seat6 = Seat(name='Seat01', status=False, flight_id='2')
        seat7 = Seat(name='Seat02', status=False, flight_id='2')
        seat8 = Seat(name='Seat03', status=False, flight_id='2')
        seat9 = Seat(name='Seat04', status=False, flight_id='2')
        seat10 = Seat(name='Seat05', status=False, flight_id='2')

        seat11 = Seat(name='Seat01', status=False, flight_id='3')
        seat12 = Seat(name='Seat02', status=False, flight_id='3')
        seat13 = Seat(name='Seat03', status=False, flight_id='3')
        seat14 = Seat(name='Seat04', status=False, flight_id='3')
        seat15 = Seat(name='Seat05', status=False, flight_id='3')

        seat16 = Seat(name='Seat01', status=False, flight_id='4')
        seat17 = Seat(name='Seat02', status=False, flight_id='4')
        seat18 = Seat(name='Seat03', status=False, flight_id='4')
        seat19 = Seat(name='Seat04', status=False, flight_id='4')
        seat20 = Seat(name='Seat05', status=False, flight_id='4')

        seat21 = Seat(name='Seat01', status=False, flight_id='5')
        seat22 = Seat(name='Seat02', status=False, flight_id='5')
        seat23 = Seat(name='Seat03', status=False, flight_id='5')
        seat24 = Seat(name='Seat04', status=False, flight_id='5')
        seat25 = Seat(name='Seat05', status=False, flight_id='5')

        seat26 = Seat(name='Seat01', status=False, flight_id='6')
        seat27 = Seat(name='Seat02', status=False, flight_id='6')
        seat28 = Seat(name='Seat03', status=False, flight_id='6')
        seat29 = Seat(name='Seat04', status=False, flight_id='6')
        seat30 = Seat(name='Seat05', status=False, flight_id='6')

        seat31 = Seat(name='Seat01', status=False, flight_id='7')
        seat32 = Seat(name='Seat02', status=False, flight_id='7')
        seat33 = Seat(name='Seat03', status=False, flight_id='7')
        seat34 = Seat(name='Seat04', status=False, flight_id='7')
        seat35 = Seat(name='Seat05', status=False, flight_id='7')

        seat36 = Seat(name='Seat01', status=False, flight_id='8')
        seat37 = Seat(name='Seat02', status=False, flight_id='8')
        seat38 = Seat(name='Seat03', status=False, flight_id='8')
        seat39 = Seat(name='Seat04', status=False, flight_id='8')
        seat40 = Seat(name='Seat05', status=False, flight_id='8')

        seat41 = Seat(name='Seat01', status=False, flight_id='9')
        seat42 = Seat(name='Seat02', status=False, flight_id='9')
        seat43 = Seat(name='Seat03', status=False, flight_id='9')
        seat44 = Seat(name='Seat04', status=False, flight_id='9')
        seat45 = Seat(name='Seat05', status=False, flight_id='9')

        seat46 = Seat(name='Seat01', status=False, flight_id='10')
        seat47 = Seat(name='Seat02', status=False, flight_id='10')
        seat48 = Seat(name='Seat03', status=False, flight_id='10')
        seat49 = Seat(name='Seat04', status=False, flight_id='10')
        seat50 = Seat(name='Seat05', status=False, flight_id='10')

        seat51 = Seat(name='Seat01', status=False, flight_id='11')
        seat52 = Seat(name='Seat02', status=False, flight_id='11')
        seat53 = Seat(name='Seat03', status=False, flight_id='11')
        seat54 = Seat(name='Seat04', status=False, flight_id='11')
        seat55 = Seat(name='Seat05', status=False, flight_id='11')

        seat56 = Seat(name='Seat01', status=False, flight_id='12')
        seat57 = Seat(name='Seat02', status=False, flight_id='12')
        seat58 = Seat(name='Seat03', status=False, flight_id='12')
        seat59 = Seat(name='Seat04', status=False, flight_id='12')
        seat60 = Seat(name='Seat05', status=False, flight_id='12')

        seat61 = Seat(name='Seat01', status=False, flight_id='13')
        seat62 = Seat(name='Seat02', status=False, flight_id='13')
        seat63 = Seat(name='Seat03', status=False, flight_id='13')
        seat64 = Seat(name='Seat04', status=False, flight_id='13')
        seat65 = Seat(name='Seat05', status=False, flight_id='13')

        seat66 = Seat(name='Seat01', status=False, flight_id='14')
        seat67 = Seat(name='Seat02', status=False, flight_id='14')
        seat68 = Seat(name='Seat03', status=False, flight_id='14')
        seat69 = Seat(name='Seat04', status=False, flight_id='14')
        seat70 = Seat(name='Seat05', status=False, flight_id='14')

        seat71 = Seat(name='Seat01', status=False, flight_id='15')
        seat72 = Seat(name='Seat02', status=False, flight_id='15')
        seat73 = Seat(name='Seat03', status=False, flight_id='15')
        seat74 = Seat(name='Seat04', status=False, flight_id='15')
        seat75 = Seat(name='Seat05', status=False, flight_id='15')

        seat76 = Seat(name='Seat01', status=False, flight_id='16')
        seat77 = Seat(name='Seat02', status=False, flight_id='16')
        seat78 = Seat(name='Seat03', status=False, flight_id='16')
        seat79 = Seat(name='Seat04', status=False, flight_id='16')
        seat80 = Seat(name='Seat05', status=False, flight_id='16')

        seat81 = Seat(name='Seat01', status=False, flight_id='17')
        seat82 = Seat(name='Seat02', status=False, flight_id='17')
        seat83 = Seat(name='Seat03', status=False, flight_id='17')
        seat84 = Seat(name='Seat04', status=False, flight_id='17')
        seat85 = Seat(name='Seat05', status=False, flight_id='17')

        seat86 = Seat(name='Seat01', status=False, flight_id='18')
        seat87 = Seat(name='Seat02', status=False, flight_id='18')
        seat88 = Seat(name='Seat03', status=False, flight_id='18')
        seat89 = Seat(name='Seat04', status=False, flight_id='18')
        seat90 = Seat(name='Seat05', status=False, flight_id='18')

        seat91 = Seat(name='Seat01', status=False, flight_id='19')
        seat92 = Seat(name='Seat02', status=False, flight_id='19')
        seat93 = Seat(name='Seat03', status=False, flight_id='19')
        seat94 = Seat(name='Seat04', status=False, flight_id='19')
        seat95 = Seat(name='Seat05', status=False, flight_id='19')

        seat96 = Seat(name='Seat01', status=False, flight_id='20')
        seat97 = Seat(name='Seat02', status=False, flight_id='20')
        seat98 = Seat(name='Seat03', status=False, flight_id='20')
        seat99 = Seat(name='Seat04', status=False, flight_id='20')
        seat100 = Seat(name='Seat05', status=False, flight_id='20')

        seat101 = Seat(name='Seat01', status=False, flight_id='21')
        seat102 = Seat(name='Seat02', status=False, flight_id='21')
        seat103 = Seat(name='Seat03', status=False, flight_id='21')
        seat104 = Seat(name='Seat04', status=False, flight_id='21')
        seat105 = Seat(name='Seat05', status=False, flight_id='21')

        seat106 = Seat(name='Seat01', status=False, flight_id='22')
        seat107 = Seat(name='Seat02', status=False, flight_id='22')
        seat108 = Seat(name='Seat03', status=False, flight_id='22')
        seat109 = Seat(name='Seat04', status=False, flight_id='22')
        seat110 = Seat(name='Seat05', status=False, flight_id='22')

        seat111 = Seat(name='Seat01', status=False, flight_id='23')
        seat112 = Seat(name='Seat02', status=False, flight_id='23')
        seat113 = Seat(name='Seat03', status=False, flight_id='23')
        seat114 = Seat(name='Seat04', status=False, flight_id='23')
        seat115 = Seat(name='Seat05', status=False, flight_id='23')

        seat116 = Seat(name='Seat01', status=False, flight_id='24')
        seat117 = Seat(name='Seat02', status=False, flight_id='24')
        seat118 = Seat(name='Seat03', status=False, flight_id='24')
        seat119 = Seat(name='Seat04', status=False, flight_id='24')
        seat120 = Seat(name='Seat05', status=False, flight_id='24')

        seat121 = Seat(name='Seat01', status=False, flight_id='25')
        seat122 = Seat(name='Seat02', status=False, flight_id='25')
        seat123 = Seat(name='Seat03', status=False, flight_id='25')
        seat124 = Seat(name='Seat04', status=False, flight_id='25')
        seat125 = Seat(name='Seat05', status=False, flight_id='25')

        seat126 = Seat(name='Seat01', status=False, flight_id='26')
        seat127 = Seat(name='Seat02', status=False, flight_id='26')
        seat128 = Seat(name='Seat03', status=False, flight_id='26')
        seat129 = Seat(name='Seat04', status=False, flight_id='26')
        seat130 = Seat(name='Seat05', status=False, flight_id='26')

        seat131 = Seat(name='Seat01', status=False, flight_id='27')
        seat132 = Seat(name='Seat02', status=False, flight_id='27')
        seat133 = Seat(name='Seat03', status=False, flight_id='27')
        seat134 = Seat(name='Seat04', status=False, flight_id='27')
        seat135 = Seat(name='Seat05', status=False, flight_id='27')

        seat136 = Seat(name='Seat01', status=False, flight_id='28')
        seat137 = Seat(name='Seat02', status=False, flight_id='28')
        seat138 = Seat(name='Seat03', status=False, flight_id='28')
        seat139 = Seat(name='Seat04', status=False, flight_id='28')
        seat140 = Seat(name='Seat05', status=False, flight_id='28')

        seat141 = Seat(name='Seat01', status=False, flight_id='29')
        seat142 = Seat(name='Seat02', status=False, flight_id='29')
        seat143 = Seat(name='Seat03', status=False, flight_id='29')
        seat144 = Seat(name='Seat04', status=False, flight_id='29')
        seat145 = Seat(name='Seat05', status=False, flight_id='29')

        seat146 = Seat(name='Seat01', status=False, flight_id='30')
        seat147 = Seat(name='Seat02', status=False, flight_id='30')
        seat148 = Seat(name='Seat03', status=False, flight_id='30')
        seat149 = Seat(name='Seat04', status=False, flight_id='30')
        seat150 = Seat(name='Seat05', status=False, flight_id='30')

        seat151 = Seat(name='Seat01', status=False, flight_id='31')
        seat152 = Seat(name='Seat02', status=False, flight_id='31')
        seat153 = Seat(name='Seat03', status=False, flight_id='31')
        seat154 = Seat(name='Seat04', status=False, flight_id='31')
        seat155 = Seat(name='Seat05', status=False, flight_id='31')

        seat156 = Seat(name='Seat01', status=False, flight_id='32')
        seat157 = Seat(name='Seat02', status=False, flight_id='32')
        seat158 = Seat(name='Seat03', status=False, flight_id='32')
        seat159 = Seat(name='Seat04', status=False, flight_id='32')
        seat160 = Seat(name='Seat05', status=False, flight_id='32')

        seat161 = Seat(name='Seat01', status=False, flight_id='33')
        seat162 = Seat(name='Seat02', status=False, flight_id='33')
        seat163 = Seat(name='Seat03', status=False, flight_id='33')
        seat164 = Seat(name='Seat04', status=False, flight_id='33')
        seat165 = Seat(name='Seat05', status=False, flight_id='33')

        seat166 = Seat(name='Seat01', status=False, flight_id='34')
        seat167 = Seat(name='Seat02', status=False, flight_id='34')
        seat168 = Seat(name='Seat03', status=False, flight_id='34')
        seat169 = Seat(name='Seat04', status=False, flight_id='34')
        seat170 = Seat(name='Seat05', status=False, flight_id='34')

        seat171 = Seat(name='Seat01', status=False, flight_id='35')
        seat172 = Seat(name='Seat02', status=False, flight_id='35')
        seat173 = Seat(name='Seat03', status=False, flight_id='35')
        seat174 = Seat(name='Seat04', status=False, flight_id='35')
        seat175 = Seat(name='Seat05', status=False, flight_id='35')

        seat176 = Seat(name='Seat01', status=False, flight_id='36')
        seat177 = Seat(name='Seat02', status=False, flight_id='36')
        seat178 = Seat(name='Seat03', status=False, flight_id='36')
        seat179 = Seat(name='Seat04', status=False, flight_id='36')
        seat180 = Seat(name='Seat05', status=False, flight_id='36')

        # Thêm tất cả các ghế vào session
        db.session.add_all([
            seat1, seat2, seat3, seat4, seat5,
            seat6, seat7, seat8, seat9, seat10,
            seat11, seat12, seat13, seat14, seat15,
            seat16, seat17, seat18, seat19, seat20,
            seat21, seat22, seat23, seat24, seat25,
            seat26, seat27, seat28, seat29, seat30,
            seat31, seat32, seat33, seat34, seat35,
            seat36, seat37, seat38, seat39, seat40,
            seat41, seat42, seat43, seat44, seat45,
            seat46, seat47, seat48, seat49, seat50,
            seat51, seat52, seat53, seat54, seat55,
            seat56, seat57, seat58, seat59, seat60,
            seat61, seat62, seat63, seat64, seat65,
            seat66, seat67, seat68, seat69, seat70,
            seat71, seat72, seat73, seat74, seat75,
            seat76, seat77, seat78, seat79, seat80,
            seat81, seat82, seat83, seat84, seat85,
            seat86, seat87, seat88, seat89, seat90,
            seat91, seat92, seat93, seat94, seat95,
            seat96, seat97, seat98, seat99, seat100,
            seat101, seat102, seat103, seat104, seat105,
            seat106, seat107, seat108, seat109, seat110,
            seat111, seat112, seat113, seat114, seat115,
            seat116, seat117, seat118, seat119, seat120,
            seat121, seat122, seat123, seat124, seat125,
            seat126, seat127, seat128, seat129, seat130,
            seat131, seat132, seat133, seat134, seat135,
            seat136, seat137, seat138, seat139, seat140,
            seat141, seat142, seat143, seat144, seat145,
            seat146, seat147, seat148, seat149, seat150,
            seat151, seat152, seat153, seat154, seat155,
            seat156, seat157, seat158, seat159, seat160,
            seat161, seat162, seat163, seat164, seat165,
            seat166, seat167, seat168, seat169, seat170,
            seat171, seat172, seat173, seat174, seat175,
            seat176, seat177, seat178, seat179, seat180
        ])
        db.session.commit()
        #
        # db.session.add_all([ticket1,ticket2,ticket3,ticket4,ticket5,
        #                     ticket6,ticket7,ticket8,ticket9,ticket10,
        #                     ticket11,ticket12,ticket13,ticket14,ticket15,
        #                     ticket16,ticket17,ticket18,ticket19,ticket20,
        #                     ticket21,ticket22,ticket23,ticket24,ticket25,ticket26])
        #
        # db.session.commit()
