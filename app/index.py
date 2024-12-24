import re
from datetime import datetime, timedelta
from flask import render_template, request, redirect, jsonify, session, flash, url_for
from app import app, login, VNPAY_CONFIG,dao,utils
from flask_login import login_user, logout_user, login_required
from app.models import UserRoleEnum, Flight, Customer, FareClass, Plane, User, MidAirport, FlightSchedule, Route, \
    Airport, Staff
from app.utils import check_pending_flighttime
from dao import db

@app.route('/')
def index():
    cmts = dao.load_comments()
    users = dao.load_users()
    
    for u in users:
        for cmt in cmts:
            if cmt.user == u.id:
                print(f"text: '{cmt.text}' / cmt_user: {cmt.user}/ time:{cmt.time} /u_id:{u.id}")
            else:
                print('none')


    return render_template('index.html',cmts = cmts,users=users)

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
                # Lưu staff_id vào session
                staff = db.session.query(Staff).filter(Staff.user_id == u.id).first()
                if staff:
                    session['staff_id'] = staff.id  # Lưu staff_id vào session
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
    customer = dao.get_customer_by_id(id=user_id)
    tickets = dao.get_tickets(customerid=customer.__getattribute__('id'))
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


        flights = dao.load_flights(depart_time=departure_time)
        planes = dao.load_plane()
        return render_template('bookticket.html', take_off_airports=airports, landing_airports=airports2,
                               airports=airportsID, route=route, flights=flights, planes=planes,
                               fareclass=fareclass)


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
    first_seats_avail = utils.count_seat_of_flight(flightid=flight_id,fareclassid='1')
    second_seats_avail = utils.count_seat_of_flight(flightid=flight_id, fareclassid='2')


    return render_template('bookticket_process.html',
                               route=route, airports=airports, flight=flight, fareclass=fareclass, plane=plane,first_seats_avail= first_seats_avail,
                           second_seats_avail= second_seats_avail)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route('/payment', methods=['GET', 'POST'])
