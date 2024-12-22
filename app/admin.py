from app.models import Thuoc, LoaiThuoc, User, UserRole
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app=app, name='CLINIC Admin', template_mode='bootstrap4')


class LoaiThuocView(ModelView):
    column_list = ['tenLoaiThuoc', 'thuoc']


class ThuocView(ModelView):
    column_list = ['id','name']
    can_export = True
    column_searchable_list = ['name']
    page_size = 10
    column_filters = ['id', 'name','price']
    column_editable_list = ['name']


admin.add_view(LoaiThuocView(LoaiThuoc, db.session))
admin.add_view(ThuocView(Thuoc, db.session))
admin.add_view(ModelView(User, db.session))