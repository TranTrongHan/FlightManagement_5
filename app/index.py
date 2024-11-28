from idlelib.rpc import request_queue

from flask import render_template,request
import dao
from app import app

@app.route('/', methods = ['GET','POST'])
def index():


    # lấy danh sách id sân bay đi
    airports = dao.load_airport_id('takeoffairport')
    # lấy danh sách id sân bay đến
    airports2 = dao.load_airport_id()
    # lấy danh sách id sân bay
    airportsID = dao.load_airport()
    # lấy danh sách tuyến bay

    # lấy giá trị value của thẻ option từ thuộc tính name của thẻ select
    takeoff_airport = request.form.get('take_off')
    landing_airport = request.form.get('landing')

    # lấy danh sách chuyến bay có nơi đi, nơi đến theo yêu cầu
    routes = dao.load_specific_routes(takeoffId = takeoff_airport, landingairportId=landing_airport)
    flights = dao.load_flights()


    return render_template('index.html' ,take_off_airports = airports,landing_airports = airports2 ,airports = airportsID,routes = routes,flights = flights)


if __name__ == '__main__':
    app.run(debug=True)