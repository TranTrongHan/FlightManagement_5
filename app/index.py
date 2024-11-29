from idlelib.rpc import request_queue

from flask import render_template, request
import dao
from app import app


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
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
