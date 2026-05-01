# TỔNG QUAN CẤU TRÚC THƯ MỤC VÀ TỆP TIN DỰ ÁN (FILE & FOLDER MAPPING)

Dưới đây là bản đồ chỉ đường giải thích vai trò của từng thư mục và tệp tin một cách chi tiết để bạn nắm được bức tranh tổng thể cấu trúc hệ thống, từ khâu nguyên liệu đầu vào tới khâu xuất mô hình. 

---

## 🗂️ 1. THƯ MỤC DỮ LIỆU ĐẦU VÀO (`data/`)
Đây là khu vực "Nhà kho" chứa toàn bộ tệp dữ liệu nguyên liệu của sinh viên.

*   **`data/raw/`**: Chứa dữ liệu gốc thô (chưa qua chỉnh sửa) tải về từ bộ OULAD của Đại học Mở Anh Quốc.
    *   `studentInfo.csv`: Khai báo nhân khẩu học (giới tính, vùng miền, độ tuổi, trình độ, khuyết tật...).
    *   `studentAssessment.csv`: Nhật ký nộp bài kiểm tra (điểm số, ngày nộp, lịch sử nộp muộn).
    *   `studentRegistration.csv`: Lịch sử thời điểm ghi danh và thời điểm rút hồ sơ bỏ học.
    *   `vle.csv`: Danh mục hệ thống Web (Virtual Learning Environment - có file PDF, có file Video để giảng bài cho sinh viên...).
    *   `assessments.csv`: Cấu trúc của các bài tập trong từng học phần.
    *   `courses.csv`: Mã khóa học cơ bản.
*   **`data/processed/`**: Chứa dữ liệu sạch, đã gộp lại làm một.
    *   `student_features_labeled.csv`: File quan trọng tối thượng. Đây là bảng số liệu siêu to khổng lồ sau quá trình gộp/nối (JOIN) điểm số, số lượt kích chuột (VLE clicks) và gắn kèm "Nhãn Rủi Ro" đích (Risk 0-3). Đây chính là thức ăn đầu vào duy nhất cho AI.
    *   `eda_summary_by_risk.csv`: File CSV tổng hợp những insight thống kê trung bình của từng nhóm rủi ro. Có thể dùng nhanh để gửi ban giám hiệu đọc hiểu tóm tắt.

---

## 🧠 2. THƯ MỤC NÃO BỘ XỬ LÝ (`notebooks/`)
Chứa toàn bộ mã nguồn lập trình và Trí tuệ nhân tạo. Quy trình chạy luân phiên nhau từ file `01` đến `03`.

*   **`01_data_cleaning.ipynb`**: Bản script phục vụ Tiền xử lý. Nó đọc dữ liệu thô ở thư mục `raw`, khắc phục lỗi điền thiếu (NaN), dồn tổng số Clicks lướt web mỗi ngày, mã hóa chữ thành số (Encoding), sinh ra thành phẩm nhét vào `processed/`.
*   **`02_eda.ipynb`**: File phân tích EDA (Exploratory Data Analysis). Mã code trong này làm nhiệm vụ quét các quy luật ẩn sâu trong dữ liệu, và tự động vẽ xuất ra các biểu đồ nhét sang thư mục `visuals/`.
*   **`03_modeling.py`**: Trái tim huấn luyện AI. Gọi công cụ `SMOTE` để khắc phục sự thiên vị (mất cân bằng lớp) và chạy thi đấu trực diện 4 thuật toán máy học trên đấu trường Python.
*   **`notebooks/models/`**: Đây là cục "Tủ đông" lưu lại kết quả trí tuệ nhân tạo.
    *   `lightgbm.pkl`: Bộ phân loại vô địch mang tên LightGBM. Nó đã "đóng băng" não bộ thành nhị phân. Khi cần mang đi làm Web App/EWS thì chỉ cần nhúng file này ra dùng, vài mili giây là dự đoán xong, không phải Train lại tốn điện tốn giờ.
    *   `random_forest.pkl`, `xgboost.pkl`, `logistic_regression.pkl`: Các bộ não dự phòng hoặc phế phẩm của những thử nghiệm thất bại/kém hơn.
    *   `scaler.pkl`: Cây thước đo chuẩn hóa. Phải lưu cái này lại để sau này đưa sinh viên mới vào, hệ thống biết tỷ lệ mà bóp data cho mượt.

