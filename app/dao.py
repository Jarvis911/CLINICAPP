from app.models import User, BenhNhan, Thuoc, PhieuKham, DonThuoc
from datetime import datetime
from app import app, db
import hashlib
import cloudinary.uploader
from flask_login import current_user


def get_user_by_id(id):
    return User.query.get(id)


def load_patients(kw=None):
    query = BenhNhan.query

    if kw:
        query = query.filter(BenhNhan.name.contains(kw))

    return query.all()


def load_medicines(kw=None):
    query = Thuoc.query

    if kw:
        query = query.filter(Thuoc.name.contains(kw))

    return query.all()


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))
    return u.first()


def add_phieukham(phone, datetime, trieu_chung, du_doan_benh, cart):
        # Tìm bệnh nhân theo số điện thoại
        patient = BenhNhan.query.filter(BenhNhan.phone.__eq__(phone)).first()
        if not patient:
            return {"message": "Bệnh nhân không tồn tại trong hệ thống."}, 404

        # Lấy thông tin bác sĩ từ current_user (Flask-Login)
        bac_si_id = current_user.id  # Bác sĩ hiện tại

        # Tạo mới phiếu khám
        new_phieu_kham = PhieuKham(
            bac_si_id=bac_si_id,
            id_benh_nhan=patient.id,
            date_kham=datetime,
            trieu_chung=trieu_chung,
            du_doan_benh=du_doan_benh
        )

        db.session.add(new_phieu_kham)
        db.session.commit()

        # Thêm đơn thuốc nếu có
        for d in cart.values():
            thuoc = Thuoc.query.filter(Thuoc.id == d['id']).first()
            if thuoc:
                don_thuoc = DonThuoc(
                    phieu_kham_id=new_phieu_kham.id,
                    thuoc_id=thuoc.id,
                    quantity=d['quantity'],
                    cach_dung=d['cach_dung']
                )
                db.session.add(don_thuoc)

        db.session.commit()

        return {"message": "Phiếu khám và đơn thuốc đã được thêm thành công!"}, 201



