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
    name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(UserRoleEnum), nullable=False)
    joined_date = Column(DateTime, default=datetime.now())
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    comments = relationship("Comment",backref='author',lazy=True)
    def __str__(self):
        return self.name

#####################################
class Customer(User):
    Cus_id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String(12),nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    ticket = relationship("Ticket", backref="customer", lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            user_id=data['user_id'],
        )

#####################################
class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flights = relationship("Flight", backref="plane", lazy=True)
    def __str__(self):
        return self.name

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

#####################################
class Airport(db.Model):
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(100), nullable=True)
    takeoff_airport = relationship("Route",foreign_keys='Route.take_off_airport_id', backref="takeoff_airport",lazy=True)
    landing_airport = relationship("Route",foreign_keys='Route.landing_airport_id', backref="landing_airport",lazy=True)

    def __str__(self):
        return self.name

#####################################
class Route(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    flights = relationship("Flight", backref="route", lazy=True)
    take_off_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=True)
    landing_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=True)

    def __str__(self):
        return self.name
    def __init__(self, name,take_off_airport_id,landing_airport_id):
        self.name = name
        self.take_off_airport_id =take_off_airport_id,
        self.landing_airport_id = landing_airport_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'take_off_airport_id':self.take_off_airport_id,
            'landing_airport_id':self.landing_airport_id
        }
#####################################
class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    take_off_time = Column(DateTime, nullable=False)
    landing_time = Column(DateTime, nullable=False)
    first_seat_quantity = Column(Integer,nullable=True)
    second_seat_quantity = Column(Integer,nullable=True)
    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=True)
    route_id = Column(Integer, ForeignKey(Route.id), nullable=True)
    mid_airport = relationship("MidAirport",backref="flight",lazy=True)
    ticket = relationship("Ticket", backref="flight", lazy=True)
    def __str__(self):
        return self.name

    def __init__(self, name, take_off_time, landing_time, first_seat_quantity, second_seat_quantity, plane_id,
                 route_id):
        self.name = name
        self.take_off_time = take_off_time
        self.landing_time = landing_time
        self.first_seat_quantity = first_seat_quantity
        self.second_seat_quantity = second_seat_quantity
        self.plane_id = plane_id
        self.route_id = route_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'take_off_time': self.take_off_time,
            'landing_time':self.landing_time,
            'first_seat_quantity':self.first_seat_quantity,
            'second_seat_quantity':self.second_seat_quantity,
            'plane_id':self.plane_id,
            'route_id': self.route_id
        }

class MidAirport(Airport):
    mid_airport_id = Column(Integer,primary_key=True,autoincrement=True)
    airport_id = Column(Integer,ForeignKey(Airport.id),nullable=True)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable=False)
    stop_time = Column(Float,nullable=True)
    note = Column(String(200),nullable=True)


class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    value = Column(Float, nullable=False)

#####################################
class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, unique=True)

#####################################
class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    seats = relationship("Seat", backref="fareclass", lazy=True)

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
    fareclass_id = Column(Integer, ForeignKey(FareClass.id), nullable=False)
    ticket_id = relationship("Ticket", backref='seat', uselist=False)
    def __str__(self):
        return self.name

#####################################
class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False, primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False, primary_key=True)
    seat_id = Column(Integer, ForeignKey(Seat.id), nullable=True, unique=True)
    created_date = Column(DateTime,nullable=False)
