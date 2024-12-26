from calendar import month
from datetime import datetime

from app import app,db,utils,dao
from flask import redirect,request
from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Customer, Flight, Route, Rule, UserRoleEnum, Plane, Airport
from flask_login import current_user,logout_user
admin = Admin(app=app,name='FlightManagementApp',template_mode='bootstrap4')

class AuthenticatedView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        if current_user.user_role != UserRoleEnum.ADMIN:
            logout_user()
            return False
        return True

class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def __index__(self):
        logout_user()
        return redirect('/admin')

class FlightView(AuthenticatedView):
    column_list = ['id','name','take_of_time','route_id','plane_id']
    page_size = '10'

class RouteView(AuthenticatedView):
    column_list = ['id','name','flights','take_off_airport_id','landing_airport_id']
    page_size = '10'
class AiportView(AuthenticatedView):
    column_list = ['id','name','takeoff_airport','landing_airport']
class PlaneView(AuthenticatedView):
    column_list = ['id','name','flights']
class StatsView(AuthenticatedBaseView):
    @expose("/")
    def __index__(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        routes = dao.load_route()
        return self.render('admin/stats.html',
                           stats = utils.route_stats(kw=kw,from_date=from_date,to_date=to_date))

class FrequencyStats(AuthenticatedBaseView):
    @expose("/", methods=['GET', 'POST'])
    def __index__(self):
        year = request.args.get('year',default=datetime.now().year)
        month = request.args.get('month',default=datetime.now().month)



        return self.render('admin/frequencystats.html',year = year,
                           monthly_stats = utils.route_month_stats(year=year,month=month))


admin.add_view(FlightView(Flight,db.session))
admin.add_view(RouteView(Route,db.session))
admin.add_view(AiportView(Airport,db.session))
admin.add_view(PlaneView(Plane,db.session))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(FrequencyStats(name='Thống kê tần suất'))
admin.add_view(LogoutView(name="Đăng xuất"))