def payment_comfirm_page():
    flight_id = request.form.get('flightid')
    user_id = request.form.get('userid')
    cus_obj = dao.get_customer_by_id(id=user_id)

    fareclass_id = request.form.get('fareclassid')
    quantity = int(request.form.get('ticket-quantity'))
    plane_id = request.form.get('plane')
    first_seats_avail = int(request.form.get('first_seats_avail'))
    second_seats_avail = int(request.form.get('second_seats_avail'))

    fareclass_price = dao.get_price(id=fareclass_id)
    fareclass_name = dao.get_name_by_id(model=FareClass, id=fareclass_id)
    customer_name = dao.get_name_by_id(User, id=user_id)
    plane_name = dao.get_name_by_id(Plane, id=plane_id)

    flight = Flight(id=flight_id)
    customer = Customer(user_id=user_id)

    fareclass = FareClass(id=fareclass_id)
    valid_time = utils.check_valid_time(flightid=flight_id)
    if not valid_time:
        flash(message="Thời gian không hợp lệ.",category="Lỗi chọn thời gian")
        return redirect('/bookticket')
    if int(first_seats_avail==0) and int(second_seats_avail) == 0:
        flash(message="Không còn chỗ trống.Vui lòng đặt chuyến khác",category="Thông báo")
        return redirect('/bookticket')
    checkseat = utils.check_seat(flightid=flight_id,quantity=quantity,fareclassid=fareclass_id)
    if checkseat == False:
        seat_class_name = dao.get_name_by_id(model=FareClass,id=fareclass_id)
        flash(message=f"Không còn đủ chỗ trống cho {seat_class_name}.", category="Thông báo")
        return redirect('/bookticket')
    booked_ticket = utils.checkduplicate_ticket(flightid=flight_id, customer_id=cus_obj.id)
    if booked_ticket:
        flash(message="Bạn đã đặt vé cho chuyến bay này.",category="Thông báo")
        return redirect('/bookticket')
    booked_flightid = check_pending_flighttime(flightid=flight_id, customerid=cus_obj.id)
    if booked_flightid:
        session['flightid_booked'] = booked_flightid
        flash(message="Bạn đã có chuyến bay đang chờ.",category="Thông báo")
        return redirect('/bookticket')
    ticket_info = {
        'order_id': f"ticket-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "flightid": flight.to_dict(),
        "customerid": customer.to_dict(),
        "customername":customer_name,
        "fareclassid": fareclass.to_dict(),
        "quantity": quantity,
        "planeid":plane_id,
        "price":fareclass_price
    }
    session['ticket_info'] = ticket_info
    seats = utils.get_seat_by_quantity(quantity=quantity, flightid=flight_id,fareclassid=fareclass_id)
    return render_template('payment.html', quantity=quantity, price=fareclass_price,
                               cus_name=customer_name,seats=seats,
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



@app.route('/create_flight_schedule', methods=['GET', 'POST'])
def create_flight_schedule():
    err_msg = ""

    # Lấy danh sách tuyến bay từ cơ sở dữ liệu
    if request.method == 'POST':
        # Nhận dữ liệu từ form
        staff_id = session.get('staff_id')
        name = request.form.get('name')
        existing_flight = Flight.query.filter_by(name=name).first()

        if existing_flight:
            flash('Tên chuyến bay đã tồn tại trong cơ sở dữ liệu', 'error')
            return redirect(url_for('create_flight_schedule'))
        route_id = request.form['route']
        plane_id = request.form['plane']
        take_of_time = request.form['take_of_time']  # Thời gian cất cánh (datetime)
        flight_duration = float(request.form['flight_duration'])  # Thời gian bay (giờ)
        num_of_1st_seat = request.form['num_of_1st_seat']
        num_of_2st_seat = request.form['num_of_2st_seat']

        # Nhận thông tin sân bay trung gian, thời gian dừng và ghi chú
        transit_airport_1 = request.form.get('transit_airport_1')
        stopover_time_1 = request.form.get('stopover_time_1')
        note_transit_1 = request.form.get('note_transit_1')

        transit_airport_2 = request.form.get('transit_airport_2')
        stopover_time_2 = request.form.get('stopover_time_2')
        note_transit_2 = request.form.get('note_transit_2')
        take_off_airport = request.form.get('take_off_airport')
        landing_airport = request.form.get('landing_airport')
        try:
            # Chuyển đổi thời gian cất cánh từ chuỗi thành đối tượng datetime
            take_of_time = datetime.fromisoformat(take_of_time)

            # Tính toán thời gian hạ cánh
            landing_time = take_of_time + timedelta(hours=flight_duration)

            # Tạo đối tượng Flight và lưu vào cơ sở dữ liệu
            new_flight = Flight(
                name=name,
                take_of_time=take_of_time,
                landing_time=landing_time,
                route_id=route_id,
                plane_id = plane_id,
                first_seat_quantity = num_of_1st_seat,
                second_seat_quantity = num_of_2st_seat
            )

            db.session.add(new_flight)
            db.session.commit()

            # Thêm sân bay trung gian 1 vào bảng MidAirport nếu có
            if transit_airport_1 and stopover_time_1:
                mid_airport_1 = MidAirport(
                    stop_time=stopover_time_1,
                    note=note_transit_1,
                    flight_id=new_flight.id,
                    mid_airport_id=transit_airport_1
                )
                db.session.add(mid_airport_1)

            # Thêm sân bay trung gian 2 vào bảng MidAirport nếu có
            if transit_airport_2 and stopover_time_2:
                mid_airport_2 = MidAirport(
                    stop_time=stopover_time_2,
                    note=note_transit_2,
                    flight_id=new_flight.id,
                    mid_airport_id=transit_airport_2
                )
                db.session.add(mid_airport_2)

            # Lưu tất cả thay đổi vào cơ sở dữ liệu
            db.session.commit()


            # Tạo đối tượng FlightSchedule
            new_flight_schedule = FlightSchedule(
                staff_id=staff_id,
                flight_id=new_flight.id
            )

            db.session.add(new_flight_schedule)
            db.session.commit()

            flash('Lưu chuyến bay thành công', 'success')
        except Exception as e:
            db.session.rollback()  # Nếu có lỗi, rollback lại các thay đổi
            flash(f'Đã có lỗi xảy ra: {str(e)}', 'error')  # Hiển thị thông báo lỗi
    routes = Route.query.all()
    planes = Plane.query.all()
    airports = Airport.query.all()


    return render_template('create_flight_schedule.html', routes = routes, planes = planes, airports = airports)


@app.route('/get-airports-by-route/<int:route_id>', methods=['GET'])
def get_airports_by_route(route_id):
    route = Route.query.get(route_id)
    if not route:
        return jsonify({"error": "Route not found"}), 404

    # Lấy thông tin sân bay đi và sân bay đến từ ID trong Route
    take_off_airport = Airport.query.get(route.take_off_airport_id)
    landing_airport = Airport.query.get(route.landing_airport_id)

    return jsonify({
        "take_off_airport": {
            "id": take_off_airport.id,
            "name": take_off_airport.name
        },
        "landing_airport": {
            "id": landing_airport.id,
            "name": landing_airport.name
        }
    })


@app.context_processor
def inject_user_role_enum():
    return dict(UserRoleEnum=UserRoleEnum)

@app.route("/api/comments", methods=['POST'])
def add_comment():
    data = request.get_json()

    if not data or 'content' not in data or not data['content'].strip():
        return jsonify({"error": "Nội dung bình luận không hợp lệ"}), 400

    try:
        # Lưu bình luận vào database
        new_comment = dao.save_comment(content=data['content'].strip())

        # Lấy thông tin khách hàng (nếu có)
        user = User.query.get(new_comment.user) if new_comment.user else None
        # Trả về JSON để cập nhật giao diện
        return jsonify({
            "content": new_comment.text,
            "time": new_comment.time.isoformat(),
            # "fname": khach_hang.fname if khach_hang else None,
            # "lname": khach_hang.lname if khach_hang else None,
            "name": user.name if user else ''
        }), 201

    except Exception as e:
        app.logger.error(f"Lỗi khi thêm bình luận: {e}")
        return jsonify({"error": "Đã xảy ra lỗi từ phía server"}), 500
if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
