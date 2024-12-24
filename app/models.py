from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime
import hashlib

class UserRole(RoleEnum):
    ADMIN = 1
    YTa = 2
    BacSi = 3
    ThuNgan = 4
    USER = 5

class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    gender = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    email = Column(String(100), nullable=True)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg')
    user_role = Column(Enum(UserRole), default=UserRole.USER)


#Fix birthday -> Age
class BenhNhan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False, unique=True)
    email = Column(String(100), nullable=True)
    birth = Column(DateTime, nullable=True, default=None)

    phieu_khams = relationship('PhieuKham', backref='phieu_kham', lazy=True)



class ADMIN(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class BacSi(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    chungChi = Column(String(100), nullable=True)
    chuyenKhoa = Column(String(100), nullable=True)
    bangCap = Column(String(100), nullable=True)

    phieu_khams = relationship('PhieuKham', backref='phieu_khams', lazy=True)


class YTa(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    chungChi = Column(String(100), nullable=True)
    chuyenMon = Column(String(100), nullable=True)

    ds_kham = relationship('DsKham', backref='ds_kham', lazy=True)

class ThuNgan(User):
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    bangCap = Column(String(100), nullable=True)

    hoa_dons = relationship('HoaDon', backref='hoa_dons', lazy=True)


class QuyDinh(db.Model):
    __tablename__ = 'quy_dinh'
    id = Column(Integer, primary_key=True, autoincrement=True)
    examineFee = Column(Integer, nullable=False, default=100000, index=True)
    numOfMed = Column(Integer, nullable=False, default=30)
    maxPatient = Column(Integer, nullable=False, default=40)

    hoa_don = relationship('HoaDon', backref='hoa_don')



class LoaiThuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenLoaiThuoc = Column(String(100), nullable=False)
    thuoc = relationship('Thuoc', backref='loai_thuoc', lazy=True)
    def __str__(self):
        return self.tenLoaiThuoc


class DsKham(db.Model):
    __tablename__ ='ds_kham'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    y_ta_id = Column(Integer, ForeignKey(YTa.id), nullable=False)
    dangKyKhams = relationship("DangKyKham", backref="ds_kham")

class DangKyKham(db.Model):
    __tablename__ ='dang_ky_kham'
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_date = Column(DateTime, default=datetime.now())
    created_date = Column(DateTime)
    state = Column(Boolean, nullable=True)
    benhNhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    dsKham_id = Column(Integer, ForeignKey(DsKham.id), nullable=True)


class DonViThuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    note = Column(String(200), nullable=True)
    thuoc = relationship('Thuoc', backref='don_vi_thuoc', lazy=True)


class Thuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    unit_id = Column(Integer, ForeignKey(DonViThuoc.id), nullable=False)
    price = Column(Float, nullable=False)
    loai_thuoc_id = Column(Integer, ForeignKey(LoaiThuoc.id), nullable=False)
    thuoc = relationship("DonThuoc", backref="thuoc")
    def __str__(self):
        return self.name


class PhieuKham(db.Model):
    __tablename__ = 'phieu_kham'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_kham = Column(DateTime, nullable=True, default=datetime.now())
    trieu_chung = Column(String(200), nullable=True)
    du_doan_benh = Column(String(200), nullable=True)
    da_xuat_hoa_don = Column(Boolean, default=False)

    bac_si_id = Column(Integer, ForeignKey('bac_si.id'))
    id_benh_nhan = Column(Integer, ForeignKey('benh_nhan.id'))
    thuoc = relationship("DonThuoc", backref="phieu_kham")
    hoa_don = relationship("HoaDon", uselist=False, backref="phieu_kham")


#Fix add created_date
class DonThuoc(db.Model):
    __tablename__ = 'don_thuoc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    cach_dung = Column(String(200), nullable=True, default="Không có")
    created_date = Column(DateTime, default=datetime.now())

    phieu_kham_id = Column(Integer, ForeignKey('phieu_kham.id'), primary_key=True, nullable=False)
    thuoc_id = Column(Integer, ForeignKey('thuoc.id'), primary_key=True, nullable=False)



class HoaDon(db.Model):
    __tablename__ = 'hoa_don'
    id = Column(Integer, primary_key=True, autoincrement=True)
    quy_dinh_id = Column(Integer, ForeignKey('quy_dinh.id'), nullable=False)
    phieu_kham_id = Column(Integer, ForeignKey('phieu_kham.id'))
    thu_ngan_id = Column(Integer, ForeignKey('thu_ngan.id'), nullable=False)
    tong_tien = Column(Integer, nullable=True)

    @property
    def tien_kham(self):
        return self.quy_dinh.examineFee



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # qd = QuyDinh(examineFee=100000, numOfMed=30, maxPatient=40)
        # db.session.add(qd)


        # dv1 = DonViThuoc(name="Vỉ")
        # dv2 = DonViThuoc(name="Viên")
        # dv3 = DonViThuoc(name="Lọ")
        # db.session.add_all([dv1, dv2, dv3])

        # l1 = LoaiThuoc(tenLoaiThuoc="Kháng sinh")
        # l2 = LoaiThuoc(tenLoaiThuoc="Cảm cúm")
        # l3 = LoaiThuoc(tenLoaiThuoc="Đau bụng")
        # db.session.add_all([l1,l2,l3])
        #
        # t1 = Thuoc(name='Paracetamol', unit_id=1, price=100000, loai_thuoc_id=2)
        # t2 = Thuoc(name='Chlorpromazin', unit_id=2, price=10000, loai_thuoc_id=1)
        # t3 = Thuoc(name='Berberin', unit_id=3, price=12000, loai_thuoc_id=3)
        # db.session.add_all([t1, t2, t3])
        #
        # bn1 = BenhNhan(name="Hồ Đức Trí", gender="Nam", phone="0914117035", birthday="02/02/2004")
        # bn2 = BenhNhan(name="Nguyễn Kiều Phước", gender="Nam", phone="0914117036", birthday="02/02/2004")
        # bn3 = BenhNhan(name="Hồ Kiều Phước", gender="Nam", phone="0914117037", birthday="02/02/2004")
        #
        # db.session.add_all([bn1, bn2, bn3])
        #
        # doctors = [
        #     {
        #         "name": "Nguyen Van A",
        #         "username": "doctorA",
        #         "password": "123",  # MD5 của "admin"
        #         "gender": "Male",
        #         "phone": "0912345678",
        #         "email": "nguyenvana@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Nội khoa",
        #         "chuyenKhoa": "Nội tổng quát",
        #         "bangCap": "Bác sĩ Nội khoa"
        #     },
        #     {
        #         "name": "Tran Thi B",
        #         "username": "doctorB",
        #         "password": "123",  # MD5 của "password"
        #         "gender": "Female",
        #         "phone": "0912345679",
        #         "email": "tranthib@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Nhi khoa",
        #         "chuyenKhoa": "Nhi tổng quát",
        #         "bangCap": "Bác sĩ Nhi khoa"
        #     },
        #     {
        #         "name": "Le Van C",
        #         "username": "doctorC",
        #         "password": "123",  # MD5 của "test"
        #         "gender": "Male",
        #         "phone": "0912345680",
        #         "email": "levanc@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Phẫu thuật",
        #         "chuyenKhoa": "Ngoại tổng quát",
        #         "bangCap": "Bác sĩ Ngoại khoa"
        #     },
        #     {
        #         "name": "Pham Thi D",
        #         "username": "doctorD",
        #         "password": "123",  # MD5 của "qwerty"
        #         "gender": "Female",
        #         "phone": "0912345681",
        #         "email": "phamthid@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Chẩn đoán hình ảnh",
        #         "chuyenKhoa": "Chẩn đoán hình ảnh",
        #         "bangCap": "Bác sĩ Chẩn đoán hình ảnh"
        #     },
        #     {
        #         "name": "Nguyen Van E",
        #         "username": "doctorE",
        #         "password": "123",  # MD5 của "123456"
        #         "gender": "Male",
        #         "phone": "0912345682",
        #         "email": "nguyenvane@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Thần kinh",
        #         "chuyenKhoa": "Thần kinh học",
        #         "bangCap": "Bác sĩ Thần kinh"
        #     },
        #     {
        #         "name": "Tran Thi F",
        #         "username": "doctorF",
        #         "password": "123",  # MD5 của "12345678"
        #         "gender": "Female",
        #         "phone": "0912345683",
        #         "email": "tranthif@example.com",
        #         "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #         "user_role": 3,
        #         "chungChi": "Chứng chỉ Tim mạch",
        #         "chuyenKhoa": "Tim mạch",
        #         "bangCap": "Bác sĩ Tim mạch"
        #     }
        # ]
        #
        # for doc in doctors:
        #     doctor = BacSi(
        #         name=doc['name'],
        #         username=doc['username'],
        #         password=str(hashlib.md5(doc['password'].encode('utf-8')).hexdigest()),  # MD5 hash đã được tạo sẵn
        #         gender=doc['gender'],
        #         phone=doc['phone'],
        #         email=doc['email'],
        #         avatar=doc['avatar'],
        #         user_role=UserRole.BacSi,  # Enum cho vai trò bác sĩ
        #         chungChi=doc['chungChi'],
        #         chuyenKhoa=doc['chuyenKhoa'],
        #         bangCap=doc['bangCap']
        #         )
        #     db.session.add(doctor)

        #DATA CASHIER

        # cashier = [
        #         {
        #             "name": "Lo Van A",
        #             "username": "cashierA",
        #             "password": "123",  # MD5 của "admin"
        #             "gender": "Male",
        #             "phone": "0912345670",
        #             "email": "nguyenvana@example.com",
        #             "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #             "user_role": 4,
        #             "bangCap": "Đại học Ngân hàng"
        #         },
        #         {
        #             "name": "Hoang Thi B",
        #             "username": "cashierrB",
        #             "password": "123",  # MD5 của "password"
        #             "gender": "Female",
        #             "phone": "0912323679",
        #             "email": "tranthib@example.com",
        #             "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #             "user_role": 4,
        #             "bangCap": "Đại học Mở"
        #         }]
        #
        #
        # for cas in cashier:
        #     cas = ThuNgan(
        #             name=cas['name'],
        #             username=cas['username'],
        #             password=str(hashlib.md5(cas['password'].encode('utf-8')).hexdigest()),  # MD5 hash đã được tạo sẵn
        #             gender=cas['gender'],
        #             phone=cas['phone'],
        #             email=cas['email'],
        #             avatar=cas['avatar'],
        #             user_role=UserRole.ThuNgan,  # Enum cho vai trò bác sĩ
        #             bangCap=cas['bangCap']
        #             )
        #     db.session.add(cas)

        #DATA NURSE

        # nurse = [
        #         {
        #             "name": "Hoang Thai Huy",
        #             "username": "nurseA",
        #             "password": "123",  # MD5 của "admin"
        #             "gender": "Male",
        #             "phone": "0912005670",
        #             "email": "nguyenvana@example.com",
        #             "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #             "user_role": 2,
        #             "chungChi": "Y tá cấp 2",
        #             "chuyenMon": "Điều dưỡng"
        #         },
        #         {
        #             "name": "Lam Van Hai",
        #             "username": "nurseB",
        #             "password": "123",  # MD5 của "admin"
        #             "gender": "Male",
        #             "phone": "0912005670",
        #             "email": "nguyenvana@example.com",
        #             "avatar": "https://res.cloudinary.com/dpfbtypxx/image/upload/v1734261617/pengu_iaejdc.jpg",
        #             "user_role": 2,
        #             "chungChi": "Y tá cấp 4",
        #             "chuyenMon": "Hồi sức"
        #         }]
        #
        #
        # for nur in nurse:
        #     nur = YTa(
        #             name=nur['name'],
        #             username=nur['username'],
        #             password=str(hashlib.md5(nur['password'].encode('utf-8')).hexdigest()),  # MD5 hash đã được tạo sẵn
        #             gender=nur['gender'],
        #             phone=nur['phone'],
        #             email=nur['email'],
        #             avatar=nur['avatar'],
        #             user_role=UserRole.YTa,  # Enum cho vai trò bác sĩ
        #             chungChi=nur['chungChi'],
        #             chuyenMon=nur['chuyenMon']
        #             )
        #     db.session.add(nur)

        db.session.commit()