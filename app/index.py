import re
from flask import render_template, request, redirect, jsonify, session
from sqlalchemy.sql.functions import current_user
import dao, utils
from app import app, login
from flask_login import login_user, logout_user, login_required
from app.models import UserRoleEnum, Flight, Customer, FareClass, Plane, User


@app.route('/', methods=['get', 'post'])
def index():
    # lấy danh sách id sân bay đi
    airports = dao.load_airport_id('takeoffairport')
    # lấy danh sách id sân bay đến
    airports2 = dao.load_airport_id()
    # lấy danh sách id sân bay
    airportsID = dao.load_airport()

    if request.method.__eq__('POST'):
        takeoff_airport = request.form.get('takeoff')
        landing_airport = request.form.get('landing')
        # lấy danh sách chuyến bay có nơi đi, nơi đến theo yêu cầu
        routes = dao.load_specific_routes(takeoffId=takeoff_airport, landingairportId=landing_airport)
        flights = dao.load_flights()
        return render_template('index.html', take_off_airports=airports, landing_airports=airports2,
                               airports=airportsID, routes=routes, flights=flights)

    return render_template('index.html', take_off_airports=airports,
                           landing_airports=airports2, airports=airportsID)


@app.route('/login', methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            role_check = dao.check_role(username=username, password=password, role=UserRoleEnum.CUSTOMER)
            if role_check:
                login_user(u)
                return redirect('/')
            elif not role_check:
                return redirect('/role_alert')
        elif not u:
            return redirect('/user_alert')

    return render_template('login.html')


@app.route('/login_staff', methods=['get', 'post'])
def login_staff():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username=username, password=password)
        if u:
            role_check = dao.check_role(username=username, password=password, role=UserRoleEnum.STAFF)
            if role_check:
                login_user(u)
                return redirect('/staffpage')
            elif not role_check:
                return redirect('/role_alert')
        elif not u:
            return redirect('/user_alert')

    return render_template('login_staff.html')


@app.route('/login_admin', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserRoleEnum.ADMIN)
    if u:
        login_user(u)
    elif not u:
        return redirect('/user_alert')

    return redirect('/admin')


@app.route('/user_alert')
def user_alert():
    return render_template('layout/user_alert.html')


@app.route('/role_alert')
def role_alert():
    return render_template('layout/user_role_alert.html')


@app.route('/staffpage')
def staff_page():
    return render_template('staffpage.html')


@app.route('/logout')
def log_out_process():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['get', 'post'])
def register_process():
    regex_username = '^[a-zA-Z0-9]+$'
    error_message = {}
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        avatar = request.form.get('avatar')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if len(phone) < 7 or len(phone) > 15:
            error_message['err_phone'] = 'Phone number must be between 7-15 digits.'
        elif dao.existence_check('phone', phone):
            error_message['err_phone'] = 'Số điện thoại đã được sử dụng.'

        if '@' not in email:
            error_message['err_email'] = 'Email is invalid.'
        elif dao.existence_check('email', email):
            error_message['err_email'] = 'Email is đã được sử dụng.'

        if dao.existence_check('username', username):
            error_message['err_username'] = 'Tên đăng nhập đã được sử dụng.'

        if not re.fullmatch(regex_username, username):
            error_message['err_format'] = 'Tên đăng nhập không hợp lê. Vui lòng chỉ nhập số và kí tự.'

        if not password.__eq__(confirm):
            error_message['err_password'] = 'Mật khẩu xác nhận và mật khẩu không khớp'

        if error_message:
            return render_template('register.html',
                                   error_message=error_message,
                                   phone=phone, email=email, username=username)
        else:
            dao.add_user(name=name, phone=phone, address=address,
                         email=email, avatar=avatar, username=username, password=password)
            return redirect('/login')

    return render_template('register.html')


