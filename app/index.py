import re
from datetime import datetime
from zoneinfo import available_timezones

from flask import render_template, request, redirect, jsonify, session, flash, url_for
import dao, utils
from app import app, login, VNPAY_CONFIG,dao
from flask_login import login_user, logout_user, login_required
from app.models import UserRoleEnum, Flight, Customer, FareClass, Plane, User
from app.utils import check_pending_flighttime


@app.route('/')
def index():
    return render_template('index.html')

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
                flash(message="Người dùng không hợp lệ..", category="Thông báo")
                return redirect('/login')
        elif not u:
            flash(message="Tên đăng nhập hoặc mật khẩu không hợp lệ..", category="Lỗi đăng nhập")
            return redirect('/login')

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
                flash(message="Người dùng không hợp lệ.", category="Thông báo")
                return redirect('/login_staff')
        elif not u:
            flash(message="Tên đăng nhập hoặc mật khẩu không hợp lệ..", category="Thông báo")
            return redirect('/login_staff')

    return render_template('login_staff.html')


@app.route('/login_admin', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserRoleEnum.ADMIN)
    if u:
        login_user(u)
        return redirect('/admin')
    return redirect('/admin')


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
        route = dao.load_specific_routes(takeoffId=takeoff_airport1, landingairportId=landing_airport1)

        if utils.check_valid_date(depart_time=departure_time, return_time=return_time):
            flights = dao.load_flights(depart_time=departure_time)
            planes = dao.load_plane()
            return render_template('bookticket.html', take_off_airports=airports, landing_airports=airports2,
                                   airports=airportsID, route=route, flights=flights, planes=planes,
                                   fareclass=fareclass)
        else:
            flash(message="Thời gian về phải cách ít nhất 1 ngày",category="Thông báo")
            return redirect('/bookticket')

    return render_template('bookticket.html', take_off_airports=airports, landing_airports=airports2,
                           airports=airportsID, fareclass=fareclass)



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
    availseats = utils.count_seat_of_flight(flightid=flight_id)

    return render_template('bookticket_process.html',
                               route=route, airports=airports, flight=flight, fareclass=fareclass, plane=plane,availseats=availseats)



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
    avail_seats = int(request.form.get('availseats'))
    # takeofftime = request.form.get('takeofftime')
    # landingtime = request.form.get('landingtime')

    fareclass_price = dao.get_price(id=fareclass_id)
    fareclass_name = dao.get_name_by_id(model=FareClass, id=fareclass_id)
    customer_name = dao.get_name_by_id(User, id=customer_id)
    plane_name = dao.get_name_by_id(Plane, id=plane_id)

    flight = Flight(id=flight_id)
    customer = Customer(user_id=customer_id)
    fareclass = FareClass(id=fareclass_id)
    valid_time = utils.check_valid_time(flightid=flight_id)
    if not valid_time:
        flash(message="Thời gian không hợp lệ.",category="Lỗi chọn thời gian")
        return redirect('/bookticket')
    if int(avail_seats) == 0:
        flash(message="Không còn chỗ trống.Vui lòng đặt chuyến khác",category="Thông báo")
        return redirect('/bookticket')
    if int(quantity) > int(avail_seats):
        flash(message="Số lượng vé yêu cầu vượt quá số vé có sẵn.",category="Lỗi nhập vé")
        return redirect('/bookticket')
    booked_ticket = utils.checkduplicate_ticket(flightid=flight_id, customer_id=customer_id)
    if booked_ticket:
        flash(message="Bạn đã đặt vé cho chuyến bay này.",category="Thông báo")
        return redirect('/bookticket')
    booked_flightid = check_pending_flighttime(flightid=flight_id, customerid=customer_id)
    if booked_flightid:
        session['flightid_booked'] = booked_flightid
        flash(message="Bạn đã có chuyến bay đang chờ.",category="Thông báo")
        return redirect('/bookticket')
    ticket_info = {
        'order_id': f"ticket-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "flightid": flight.to_dict(),
        "customerid": customer.to_dict(),
        "customername":customer_name,
        "fareclassid": fareclass.to_dict(),
        "quantity": quantity,
        "planeid":plane_id,
        "price":fareclass_price
    }
    session['ticket_info'] = ticket_info
    seats = utils.get_seat_by_quantity(quantity=quantity, flightid=flight_id)
    return render_template('payment.html', seats=seats, quantity=quantity, price=fareclass_price,
                               cus_name=customer_name,
                               fareclass_name=fareclass_name, plane_name=plane_name)


@app.route('/payment_process',methods=['GET','POST'])
def paymentprocess():
    if request.method == 'POST':
        ticket_info = session.get('ticket_info')
        amount = ticket_info.get('quantity') * ticket_info.get('price')
        order_id = ticket_info.get('order_id')
        vnp = dao.vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = VNPAY_CONFIG['vnp_TmnCode']
        vnp.requestData['vnp_Amount'] = str(int(amount * 100))
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = order_id
        vnp.requestData['vnp_OrderInfo'] = 'Thanhtoan'  # Nội dung thanh toán
        vnp.requestData['vnp_OrderType'] = 'ticket'

        vnp.requestData['vnp_Locale'] = 'vn'

        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = "127.0.0.1"
        vnp.requestData['vnp_ReturnUrl'] = url_for('vnpay_return', _external=True)

        vnp_payment_url = vnp.get_payment_url(VNPAY_CONFIG['vnp_Url'], VNPAY_CONFIG['vnp_HashSecret'])

        print(vnp_payment_url)

        return redirect(vnp_payment_url)


@app.route('/vnpay_return')
def vnpay_return():
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')
    if vnp_ResponseCode == '00':
        utils.add_ticket(session.get('ticket_info'))
        utils.send_ticket_email(session.get('ticket_info'))
        del session['ticket_info']
        flash(message="Đặt vé thành công", category="Thông báo")
    return redirect('/')


@app.route('/api/checkavailseat', methods=['POST'])
@login_required
def checkavailseat():
    pass






if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
