from symtable import Class

from app import db, app
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, values
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
import  hashlib
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
#####################################
class User(db.Model,UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    avatar = Column(String(100), default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(UserRoleEnum),nullable=False)
    joined_date = Column(DateTime, default=datetime.now())
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    staff_id = relationship("Staff",uselist=False)
    admin_id = relationship("Admin", uselist=False)
    customer_id = relationship("Customer", uselist=False)
    def __str__(self):
        return self.firstname

#####################################
class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    flights = relationship("Ticket",backref="Customer")

#####################################
class Staff(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey(User.id),nullable=False,unique=True)
    flight_schedules = relationship("FlightSchedule",backref="Staff",lazy=True)

    # user = relationship("User",uselist=False)

#####################################
class Admin(db.Model):
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey(User.id),nullable=False,unique=True)

#####################################
class Plane(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    seats = relationship("Seat",backref="Plane",lazy=True)
    flights = relationship("Flight",backref="Plane",lazy=True)
    def __str__(self):
        return self.name

#####################################
class Airport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False,unique=True)
    take_off_airport = relationship("Route", foreign_keys="Route.take_off_airport_id",backref="takeoff_airport")
    landing_airport = relationship("Route", foreign_keys="Route.landing_airport_id",backref="landing_airport_ref")
    flights = relationship("MidAirport",backref="Airport")
    def __str__(self):
        return self.name

