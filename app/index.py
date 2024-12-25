
from flask import render_template, request, redirect, session, jsonify, flash, url_for
import dao
from app import app, login
from flask_login import login_user, logout_user, login_required, current_user
from datetime import  datetime



@app.route("/")
def home():
    user_role = dao.load_user_role()
    return render_template('index.html', user_role=user_role)



# DANG NHAP
@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            return redirect('/')
    user_role = dao.load_user_role()
    return render_template('login.html',user_role=user_role)

@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, role=1)
    if u:
        login_user(u)


    return redirect('/admin')

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)


# PHIEU KHAM BENH
@app.route("/doctorform")
@login_required
def index():
    if 'cart' not in session:
        session['cart'] = {}

    kw = request.args.get('kw')
    type_ = request.args.get('type', '')

    show_patients = True if type_ == 'patients' else False

    patients = dao.load_patients(kw) if show_patients else []
    medicines = dao.load_medicines(kw) if not show_patients else []

    user_role = dao.load_user_role()
    print(user_role)
    return render_template('doctorform.html', patients=patients,
                           show_patients=show_patients, medicines=medicines, user_role=user_role)

@app.route('/save_form_data', methods=['POST'])
def save_form_data():
    data = request.json  # Nhận dữ liệu dưới dạng JSON từ frontend

    # Lưu thông tin vào session (hoặc bạn có thể lưu vào database)
    session['form_data'] = data

    return jsonify({"message": "Data saved successfully!"})


@app.route('/get_form_data', methods=['get'])
def get_form_data():
    # Lấy lại dữ liệu đã lưu trong session
    form_data = session.get('form_data', {})

    return jsonify(form_data)  # Trả lại dữ liệu dưới dạng JSON


@app.route('/api/carts', methods=['post'])
def add_to_cart():
    """
    {
        "1": {
            "id": "1",
            "name": "..",
            "unit-id": "1",
            "quantity": 2
        }, "2": {
            "id": "2",
            "name": "..",
            "unit-id": "2",
            "quantity": 1
        }
    }
    """
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get('id'))
    name = request.json.get('name')
    unit = request.json.get('unit')

    print(f"Received data: id={id}, name={name}, unit_name={unit}")

    if id in cart:
        cart[id]["quantity"] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "unit": unit,
            "quantity": 1
        }

    session['cart'] = cart

    print(cart)

    return jsonify(cart)


@app.route('/api/carts/<id>', methods=['put'])
def update_cart(id):
    cart = session.get('cart')

    if cart and id in cart:
        data = request.json

        if 'quantity' in data:
            cart[id]['quantity'] = data['quantity']

        if 'cach_dung' in data:
            cart[id]['cach_dung'] = data['cach_dung']

    session['cart'] = cart

    return jsonify(cart)


@app.route('/api/carts/<id>', methods=['delete'])
def delete_cart(id):
    cart = session.get('cart')

    if cart and id in cart:
        del cart[id]

    session['cart'] = cart

    return jsonify(cart)

@app.route('/api/confirm_phieukham', methods=['post'])
def confirm_phieukham():
    phone = request.form.get('phone')
    trieu_chung = request.form.get('trieu_chung')
    du_doan_benh = request.form.get('du_doan_benh')
    appointment_date_str = request.form.get('appointment_date')

    appointment_date = None
    #Bug - not debug
    if appointment_date_str:
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%d-%m-%YT%H:%M')
        except ValueError:
            return jsonify({'status': 400, 'error': 'Invalid appointment date format'})
    cart = session.get('cart',[])

    dao.add_phieukham(phone, appointment_date, trieu_chung, du_doan_benh, cart)

    del session['cart']

    return jsonify({'status': 200})


#RECEIPT
@app.route('/receipt', methods=['GET', 'POST'])
@login_required
def list_unpaid_phieukham():
    unpaid_phieukham = dao.load_unpaid_phieukham()
    user_role = dao.load_user_role()
    return render_template('receipt.html', unpaid_phieukham=unpaid_phieukham, thu_ngan_name=dao.get_thu_ngan_name(),
        benh_nhan_name=None,
        phieu_kham_id=None,
        tien_kham=None,
        tong_tien=None, user_role=user_role)

@app.route('/api/phieu_kham/<int:phieu_kham_id>', methods=['GET', 'POST'])
def get_phieu_kham(phieu_kham_id):
    phieu_kham = dao.get_phieu_kham_id(phieu_kham_id)
    if not phieu_kham:
        return jsonify({'error': 'Phiếu khám không tồn tại'}), 404

    # Lấy thông tin chi tiết phiếu khám
    phieu_data = {
        'id': phieu_kham.id,
        'benh_nhan_name': dao.get_benh_nhan_name(phieu_kham_id),
        'date_kham': phieu_kham.date_kham.strftime('%d-%m-%Y'),
        'tien_kham': dao.get_tien_kham(),
        'tong_tien': dao.get_tong_tien_thuoc(phieu_kham_id)
    }

    return jsonify(phieu_data)


@app.route('/create_hoadon/<int:phieu_kham_id>', methods=['GET','POST'])
def create_hoadon(phieu_kham_id):
    dao.tao_hoa_don(phieu_kham_id)
    flash(f'Hóa đơn cho phiếu khám {phieu_kham_id} đã được tạo thành công!', 'success')
    return redirect(url_for('list_unpaid_phieukham'))


#DANG KI KHAM
@app.route('/examine', methods=['GET', 'POST'])
def submit_form():
    success_msg = None

    if request.method.__eq__('POST'):
        name = request.form['name']
        phone = request.form['phone']
        birth = request.form['birth']
        email = request.form['email']
        gender = request.form['gender']
        appointment_date_str = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').strftime('%Y-%m-%d')

        dangki = dao.add_ExamineForm(phone,name, birth, gender,email, appointment_date_str)

        success_msg = dangki

    user_role = dao.load_user_role()
    return render_template('examine.html', success_msg = success_msg, user_role=user_role)


# LAP DANH SACH KHAM

@app.route('/list', methods=['GET', 'POST'])
@login_required
def lap_danh_sach_view():
    if request.method.__eq__('POST'):
        date = request.form.get("date")
        list = dao.get_phieu_list(date)
        user_role = dao.load_user_role()


        return render_template('list.html', list=list, user_role=user_role)

    user_role = dao.load_user_role()
    return render_template('list.html', user_role=user_role)




@app.route('/lap-danh-sach', methods=['POST'])
def lap_danh_sach():
    data = request.get_json()
    phieu_ids = data.get('phieu_ids')

    if not data:
        return jsonify({'message': 'Không có phiếu nào được chọn!'}), 400

    dao.add_ds_kham(phieu_ids)
    return jsonify({'message': 'Lập thành công!'}), 200



if __name__ == '__main__':
    with app.app_context():
        from app import admin
        app.run(debug=True)
