from idlelib.rpc import request_queue
import re
from flask import render_template, request,redirect
import dao
from app import app,login
from flask_login import login_user,logout_user

@app.route('/', methods=['GET', 'POST'])
def index():
    # lấy danh sách id sân bay đi
    airports = dao.load_airport_id('takeoffairport')
    # lấy danh sách id sân bay đến
    airports2 = dao.load_airport_id()
    # lấy danh sách id sân bay
    airportsID = dao.load_airport()




    takeoff_airport = request.form.get('takeoff')
    # kiểm tra có lấy được option không/ nếu không in ra yes
    landing_airport = request.form.get('landing')
    # lấy danh sách chuyến bay có nơi đi, nơi đến theo yêu cầu
    routes = dao.load_specific_routes(takeoffId=1, landingairportId=2)


    flights = dao.load_flights()

    return render_template('index.html', take_off_airports=airports, landing_airports=airports2, airports=airportsID,
                           routes=routes, flights=flights)

@app.route('/login', methods = ['get','post'])
def login_process():

    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username,password=password)
        if u:
            login_user(u)
            return redirect('/')

    return render_template('login.html')
@app.route('/logout')
def log_out_process():
    logout_user()
    return redirect('/login')

@app.route('/register',methods=['get','post'])
def register_process():
    regex_username = '^[a-zA-Z0-9]+$'
    error_message = {}
    if request.method.__eq__('POST'):
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
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

        if dao.existence_check('username',username):
            error_message['err_username'] = 'Tên đăng nhập đã được sử dụng.'

        if not re.fullmatch(regex_username, username):
            error_message['err_format'] = 'Tên đăng nhập không hợp lê. Vui lòng chỉ nhập số và kí tự.'

        if not password.__eq__(confirm):
            error_message['err_password'] = 'Mật khẩu xác nhận và mật khẩu không khớp'

        if error_message:
            return render_template('register.html',
                                   error_message = error_message,
                                   phone = phone,email = email,username = username)
        else:
            dao.add_user(last_name=lastname, first_name=firstname, phone=phone, address=address,
                         email=email, avatar=avatar, username=username, password=password)
            return redirect('/login')


    return render_template('register.html')

@login.user_loader
def load_user(user_id):
 return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    app.run(debug=True)