#####################################
class Comment(db.Model):
    _tablename_ = 'Comment'
    comment_id = Column(Integer, primary_key=True,autoincrement=True)
    user = Column(Integer, ForeignKey(User.id), nullable=True)
    text = Column(String(255), nullable=False)
    time = Column(DateTime, default=datetime.now)

    def __init__(self, user, text, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.text = text
if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()


        rule1 = Rule(name='Số lượng ghế hạng 1',value ='5')
        rule2 = Rule(name='Số lượng ghế hạng 2', value='5')
        rule3 = Rule(name='Minimum_downtime', value='20')
        rule4 = Rule(name='1st_seat_price', value=1500000)
        rule5 = Rule(name='2st_seat_price', value=1000000)
        rule6 = Rule(name='khoảng thời gian cho phép đặt vé',value='12')
        rule7 = Rule(name='Maximum_downtime', value='30')
        rule8 = Rule(name='Minimum_flight_time', value='0.5')
        rule9 = Rule(name='Max_transit_airports', value='2')
        db.session.add_all([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
        db.session.commit()
        user1 = User(name='Nguyễn An', phone='0123456789', address='123 Street A', email='an.nguyen@example.com',
                     user_role=UserRoleEnum.ADMIN, username='admin1',
                     password=str(hashlib.md5('admin1'.encode('utf-8')).hexdigest()))
        user2 = User(name='Trần Lê Bình', phone='0123456790', address='456 Street B', email='binh.tran@example.com',
                     user_role=UserRoleEnum.ADMIN, username='admin2',
                     password=str(hashlib.md5('admin2'.encode('utf-8')).hexdigest()))
        user3 = User(name='Lê Kim Cúc', phone='0123456791', address='789 Street C', email='cuc.le@example.com',
                     user_role=UserRoleEnum.STAFF, username='staff1',
                     password=str(hashlib.md5('staff1'.encode('utf-8')).hexdigest()))
        user4 = User(name='Phạm Hải Dương', phone='0123456792', address='101 Street D', email='duong.pham@example.com',
                     user_role=UserRoleEnum.STAFF, username='staff2',
                     password=str(hashlib.md5('staff2'.encode('utf-8')).hexdigest()))
        user5 = Customer(name='Nguyễn Duy Minh',card_id='012345678910', phone='0123456793', address='202 Street W',
                     email='minh.nguyen@example.com', user_role=UserRoleEnum.CUSTOMER, username='customer1',
                     password=str(hashlib.md5('customer1'.encode('utf-8')).hexdigest()))
        user6 = Customer(name='Hoàng Minh Tú',card_id='012345678710', phone='0123456723', address='202 Street B', email='tu.hoang@example.com',
                     user_role=UserRoleEnum.CUSTOMER, username='customer2',
                     password=str(hashlib.md5('customer2'.encode('utf-8')).hexdigest()))
        user7 = Customer(name='Trần Văn A',card_id='012345678810', phone='0133456723', address='202 Street B', email='a.tran@example.com',
                     user_role=UserRoleEnum.CUSTOMER, username='customer3',
                     password=str(hashlib.md5('customer3'.encode('utf-8')).hexdigest()))
        user8 = Customer(name='Cao Thị C',card_id='012345672410', phone='0124456723', address='202 Street B', email='c.cao@example.com',
                     user_role=UserRoleEnum.CUSTOMER, username='customer4',
                     password=str(hashlib.md5('customer4'.encode('utf-8')).hexdigest()))
        user9 = Customer(name='Nguyễn Minh Khải',card_id='012345678110', phone='01255456723', address='202 Street B', email='khai.nguyen@example.com',
                     user_role=UserRoleEnum.CUSTOMER, username='customer5',
                     password=str(hashlib.md5('customer5'.encode('utf-8')).hexdigest()))
        db.session.add_all([user1, user2, user3, user4, user5, user6,user7,user8,user9])


        cmt1 = Comment(user=None, text='thật tuyệt vời')
        cmt2 = Comment(user='1', text='tôi vừa đặt vé')
        cmt3 = Comment(user='2', text='test bình luận')
        cmt4 = Comment(user='3', text='giao diện chưa đẹp')
        cmt5 = Comment(user=None, text='web thiếu nhiều')
        db.session.add_all([cmt1, cmt2, cmt3, cmt4, cmt5])
        db.session.commit()


        #
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

        db.session.add_all([rule1,rule2,rule6])
        db.session.commit()
        #         ==============================Tuyến Hà Nội(HAN) - Hồ Chí Minh(SGN) ======================================
        flight1 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                         landing_time=datetime(2024, 12, 28, 23, 00, 00),
                            first_seat_quantity = rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='1')
        flight2 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                         landing_time=datetime(2024, 12, 27 , 11, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='1')
        flight3 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_off_time=datetime(2024, 12, 27, 23, 00, 00),
                         landing_time=datetime(2024, 12, 28, 12, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='3', route_id='1')
        flight4 = Flight(name='Hà Nội(HAN) - Hồ Chí Minh(SGN)', take_off_time=datetime(2024, 12, 27, 5, 00, 00),
                         landing_time=datetime(2024, 12, 27, 10, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='4', route_id='1')
        #         ==============================Tuyến Hà Nội(HAN) - Đà Nẵng(DAD) ======================================
        flight5 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_off_time=datetime(2024, 12, 27, 10, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='2')
        flight6 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_off_time=datetime(2024, 12, 28, 8, 00, 00),
                         landing_time=datetime(2024, 12, 28, 11, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='2')
        flight7 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_off_time=datetime(2024, 12, 27, 10, 00, 00),
                         landing_time=datetime(2024, 12, 28, 12, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='3', route_id='1')
        flight8 = Flight(name='Hà Nội(HAN) - Đà Nẵng(DAD)', take_off_time=datetime(2024, 12, 30, 5, 00, 00),
                         landing_time=datetime(2024, 12, 30, 10, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='4', route_id='2')

        #         ==============================Tuyến Hà Nội(HAN) - Nha Trang(CXR) ======================================
        flight9 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                         landing_time=datetime(2024, 12, 28, 23, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='4')
        flight10 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                         landing_time=datetime(2024, 12, 27, 11, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='4')
        flight11 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 23, 00, 00),
                         landing_time=datetime(2024, 12, 27, 12, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='3', route_id='4')
        flight12 = Flight(name='Hà Nội(HAN) - Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 5, 00, 00),
                         landing_time=datetime(2024, 12, 27, 10, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='4', route_id='4')

        #         ==============================Tuyến Đà Nẵng(DAD) - TP HCM(SG) ======================================
        flight13 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                         landing_time=datetime(2024, 12, 28, 23, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='3')
        flight14 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                         landing_time=datetime(2024, 12, 28, 21, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='3')
        flight15 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_off_time=datetime(2024, 12, 27, 23, 00, 00),
                         landing_time=datetime(2024, 12, 27, 1, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='3', route_id='3')
        flight16 = Flight(name='Đà Nẵng(DAD) - TP HCM(SG)', take_off_time=datetime(2024, 12, 27, 5, 00, 00),
                         landing_time=datetime(2024, 12, 27, 10, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='4', route_id='3')

        #         ==============================Tuyến TP HCM(SG)- Nha Trang(CXR) ======================================
        flight17 = Flight(name='TP HCM(SG)- Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                         landing_time=datetime(2024, 12, 27, 23, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='5')
        flight18 = Flight(name='TP HCM(SG)- Nha Trang(CXR)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                         landing_time=datetime(2024, 12, 27, 20, 00, 00),
                         first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='5')

        #         ==============================Tuyến Hà Nội(HAN) - Phú Quốc(PQH) ======================================
        flight19 = Flight(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 15, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='6')
        flight20 = Flight(name='Hà Nội(HAN) - Phú Quốc(PQH)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                          landing_time=datetime(2024, 12, 27, 15, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='6')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Phú Quốc(PQH) ======================================
        flight21 = Flight(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 12, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='7')
        flight22 = Flight(name='Hồ Chí Minh(SGN) - Phú Quốc(PQH)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                          landing_time=datetime(2024, 12, 28, 16, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='7')

        #         ==============================Tuyến Hà Nội(HAN) - Quy Nhơn(UIH) ======================================
        flight23 = Flight(name='Hà Nội(HAN) - Quy Nhơn(UIH)', take_off_time=datetime(2024, 12, 28, 11, 00, 00),
                          landing_time=datetime(2024, 12, 29, 19, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='8')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Đà Lạt(DLI) ======================================
        flight24 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 20, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='9')
        flight25 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_off_time=datetime(2024, 12, 27, 12, 00, 00),
                          landing_time=datetime(2024, 12, 27, 19, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='9')

        #         ==============================Tuyến Hà Nội(HAN) - Hải Phòng(HPH) ======================================
        flight26 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_off_time=datetime(2024, 12, 26, 11, 00, 00),
                          landing_time=datetime(2024, 12, 26, 15, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='10')
        flight27 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_off_time=datetime(2024, 12, 26, 12, 00, 00),
                          landing_time=datetime(2024, 12, 26, 18, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='2', route_id='10')

        #         ==============================Tuyến Hà Nội(HAN) - Điện Biên Phủ(DIN) ======================================
        flight28 = Flight(name='Hà Nội(HAN) - Hải Phòng(HPH)', take_off_time=datetime(2024, 12, 25, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='11')

        #         ==============================Tuyến Hồ Chí Minh(SGN) - Côn Đảo(VCS) ======================================
        flight29 = Flight(name='Hồ Chí Minh(SGN) - Côn Đảo(VCS)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='12')

        #         ==============================Tuyến Hà Nội(HAN) - Phú Yên(UIH) ======================================
        flight30 = Flight(name='Hà Nội(HAN) - Phú Yên(UIH)', take_off_time=datetime(2024, 12, 27, 11, 00, 00),
                          landing_time=datetime(2024, 12, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value,second_seat_quantity = rule2.value, plane_id='1', route_id='13')



        db.session.add_all([flight1, flight2, flight3, flight4, flight5,
                            flight6, flight7, flight8, flight9, flight10,
                            flight11, flight12, flight13, flight14, flight15,
                            flight16, flight17, flight18, flight19, flight20,
                            flight21, flight22, flight23, flight24, flight25,
                            flight26, flight27, flight28, flight29, flight30,
                            ])
        db.session.commit()


        mid_airport1 = MidAirport(name='Sân bay Nội Bài (HAN)',airport_id='1', flight_id='1',stop_time=rule3.value, note='Dừng x giờ')
        # mid_airport2 = MidAirport(name='Sân bay Nội Bài (HAN)',stop_time=rule3.value, note='Dừng x giờ', mid_airport_id='6', flight_id='2')
        db.session.add_all([mid_airport1])
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
        seat1 = Seat(name='Seat01', status=False, flight_id='1',fareclass_id='1')
        seat2 = Seat(name='Seat02', status=False, flight_id='1',fareclass_id='1')
        seat3 = Seat(name='Seat03', status=False, flight_id='1',fareclass_id='1')
        seat4 = Seat(name='Seat04', status=False, flight_id='1',fareclass_id='1')
        seat5 = Seat(name='Seat05', status=False, flight_id='1',fareclass_id='1')

        seat6 = Seat(name='Seat01', status=False, flight_id='2',fareclass_id='1')
        seat7 = Seat(name='Seat02', status=False, flight_id='2',fareclass_id='1')
        seat8 = Seat(name='Seat03', status=False, flight_id='2',fareclass_id='1')
        seat9 = Seat(name='Seat04', status=False, flight_id='2',fareclass_id='1')
        seat10 = Seat(name='Seat05', status=False, flight_id='2',fareclass_id='1')

        seat11 = Seat(name='Seat01', status=False, flight_id='3',fareclass_id='1')
        seat12 = Seat(name='Seat02', status=False, flight_id='3',fareclass_id='1')
        seat13 = Seat(name='Seat03', status=False, flight_id='3',fareclass_id='1')
        seat14 = Seat(name='Seat04', status=False, flight_id='3',fareclass_id='1')
        seat15 = Seat(name='Seat05', status=False, flight_id='3',fareclass_id='1')

        seat16 = Seat(name='Seat01', status=False, flight_id='4',fareclass_id='1')
        seat17 = Seat(name='Seat02', status=False, flight_id='4',fareclass_id='1')
        seat18 = Seat(name='Seat03', status=False, flight_id='4',fareclass_id='1')
        seat19 = Seat(name='Seat04', status=False, flight_id='4',fareclass_id='1')
        seat20 = Seat(name='Seat05', status=False, flight_id='4',fareclass_id='1')

        seat21 = Seat(name='Seat01', status=False, flight_id='5',fareclass_id='1')
        seat22 = Seat(name='Seat02', status=False, flight_id='5',fareclass_id='1')
        seat23 = Seat(name='Seat03', status=False, flight_id='5',fareclass_id='1')
        seat24 = Seat(name='Seat04', status=False, flight_id='5',fareclass_id='1')
        seat25 = Seat(name='Seat05', status=False, flight_id='5',fareclass_id='1')

        seat26 = Seat(name='Seat01', status=False, flight_id='6',fareclass_id='1')
        seat27 = Seat(name='Seat02', status=False, flight_id='6',fareclass_id='1')
        seat28 = Seat(name='Seat03', status=False, flight_id='6',fareclass_id='1')
        seat29 = Seat(name='Seat04', status=False, flight_id='6',fareclass_id='1')
        seat30 = Seat(name='Seat05', status=False, flight_id='6',fareclass_id='1')

        seat31 = Seat(name='Seat01', status=False, flight_id='7',fareclass_id='1')
        seat32 = Seat(name='Seat02', status=False, flight_id='7',fareclass_id='1')
        seat33 = Seat(name='Seat03', status=False, flight_id='7',fareclass_id='1')
        seat34 = Seat(name='Seat04', status=False, flight_id='7',fareclass_id='1')
        seat35 = Seat(name='Seat05', status=False, flight_id='7',fareclass_id='1')

        seat36 = Seat(name='Seat01', status=False, flight_id='8',fareclass_id='1')
        seat37 = Seat(name='Seat02', status=False, flight_id='8',fareclass_id='1')
        seat38 = Seat(name='Seat03', status=False, flight_id='8',fareclass_id='1')
        seat39 = Seat(name='Seat04', status=False, flight_id='8',fareclass_id='1')
        seat40 = Seat(name='Seat05', status=False, flight_id='8',fareclass_id='1')

        seat41 = Seat(name='Seat01', status=False, flight_id='9',fareclass_id='1')
        seat42 = Seat(name='Seat02', status=False, flight_id='9',fareclass_id='1')
        seat43 = Seat(name='Seat03', status=False, flight_id='9',fareclass_id='1')
        seat44 = Seat(name='Seat04', status=False, flight_id='9',fareclass_id='1')
        seat45 = Seat(name='Seat05', status=False, flight_id='9',fareclass_id='1')

        seat46 = Seat(name='Seat01', status=False, flight_id='10',fareclass_id='1')
        seat47 = Seat(name='Seat02', status=False, flight_id='10',fareclass_id='1')
        seat48 = Seat(name='Seat03', status=False, flight_id='10',fareclass_id='1')
        seat49 = Seat(name='Seat04', status=False, flight_id='10',fareclass_id='1')
        seat50 = Seat(name='Seat05', status=False, flight_id='10',fareclass_id='1')

        seat51 = Seat(name='Seat01', status=False, flight_id='11',fareclass_id='1')
        seat52 = Seat(name='Seat02', status=False, flight_id='11',fareclass_id='1')
        seat53 = Seat(name='Seat03', status=False, flight_id='11',fareclass_id='1')
        seat54 = Seat(name='Seat04', status=False, flight_id='11',fareclass_id='1')
        seat55 = Seat(name='Seat05', status=False, flight_id='11',fareclass_id='1')

        seat56 = Seat(name='Seat01', status=False, flight_id='12',fareclass_id='1')
        seat57 = Seat(name='Seat02', status=False, flight_id='12',fareclass_id='1')
        seat58 = Seat(name='Seat03', status=False, flight_id='12',fareclass_id='1')
        seat59 = Seat(name='Seat04', status=False, flight_id='12',fareclass_id='1')
        seat60 = Seat(name='Seat05', status=False, flight_id='12',fareclass_id='1')

        seat61 = Seat(name='Seat01', status=False, flight_id='13',fareclass_id='1')
        seat62 = Seat(name='Seat02', status=False, flight_id='13',fareclass_id='1')
        seat63 = Seat(name='Seat03', status=False, flight_id='13',fareclass_id='1')
        seat64 = Seat(name='Seat04', status=False, flight_id='13',fareclass_id='1')
        seat65 = Seat(name='Seat05', status=False, flight_id='13',fareclass_id='1')

        seat66 = Seat(name='Seat01', status=False, flight_id='14',fareclass_id='1')
        seat67 = Seat(name='Seat02', status=False, flight_id='14',fareclass_id='1')
        seat68 = Seat(name='Seat03', status=False, flight_id='14',fareclass_id='1')
        seat69 = Seat(name='Seat04', status=False, flight_id='14',fareclass_id='1')
        seat70 = Seat(name='Seat05', status=False, flight_id='14',fareclass_id='1')

        seat71 = Seat(name='Seat01', status=False, flight_id='15',fareclass_id='1')
        seat72 = Seat(name='Seat02', status=False, flight_id='15',fareclass_id='1')
        seat73 = Seat(name='Seat03', status=False, flight_id='15',fareclass_id='1')
        seat74 = Seat(name='Seat04', status=False, flight_id='15',fareclass_id='1')
        seat75 = Seat(name='Seat05', status=False, flight_id='15',fareclass_id='1')

        seat76 = Seat(name='Seat01', status=False, flight_id='16',fareclass_id='1')
        seat77 = Seat(name='Seat02', status=False, flight_id='16',fareclass_id='1')
        seat78 = Seat(name='Seat03', status=False, flight_id='16',fareclass_id='1')
        seat79 = Seat(name='Seat04', status=False, flight_id='16',fareclass_id='1')
        seat80 = Seat(name='Seat05', status=False, flight_id='16',fareclass_id='1')

        seat81 = Seat(name='Seat01', status=False, flight_id='17',fareclass_id='1')
        seat82 = Seat(name='Seat02', status=False, flight_id='17',fareclass_id='1')
        seat83 = Seat(name='Seat03', status=False, flight_id='17',fareclass_id='1')
        seat84 = Seat(name='Seat04', status=False, flight_id='17',fareclass_id='1')
        seat85 = Seat(name='Seat05', status=False, flight_id='17',fareclass_id='1')

        seat86 = Seat(name='Seat01', status=False, flight_id='18',fareclass_id='1')
        seat87 = Seat(name='Seat02', status=False, flight_id='18',fareclass_id='1')
        seat88 = Seat(name='Seat03', status=False, flight_id='18',fareclass_id='1')
        seat89 = Seat(name='Seat04', status=False, flight_id='18',fareclass_id='1')
        seat90 = Seat(name='Seat05', status=False, flight_id='18',fareclass_id='1')

        seat91 = Seat(name='Seat01', status=False, flight_id='19',fareclass_id='1')
        seat92 = Seat(name='Seat02', status=False, flight_id='19',fareclass_id='1')
        seat93 = Seat(name='Seat03', status=False, flight_id='19',fareclass_id='1')
        seat94 = Seat(name='Seat04', status=False, flight_id='19',fareclass_id='1')
        seat95 = Seat(name='Seat05', status=False, flight_id='19',fareclass_id='1')

        seat96 = Seat(name='Seat01', status=False, flight_id='20',fareclass_id='1')
        seat97 = Seat(name='Seat02', status=False, flight_id='20',fareclass_id='1')
        seat98 = Seat(name='Seat03', status=False, flight_id='20',fareclass_id='1')
        seat99 = Seat(name='Seat04', status=False, flight_id='20',fareclass_id='1')
        seat100 = Seat(name='Seat05', status=False, flight_id='20',fareclass_id='1')

        seat101 = Seat(name='Seat01', status=False, flight_id='21',fareclass_id='1')
        seat102 = Seat(name='Seat02', status=False, flight_id='21',fareclass_id='1')
        seat103 = Seat(name='Seat03', status=False, flight_id='21',fareclass_id='1')
        seat104 = Seat(name='Seat04', status=False, flight_id='21',fareclass_id='1')
        seat105 = Seat(name='Seat05', status=False, flight_id='21',fareclass_id='1')

        seat106 = Seat(name='Seat01', status=False, flight_id='22',fareclass_id='1')
        seat107 = Seat(name='Seat02', status=False, flight_id='22',fareclass_id='1')
        seat108 = Seat(name='Seat03', status=False, flight_id='22',fareclass_id='1')
        seat109 = Seat(name='Seat04', status=False, flight_id='22',fareclass_id='1')
        seat110 = Seat(name='Seat05', status=False, flight_id='22',fareclass_id='1')

        seat111 = Seat(name='Seat01', status=False, flight_id='23',fareclass_id='1')
        seat112 = Seat(name='Seat02', status=False, flight_id='23',fareclass_id='1')
        seat113 = Seat(name='Seat03', status=False, flight_id='23',fareclass_id='1')
        seat114 = Seat(name='Seat04', status=False, flight_id='23',fareclass_id='1')
        seat115 = Seat(name='Seat05', status=False, flight_id='23',fareclass_id='1')

        seat116 = Seat(name='Seat01', status=False, flight_id='24',fareclass_id='1')
        seat117 = Seat(name='Seat02', status=False, flight_id='24',fareclass_id='1')
        seat118 = Seat(name='Seat03', status=False, flight_id='24',fareclass_id='1')
        seat119 = Seat(name='Seat04', status=False, flight_id='24',fareclass_id='1')
        seat120 = Seat(name='Seat05', status=False, flight_id='24',fareclass_id='1')

        seat121 = Seat(name='Seat01', status=False, flight_id='25',fareclass_id='1')
        seat122 = Seat(name='Seat02', status=False, flight_id='25',fareclass_id='1')
        seat123 = Seat(name='Seat03', status=False, flight_id='25',fareclass_id='1')
        seat124 = Seat(name='Seat04', status=False, flight_id='25',fareclass_id='1')
        seat125 = Seat(name='Seat05', status=False, flight_id='25',fareclass_id='1')

        seat126 = Seat(name='Seat01', status=False, flight_id='26',fareclass_id='1')
        seat127 = Seat(name='Seat02', status=False, flight_id='26',fareclass_id='1')
        seat128 = Seat(name='Seat03', status=False, flight_id='26',fareclass_id='1')
        seat129 = Seat(name='Seat04', status=False, flight_id='26',fareclass_id='1')
        seat130 = Seat(name='Seat05', status=False, flight_id='26',fareclass_id='1')

        seat131 = Seat(name='Seat01', status=False, flight_id='27',fareclass_id='1')
        seat132 = Seat(name='Seat02', status=False, flight_id='27',fareclass_id='1')
        seat133 = Seat(name='Seat03', status=False, flight_id='27',fareclass_id='1')
        seat134 = Seat(name='Seat04', status=False, flight_id='27',fareclass_id='1')
        seat135 = Seat(name='Seat05', status=False, flight_id='27',fareclass_id='1')

        seat136 = Seat(name='Seat01', status=False, flight_id='28',fareclass_id='1')
        seat137 = Seat(name='Seat02', status=False, flight_id='28',fareclass_id='1')
        seat138 = Seat(name='Seat03', status=False, flight_id='28',fareclass_id='1')
        seat139 = Seat(name='Seat04', status=False, flight_id='28',fareclass_id='1')
        seat140 = Seat(name='Seat05', status=False, flight_id='28',fareclass_id='1')

        seat141 = Seat(name='Seat01', status=False, flight_id='29',fareclass_id='1')
        seat142 = Seat(name='Seat02', status=False, flight_id='29',fareclass_id='1')
        seat143 = Seat(name='Seat03', status=False, flight_id='29',fareclass_id='1')
        seat144 = Seat(name='Seat04', status=False, flight_id='29',fareclass_id='1')
        seat145 = Seat(name='Seat05', status=False, flight_id='29',fareclass_id='1')

        seat146 = Seat(name='Seat01', status=False, flight_id='30',fareclass_id='1')
        seat147 = Seat(name='Seat02', status=False, flight_id='30',fareclass_id='1')
        seat148 = Seat(name='Seat03', status=False, flight_id='30',fareclass_id='1')
        seat149 = Seat(name='Seat04', status=False, flight_id='30',fareclass_id='1')
        seat150 = Seat(name='Seat05', status=False, flight_id='30',fareclass_id='1')


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
        ])
        db.session.commit()
        seat181 = Seat(name='Seat01', status=False, flight_id='1', fareclass_id='2')
        seat182 = Seat(name='Seat02', status=False, flight_id='1', fareclass_id='2')
        seat183 = Seat(name='Seat03', status=False, flight_id='1', fareclass_id='2')
        seat184 = Seat(name='Seat04', status=False, flight_id='1', fareclass_id='2')
        seat185 = Seat(name='Seat05', status=False, flight_id='1', fareclass_id='2')
        seat186 = Seat(name='Seat01', status=False, flight_id='2', fareclass_id='2')
        seat187 = Seat(name='Seat02', status=False, flight_id='2', fareclass_id='2')
        seat188 = Seat(name='Seat03', status=False, flight_id='2', fareclass_id='2')
        seat189 = Seat(name='Seat04', status=False, flight_id='2', fareclass_id='2')
        seat190 = Seat(name='Seat05', status=False, flight_id='2', fareclass_id='2')
        seat191 = Seat(name='Seat01', status=False, flight_id='3', fareclass_id='2')
        seat192 = Seat(name='Seat02', status=False, flight_id='3', fareclass_id='2')
        seat193 = Seat(name='Seat03', status=False, flight_id='3', fareclass_id='2')
        seat194 = Seat(name='Seat04', status=False, flight_id='3', fareclass_id='2')
        seat195 = Seat(name='Seat05', status=False, flight_id='3', fareclass_id='2')
        seat196 = Seat(name='Seat01', status=False, flight_id='4', fareclass_id='2')
        seat197 = Seat(name='Seat02', status=False, flight_id='4', fareclass_id='2')
        seat198 = Seat(name='Seat03', status=False, flight_id='4', fareclass_id='2')
        seat199 = Seat(name='Seat04', status=False, flight_id='4', fareclass_id='2')
        seat200 = Seat(name='Seat05', status=False, flight_id='4', fareclass_id='2')
        seat201 = Seat(name='Seat01', status=False, flight_id='5', fareclass_id='2')
        seat202 = Seat(name='Seat02', status=False, flight_id='5', fareclass_id='2')
        seat203 = Seat(name='Seat03', status=False, flight_id='5', fareclass_id='2')
        seat204 = Seat(name='Seat04', status=False, flight_id='5', fareclass_id='2')
        seat205 = Seat(name='Seat05', status=False, flight_id='5', fareclass_id='2')
        seat206 = Seat(name='Seat01', status=False, flight_id='6', fareclass_id='2')
        seat207 = Seat(name='Seat02', status=False, flight_id='6', fareclass_id='2')
        seat208 = Seat(name='Seat03', status=False, flight_id='6', fareclass_id='2')
        seat209 = Seat(name='Seat04', status=False, flight_id='6', fareclass_id='2')
        seat210 = Seat(name='Seat05', status=False, flight_id='6', fareclass_id='2')
        seat211 = Seat(name='Seat01', status=False, flight_id='7', fareclass_id='2')
        seat212 = Seat(name='Seat02', status=False, flight_id='7', fareclass_id='2')
        seat213 = Seat(name='Seat03', status=False, flight_id='7', fareclass_id='2')
        seat214 = Seat(name='Seat04', status=False, flight_id='7', fareclass_id='2')
        seat215 = Seat(name='Seat05', status=False, flight_id='7', fareclass_id='2')
        seat216 = Seat(name='Seat01', status=False, flight_id='8', fareclass_id='2')
        seat217 = Seat(name='Seat02', status=False, flight_id='8', fareclass_id='2')
        seat218 = Seat(name='Seat03', status=False, flight_id='8', fareclass_id='2')
        seat219 = Seat(name='Seat04', status=False, flight_id='8', fareclass_id='2')
        seat220 = Seat(name='Seat05', status=False, flight_id='8', fareclass_id='2')
        seat221 = Seat(name='Seat01', status=False, flight_id='9', fareclass_id='2')
        seat222 = Seat(name='Seat02', status=False, flight_id='9', fareclass_id='2')
        seat223 = Seat(name='Seat03', status=False, flight_id='9', fareclass_id='2')
        seat224 = Seat(name='Seat04', status=False, flight_id='9', fareclass_id='2')
        seat225 = Seat(name='Seat05', status=False, flight_id='9', fareclass_id='2')
        seat226 = Seat(name='Seat01', status=False, flight_id='10', fareclass_id='2')
        seat227 = Seat(name='Seat02', status=False, flight_id='10', fareclass_id='2')
        seat228 = Seat(name='Seat03', status=False, flight_id='10', fareclass_id='2')
        seat229 = Seat(name='Seat04', status=False, flight_id='10', fareclass_id='2')
        seat230 = Seat(name='Seat05', status=False, flight_id='10', fareclass_id='2')
        seat231 = Seat(name='Seat01', status=False, flight_id='11', fareclass_id='2')
        seat232 = Seat(name='Seat02', status=False, flight_id='11', fareclass_id='2')
        seat233 = Seat(name='Seat03', status=False, flight_id='11', fareclass_id='2')
        seat234 = Seat(name='Seat04', status=False, flight_id='11', fareclass_id='2')
        seat235 = Seat(name='Seat05', status=False, flight_id='11', fareclass_id='2')
        seat236 = Seat(name='Seat01', status=False, flight_id='12', fareclass_id='2')
        seat237 = Seat(name='Seat02', status=False, flight_id='12', fareclass_id='2')
        seat238 = Seat(name='Seat03', status=False, flight_id='12', fareclass_id='2')
        seat239 = Seat(name='Seat04', status=False, flight_id='12', fareclass_id='2')
        seat240 = Seat(name='Seat05', status=False, flight_id='12', fareclass_id='2')
        seat241 = Seat(name='Seat01', status=False, flight_id='13', fareclass_id='2')
        seat242 = Seat(name='Seat02', status=False, flight_id='13', fareclass_id='2')
        seat243 = Seat(name='Seat03', status=False, flight_id='13', fareclass_id='2')
        seat244 = Seat(name='Seat04', status=False, flight_id='13', fareclass_id='2')
        seat245 = Seat(name='Seat05', status=False, flight_id='13', fareclass_id='2')
        seat246 = Seat(name='Seat01', status=False, flight_id='14', fareclass_id='2')
        seat247 = Seat(name='Seat02', status=False, flight_id='14', fareclass_id='2')
        seat248 = Seat(name='Seat03', status=False, flight_id='14', fareclass_id='2')
        seat249 = Seat(name='Seat04', status=False, flight_id='14', fareclass_id='2')
        seat250 = Seat(name='Seat05', status=False, flight_id='14', fareclass_id='2')
        seat251 = Seat(name='Seat01', status=False, flight_id='15', fareclass_id='2')
        seat252 = Seat(name='Seat02', status=False, flight_id='15', fareclass_id='2')
        seat253 = Seat(name='Seat03', status=False, flight_id='15', fareclass_id='2')
        seat254 = Seat(name='Seat04', status=False, flight_id='15', fareclass_id='2')
        seat255 = Seat(name='Seat05', status=False, flight_id='15', fareclass_id='2')
        seat256 = Seat(name='Seat01', status=False, flight_id='16', fareclass_id='2')
        seat257 = Seat(name='Seat02', status=False, flight_id='16', fareclass_id='2')
        seat258 = Seat(name='Seat03', status=False, flight_id='16', fareclass_id='2')
        seat259 = Seat(name='Seat04', status=False, flight_id='16', fareclass_id='2')
        seat260 = Seat(name='Seat05', status=False, flight_id='16', fareclass_id='2')
        seat261 = Seat(name='Seat01', status=False, flight_id='17', fareclass_id='2')
        seat262 = Seat(name='Seat02', status=False, flight_id='17', fareclass_id='2')
        seat263 = Seat(name='Seat03', status=False, flight_id='17', fareclass_id='2')
        seat264 = Seat(name='Seat04', status=False, flight_id='17', fareclass_id='2')
        seat265 = Seat(name='Seat05', status=False, flight_id='17', fareclass_id='2')
        seat266 = Seat(name='Seat01', status=False, flight_id='18', fareclass_id='2')
        seat267 = Seat(name='Seat02', status=False, flight_id='18', fareclass_id='2')
        seat268 = Seat(name='Seat03', status=False, flight_id='18', fareclass_id='2')
        seat269 = Seat(name='Seat04', status=False, flight_id='18', fareclass_id='2')
        seat270 = Seat(name='Seat05', status=False, flight_id='18', fareclass_id='2')
        seat271 = Seat(name='Seat01', status=False, flight_id='19', fareclass_id='2')
        seat272 = Seat(name='Seat02', status=False, flight_id='19', fareclass_id='2')
        seat273 = Seat(name='Seat03', status=False, flight_id='19', fareclass_id='2')
        seat274 = Seat(name='Seat04', status=False, flight_id='19', fareclass_id='2')
        seat275 = Seat(name='Seat05', status=False, flight_id='19', fareclass_id='2')
        seat276 = Seat(name='Seat01', status=False, flight_id='20', fareclass_id='2')
        seat277 = Seat(name='Seat02', status=False, flight_id='20', fareclass_id='2')
        seat278 = Seat(name='Seat03', status=False, flight_id='20', fareclass_id='2')
        seat279 = Seat(name='Seat04', status=False, flight_id='20', fareclass_id='2')
        seat280 = Seat(name='Seat05', status=False, flight_id='20', fareclass_id='2')
        seat281 = Seat(name='Seat01', status=False, flight_id='21', fareclass_id='2')
        seat282 = Seat(name='Seat02', status=False, flight_id='21', fareclass_id='2')
        seat283 = Seat(name='Seat03', status=False, flight_id='21', fareclass_id='2')
        seat284 = Seat(name='Seat04', status=False, flight_id='21', fareclass_id='2')
        seat285 = Seat(name='Seat05', status=False, flight_id='21', fareclass_id='2')
        seat286 = Seat(name='Seat01', status=False, flight_id='22', fareclass_id='2')
        seat287 = Seat(name='Seat02', status=False, flight_id='22', fareclass_id='2')
        seat288 = Seat(name='Seat03', status=False, flight_id='22', fareclass_id='2')
        seat289 = Seat(name='Seat04', status=False, flight_id='22', fareclass_id='2')
        seat290 = Seat(name='Seat05', status=False, flight_id='22', fareclass_id='2')
        seat291 = Seat(name='Seat01', status=False, flight_id='23', fareclass_id='2')
        seat292 = Seat(name='Seat02', status=False, flight_id='23', fareclass_id='2')
        seat293 = Seat(name='Seat03', status=False, flight_id='23', fareclass_id='2')
        seat294 = Seat(name='Seat04', status=False, flight_id='23', fareclass_id='2')
        seat295 = Seat(name='Seat05', status=False, flight_id='23', fareclass_id='2')
        seat296 = Seat(name='Seat01', status=False, flight_id='24', fareclass_id='2')
        seat297 = Seat(name='Seat02', status=False, flight_id='24', fareclass_id='2')
        seat298 = Seat(name='Seat03', status=False, flight_id='24', fareclass_id='2')
        seat299 = Seat(name='Seat04', status=False, flight_id='24', fareclass_id='2')
        seat300 = Seat(name='Seat05', status=False, flight_id='24', fareclass_id='2')
        seat301 = Seat(name='Seat01', status=False, flight_id='25', fareclass_id='2')
        seat302 = Seat(name='Seat02', status=False, flight_id='25', fareclass_id='2')
        seat303 = Seat(name='Seat03', status=False, flight_id='25', fareclass_id='2')
        seat304 = Seat(name='Seat04', status=False, flight_id='25', fareclass_id='2')
        seat305 = Seat(name='Seat05', status=False, flight_id='25', fareclass_id='2')
        seat306 = Seat(name='Seat01', status=False, flight_id='26', fareclass_id='2')
        seat307 = Seat(name='Seat02', status=False, flight_id='26', fareclass_id='2')
        seat308 = Seat(name='Seat03', status=False, flight_id='26', fareclass_id='2')
        seat309 = Seat(name='Seat04', status=False, flight_id='26', fareclass_id='2')
        seat310 = Seat(name='Seat05', status=False, flight_id='26', fareclass_id='2')
        seat311 = Seat(name='Seat01', status=False, flight_id='27', fareclass_id='2')
        seat312 = Seat(name='Seat02', status=False, flight_id='27', fareclass_id='2')
        seat313 = Seat(name='Seat03', status=False, flight_id='27', fareclass_id='2')
        seat314 = Seat(name='Seat04', status=False, flight_id='27', fareclass_id='2')
        seat315 = Seat(name='Seat05', status=False, flight_id='27', fareclass_id='2')
        seat316 = Seat(name='Seat01', status=False, flight_id='28', fareclass_id='2')
        seat317 = Seat(name='Seat02', status=False, flight_id='28', fareclass_id='2')
        seat318 = Seat(name='Seat03', status=False, flight_id='28', fareclass_id='2')
        seat319 = Seat(name='Seat04', status=False, flight_id='28', fareclass_id='2')
        seat320 = Seat(name='Seat05', status=False, flight_id='28', fareclass_id='2')
        seat321 = Seat(name='Seat01', status=False, flight_id='29', fareclass_id='2')
        seat322 = Seat(name='Seat02', status=False, flight_id='29', fareclass_id='2')
        seat323 = Seat(name='Seat03', status=False, flight_id='29', fareclass_id='2')
        seat324 = Seat(name='Seat04', status=False, flight_id='29', fareclass_id='2')
        seat325 = Seat(name='Seat05', status=False, flight_id='29', fareclass_id='2')
        seat326 = Seat(name='Seat01', status=False, flight_id='30', fareclass_id='2')
        seat327 = Seat(name='Seat02', status=False, flight_id='30', fareclass_id='2')
        seat328 = Seat(name='Seat03', status=False, flight_id='30', fareclass_id='2')
        seat329 = Seat(name='Seat04', status=False, flight_id='30', fareclass_id='2')
        seat330 = Seat(name='Seat05', status=False, flight_id='30', fareclass_id='2')
        db.session.add_all([
            seat181, seat182, seat183, seat184, seat185,
            seat186, seat187, seat188, seat189, seat190,
            seat191, seat192, seat193, seat194, seat195,
            seat196, seat197, seat198, seat199, seat200,
            seat201, seat202, seat203, seat204, seat205,
            seat206, seat207, seat208, seat209, seat210,
            seat211, seat212, seat213, seat214, seat215,
            seat216, seat217, seat218, seat219, seat220,
            seat221, seat222, seat223, seat224, seat225,
            seat226, seat227, seat228, seat229, seat230,
            seat231, seat232, seat233, seat234, seat235,
            seat236, seat237, seat238, seat239, seat240,
            seat241, seat242, seat243, seat244, seat245,
            seat246, seat247, seat248, seat249, seat250,
            seat251, seat252, seat253, seat254, seat255,
            seat256, seat257, seat258, seat259, seat260,
            seat261, seat262, seat263, seat264, seat265,
            seat266, seat267, seat268, seat269, seat270,
            seat271, seat272, seat273, seat274, seat275,
            seat276, seat277, seat278, seat279, seat280,
            seat281, seat282, seat283, seat284, seat285,
            seat286, seat287, seat288, seat289, seat290,
            seat291, seat292, seat293, seat294, seat295,
            seat296, seat297, seat298, seat299, seat300,
            seat301, seat302, seat303, seat304, seat305,
            seat306, seat307, seat308, seat309, seat310,
            seat311, seat312, seat313, seat314, seat315,
            seat316, seat317, seat318, seat319, seat320,
            seat321, seat322, seat323, seat324, seat325,
            seat326, seat327, seat328, seat329, seat330,
        ])
        db.session.commit()



        # CHUYEN BAY THANG 10
        flight31 = Flight(name='Hà Nội(HAN) - Phú Yên(UIH)', take_off_time=datetime(2024, 10, 15, 11, 00, 00),
                          landing_time=datetime(2024, 10, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value, second_seat_quantity=rule2.value, plane_id='1',
                          route_id='1')
        db.session.add(flight31)
        db.session.commit()
        # CHO NGOI CUA CHUYEN BAY THANG 10,STATUS = TRUE CHO NHUNG VE DUOC DAT
        seat151 = Seat(name='Seat01', status=True, flight_id='31', fareclass_id='1')
        seat152 = Seat(name='Seat02', status=True, flight_id='31', fareclass_id='1')
        seat153 = Seat(name='Seat03', status=True, flight_id='31', fareclass_id='1')
        seat154 = Seat(name='Seat04', status=False, flight_id='31', fareclass_id='1')
        seat155 = Seat(name='Seat05', status=False, flight_id='31', fareclass_id='1')
        seat331 = Seat(name='Seat01', status=True, flight_id='31', fareclass_id='2')
        seat332 = Seat(name='Seat02', status=True, flight_id='31', fareclass_id='2')
        seat333 = Seat(name='Seat03', status=False, flight_id='31', fareclass_id='2')
        seat334 = Seat(name='Seat04', status=False, flight_id='31', fareclass_id='2')
        seat335 = Seat(name='Seat05', status=False, flight_id='31', fareclass_id='2')
        db.session.add_all([ seat151,seat152,seat153,seat154,seat155,seat331,seat332,seat333,seat334,seat335])
        db.session.commit()
        # VE CUA THANG 10
        ticket1 = Ticket(customer_id='1', flight_id='31', seat_id='301', created_date=datetime(2024, 10, 1, 11, 00, 00))
        ticket2 = Ticket(customer_id='2', flight_id='31', seat_id='302', created_date=datetime(2024, 10, 1, 11, 00, 00))
        ticket3 = Ticket(customer_id='3', flight_id='31', seat_id='303', created_date=datetime(2024, 10, 1, 11, 00, 00))
        ticket4 = Ticket(customer_id='4', flight_id='31', seat_id='306', created_date=datetime(2024, 10, 1, 11, 00, 00))
        ticket5 = Ticket(customer_id='5', flight_id='31', seat_id='307', created_date=datetime(2024, 10, 1, 11, 00, 00))
        db.session.add_all([ticket1,ticket2,ticket3,ticket4,ticket5])
        db.session.commit()
        # CHUYEN BAY THANG 11
        flight32 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_off_time=datetime(2024, 11, 15, 11, 00, 00),
                          landing_time=datetime(2024, 11, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value, second_seat_quantity=rule2.value, plane_id='1', route_id='2')
        db.session.add(flight32)
        db.session.commit()
        # CHO NGOI CUA CHUYEN BAY THANG 11,STATUS = TRUE CHO NHUNG VE DUOC DAT
        seat156 = Seat(name='Seat01', status=False, flight_id='32', fareclass_id='1')
        seat157 = Seat(name='Seat02', status=True, flight_id='32', fareclass_id='1')
        seat158 = Seat(name='Seat03', status=True, flight_id='32', fareclass_id='1')
        seat159 = Seat(name='Seat04', status=False, flight_id='32', fareclass_id='1')
        seat160 = Seat(name='Seat05', status=False, flight_id='32', fareclass_id='1')
        seat336 = Seat(name='Seat01', status=True, flight_id='32', fareclass_id='2')
        seat337 = Seat(name='Seat02', status=True, flight_id='32', fareclass_id='2')
        seat338 = Seat(name='Seat03', status=True, flight_id='32', fareclass_id='2')
        seat339 = Seat(name='Seat04', status=False, flight_id='32', fareclass_id='2')
        seat340 = Seat(name='Seat05', status=False, flight_id='32', fareclass_id='2')
        db.session.add_all([seat156, seat157, seat158, seat159, seat160, seat336, seat337, seat338, seat339, seat340])
        db.session.commit()
        # VE CUA THANG 11
        ticket9 = Ticket(customer_id='1', flight_id='32', seat_id='312', created_date=datetime(2024, 11, 1, 11, 00, 00))
        ticket10 = Ticket(customer_id='2', flight_id='32', seat_id='313', created_date=datetime(2024, 11, 1, 11, 00, 00))
        ticket11 = Ticket(customer_id='3', flight_id='32', seat_id='316', created_date=datetime(2024, 11, 1, 11, 00, 00))
        ticket12 = Ticket(customer_id='4', flight_id='32', seat_id='317', created_date=datetime(2024, 11, 1, 11, 00, 00))
        ticket13 = Ticket(customer_id='5', flight_id='32', seat_id='318', created_date=datetime(2024, 11, 1, 11, 00, 00))
        db.session.add_all([ticket9, ticket10, ticket11, ticket12, ticket13])
        db.session.commit()
        #
        # CHUYEN BAY THANG 8
        flight33 = Flight(name='Hồ Chí Minh(SGN) - Đà Lạt(DLI)', take_off_time=datetime(2024, 8, 15, 11, 00, 00),
                          landing_time=datetime(2024, 8, 27, 23, 00, 00),
                          first_seat_quantity=rule1.value, second_seat_quantity=rule2.value, plane_id='1', route_id='13')
        db.session.add(flight33)
        db.session.commit()
        # CHO NGOI CUA CHUYEN BAY THANG 8,STATUS = TRUE CHO NHUNG VE DUOC DAT
        seat161 = Seat(name='Seat01', status=True, flight_id='33', fareclass_id='1')
        seat162 = Seat(name='Seat02', status=True, flight_id='33', fareclass_id='1')
        seat163 = Seat(name='Seat03', status=True, flight_id='33', fareclass_id='1')
        seat164 = Seat(name='Seat04', status=True, flight_id='33', fareclass_id='1')
        seat165 = Seat(name='Seat05', status=False, flight_id='33', fareclass_id='1')
        seat341 = Seat(name='Seat341', status=False, flight_id='33', fareclass_id='2')
        seat342 = Seat(name='Seat342', status=False, flight_id='33', fareclass_id='2')
        seat343 = Seat(name='Seat343', status=True, flight_id='33', fareclass_id='2')
        seat344 = Seat(name='Seat344', status=False, flight_id='33', fareclass_id='2')
        seat345 = Seat(name='Seat345', status=False, flight_id='33', fareclass_id='2')
        db.session.add_all([seat161, seat162, seat163, seat164, seat165, seat341, seat342, seat343, seat344, seat345])
        db.session.commit()
        # VE CUA THANG 8
        ticket17 = Ticket(customer_id='1', flight_id='33', seat_id='321', created_date=datetime(2024, 8, 1, 11, 00, 00))
        ticket18 = Ticket(customer_id='2', flight_id='33', seat_id='322', created_date=datetime(2024, 8, 1, 11, 00, 00))
        ticket19 = Ticket(customer_id='3', flight_id='33', seat_id='323', created_date=datetime(2024, 8, 1, 11, 00, 00))
        ticket20 = Ticket(customer_id='4', flight_id='33', seat_id='324', created_date=datetime(2024, 8, 1, 11, 00, 00))
        ticket21 = Ticket(customer_id='5', flight_id='33', seat_id='328',created_date=datetime(2024, 8, 1, 11, 00, 00))
        db.session.add_all([ticket17, ticket18, ticket19, ticket20, ticket21])
        db.session.commit()



