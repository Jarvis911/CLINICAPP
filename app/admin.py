from app.models import Thuoc, LoaiThuoc, User, UserRole, QuyDinh, DonViThuoc
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, request
from datetime import datetime

admin = Admin(app=app, name='CLINIC Admin', template_mode='bootstrap4')

class MyAdminIndexView(AdminIndexView):
    @expose("/", methods=['GET', 'POST'])
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

class ViewQuyDinh(AdminView):
    column_list = ['id', 'examineFee', 'numOfMed', 'maxPatient']
    can_export = True
    page_size = 10
    column_editable_list = ['examineFee', 'numOfMed', 'maxPatient']

class ViewDonViThuoc(AdminView):
    column_list = ['id', 'name', 'note']
    can_export = True
    column_searchable_list = ['name']
    page_size = 10
    column_filters = ['id', 'name', 'note']
    column_editable_list = ['name', 'note']


class StatsView(AuthenticatedView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        # Lấy tháng từ request, mặc định là tháng hiện tại
        month = request.args.get('month', default=datetime.now().month, type=int)
        year = datetime.now().year  # Lấy năm hiện tại

        # Thực hiện thống kê doanh thu và số bệnh nhân theo ngày trong tháng
        stats2, total_revenue = dao.revenue_stats_by_time(month, year)
        stats3 = dao.medicine_statistics(month, year)

        return self.render('admin/statistic.html', stats2=stats2, month=month, total_revenue=total_revenue, stats3=stats3)

admin.add_view(LoaiThuocView(LoaiThuoc, db.session))
admin.add_view(ThuocView(Thuoc, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(StatsView(name = 'Thống kê'))
admin.add_view(ViewQuyDinh(QuyDinh, db.session))
admin.add_view(ViewDonViThuoc(DonViThuoc, db.session))
admin.add_view(LogoutView(name = 'Đăng xuất'))