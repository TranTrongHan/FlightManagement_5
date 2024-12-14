from datetime import datetime

from app import app,db,utils
from flask import redirect,request
from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Customer, Flight, Route, Rule, UserRoleEnum, Plane, Airport
from flask_login import current_user,logout_user
admin = Admin(app=app,name='FlightManagementApp',template_mode='bootstrap4')

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRoleEnum.ADMIN)

class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(AuthenticatedBaseView):
    @expose("/")
    def __index__(self):
        logout_user()
        return redirect('/admin')


class FlightView(AuthenticatedView):

    column_searchable_list = ['name']

class RouteView(AuthenticatedView):
    column_list = ['name','flights','take_off_airport_id','landing_airport_id']

class StatsView(AuthenticatedBaseView):
    @expose("/")
    def __index__(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year',datetime.now().year)
        return self.render('admin/stats.html',
                           stats = utils.route_stats(kw=kw,from_date=from_date,to_date=to_date),
                           months_stats = utils.route_month_stats(year=year))

admin.add_view(FlightView(Flight,db.session))
admin.add_view(RouteView(Route,db.session))
admin.add_view(AuthenticatedView(Rule,db.session))
admin.add_view(AuthenticatedView(User,db.session))
admin.add_view(AuthenticatedView(Plane,db.session))
admin.add_view(AuthenticatedView(Airport,db.session))
admin.add_view(LogoutView(name="Đăng xuất"))
admin.add_view(StatsView(name="Thống kê"))


