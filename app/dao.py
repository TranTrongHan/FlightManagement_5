import hmac
import urllib
from datetime import datetime
from flask_login import login_user, current_user
from app import db
from app.models import Flight, Route, Airport, Customer, User, UserRoleEnum, FareClass, Plane, Seat, Ticket, \
    Comment,Rule
import hashlib
import cloudinary.uploader
def load_route(route_id = None):
    query = Route.query
    if route_id:
        query = query.filter(Route.id  == route_id)
    return query.all()

def load_specific_routes(takeoffId = None, landingairportId=None):
    route = None
    if int(takeoffId) == int(landingairportId):
        return route
    elif takeoffId != landingairportId:
        route =  Route.query.filter(Route.take_off_airport_id == takeoffId,
                                     Route.landing_airport_id == landingairportId).first()
        return route
def load_airport_id(airportrole =None):
    if(airportrole):
        query = Route.query.order_by('name').filter(Route.take_off_airport_id)
    else:
        query = Route.query.order_by('name').filter(Route.landing_airport_id)
    return query.all()

def load_seats(flightid=None,fareclassid=None):
    seat = Seat.query
    if flightid:
        seat = seat.filter(Seat.flight_id == flightid)
    if flightid and fareclassid:
        seat = seat.filter(Seat.flight_id == flightid,Seat.fareclass_id == fareclassid)
    return seat.all()
def get_rule_by_id(id):
    return Rule.query.get(id)
def load_airport():
    return Airport.query.all()
def get_tickets(userid = None):
    tickets = Ticket.query
    if userid:
        tickets = tickets.filter(Ticket.customer_id == userid)
    return tickets.all()
# hàm chuyển chuỗi thành kiểu dữ liệu datetime
def convert_to_datetime(date_input):
    if isinstance(date_input, str):  # Nếu là chuỗi
        try:
            return datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError as e:
            # Nếu không thể chuyển đổi chuỗi, xử lý lỗi ở đây
            print(f"Error converting date: {e}")
            return None
    elif isinstance(date_input, datetime):  # Nếu đã là đối tượng datetime
        return date_input
    else:
        print("Invalid input type. Expected string or datetime.")
        return None

def load_flights(flight_id=None,depart_time=None,route_id=None,flight_id_of_ticket=None):
    if flight_id:
        query = Flight.query.filter(Flight.id == flight_id).all()
        return query
    if depart_time and route_id:
        # depart_time = datetime.strptime(depart_time, '%Y-%m-%d')
        # return_time = datetime.strptime(return_time, '%Y-%m-%d')
        flights = Flight.query.filter(Flight.take_off_time >= depart_time,Flight.route_id==route_id).all()
        return flights
    if flight_id_of_ticket:
        flights = Flight.query.filter(Flight.id== flight_id_of_ticket)
    return Flight.query.all()


def load_fareclass():
    return FareClass.query.all()
def load_plane():
    return Plane.query.all()
def load_empty_seat_by_plane(planeid):
    return Seat.query.filter(Seat.plane_id == planeid,Seat.status==0)
def auth_user(username,password,role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username),User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))
    return u.first()
def check_role(username , password,role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u =  User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()
    if u.__getattribute__('user_role') == role:
        return True
    return False

def add_user(name, phone,card_id, address,email ,avatar ,username,password ):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    name = name.strip()
    phone = phone.strip()
    card_id = card_id.strip()
    address = address.strip()
    email = email.strip()
    username = username.strip()
    password = password.strip()

    u = Customer(name=name,phone = phone,card_id = card_id,address = address , email=email,
             avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg',
             user_role = UserRoleEnum.CUSTOMER,joined_date =datetime.now(),
             username = username,password = password)
    if avatar:
        res =cloudinary.uploader.upload(avatar)
        u.avatar = res.get ('secure_url')
    db.session.add(u)
    db.session.commit()

def edit_user(name = None,phone=None,card_id =None,address=None,email = None,avatar = None,passwd = None,user_id=None):
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found.")
    if name:
        user.name=name.strip()
    if phone:
        user.phone = phone.strip()
    if card_id:
        user.card_id = card_id.strip()
    if address:
        user.address = address.strip()
    if email:
        user.email = email.strip()
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        user.avatar = res.get ('secure_url').strip()
    if passwd:
        user.password=str(hashlib.md5(passwd.strip().encode('utf-8')).hexdigest())

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
def check_booked_ticket(flightid):
    return Ticket.query.filter(Ticket.flight_id == flightid)
def existence_check(attribute ,value):
    return User.query.filter(getattr(User, attribute).__eq__(value)).first()

def get_user_by_id(id):
    return User.query.get(id)
def get_customer_by_id(id):
    return Customer.query.filter(Customer.user_id==id).first()
def get_route_by_id(id):
    return Route.query.get(id)
def get_flight_by_id(id):
    return Flight.query.get(id)
def get_plane_by_id(id):
    return Plane.query.get(id)
def get_ticket_by_seat(id):
    return Ticket.query.filter(Ticket.seat_id==id).first()
def count_seat(planeid):
    return Seat.query.filter(Seat.plane_id == planeid,Seat.status==0).count()
def get_fareclass_by_name(name):
    return FareClass.query.get(name)
def get_fareclass_by_id(id):
    return FareClass.query.get(id)
def get_seat_by_id(id):
    return Seat.query.get(id)

def get_name_by_id(model, id):
    instance = model.query.filter(model.id == id).first()  # Lấy đối tượng theo id
    if instance:
        return instance.name  # Trả về tên nếu tìm thấy
    return None  # Trả về None nếu không tìm thấy
def get_price(id):
    fareclass = FareClass.query.filter(FareClass.id==id).first()
    if fareclass:
        return fareclass.price
    return '0'
def load_users():
    return User.query.all()
def load_comments():
    return Comment.query.all()

def save_comment(content):
    user_id = current_user.id if current_user.is_authenticated else None

    if user_id and not User.query.get(user_id):
        raise ValueError("Khách hàng không hợp lệ")

    new_comment = Comment(
        user=user_id,
        text=content,
        time=datetime.now()
    )
    db.session.add(new_comment)
    db.session.commit()
    return new_comment
class vnpay:
    requestData = {}
    responseData = {}
    def get_payment_url(self, vnpay_payment_url, secret_key):
        # Dữ liệu thanh toán được sắp xếp dưới dạng danh sách các cặp khóa-giá trị theo thứ tự tăng dần của khóa.
        inputData = sorted(self.requestData.items())
        # Duyệt qua danh sách đã sắp xếp và tạo chuỗi query sử dụng urllib.parse.quote_plus để mã hóa giá trị
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        # Sử dụng phương thức __hmacsha512 để tạo mã hash từ chuỗi query và khóa bí mật
        hashValue = self.__hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        # Lấy giá trị của vnp_SecureHash từ self.responseData.
        vnp_SecureHash = self.responseData['vnp_SecureHash']
        # Loại bỏ các tham số liên quan đến mã hash
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')
        # Sắp xếp dữ liệu (inputData)
        inputData = sorted(self.responseData.items())

        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        # Tạo mã hash
        hashValue = self.__hmacsha512(secret_key, hasData)

        print(
            'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    # tạo mã hash dựa trên thuật toán HMAC-SHA-512
    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
