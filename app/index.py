from idlelib.rpc import request_queue

from flask import render_template,request
import dao
from app import app

@app.route('/', methods = ['GET','POST'])
def index():
    # lấy danh sách các tuyến bay có role theo yêu cầu
    routes_depart = dao.load_routesdetails('DEPARTURE')
    routes_arri = dao.load_routesdetails('ARRIVAL')
    # lấy danh sách sân bay
    airports = dao.load_airport()
    # kiểm tra một sân bay có nhiều tuyến bay

    # lấy giá trị value của thẻ option từ thuộc tính name của thẻ select
    depart_airport = request.form.get('departure')
    arrival_airport = request.form.get('arrival')
    # lấy danh sách chuyến bay có nơi đi, nơi đến theo yêu cầu
    flights = dao.find_flight(departure=depart_airport,arrival=arrival_airport)

    return render_template('index.html',routes_depart = routes_depart,routes_arri = routes_arri,airports = airports
    ,depart_airport = depart_airport  ,flights = flights,list = list)

if __name__ == '__main__':
    app.run(debug=True)