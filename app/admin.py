from app.models import Thuoc, LoaiThuoc, User, UserRole
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app=app, name='CLINIC Admin', template_mode='bootstrap4')

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html', cates=dao.stats_products())


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class LoaiThuocView(AdminView):
    column_list = ['tenLoaiThuoc', 'thuoc']


class ThuocView(AdminView):
    column_list = ['id','name']
    can_export = True
    column_searchable_list = ['name']
    page_size = 10
    column_filters = ['id', 'name','price']
    column_editable_list = ['name']


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(AuthenticatedView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedView):
    @expose("/")
    def index(self):
        return self.render('admin/statistic.html', stats=dao.revenue_stats(), stats2=dao.period_stats())

admin.add_view(LoaiThuocView(LoaiThuoc, db.session))
admin.add_view(ThuocView(Thuoc, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(LogoutView(name = 'Đăng xuất'))
admin.add_view(StatsView(name = 'Thống kê'))