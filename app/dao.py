from app.models import (User, BenhNhan, Thuoc, PhieuKham, DonThuoc,
                        DonViThuoc, HoaDon, QuyDinh, ThuNgan)
from datetime import datetime
from app import app, db
import hashlib
import cloudinary.uploader
from flask_login import current_user


def get_user_by_id(id):
    return User.query.get(id)


def load_medicines_unit():
    units = DonViThuoc.query.all()  # Lấy tất cả các đơn vị thuốc
    return {unit.id: {"name": unit.name} for unit in units}


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
            du_doan_benh=du_doan_benh,
            da_xuat_hoa_don=False
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


def load_unpaid_phieukham():
    unpaid_phieukham = db.session.query(
        PhieuKham.id,
        PhieuKham.date_kham,
        BenhNhan.name.label('benh_nhan_name')
    ).join(BenhNhan, PhieuKham.id_benh_nhan == BenhNhan.id).filter(
        PhieuKham.da_xuat_hoa_don == False
    ).all()

    return unpaid_phieukham


def tao_hoa_don(phieu_kham_id):
    # Lấy phiếu khám từ ID
    phieu_kham = PhieuKham.query.get(phieu_kham_id)
    if not phieu_kham:
        raise ValueError("Phiếu khám không tồn tại.")

    #Kiểm tra xem hóa đơn được tạo chưa
    existing_hoa_don = HoaDon.query.filter_by(phieu_kham_id=phieu_kham.id).first()
    if existing_hoa_don:
        raise ValueError("Hóa đơn đã được tạo cho phiếu khám này.")

    # Lấy quy định hệ thống (mặc định chỉ có 1 dòng trong bảng QuyDinh)
    quy_dinh = QuyDinh.query.first()
    if not quy_dinh:
        raise ValueError("Không tìm thấy quy định hệ thống.")

    # Tính tổng tiền thuốc
    tong_tien_thuoc = 0
    for don_thuoc in phieu_kham.thuoc:  # Lặp qua các đơn thuốc của phiếu khám
        if don_thuoc.thuoc:  # Kiểm tra xem đơn thuốc có liên kết với thuốc không
            tong_tien_thuoc += don_thuoc.quantity * don_thuoc.thuoc.price  # Cộng dồn giá * số lượng

    # Tạo hóa đơn
    hoa_don = HoaDon(
        quy_dinh_id=quy_dinh.id,  # Liên kết với quy định hiện tại
        phieu_kham_id=phieu_kham.id,
        thu_ngan_id=current_user.id,  # ID người thu ngân là current user
        tong_tien=tong_tien_thuoc + quy_dinh.examineFee  # Tổng tiền = tiền thuốc + tiền khám
    )
    db.session.add(hoa_don)

    # Cập nhật trạng thái phiếu khám
    phieu_kham.da_xuat_hoa_don = True

    # Lưu vào DB
    db.session.commit()

    return hoa_don

def get_phieu_kham_id(phieu_kham_id):
    return PhieuKham.query.get(phieu_kham_id)

def get_tien_kham():
    quy_dinh = QuyDinh.query.first()
    tien_kham = quy_dinh.examineFee
    return tien_kham


def get_thu_ngan_name():
    thu_ngan = ThuNgan.query.get(current_user.id)
    return thu_ngan.name

def get_benh_nhan_name(phieu_kham_id):
    phieu_kham = PhieuKham.query.get(phieu_kham_id)
    benh_nhan = BenhNhan.query.get(phieu_kham.id_benh_nhan)

    return benh_nhan.name
def get_tong_tien_thuoc(phieu_kham_id):
    phieu_kham = PhieuKham.query.get(phieu_kham_id)
    quy_dinh = QuyDinh.query.first()
    tong_tien_thuoc = 0
    for don_thuoc in phieu_kham.thuoc:  # Lặp qua các đơn thuốc của phiếu khám
        if don_thuoc.thuoc:  # Kiểm tra xem đơn thuốc có liên kết với thuốc không
            tong_tien_thuoc += don_thuoc.quantity * don_thuoc.thuoc.price  # Cộng dồn giá * số lượng


    return tong_tien_thuoc + quy_dinh.examineFee
