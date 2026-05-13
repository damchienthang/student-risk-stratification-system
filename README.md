# Student Risk Stratification System (RiskSight)

Hệ thống phân tầng mức độ rủi ro học tập của sinh viên dựa trên bộ dữ liệu OULAD và thuật toán XGBoost.

## 🌟 Tổng quan
Hệ thống là một giải pháp toàn diện giúp giảng viên và sinh viên nhận diện sớm các rủi ro trong quá trình học tập trực tuyến. Sử dụng mô hình học máy tiên tiến, hệ thống phân tích hành vi tương tác và kết quả điểm số để đưa ra dự báo với độ chính xác cao.

## 🏗 Cấu trúc Thư mục
```text
Dataset/
├── main.py                 # Điểm khởi chạy ứng dụng (FastAPI)
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── data/
│   ├── processed/          # Dữ liệu đã xử lý và Database (SQLite)
│   └── raw/                # Dữ liệu gốc OULAD (CSV)
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_modeling.py     # Quy trình huấn luyện mô hình
│   └── models/             # Lưu trữ file .pkl (XGBoost, Scaler)
├── src/
│   ├── api/v1/             # Các API Endpoint (Auth, Student, Admin)
│   ├── core/               # Cấu hình hệ thống, Bảo mật, DB
│   ├── models/             # Định nghĩa Schema Database (SQLModel)
│   ├── services/           # Logic nghiệp vụ (Predictor, AuthService)
│   └── web/                # Giao diện người dùng (Jinja2, Static)
└── visuals/                # Các biểu đồ phân tích và kết quả mô hình
```

## 🚀 Tính năng Chính
1. **Dự báo rủi ro tự động**: Tự động tải kết quả cho sinh viên khi đăng nhập.
2. **Thử nghiệm tự do (Guest Trial)**: Cho phép người dùng ngoài nhập liệu và nhận phân tích tức thì.
3. **Giải thích AI (Explainable AI)**: Phân tích chi tiết các yếu tố (Điểm số, Click, Kỷ luật) ảnh hưởng đến kết quả rủi ro.
4. **Quản lý Tài khoản (RBAC)**: Phân quyền chặt chẽ giữa Admin, Student và External Guest.
5. **Quản lý Hồ sơ**: Cho phép người dùng xem và cập nhật thông tin cá nhân (Họ tên, Email, SĐT).
6. **Lịch sử Dự báo**: Lưu trữ và truy xuất các lần thực hiện dự báo trong quá khứ.

## 📊 Thông số Mô hình
- **Thuật toán chính**: XGBoost Classifier.
- **Độ chính xác (Accuracy)**: 92.71%.
- **AUC Score**: 98.68%.
- **Dữ liệu huấn luyện**: 32,593 bản ghi từ Open University Learning Analytics Dataset.

## 🛠 Cài đặt & Khởi chạy

### 1. Cài đặt môi trường
Yêu cầu Python 3.9 trở lên.
```bash
pip install -r requirements.txt
```

### 2. Khởi tạo dữ liệu
Chạy script migration để tạo cấu trúc bảng và nạp dữ liệu gốc:
```bash
python src/scripts/migrate_db.py
```

### 3. Chạy ứng dụng
```bash
python main.py
```
Truy cập giao diện tại: `http://localhost:8000`

## 👥 Vai trò Người dùng
- **Admin**: Tài khoản `admin` / mật khẩu `admin123`. Toàn quyền quản lý sinh viên và người dùng.
- **Sinh viên OULAD**: Đăng nhập bằng Mã SV (VD: `11391` / `11391`). Xem kết quả chính thức.
- **Người dùng ngoài**: Đăng ký tài khoản tự do. Sử dụng tính năng thử nghiệm và lưu kết quả cá nhân.

---
© 2026 Student Risk Stratification Project. Giao diện được tối ưu hóa theo phong cách Minimalist chuyên nghiệp.
