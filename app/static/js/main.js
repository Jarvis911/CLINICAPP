function showPatients() {
            const kw = document.getElementById("kw").value;
            window.location.href = `/doctorform?kw=${encodeURIComponent(kw)}&type=patients`;
        }

function showMedicines() {
           const kw = document.getElementById("kw").value;
           window.location.href = `/doctorform?kw=${encodeURIComponent(kw)}&type=medicines`;
        }

function setType(type) {
    document.getElementById("type").value = type; // Cập nhật giá trị trường ẩn
    document.getElementById("searchForm").submit(); // Gửi form ngay lập tức
}

function fillForm(name, phone, birthday) {
        // Gán giá trị vào các trường của form
        document.getElementById('name-of-patient').value = name;
        document.getElementById('phone').value = phone;
//        document.getElementById('birthday').value = birthday;
        document.getElementById('name-of-patient').dispatchEvent(new Event('input'));
        document.getElementById('phone').dispatchEvent(new Event('input'));
    }

function saveFormData() {
        const formData = {
            name_of_patient: document.getElementById("name-of-patient").value,
            phone: document.getElementById("phone").value,
            appointment_date: document.getElementById("appointment-date").value,
            symptom: document.getElementById("symptom").value,
            predict: document.getElementById("predict").value
        };

        // Gửi dữ liệu lên API
        fetch('/save_form_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);  // In ra thông báo thành công
        })
        .catch(error => console.error('Error:', error));
    }

    // Lấy lại dữ liệu từ API khi trang được tải
    window.onload = function () {
        fetch('/get_form_data')
            .then(response => response.json())
            .then(data => {
                if (data.name_of_patient) {
                    document.getElementById("name-of-patient").value = data.name_of_patient;
                }
                if (data.phone) {
                    document.getElementById("phone").value = data.phone;
                }
                if (data.appointment_date) {
                    document.getElementById("appointment-date").value = data.appointment_date;
                }
                if (data.gender) {
                    document.getElementById("symptom").value = data.symptom;
                }
                if (data.mobile) {
                    document.getElementById("predict").value = data.predict;
                }
            })
            .catch(error => console.error('Error:', error));

};

function submitForm(event) {
    event.preventDefault(); // Ngăn form gửi theo cách mặc định

    const form = document.getElementById('phieu-kham-form');
    const formData = new FormData(form); // Lấy dữ liệu từ form

    fetch('/api/confirm_phieukham', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 200) {
            alert('Lưu thành công');
        } else {
            alert('Có lỗi xảy ra: ' + (data.error || 'Không xác định'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

 // CART

function update(data) {
    let items = document.getElementsByClassName("cart-counter");
    for (let item of items)
        item.innerText = data.total_quantity;
}

function addToCart(id, name, unit) {
    fetch("/api/carts", {
        method: "POST",
        body: JSON.stringify({
            "id": id,
            "name": name,
            "unit": unit
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        update(data);
        location.reload();
    });
}

function updateCart(id, obj) {
    fetch(`/api/carts/${id}`, {
        method: "put",
        body: JSON.stringify({
            quantity: obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        update(data);
        location.reload();
    })
}

function updateCachDung(id, obj) {
    const cachDung = obj.value; // Lấy giá trị cách dùng từ input

    fetch(`/api/carts/${id}`, {
        method: "PUT",
        body: JSON.stringify({
            cach_dung: cachDung
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.log("Cách dùng đã được cập nhật:", data);
    }).catch(error => console.error("Lỗi khi cập nhật cách dùng:", error));
}

function deleteCart(id) {
    if (confirm("Bạn chắc chắn xóa không?") === true) {
        fetch(`/api/carts/${id}`, {
            method: "delete"
        }).then(res => res.json()).then(data => {
            update(data);

            document.getElementById(`cart${id}`).style.display = "none";
            location.reload();
        })
    }
}

function confirm_phieukham() {
    if (confirm("Bạn chắc chắn thêm phiếu khám không?") === true) {
        fetch('/api/confirm_phieukham', {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if (data.status === 200) {
                alert("Thêm phiếu !");
                location.reload();
            }
        })
    }
}


//RECEIPT


function getPhieuKham(phieuKhamId) {
    fetch(`/api/phieu_kham/${phieuKhamId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);  // Hiển thị thông báo lỗi nếu không tìm thấy phiếu khám
            } else {
                // Điền dữ liệu vào container
                document.querySelector('#benh_nhan_name').textContent = data.benh_nhan_name;
                document.querySelector('#phieu_kham_id').textContent = data.id;
                document.querySelector('#date_kham').textContent = data.date_kham;
                document.querySelector('#tien_kham').textContent = `${data.tien_kham} VND`;

                // Hiển thị tổng tiền thuốc
                document.querySelector('#tong_tien').textContent = `${data.tong_tien} VND`;
            }
        })
        .catch(error => console.error('Error:', error));  // Xử lý lỗi nếu có
}

function redirectToHoaDon() {
if (confirm("Bạn chắc chắn lập hóa đơn không?") === true) {
var phieuKhamId = document.querySelector('#phieu_kham_id').textContent;  // Lấy giá trị ID từ phần tử <p> có id="phieu_kham_id"

    if (phieuKhamId && phieuKhamId !== 'None') {
        // Chuyển hướng đến URL tương ứng với phieu_kham_id
        window.location.href = `/create_hoadon/${phieuKhamId}`;
    } else {
        alert("Mã phiếu khám không hợp lệ!");
    }
}

}



// DS KHAM
function submitDanhSach() {
    // Lấy tất cả các checkbox được chọn
    const checkboxes = document.querySelectorAll('#phieu-dang-lap tbody input[type="checkbox"]:checked');
    const selectedPhieuIds = Array.from(checkboxes).map(cb => cb.dataset.phieuId); // Lấy danh sách ID từ data attribute

    // Kiểm tra nếu không có phiếu nào được chọn
    if (selectedPhieuIds.length === 0) {
        alert('Vui lòng chọn ít nhất một phiếu để lập danh sách!');
        return;
    }

    // Gửi dữ liệu qua AJAX (Fetch API)
    fetch('/lap-danh-sach', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phieu_ids: selectedPhieuIds }),
    })
        .then(response => {
            if (response.ok) {
                alert('Lập danh sách thành công!');
                location.reload(); // Reload lại trang
            } else {
                alert('Có lỗi xảy ra, vui lòng thử lại.');
            }
        })
        .catch(error => console.error('Error:', error));
}