#####################################
class Route(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    flights = relationship("Flight",backref="Route",lazy=True)
    take_off_airport_id = Column(Integer,ForeignKey(Airport.id),nullable=False)
    landing_airport_id  = Column(Integer,ForeignKey(Airport.id),nullable=False)


    def __str__(self):
        return self.name
#####################################
class Flight(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    take_of_time = Column(DateTime,nullable=True)
    landing_time = Column(DateTime, nullable=True)
    num_of_1st_seat = Column(Integer,nullable=False)
    num_of_2st_seat = Column(Integer,nullable=False)
    mid_airports = relationship("MidAirport",backref="Flight")
    customers = relationship("Ticket",backref="Flight")
    plane_id = Column(Integer,ForeignKey(Plane.id),nullable=False)
    route_id = Column(Integer,ForeignKey(Route.id),nullable=False)
    flight_schedule_id = relationship("FlightSchedule",uselist=False)
    def __str__(self):
        return self.name
#####################################
class MidAirport(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    stop_time = Column(Float(),nullable=False)
    note = Column(String(255),nullable=True)
    mid_airport_id = Column(Integer, ForeignKey(Airport.id),nullable=False,primary_key=True)
    flight_id = Column(Integer, ForeignKey(Flight.id),nullable=False,primary_key=True)

class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    value = Column(Float, nullable=False)

#####################################
class FlightSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer,ForeignKey(Staff.id),nullable=False)
    # flight_details = relationship("FlightDetails",backref="FlightSchedule",lazy=True)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable=False,unique=True)

#####################################
class FareClass(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50),nullable=False)
    price = Column(Float,nullable=False)
    tickets = relationship("Ticket",backref="FareClass",lazy=True)
    def __str__(self):
        return self.name
#####################################
class Seat(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    status = Column(Boolean,nullable=False)
    # ticket_id = Column(Integer,ForeignKey(Ticket.id),nullable=False, unique=True)
    ticket_id = relationship("Ticket",uselist=False)
    plane_id = Column(Integer,ForeignKey(Plane.id),nullable=False)
    def __str__(self):
        return self.name

#####################################
class Ticket(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer,ForeignKey(Customer.id),nullable=False,primary_key=True)
    flight_id = Column(Integer,ForeignKey(Flight.id),nullable=False,primary_key=True)
    fareclass_id = Column(Integer,ForeignKey(FareClass.id),nullable=False)
    # seat_id  = relationship("Seat",uselist=False)
    seat_id = Column(Integer,ForeignKey(Seat.id),nullable=True,unique=True)


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.create_all()
        #
        # user1 = User(last_name='Nguyen', first_name='An', phone='0123456789', address='123 Street A', email='an.nguyen@example.com',user_role=UserRoleEnum.ADMIN,username='admin1',password=str(hashlib.md5('admin1'.encode('utf-8')).hexdigest()))
        # user2 = User(last_name='Tran', first_name='Binh', phone='0123456790', address='456 Street B', email='binh.tran@example.com', user_role=UserRoleEnum.ADMIN, username='admin2', password=str(hashlib.md5('admin2'.encode('utf-8')).hexdigest()))
        # user3 = User(last_name='Le', first_name='Cuc', phone='0123456791', address='789 Street C', email='cuc.le@example.com', user_role=UserRoleEnum.STAFF,username='staff1',password=str(hashlib.md5('staff1'.encode('utf-8')).hexdigest()))
        # user4 = User(last_name='Pham', first_name='Duong', phone='0123456792', address='101 Street D', email='duong.pham@example.com',user_role=UserRoleEnum.STAFF,username='staff2',password=str(hashlib.md5('staff2'.encode('utf-8')).hexdigest()))
        # user5 = User(last_name='Nguyen', first_name='Minh', phone='0123456793', address='202 Street W', email='minh.nguyen@example.com',user_role=UserRoleEnum.CUSTOMER,username='customer1',password=str(hashlib.md5('customer1'.encode('utf-8')).hexdigest()))
        # user6 = User(last_name='Hoang', first_name='Tu', phone='0123456723', address='202 Street B', email='tu.hoang@example.com',user_role=UserRoleEnum.CUSTOMER, username='customer2',password=str(hashlib.md5('customer2'.encode('utf-8')).hexdigest()))
        #
        # db.session.add_all([user1,user2,user3,user4,user5,user6])
        # db.session.commit()
        #
        # admin1 = Admin(user_id='1')
        # admin2 = Admin(user_id='2')
        # db.session.add_all([admin1,admin2])
        # db.session.commit()

        # staff1 = Staff(user_id='3')
        # staff2 = Staff(user_id='4')
        # db.session.add_all([staff1])
        # db.session.commit()

        # customer1 = Customer(user_id='5')
        # customer2 = Customer(user_id='6')
        # db.session.add_all([customer1,customer2])
        # db.session.commit()

        # plane1 = Plane(name='VietNam Airlines')
        # plane2 = Plane(name='Vietjet Air')
        # plane3 = Plane(name='Jetstar Pacific')
        # plane4 = Plane(name='Bamboo Airways')
        # plane5 = Plane(name='Japan Airlines')
        # db.session.add_all([plane1, plane2, plane3, plane4, plane5])
        # db.session.commit()

        # airport1 = Airport(name='Nội Bài')
        # airport2 = Airport(name='Tân Sơn Nhất')
        # airport3 = Airport(name='Cần Thơ')
        # airport4 = Airport(name='Đà Nẵng')
        # airport5 = Airport(name='Cà Mau')
        # airport6 = Airport(name='Phú Quốc')
        # airport7 = Airport(name='Điện Biên Phủ')
        # airport8 = Airport(name='Thọ Xuân')
        # airport9 = Airport(name='Phú Bài')
        # airport10 = Airport(name='Pleiku')
        # airport11 = Airport(name='Rạch Giá')
        # airport12 = Airport(name='Buôn Ma Thuột')
        # airport13 = Airport(name='Liên Khương')
        # airport14 = Airport(name='Côn Đảo')
        # airport15 = Airport(name='TP Vinh')
        #
        # db.session.add_all([airport1, airport2, airport3, airport4, airport5, airport6, airport7, airport8, airport9 , airport10,
        #                     airport11, airport12, airport13, airport14,airport15])
        # db.session.commit()

        # route1 = Route(name='Hà Nội - TP HCM',take_off_airport_id = "1", landing_airport_id = "2")
        # route2 = Route(name='Cần Thơ - TP HCM',take_off_airport_id = "3", landing_airport_id = "2")
        # route3= Route(name='Đà Nẵng - TP HCM',take_off_airport_id = "4", landing_airport_id = "2")
        # route4 = Route(name='Cà Mau - Phu Quoc',take_off_airport_id = "5", landing_airport_id = "6")
        # route5= Route(name='Cần Thơ - Hà Nội',take_off_airport_id = "3", landing_airport_id = "1")
        # route6 = Route(name='Phú Quốc - Thọ Xuân',take_off_airport_id = "6", landing_airport_id = "8")
        # route7 = Route(name='Điện Biên Phủ - Thọ Xuân',take_off_airport_id = "7", landing_airport_id = "8")
        # route8 = Route(name='Thọ Xuân - Cần Thơ',take_off_airport_id = "8", landing_airport_id = "3")
        # route9 = Route(name='Hà Nội - Phú Bài',take_off_airport_id = "1", landing_airport_id = "9")
        # route10 = Route(name='Thọ Xuân - TP HCM',take_off_airport_id = "8", landing_airport_id = "2")
        # route11 = Route(name='Rạch Giá - Cần Thơ',take_off_airport_id = "11", landing_airport_id = "3")
        # route12 = Route(name='Buôn Ma Thuột - TP HCM',take_off_airport_id = "12", landing_airport_id = "2")
        # route13 = Route(name='Rạch Giá - Liên Khương',take_off_airport_id = "11", landing_airport_id = "13")
        # route14 = Route(name='Côn Đảo - Phú Quốc',take_off_airport_id = "14", landing_airport_id = "6")
        # route15 = Route(name='TP Vinh - Thọ Xuân',take_off_airport_id = "15", landing_airport_id = "8")
        # route16 = Route(name='Liên Khương - Cần Thơ',take_off_airport_id = "13", landing_airport_id = "3")
        # db.session.add_all([route1, route2, route3, route4, route5,
        #                     route6, route7, route8, route9,route10,
        #                     route11, route12, route13,route14,route15,
        #                     route16])
        # db.session.commit()

        # # num_of_airport = Column(Integer, nullable=False)
        #     # minimum_duration = Column(Integer, nullable=False)
        #     # num_of_intermediate_airport = Column(Integer, nullable=False)
        #     # max_stoptime = Column(Float, nullable=False)
        #     # min_stoptime = Column(Float, nullable=False)
        #     # num_of_seats_1st_class = Column(Integer, nullable=False)
        #     # num_of_seats_2st_class = Column(Integer, nullable=False)
        #     # price_of_seats_1st_class = Column(Float, nullable=False)
        rule1 = Rule(name='num_of_1st_class_seat',value=10)
        rule2 = Rule(name='num_of_2st_class_seat',value=10)
        # db.session.add_all([rule1,rule2])
        # db.session.commit()
        # flight1 = Flight(name='VN001', take_of_time =datetime(2024, 5, 9, 11, 00, 00 ),
        #                  landing_time =datetime(2024, 5, 12, 12, 00, 00 ),num_of_1st_seat = rule1.value,
        #                  num_of_2st_seat= rule2.value, plane_id='1', route_id='1')
        # flight2 = Flight(name='VN002', take_of_time=datetime(2024, 6, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 6, 10, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='2', route_id='1')
        # flight3 = Flight(name='VN003', take_of_time=datetime(2024, 10, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 10, 13, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='4', route_id='1')
        # flight4 = Flight(name='VN004', take_of_time=datetime(2024,8, 1, 11, 00, 00),
        #                  landing_time=datetime(2024, 8, 4, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='2', route_id='2')
        # flight5 = Flight(name='VN005', take_of_time=datetime(2024, 10, 12, 11, 00, 00),
        #                  landing_time=datetime(2024, 10, 13, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='1', route_id='2')
        # flight6 = Flight(name='VN006', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='1', route_id='3')
        # flight7 = Flight(name='VN007', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='2', route_id='4')
        # flight8 = Flight(name='VN008', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='5', route_id='4')
        # flight9 = Flight(name='VN009', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='3', route_id='5')
        # flight10 = Flight(name='VN010', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='3', route_id='6')
        # flight11 = Flight(name='VN011', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='1', route_id='7')
        # flight12 = Flight(name='VN012', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='2', route_id='7')
        # flight13 = Flight(name='VN013', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='4', route_id='8')
        # flight14 = Flight(name='VN014', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                  landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                  num_of_2st_seat=rule2.value, plane_id='4', route_id='9')
        # flight15 = Flight(name='VN015', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='3', route_id='9')
        # flight16 = Flight(name='VN016', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='2', route_id='9')
        # flight17 = Flight(name='VN017', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='1', route_id='10')
        # flight18 = Flight(name='VN018', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='4', route_id='10')
        # flight19 = Flight(name='VN019', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='3', route_id='11')
        # flight20 = Flight(name='VN020', take_of_time=datetime(2024, 5, 9, 11, 00, 00),
        #                   landing_time=datetime(2024, 5, 9, 11, 00, 00), num_of_1st_seat=rule1.value,
        #                   num_of_2st_seat=rule2.value, plane_id='4', route_id='12')
        #
        # db.session.add_all([flight1,flight2, flight3, flight4, flight5,
        #                     flight6, flight7, flight8, flight9, flight10,
        #                     flight11,flight12,flight13,flight14,flight15,
        #                     flight16,flight17,flight18,flight19,flight20])
        # db.session.commit()

        rule3 = Rule(name='thời gian dừng tối thiểu',value = '20')
        # db.session.add(rule3)
        # db.session.commit()

        # mid_airport1 = MidAirport(stop_time = rule3.value,note= 'Dừng x giờ',mid_airport_id = '5', flight_id = '1')
        # mid_airport2 = MidAirport(stop_time=rule3.value,note='Dừng x giờ', mid_airport_id='6', flight_id='2')
        # db.session.add_all([mid_airport1,mid_airport2])
        # db.session.commit()

        # flight_schedule1=  FlightSchedule(staff_id = '1' ,flight_id = '2')
        # flight_schedule2 = FlightSchedule(staff_id='1', flight_id='3')
        # flight_schedule3 = FlightSchedule(staff_id='1', flight_id='4')
        # flight_schedule4 = FlightSchedule(staff_id='1', flight_id='5')
        # flight_schedule5 = FlightSchedule(staff_id='1', flight_id='6')
        # db.session.add_all([flight_schedule1,flight_schedule2,flight_schedule3,flight_schedule4,flight_schedule5])
        # db.session.commit()

        rule4 = Rule(name='1st_seat_price',value=1500000)
        rule5 = Rule(name='2st_seat_price',value=1000000)
        # db.session.add_all([rule4,rule5])
        # db.session.commit()

        # fareclass1 = FareClass(name='Ghế Hạng 1',price=rule4.value)
        # fareclass2 = FareClass(name='Ghế Hạng 2',price=rule5.value)
        # db.session.add_all([fareclass1,fareclass2])
        # db.session.commit()
        #
        # TRUE = BOOKED, FALSE = EMPTY
        # BOOKED SEAT
        # seat1 = Seat(name='Seat001',status=True,plane_id='1')
        # seat2 = Seat(name='Seat002',status=True,plane_id='2')
        # seat3 = Seat(name='Seat003',status=True,plane_id='3')
        # seat4 = Seat(name='Seat004',status=True,plane_id='1')
        # seat5 = Seat(name='Seat005',status=True,plane_id='2')
        # seat6 = Seat(name='Seat006',status=True,plane_id='3')
        # seat7 = Seat(name='Seat007',status=True,plane_id='1')
        # seat8 = Seat(name='Seat008',status=True,plane_id='2')
        # seat9 = Seat(name='Seat008',status=True,plane_id='3')
        # seat10 = Seat(name='Seat010',status=True,plane_id='1')
        # seat11 = Seat(name='Seat011',status=True,plane_id='2')
        # seat12 = Seat(name='Seat012',status=True,plane_id='3')
        # seat13 = Seat(name='Seat013',status=True,plane_id='1')
        # seat14 = Seat(name='Seat014',status=True,plane_id='2')
        # seat15= Seat(name='Seat015',status=True,plane_id='3')
        # #EMPTY SEAT
        # seat16 = Seat(name='Seat016', status=False, plane_id='1')
        # seat17 = Seat(name='Seat017', status=False, plane_id='2')
        # seat18 = Seat(name='Seat018', status=False, plane_id='3')
        # seat19 = Seat(name='Seat019', status=False, plane_id='1')
        # seat20 = Seat(name='Seat020', status=False, plane_id='2')
        # seat21 = Seat(name='Seat021', status=False, plane_id='3')
        # seat22 = Seat(name='Seat022', status=False, plane_id='1')
        # seat23 = Seat(name='Seat023', status=False, plane_id='2')
        # seat24 = Seat(name='Seat024', status=False, plane_id='3')
        # seat25 = Seat(name='Seat025', status=False, plane_id='1')
        # seat26 = Seat(name='Seat026', status=False, plane_id='2')
        # seat27 = Seat(name='Seat027', status=False, plane_id='3')
        # seat28 = Seat(name='Seat028', status=False, plane_id='1')
        # seat29 = Seat(name='Seat029', status=False, plane_id='2')
        # seat30 = Seat(name='Seat030', status=False, plane_id='3')
        # db.session.add_all([seat1,seat2,seat3,seat4,seat5,
        #                     seat6,seat7,seat8,seat9,seat10,
        #                     seat11,seat12,seat13,seat14,seat15,
        #                     seat16,seat17,seat18,seat19,seat20,
        #                     seat21,seat22,seat23,seat24,seat25,
        #                     seat26,seat27,seat28,seat29,seat30])
        # db.session.commit()

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