---

## 📊 3. THƯ MỤC HÌNH ẢNH BIỂU ĐỒ (`visuals/`)
Trưng bày tất cả các bảng biểu, hỗ trợ chèn trực tiếp cho báo cáo và Slide thuyết trình. 

**Bộ ảnh Khám phá dữ liệu (Sinh ra bởi `02_eda.ipynb`):**
*   `01_class_distribution.png` & `02_01_imbalance_analysis.png`: Biểu diễn sự chia rẽ khủng khiếp (28:1) giữa nhóm bình thường và nhóm thiều số cá biệt.
*   `02_02_risk_by_module_presentation.png`: Rủi ro chia theo tên học phần.
*   `02_03_demographic_features.png`: Tương quan khuyết tật/nghèo đói vs Cảnh báo học tập.
*   `02_04_vle_features.png`: Khẳng định quyền lực của việc Click chuột đối với khả năng thi đỗ/trượt.
*   `02_05_assessment_features.png`: Biểu đồ phân tích điểm thi.
*   `02_06_scatter_score_vle.png`: Chấm rải rác nhìn ma trận tương quan giữa Điểm thấp/cao chéo mức Clicks bùng nổ.
*   `02_07_correlation.png` & `02_feature_correlation.png`: Ma trận Heatmap mức độ "kết dính" thống kê giữa từng chỉ số đầu vào.
*   `02_08_outlier_detection.png`: Dò lỗi các giá trị bất thường nằm vọt ra khỏi chuẩn mực (Outliers) như "Bot spam clicks".

**Bộ ảnh Đánh giá trí tuệ AI (Sinh ra bởi `03_modeling.py`):**
*   `03_model_comparison.png`: Cột so sánh ai vượt mức điểm F1 Macro.
*   `03_roc_curve_ovr.png`: Vùng diện tích độ kiêu hãnh của LightGBM (Chỉ số AUC).
*   `03_confusion_matrix_lightgbm.png`: Bảng Ma trận nhầm lẫn biên giới khẳng định siêu ít báo động giả.
*   `03_feature_importance_lightgbm.png`: AI chốt hạ lý do nguyên nhân 1 học sinh bỏ học là vì thiếu tương tác lướt Web chứ không phải vì sinh viên đó nghèo.

---

## 📄 4. THƯ MỤC GỐC NGOÀI CÙNG (Quản trị hành chính)
*   **`.git`, `.gitignore`, `.gitattributes`**: Quản lý lịch sử code qua Github.
*   **`readme.md`**: Cẩm nang hướng dẫn sử dụng Project để người ngoài công ty đọc trước khi tải máy bóp nút RUN.
*   **`Baocao_Hoan_Chinh_Chuong_3_4_5_6.md`**: Bản Báo Cáo Xương Sống xịn xò nhất, bao trọn bộ thành phẩm luận văn từ quy trình EDA, xử lý mất cân bằng, đến kết quả đầu ra Confusion Matrix mà nhóm vừa tạo.
*   **`Slide_Bao_Cao.md`**: Kịch bản chuẩn bị rèn luyện cho buổi Thuyết trình PowerPoint bảo vệ Đồ án.
*   **`Baocaochitiet.docx` & `Tôi.pdf`**: Tệp văn bản mục tiêu thô ban đầu để theo dõi luận án.
*   **`toi_to_text.txt` & `full_toi.txt`**: Khối nháp phiên dịch từ PDF lấy nội dung đọc (Tùy chỉnh có thể xóa đi cũng được).

### 🚀 TÓM GỌN TƯ DUY 
Project của bạn chạy trên một đường băng liền mạch:
1️⃣ Trích xuất `data/raw` 
$\rightarrow$ 2️⃣ Rửa sạch chắt lọc qua `notebooks/01` và chốt file `student_features_labeled` 
$\rightarrow$ 3️⃣ Khám phá thị giác qua `notebooks/02` vẽ ra folder `visuals/` 
$\rightarrow$ 4️⃣ Nhồi não học máy qua `notebooks/03` và "cất hộp sọ" LightGBM đuôi `.pkl` vào Tủ đông Models 
$\rightarrow$ 5️⃣ Viết tổng kết vào Báo cáo `Baocao_Hoan_Chinh_Chuong_3_4_5_6.md`.