@app.route('/myinfo', methods = ['GET', 'POST'])
def my_info():


    if request.method.__eq__('POST'):
        error_message = {}
        user_id = request.form.get('userid')
        name = request.form.get('fullname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        avatar = request.form.get('avatar')
        passwd = request.form.get('passwd')
        passwd2 = request.form.get('passwd2')
        if len(phone) < 7 or len(phone) > 15:
            error_message['err_phone'] = 'Phone number must be between 7-15 digits.'
        elif dao.existence_check('phone', phone):
            error_message['err_phone'] = 'Số điện thoại đã được sử dụng.'
        if '@' not in email:
            error_message['err_email'] = 'Email is invalid.'
        elif dao.existence_check('email', email):
            error_message['err_email'] = 'Email is đã được sử dụng.'

        if not passwd.__eq__(passwd2):
            error_message['err_password'] = 'Mật khẩu xác nhận và mật khẩu không khớp'

        if error_message:
            return render_template('user_page.html',
                                   error_message=error_message,
                                   phone=phone, email=email)
        else:
            dao.edit_user(name=name, phone=phone, address=address, email=email, passwd=passwd,user_id= user_id)
            return redirect('/myinfo')

    return render_template('user_page.html')
@app.route('/my_booked_tickets')
def my_tickets():
    user_id = request.args.get('user_id')
    tickets = dao.load_tickets(userid=user_id)
    seats = dao.load_seats()
    flights = dao.load_flights()
    routes  = dao.load_route()
    fareclass = dao.load_fareclass()
    return render_template('bookedtickets.html',tickets = tickets,seats=seats,flights=flights,routes=routes,fareclass=fareclass)
@app.route('/bookticket', methods=['GET', 'POST'])
@login_required
def bookticket():
    # lấy danh sách id sân bay đi
    airports = dao.load_airport_id('takeoffairport')
    # lấy danh sách id sân bay đến
    airports2 = dao.load_airport_id()
    # lấy danh sách id sân bay
    airportsID = dao.load_airport()
    fareclass = dao.load_fareclass()

    if request.method.__eq__('POST'):
        takeoff_airport1 = request.form.get('takeoff1')
        landing_airport1 = request.form.get('landing1')
        departure_time = request.form.get('departureTime')
        return_time = request.form.get('returnTime')

        # lấy danh sách chuyến bay có nơi đi, nơi đến theo yêu cầu
        routes = dao.load_specific_routes(takeoffId=takeoff_airport1, landingairportId=landing_airport1)

        if utils.check_valid_date(depart_time=departure_time, return_time=return_time):
            flights = dao.load_flights(depart_time=departure_time, return_time=return_time)
            planes = dao.load_plane()
            return render_template('bookticket.html', take_off_airports=airports, landing_airports=airports2,
                                   airports=airportsID, routes=routes, flights=flights, planes=planes,
                                   fareclass=fareclass)
        else:
            return redirect('/invalid_date')

    return render_template('bookticket.html', take_off_airports=airports, landing_airports=airports2,
                           airports=airportsID, fareclass=fareclass)


@app.route('/invalid_date')
def invalid_date_form():
    return render_template('layout/invalid_date.html')


@app.route('/bookticket_process', methods=['GET', 'POST'])
@login_required
def bookticket_process():
    flight_id = request.args.get('flight')
    plane_id = request.args.get('plane')
    route_id = request.args.get('route')

    # lấy thời gian của chuyến bay đang đặt vé
    takeoff_time = request.args.get('takeoff_time')
    landing_time = request.args.get('landing_time')
    flight = dao.get_flight_by_id(id=flight_id)
    route = dao.load_route(route_id=route_id)
    plane = dao.get_plane_by_id(id=plane_id)

    airports = dao.load_airport()
    fareclass = dao.load_fareclass()

    check_used_to_bookticket = utils.check_used_to_bookticket(flightid=flight_id)
    has_ticket = utils.check_unvalid_ticket(takeofftime=takeoff_time,landingtime=landing_time,flightid=flight_id)

    return render_template('bookticket_process.html',
                               route=route, airports=airports, flight=flight, fareclass=fareclass, plane=plane)



@app.route('/bookticket_error')
def error_alert():
    return render_template('layout/bookticket_error_alert.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/payment', methods=['GET', 'POST'])
def payment_comfirm_page():
    flight_id = request.form.get('flightid')
    customer_id = request.form.get('customerid')
    fareclass_id = request.form.get('fareclassid')
    quantity = int(request.form.get('ticket-quantity'))
    plane_id = request.form.get('plane')

    fareclass_price = dao.get_price(id=fareclass_id)
    fareclass_name = dao.get_name_by_id(model=FareClass, id=fareclass_id)
    customer_name = dao.get_name_by_id(User, id=customer_id)
    plane_name = dao.get_name_by_id(Plane, id=plane_id)

    flight = Flight(id=flight_id)
    customer = Customer(user_id=customer_id)
    fareclass = FareClass(id=fareclass_id)

    ticket_info = {
        "flightid": flight.to_dict(),
        "customerid": customer.to_dict(),
        "fareclassid": fareclass.to_dict(),
        "quantity": quantity,
    }
    session['ticket_info'] = ticket_info
    seats = utils.get_seat_by_quantity(quantity=quantity, flightid=flight_id)
    if seats:
        return render_template('payment.html', seats=seats, quantity=quantity, price=fareclass_price,
                               cus_name=customer_name,
                               fareclass_name=fareclass_name, plane_name=plane_name)

    return render_template('payment.html')


@app.route('/test')
def test():
    selected_seats = utils.create_ticket(session.get('ticket_info'))
    if selected_seats:
        return render_template("/layout/test.html", selected_seats=selected_seats)
    return render_template("/layout/test.html")


@app.route('/api/payment', methods=['POST'])
@login_required
def payment():
    try:
        utils.add_ticket(session.get('ticket_info'))
        del session['ticket_info']
    except:
        return jsonify({'code': 400, 'redirect_url': '/bookticket'})

    return jsonify({'code': 200, 'redirect_url': '/bookticket'})


@app.route('/api/create_ticket_info', methods=['POST'])
def create_ticket():
    flight_id = ''
    customer_id = ''
    fareclass_id = ''
    quantity = ''
    plane_id = ''

    # import pdb
    # pdb.set_trace()
    ticket_info = {
        "flightid": flight_id,
        "customerid": customer_id,
        "fareclassid": fareclass_id,
        "quantity": quantity,
        "planeid": plane_id
    }
    session['ticket_info'] = ticket_info

    return jsonify()


if __name__ == '__main__':
    from app import admin

    app.run(debug=True)
