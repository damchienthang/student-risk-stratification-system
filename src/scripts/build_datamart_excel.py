import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def build_datamart_workbook():
    wb = openpyxl.Workbook()
    
    # ---------------------------------------------------------
    # Styles & Palettes
    # ---------------------------------------------------------
    font_family = "Segoe UI"
    
    title_font = Font(name=font_family, size=15, bold=True, color="1F4E78")
    subtitle_font = Font(name=font_family, size=10.5, italic=True, color="595959")
    section_font = Font(name=font_family, size=12, bold=True, color="1F4E78")
    table_header_font = Font(name=font_family, size=10.5, bold=True, color="FFFFFF")
    group_header_font = Font(name=font_family, size=11, bold=True, color="002060")
    data_font = Font(name=font_family, size=9.5, color="000000")
    bold_data_font = Font(name=font_family, size=9.5, bold=True, color="000000")
    code_font = Font(name="Consolas", size=9.5, color="A00000", bold=True)
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    group_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    zebra_fill = PatternFill(start_color="F9FAFC", end_color="F9FAFC", fill_type="solid")
    accent_green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    accent_orange_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    accent_yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    accent_red_fill = PatternFill(start_color="F8CBAD", end_color="F8CBAD", fill_type="solid")
    
    thin_border_side = Side(border_style="thin", color="D9D9D9")
    data_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    header_border = Border(
        left=Side(border_style="thin", color="FFFFFF"),
        right=Side(border_style="thin", color="FFFFFF"),
        top=Side(border_style="medium", color="1F4E78"),
        bottom=Side(border_style="medium", color="1F4E78")
    )
    
    # ---------------------------------------------------------
    # SHEET 1: TongQuan_KienTruc
    # ---------------------------------------------------------
    ws1 = wb.active
    ws1.title = "1. TongQuan_KienTruc"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1.append(["KIẾN TRÚC DỮ LIỆU CHUẨN HÓA: STUDENT RISK STRATIFICATION DATA MART"])
    ws1.append(["Chuẩn hóa theo Quy chế Đào tạo Tín chỉ Đại học Việt Nam (Thông tư 08/2021/TT-BGDĐT) & Tương thích Benchmark Quốc tế (OULAD, UCI)"])
    ws1.append([])
    
    ws1["A1"].font = title_font
    ws1["A2"].font = subtitle_font
    
    intro_rows = [
        ["1. Bối cảnh & Mục tiêu", "Xây dựng Data Mart dữ liệu sinh viên chuẩn hóa phục vụ bài toán Phân tầng Rủi ro Học tập (Student Risk Stratification). Hỗ trợ chuẩn hóa dữ liệu từ nhiều nguồn: Hệ thống đào tạo tín chỉ Việt Nam, LMS trực tuyến (Moodle/Canvas), và ánh xạ trực tiếp sang các tập benchmark quốc tế như OULAD (UK), UCI Dropout (Bồ Đào Nha), UCI Student Performance."],
        ["2. Mô hình kiến trúc (Star Schema)", "Kiến trúc gồm 4 Bảng Chiều (Dimensions) + 3 Bảng Sự kiện (Facts) + 1 Bảng Phẳng ML (Flattened Feature Mart). Cấu trúc này cho phép vừa lưu trữ đa chiều theo tiêu chuẩn Business Intelligence, vừa trải phẳng dễ dàng để đưa vào mô hình Machine Learning."],
        ["3. Bám sát thực tế Việt Nam", "Quy đổi theo thang điểm 10 -> Điểm chữ (A, B+, B, C+, C, D+, D, F) -> Thang điểm 4 (GPA/CPA). Tích hợp tiêu chí Cảnh báo học vụ (Mức 1, Mức 2, Buộc thôi học), Điểm rèn luyện (DRL), Cấm thi do chuyên cần, và Nợ học phí theo Thông tư 08/2021."],
        ["4. Mốc can thiệp sớm (Early Warning)", "Phân tầng rủi ro không chỉ vào cuối kỳ mà chia theo 4 mốc: Tuần 4 (Chuyên cần & LMS), Tuần 8 (Kiểm tra giữa kỳ), Tuần 12 (Trước kỳ thi - Nguy cơ cấm thi), và Tuần 16 (Tổng kết kỳ & Cảnh báo học vụ)."]
    ]
    
    for title, desc in intro_rows:
        r = ws1.max_row + 1
        ws1.cell(row=r, column=1, value=title).font = bold_data_font
        ws1.cell(row=r, column=2, value=desc).font = data_font
        ws1.cell(row=r, column=2).alignment = Alignment(wrap_text=True)
        ws1.row_dimensions[r].height = 40
    
    ws1.append([])
    ws1.append(["DANH MỤC CÁC BẢNG TRONG DATA MART", ""])
    ws1.cell(row=ws1.max_row, column=1).font = section_font
    
    table_list_headers = ["Mã Bảng", "Tên Nghiệp Vụ", "Loại Bảng", "Mô Tả Vai Trò Trong Hệ Thống", "Số Trường Chính", "Tương Ứng OULAD / UCI"]
    ws1.append(table_list_headers)
    hdr_row = ws1.max_row
    for col_idx in range(1, len(table_list_headers) + 1):
        c = ws1.cell(row=hdr_row, column=col_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = header_border
    ws1.row_dimensions[hdr_row].height = 25
    
    table_meta = [
        ["Dim_SinhVien", "Chiều Sinh viên", "Dimension", "Lưu trữ nhân khẩu học, tuyển sinh, chính sách, quê quán, ngành học", "13", "studentInfo.csv (OULAD) / Demographics (UCI)"],
        ["Dim_HocPhan", "Chiều Học phần", "Dimension", "Danh mục môn học, số tín chỉ, khối kiến thức, môn tiên quyết, hình thức thi", "8", "courses.csv, assessments.csv (OULAD)"],
        ["Dim_HocKy", "Chiều Học kỳ & Thời gian", "Dimension", "Học kỳ, năm học, mốc thời gian tuần học và milestone cảnh báo sớm", "7", "code_presentation (OULAD) / Semester (UCI)"],
        ["Fact_KetQuaHocPhan", "Điểm chi tiết Học phần", "Fact", "Điểm CC (10%), Giữa kỳ (30%), Thi cuối kỳ (60%), Điểm chữ, Điểm hệ 4, Cấm thi", "14", "studentAssessment.csv (OULAD) / Curricular Units (UCI)"],
        ["Fact_TuongTac_LMS", "Hành vi Tương tác LMS", "Fact", "Log học tập Moodle/Canvas: Lượt clicks, xem video, làm quiz, nộp bài muộn", "14", "studentVle.csv (OULAD) / LMS Logs (Kalboard)"],
        ["Fact_HocVu_HocKy", "Học vụ & Rèn luyện kỳ", "Fact", "Tổng kết kỳ: Tín chỉ tích lũy, GPA kỳ, CPA tích lũy, Điểm rèn luyện DRL, Nợ học phí, Cảnh báo HV", "15", "studentRegistration.csv / Academic History (UCI)"],
        ["DataMart_Student_Risk_Flat", "Bảng phẳng Đặc trưng ML", "Flattened Mart", "Trải phẳng từ 6 bảng trên thành bảng đặc trưng chuẩn hóa + Nhãn Risk_Level (0,1,2,3)", "22", "student_features_labeled.csv (Bộ dữ liệu huấn luyện ML)"]
    ]
    
    for row_data in table_meta:
        ws1.append(row_data)
        curr_r = ws1.max_row
        for col_idx in range(1, len(row_data) + 1):
            c = ws1.cell(row=curr_r, column=col_idx)
            c.font = bold_data_font if col_idx <= 2 else data_font
            c.border = data_border
            if col_idx in [3, 5]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 1:
                c.font = code_font
        ws1.row_dimensions[curr_r].height = 24
        
    ws1.column_dimensions["A"].width = 28
    ws1.column_dimensions["B"].width = 25
    ws1.column_dimensions["C"].width = 18
    ws1.column_dimensions["D"].width = 65
    ws1.column_dimensions["E"].width = 16
    ws1.column_dimensions["F"].width = 45

    # ---------------------------------------------------------
    # SHEET 2: TuDien_DataMart (TỪ ĐIỂN DỮ LIỆU & ROW GROUPING)
    # ---------------------------------------------------------
    ws2 = wb.create_sheet(title="2. TuDien_DataMart")
    ws2.views.sheetView[0].showGridLines = True
    
    ws2.append(["TỪ ĐIỂN DỮ LIỆU DATA MART CHUẨN HÓA (DATA DICTIONARY & FLATTENED SCHEMA)"])
    ws2.append(["Bao gồm mô hình quan hệ, công thức tính toán theo quy chế đại học VN và ánh xạ chuẩn hóa đa tập dữ liệu. Dùng nút [-] / [+] bên trái để thu gọn/mở rộng từng bảng."])
    ws2.append([])
    
    ws2["A1"].font = title_font
    ws2["A2"].font = subtitle_font
    
    columns_spec = [
        "STT", "Nhóm Bảng", "Tên Trường (Field)", "Tên Tiếng Việt", 
        "Kiểu Dữ Liệu", "Ràng Buộc (Key)", "Cho Phép Null", 
        "Công Thức Tính / Nguồn", "Mô Tả Nghiệp Vụ & Quy Chế Đào Tạo VN", 
        "Giá Trị Mẫu / Miền Giá Trị", "Ánh Xạ Quốc Tế (OULAD/UCI)"
    ]
    
    ws2.append(columns_spec)
    hdr_row_2 = ws2.max_row
    for col_idx in range(1, len(columns_spec) + 1):
        c = ws2.cell(row=hdr_row_2, column=col_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = header_border
    ws2.row_dimensions[hdr_row_2].height = 28
    
    # Define detailed fields by table groups
    tables_data = [
        {
            "group_name": "BẢNG 1: Dim_SinhVien (Chiều Thông Tin Sinh Viên & Tuyển Sinh)",
            "fields": [
                [1, "Dim_SinhVien", "student_id", "Mã ID Sinh Viên", "BIGINT", "PK", "No", "Hệ thống sinh mã tự tăng", "Mã định danh duy nhất của sinh viên trong cơ sở dữ liệu Data Mart", "10001, 10002", "id_student (OULAD)"],
                [2, "Dim_SinhVien", "student_code", "Mã Số Sinh Viên (MSSV)", "VARCHAR(20)", "Unique, Index", "No", "Hồ sơ tuyển sinh", "MSSV do trường cấp, phân biệt khóa học và khoa đào tạo", "2021600123", "id_student"],
                [3, "Dim_SinhVien", "full_name", "Họ và Tên", "NVARCHAR(100)", "None", "No", "Hồ sơ tuyển sinh", "Họ tên đầy đủ của sinh viên", "Nguyễn Văn An", "N/A (Bảo mật OULAD)"],
                [4, "Dim_SinhVien", "gender", "Giới Tính", "VARCHAR(10)", "None", "No", "Hồ sơ tuyển sinh", "Giới tính sinh viên (Nam, Nữ, Khác)", "Nam / Nu", "gender (M/F)"],
                [5, "Dim_SinhVien", "birth_year", "Năm Sinh", "INT", "None", "No", "Hồ sơ tuyển sinh", "Năm sinh của sinh viên, dùng tính tuổi nhập học", "2003", "age_band (0-35, 35-55, 55<=)"],
                [6, "Dim_SinhVien", "hometown_province", "Quê Quán / Tỉnh Thành", "NVARCHAR(50)", "None", "Yes", "Hồ sơ tuyển sinh", "Tỉnh/thành phố nơi sinh viên cư trú trước khi vào trường", "Hà Nội, Nam Định, Nghệ An", "region (OULAD)"],
                [7, "Dim_SinhVien", "admission_year", "Năm Nhập Học", "INT", "None", "No", "Hồ sơ tuyển sinh", "Năm sinh viên bắt đầu khóa đào tạo (xác định sinh viên năm 1, 2, 3, 4)", "2021", "cohort / presentation"],
                [8, "Dim_SinhVien", "major_code", "Mã Ngành Học", "VARCHAR(20)", "FK", "No", "Phòng Đào tạo", "Mã ngành đào tạo chuẩn của Bộ GD&ĐT", "7480201 (CNTT), 7480202 (ATTT)", "code_module (OULAD) / Course (UCI)"],
                [9, "Dim_SinhVien", "major_name", "Tên Ngành Học", "NVARCHAR(100)", "None", "No", "Phòng Đào tạo", "Tên đầy đủ của chuyên ngành sinh viên đang theo học", "Công nghệ thông tin", "code_module name"],
                [10, "Dim_SinhVien", "education_type", "Loại Hình Đào Tạo", "VARCHAR(30)", "None", "No", "Phòng Đào tạo", "Chương trình chuẩn, Chất lượng cao, Liên thông, Vừa học vừa làm", "Chinh quy / Chat luong cao", "Daytime/evening attendance (UCI)"],
                [11, "Dim_SinhVien", "admission_score", "Điểm Trúng Tuyển", "DECIMAL(4,2)", "None", "Yes", "Kỳ thi THPT / ĐGNL", "Tổng điểm đầu vào đại học (thang 30 hoặc quy đổi)", "26.50", "Admission grade (UCI)"],
                [12, "Dim_SinhVien", "priority_group", "Đối Tượng Ưu Tiên", "VARCHAR(30)", "None", "Yes", "Hồ sơ chính sách", "Diện hộ nghèo, cận nghèo, con thương binh, vùng sâu vùng xa", "Khu vuc 1, Ho ngheo, Khong", "imd_band, disability (OULAD)"],
                [13, "Dim_SinhVien", "scholarship_status", "Tình Trạng Học Bổng", "VARCHAR(30)", "None", "No", "Phòng CTSV", "Sinh viên có nhận học bổng khuyến khích học tập hay không", "Khong / Khuyen khich / Toan phan", "Scholarship holder (UCI)"]
            ]
        },
        {
            "group_name": "BẢNG 2: Dim_HocPhan (Chiều Danh Mục Môn Học & Chương Trình Đào Tạo)",
            "fields": [
                [14, "Dim_HocPhan", "course_id", "Mã ID Học Phần", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Mã định danh duy nhất của học phần trong hệ thống", "501, 502", "code_module (OULAD)"],
                [15, "Dim_HocPhan", "course_code", "Mã Môn Học", "VARCHAR(20)", "Unique, Index", "No", "Phòng Đào tạo", "Mã môn học theo khung chương trình đào tạo", "IT3010, MI1010", "code_module"],
                [16, "Dim_HocPhan", "course_name", "Tên Học Phần", "NVARCHAR(150)", "None", "No", "Phòng Đào tạo", "Tên môn học giảng dạy", "Cấu trúc dữ liệu & Giải thuật", "module_name"],
                [17, "Dim_HocPhan", "credits", "Số Tín Chỉ", "INT", "None", "No", "Quy chế đào tạo", "Số tín chỉ của môn học (thường 2, 3 hoặc 4 tín chỉ)", "3", "Curricular units credits (UCI)"],
                [18, "Dim_HocPhan", "knowledge_block", "Khối Kiến Thức", "VARCHAR(30)", "None", "No", "Khung chương trình", "Đại cương, Cơ sở ngành, Chuyên ngành, Đồ án/Tốt nghiệp", "Co so nganh", "subject_type"],
                [19, "Dim_HocPhan", "is_required", "Bắt Buộc / Tự Chọn", "BOOLEAN", "None", "No", "Khung chương trình", "1 nếu là môn học bắt buộc, 0 nếu là tự chọn", "1 (Bat buoc)", "mandatory_flag"],
                [20, "Dim_HocPhan", "has_prerequisite", "Có Môn Tiên Quyết", "BOOLEAN", "None", "No", "Khung chương trình", "1 nếu môn này yêu cầu phải qua môn tiên quyết trước", "1 (Co tien quyet)", "prerequisite_flag"],
                [21, "Dim_HocPhan", "evaluation_method", "Hình Thức Đánh Giá", "VARCHAR(50)", "None", "No", "Đề cương chi tiết", "Thi tự luận, trắc nghiệm, vấn đáp, bảo vệ đồ án", "Thi viet tu luan (60%)", "assessment_type (OULAD)"]
            ]
        },
        {
            "group_name": "BẢNG 3: Dim_HocKy (Chiều Thời Gian & Mốc Đánh Giá Học Kỳ)",
            "fields": [
                [22, "Dim_HocKy", "semester_id", "Mã ID Học Kỳ", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Định danh duy nhất của học kỳ", "20231, 20232", "code_presentation (OULAD)"],
                [23, "Dim_HocKy", "semester_code", "Mã Học Kỳ", "VARCHAR(20)", "Unique, Index", "No", "Phòng Đào tạo", "Ký hiệu học kỳ theo năm học chuẩn tại Việt Nam", "2023.1, 2023.2, 2023.3 (Kỳ hè)", "code_presentation (2013J, 2014B)"],
                [24, "Dim_HocKy", "academic_year", "Năm Học", "VARCHAR(20)", "None", "No", "Phòng Đào tạo", "Năm học tương ứng", "2023-2024", "academic_year"],
                [25, "Dim_HocKy", "semester_order", "Học Kỳ Thứ Mấy", "INT", "None", "No", "Quy chế đào tạo", "Học kỳ 1 (chính), Học kỳ 2 (chính), Học kỳ 3 (kỳ phụ/hè)", "1, 2, 3", "1st sem / 2nd sem (UCI)"],
                [26, "Dim_HocKy", "start_date", "Ngày Bắt Đầu Học Kỳ", "DATE", "None", "No", "Biểu đồ kế hoạch học tập", "Thời điểm bắt đầu tuần 1 của kỳ học", "2023-09-05", "presentation start date"],
                [27, "Dim_HocKy", "end_date", "Ngày Kết Thúc Học Kỳ", "DATE", "None", "No", "Biểu đồ kế hoạch học tập", "Thời điểm kết thúc đợt thi học kỳ", "2024-01-20", "presentation end date"],
                [28, "Dim_HocKy", "current_milestone", "Mốc Đánh Giá Can Thiệp", "VARCHAR(30)", "None", "No", "Quy trình Early Warning", "Tuần 4 (LMS/Chuyên cần), Tuần 8 (Giữa kỳ), Tuần 12 (Trước thi), Tuần 16 (Cuối kỳ)", "Tuan 8 - Giua ky", "Day 60 milestone (OULAD)"]
            ]
        },
        {
            "group_name": "BẢNG 4: Fact_KetQuaHocPhan (Sự Kiện Điểm Chi Tiết Học Phần)",
            "fields": [
                [29, "Fact_KetQuaHocPhan", "result_id", "Mã Kết Quả", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Định danh bản ghi điểm học phần của sinh viên", "900001", "id_assessment_result"],
                [30, "Fact_KetQuaHocPhan", "student_id", "Mã ID Sinh Viên", "BIGINT", "FK -> Dim_SinhVien", "No", "Dim_SinhVien", "Khóa ngoại liên kết sinh viên", "10001", "id_student (OULAD)"],
                [31, "Fact_KetQuaHocPhan", "course_id", "Mã ID Học Phần", "BIGINT", "FK -> Dim_HocPhan", "No", "Dim_HocPhan", "Khóa ngoại liên kết môn học", "501", "code_module (OULAD)"],
                [32, "Fact_KetQuaHocPhan", "semester_id", "Mã ID Học Kỳ", "BIGINT", "FK -> Dim_HocKy", "No", "Dim_HocKy", "Khóa ngoại liên kết học kỳ", "20231", "code_presentation (OULAD)"],
                [33, "Fact_KetQuaHocPhan", "attendance_score", "Điểm Chuyên Cần", "DECIMAL(3,1)", "None", "Yes", "Giảng viên / Điểm danh LMS", "Điểm chuyên cần và thái độ học tập trên lớp (thang 10, tỷ trọng ~10%)", "8.5", "vle interaction proxy"],
                [34, "Fact_KetQuaHocPhan", "midterm_score", "Điểm Kiểm Tra Giữa Kỳ", "DECIMAL(3,1)", "None", "Yes", "Giảng viên chấm thi", "Điểm kiểm tra giữa kỳ / bài tập lớn (thang 10, tỷ trọng 30% - 40%)", "6.0", "TMA score (OULAD) / G1, G2 (Cortez)"],
                [35, "Fact_KetQuaHocPhan", "assignment_score", "Điểm Bài Tập / Thực Hành", "DECIMAL(3,1)", "None", "Yes", "Hệ thống chấm lab / LMS", "Điểm trung bình các bài tập thực hành, bài tập tuần", "7.0", "CMA score (OULAD)"],
                [36, "Fact_KetQuaHocPhan", "final_exam_score", "Điểm Thi Cuối Kỳ", "DECIMAL(3,1)", "None", "Yes", "Kỳ thi tập trung của trường", "Điểm thi kết thúc học phần (thang 10, tỷ trọng 50% - 60%)", "4.0", "Exam score (OULAD) / G3 (Cortez)"],
                [37, "Fact_KetQuaHocPhan", "course_score_10", "Điểm Học Phần Hệ 10", "DECIMAL(3,1)", "Calculated", "No", "CC*0.1 + GK*0.3 + CK*0.6", "Điểm tổng kết môn thang 10 theo đề cương chi tiết học phần", "5.1", "weighted_score (OULAD) / Grade (UCI)"],
                [38, "Fact_KetQuaHocPhan", "course_grade_letter", "Điểm Chữ Học Phần", "VARCHAR(5)", "Calculated", "No", "Quy đổi theo TT 08/2021", "Thang điểm chữ: A (8.5-10), B+ (8.0-8.4), B (7.0-7.9), C+ (6.5-6.9), C (5.5-6.4), D+ (5.0-5.4), D (4.0-4.9), F (<4.0)", "D", "Letter Grade"],
                [39, "Fact_KetQuaHocPhan", "course_score_4", "Điểm Học Phần Hệ 4", "DECIMAL(2,1)", "Calculated", "No", "Quy đổi từ Điểm chữ", "A: 4.0, B+: 3.5, B: 3.0, C+: 2.5, C: 2.0, D+: 1.5, D: 1.0, F: 0.0 (Dưới 1.0 là không đạt)", "1.0", "Grade point (GPA)"],
                [40, "Fact_KetQuaHocPhan", "is_passed", "Đạt Môn (Qua Môn)", "BOOLEAN", "Calculated", "No", "IF(course_score_4 >= 1.0, 1, 0)", "1 nếu hoàn thành học phần (tích lũy được tín chỉ), 0 nếu điểm F (phải học lại)", "1 (Qua mon) / 0 (Truot)", "final_result (Pass/Fail)"],
                [41, "Fact_KetQuaHocPhan", "is_barred_from_exam", "Bị Cấm Thi", "BOOLEAN", "Calculated", "No", "IF(vắng > 20% OR CC < 3.0, 1, 0)", "Sinh viên vi phạm quy chế điểm danh hoặc bài tập -> cấm thi cuối kỳ", "0 (Khong bi cam thi)", "Withdrawn prior to exam"],
                [42, "Fact_KetQuaHocPhan", "attempt_count", "Số Lần Học Môn Này", "INT", "Calculated", "No", "COUNT(*) lịch sử môn", "1: Học lần đầu; >= 2: Học lại do rớt môn hoặc học cải thiện điểm", "1", "num_of_prev_attempts (OULAD) / failures"]
            ]
        },
        {
            "group_name": "BẢNG 5: Fact_TuongTac_LMS (Sự Kiện Hành Vi Tương Tác Học Tập Trực Tuyến)",
            "fields": [
                [43, "Fact_TuongTac_LMS", "interaction_id", "Mã Tương Tác LMS", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Định danh bản ghi thống kê tương tác LMS của sinh viên theo môn", "700001", "id_site_interaction"],
                [44, "Fact_TuongTac_LMS", "student_id", "Mã ID Sinh Viên", "BIGINT", "FK -> Dim_SinhVien", "No", "Dim_SinhVien", "Khóa ngoại liên kết sinh viên", "10001", "id_student"],
                [45, "Fact_TuongTac_LMS", "course_id", "Mã ID Học Phần", "BIGINT", "FK -> Dim_HocPhan", "No", "Dim_HocPhan", "Khóa ngoại liên kết môn học", "501", "code_module"],
                [46, "Fact_TuongTac_LMS", "semester_id", "Mã ID Học Kỳ", "BIGINT", "FK -> Dim_HocKy", "No", "Dim_HocKy", "Khóa ngoại liên kết học kỳ", "20231", "code_presentation"],
                [47, "Fact_TuongTac_LMS", "total_logins", "Tổng Số Lần Đăng Nhập", "INT", "Aggregated", "No", "Log LMS Moodle/Canvas", "Số lượt đăng nhập vào hệ thống học tập trực tuyến trong kỳ", "45", "vle_login_count"],
                [48, "Fact_TuongTac_LMS", "total_clicks", "Tổng Lượt Tương Tác Clicks", "INT", "Aggregated", "No", "SUM(sum_click) từ LMS log", "Tổng số lần nhấp chuột vào bài giảng, tài liệu, video, bài tập", "620", "total_clicks (OULAD)"],
                [49, "Fact_TuongTac_LMS", "active_days", "Số Ngày Học Tích Cực", "INT", "Aggregated", "No", "COUNT(DISTINCT date)", "Số ngày riêng biệt sinh viên có phát sinh thao tác trên LMS", "28", "active_days (OULAD)"],
                [50, "Fact_TuongTac_LMS", "video_watch_time_minutes", "Thời Gian Xem Video (Phút)", "INT", "Aggregated", "Yes", "LMS video player log", "Tổng số phút xem video bài giảng e-learning môn học", "480", "video_duration_watched"],
                [51, "Fact_TuongTac_LMS", "video_completion_rate", "Tỷ Lệ Hoàn Thành Video (%)", "DECIMAL(4,1)", "Calculated", "Yes", "Xem thực tế / Tổng thời lượng", "Tỷ lệ phần trăm hoàn thành các bài giảng video bắt buộc", "75.0%", "resource_completion_rate"],
                [52, "Fact_TuongTac_LMS", "quiz_attempts", "Số Lần Làm Quiz Tự Luyện", "INT", "Aggregated", "No", "LMS quiz log", "Số lượt thực hiện các bài trắc nghiệm củng cố kiến thức", "12", "quiz_attempts"],
                [53, "Fact_TuongTac_LMS", "avg_quiz_score", "Điểm Trung Bình Quiz LMS", "DECIMAL(3,1)", "Calculated", "Yes", "AVG(score) bài quiz", "Điểm trung bình các bài tập trắc nghiệm ngắn trên LMS (thang 10)", "7.2", "avg_quiz_score"],
                [54, "Fact_TuongTac_LMS", "forum_posts", "Số Lượt Thảo Luận Diễn Đàn", "INT", "Aggregated", "No", "LMS forum log", "Số bài đăng/bình luận trao đổi học thuật trên forum môn học", "3", "forum_ng_clicks (OULAD) / Discussion (Kalboard)"],
                [55, "Fact_TuongTac_LMS", "late_submissions_count", "Số Bài Nộp Trễ Hạn", "INT", "Calculated", "No", "COUNT(*) IF(submit_date > deadline)", "Số bài tập nộp sau thời hạn quy định trên LMS", "2", "n_late (OULAD)"],
                [56, "Fact_TuongTac_LMS", "avg_submission_delay_hours", "Số Giờ Trễ Trung Bình", "DECIMAL(5,1)", "Calculated", "No", "AVG(submit_date - deadline)", "Số giờ nộp bài muộn trung bình so với hạn chót", "18.5", "avg_submit_delay (OULAD)"]
            ]
        },
        {
            "group_name": "BẢNG 6: Fact_HocVu_HocKy (Sự Kiện Tổng Hợp Học Vụ & Cảnh Báo Kỳ)",
            "fields": [
                [57, "Fact_HocVu_HocKy", "summary_id", "Mã Tổng Hợp Học Kỳ", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Định danh bản ghi tổng kết học kỳ của sinh viên", "800001", "id_term_summary"],
                [58, "Fact_HocVu_HocKy", "student_id", "Mã ID Sinh Viên", "BIGINT", "FK -> Dim_SinhVien", "No", "Dim_SinhVien", "Khóa ngoại liên kết sinh viên", "10001", "id_student"],
                [59, "Fact_HocVu_HocKy", "semester_id", "Mã ID Học Kỳ", "BIGINT", "FK -> Dim_HocKy", "No", "Dim_HocKy", "Khóa ngoại liên kết học kỳ", "20231", "code_presentation"],
                [60, "Fact_HocVu_HocKy", "enrolled_credits", "Số Tín Chỉ Đăng Ký Kỳ", "INT", "Aggregated", "No", "SUM(Dim_HocPhan.credits)", "Tổng số tín chỉ sinh viên đăng ký học trong kỳ (thường từ 12-24 tín chỉ)", "18", "Curricular units 1st/2nd sem enrolled (UCI)"],
                [61, "Fact_HocVu_HocKy", "earned_credits", "Số Tín Chỉ Đạt Trong Kỳ", "INT", "Calculated", "No", "SUM(TC môn đạt - Điểm >= D)", "Số tín chỉ hoàn thành thành công trong học kỳ", "15", "Curricular units approved (UCI)"],
                [62, "Fact_HocVu_HocKy", "failed_credits", "Số Tín Chỉ Rớt (Điểm F)", "INT", "Calculated", "No", "enrolled_credits - earned_credits", "Số tín chỉ bị trượt trong kỳ (phải đăng ký học lại)", "3", "Curricular units failed / without evaluations"],
                [63, "Fact_HocVu_HocKy", "cumulative_credits", "Tổng Tín Chỉ Tích Lũy", "INT", "Calculated", "No", "Cộng dồn các kỳ trước", "Tổng số tín chỉ sinh viên đã tích lũy từ đầu khóa học", "48", "Cumulative credits earned"],
                [64, "Fact_HocVu_HocKy", "gpa_semester", "Điểm GPA Học Kỳ (Hệ 4)", "DECIMAL(3,2)", "Calculated", "No", "SUM(score_4 * credits) / enrolled_credits", "Điểm trung bình học kỳ theo thang 4 chuẩn Thông tư 08/2021", "2.42", "Semester GPA / Curricular grade (UCI)"],
                [65, "Fact_HocVu_HocKy", "cpa_cumulative", "Điểm CPA Tích Lũy (Hệ 4)", "DECIMAL(3,2)", "Calculated", "No", "SUM(score_4 * credits) / cumulative_credits", "Điểm trung bình chung tích lũy toàn khóa đến thời điểm hiện tại", "2.35", "Cumulative GPA"],
                [66, "Fact_HocVu_HocKy", "training_point", "Điểm Rèn Luyện (DRL)", "INT", "Hệ thống CTSV", "No", "Đánh giá điểm rèn luyện (thang 100)", "Điểm đánh giá đạo đức, kỷ luật và hoạt động phong trào (thang 100)", "72", "Extra-curricular / Conduct score"],
                [67, "Fact_HocVu_HocKy", "training_grade", "Xếp Loại Rèn Luyện", "VARCHAR(20)", "Calculated", "No", "Quy chế CTSV", "Xuất sắc (90-100), Tốt (80-89), Khá (65-79), Trung bình (50-64), Yếu (35-49), Kém (<35)", "Kha", "Conduct grade"],
                [68, "Fact_HocVu_HocKy", "tuition_debt_amount", "Số Tiền Học Phí Còn Nợ", "DECIMAL(12,0)", "Phòng Kế toán", "No", "Học phí phải đóng - Đã đóng", "Số tiền nợ học phí của sinh viên tính đến hạn chót (VND)", "0", "Tuition fees up to date (UCI: 1/0)"],
                [69, "Fact_HocVu_HocKy", "is_tuition_debt", "Cờ Nợ Học Phí", "BOOLEAN", "Calculated", "No", "IF(tuition_debt_amount > 0, 1, 0)", "1 nếu đang nợ học phí (nguy cơ bị khóa tài khoản, cấm thi), 0 nếu đã hoàn thành", "0 (Khong no)", "Tuition fees up to date (UCI)"],
                [70, "Fact_HocVu_HocKy", "academic_warning_level", "Mức Cảnh Báo Học Vụ", "INT", "Calculated", "No", "Chiếu theo Điều 11 TT 08/2021", "0: Bình thường; 1: Cảnh báo Mức 1; 2: Cảnh báo Mức 2; 3: Buộc thôi học", "0", "Official Academic Warning Level"],
                [71, "Fact_HocVu_HocKy", "times_warned_cumulative", "Số Lần Đã Bị Cảnh Báo", "INT", "Calculated", "No", "COUNT(cảnh báo tích lũy)", "Tổng số lần đã từng bị xử lý cảnh cáo học vụ từ đầu khóa đến nay", "1", "Previous warnings count"]
            ]
        },
        {
            "group_name": "BẢNG 7: DataMart_Student_Risk_Flat (Bảng Phẳng Đặc Trưng Mô Hình Machine Learning)",
            "fields": [
                [72, "DataMart_Student_Risk_Flat", "flat_id", "Mã Dòng Đặc Trưng ML", "BIGINT", "PK", "No", "Hệ thống tự sinh", "Khóa chính của từng mẫu huấn luyện/dự báo trong bảng phẳng", "1", "N/A"],
                [73, "DataMart_Student_Risk_Flat", "student_code", "Mã Số Sinh Viên (MSSV)", "VARCHAR(20)", "Index", "No", "Dim_SinhVien", "Mã sinh viên dùng tra cứu và hiển thị Dashboard", "2021600123", "id_student (OULAD)"],
                [74, "DataMart_Student_Risk_Flat", "academic_year_order", "Sinh Viên Năm Thứ", "INT", "Calculated", "No", "Học kỳ hiện tại - Năm nhập học + 1", "Năm đào tạo của sinh viên: Năm 1, Năm 2, Năm 3, Năm 4", "3", "Academic year level"],
                [75, "DataMart_Student_Risk_Flat", "admission_score_norm", "Điểm Tuyển Sinh (Chuẩn Hóa)", "DECIMAL(4,3)", "Calculated", "Yes", "admission_score / 30.0", "Điểm đầu vào chuẩn hóa về đoạn [0, 1]", "0.883", "Admission grade norm (UCI)"],
                [76, "DataMart_Student_Risk_Flat", "priority_flag", "Cờ Chính Sách Ưu Tiên", "BOOLEAN", "Calculated", "No", "IF(priority_group IS NOT NULL, 1, 0)", "Sinh viên thuộc diện chính sách khó khăn / cần hỗ trợ đặc biệt", "0", "disability (OULAD)"],
                [77, "DataMart_Student_Risk_Flat", "credits_registered", "Tín Chỉ Đăng Ký Trong Kỳ", "INT", "Fact_HocVu_HocKy", "No", "enrolled_credits", "Số lượng tín chỉ sinh viên gánh trong học kỳ này", "18", "Curricular units enrolled (UCI)"],
                [78, "DataMart_Student_Risk_Flat", "credit_completion_ratio", "Tỷ Lệ Hoàn Thành Tín Chỉ", "DECIMAL(4,3)", "Calculated", "No", "earned_credits / enrolled_credits", "Tỷ lệ tín chỉ đậu trên tổng số đăng ký (1.0 = đậu hết, 0.0 = rớt sạch)", "0.833", "Approved / Enrolled ratio"],
                [79, "DataMart_Student_Risk_Flat", "cumulative_credit_debt", "Tổng Số Tín Chỉ Nợ Tích Lũy", "INT", "Fact_HocVu_HocKy", "No", "SUM(failed_credits chưa học lại)", "Tổng số tín chỉ nợ đọng chưa trả (đe dọa chạm trần 24 TC bị đuổi học)", "6", "Cumulative failed credits"],
                [80, "DataMart_Student_Risk_Flat", "gpa_current_semester", "Điểm GPA Kỳ Hiện Tại (Hệ 4)", "DECIMAL(3,2)", "Fact_HocVu_HocKy", "No", "gpa_semester", "Điểm trung bình học kỳ hiện tại hệ 4", "2.42", "Semester GPA / avg_score (OULAD)"],
                [81, "DataMart_Student_Risk_Flat", "cpa_cumulative_score", "Điểm CPA Tích Lũy (Hệ 4)", "DECIMAL(3,2)", "Fact_HocVu_HocKy", "No", "cpa_cumulative", "Điểm trung bình chung tích lũy tính đến kỳ đánh giá", "2.35", "Cumulative GPA"],
                [82, "DataMart_Student_Risk_Flat", "cpa_growth_delta", "Độ Tăng Trưởng CPA (Delta)", "DECIMAL(4,2)", "Calculated", "Yes", "CPA_ky_nay - CPA_ky_truoc", "Độ dốc học tập: Dương là tiến bộ, Âm là tụt dốc học lực", "-0.15", "Performance trajectory"],
                [83, "DataMart_Student_Risk_Flat", "failed_courses_count", "Số Môn Bị Điểm F Trong Kỳ", "INT", "Fact_KetQuaHocPhan", "No", "COUNT(*) IF(is_passed == 0)", "Số môn học sinh viên bị rớt trong kỳ", "1", "failures (Cortez) / failed courses"],
                [84, "DataMart_Student_Risk_Flat", "training_point_norm", "Điểm Rèn Luyện (Chuẩn Hóa)", "DECIMAL(4,3)", "Calculated", "No", "training_point / 100.0", "Điểm rèn luyện đạo đức chuẩn hóa về đoạn [0, 1]", "0.720", "Conduct score norm"],
                [85, "DataMart_Student_Risk_Flat", "tuition_debt_flag", "Cờ Nợ Học Phí", "BOOLEAN", "Fact_HocVu_HocKy", "No", "is_tuition_debt", "1: Đang nợ học phí (nguy cơ cấm thi/buộc dừng học); 0: Không nợ", "0", "Tuition fees up to date (UCI)"],
                [86, "DataMart_Student_Risk_Flat", "lms_total_clicks", "Tổng Tương Tác LMS (Clicks)", "INT", "Fact_TuongTac_LMS", "No", "total_clicks", "Tổng số lượt click tài nguyên bài giảng online trong kỳ", "620", "total_clicks (OULAD)"],
                [87, "DataMart_Student_Risk_Flat", "lms_active_days", "Số Ngày Học LMS Tích Cực", "INT", "Fact_TuongTac_LMS", "No", "active_days", "Số ngày riêng biệt đăng nhập học tập trên hệ thống trực tuyến", "28", "active_days (OULAD)"],
                [88, "DataMart_Student_Risk_Flat", "lms_late_submits", "Số Bài Tập Nộp Trễ Hạn", "INT", "Fact_TuongTac_LMS", "No", "late_submissions_count", "Số lần nộp bài tập trễ hạn deadline quy định", "2", "n_late (OULAD)"],
                [89, "DataMart_Student_Risk_Flat", "lms_avg_quiz", "Điểm Quiz Trực Tuyến LMS", "DECIMAL(3,1)", "Fact_TuongTac_LMS", "Yes", "avg_quiz_score", "Điểm trung bình các bài kiểm tra ngắn online", "7.2", "avg_quiz_score"],
                [90, "DataMart_Student_Risk_Flat", "previous_academic_warnings", "Số Lần Cảnh Báo HV Quá Khứ", "INT", "Fact_HocVu_HocKy", "No", "times_warned_cumulative", "Số lần đã nhận quyết định cảnh cáo học vụ từ trường", "1", "Previous warnings"],
                [91, "DataMart_Student_Risk_Flat", "risk_score_continuous", "Điểm Rủi Ro Liên Tục Dự Báo", "DECIMAL(4,3)", "Model Output", "Yes", "Mô hình xác suất P(Risk)", "Xác suất mô hình dự đoán sinh viên rơi vào nhóm nguy cơ (0.000 -> 1.000)", "0.345", "Predicted failure probability"],
                [92, "DataMart_Student_Risk_Flat", "target_risk_level", "NHÃN PHÂN TẦNG RỦI RO (MỤC TIÊU)", "INT", "Target Variable", "No", "Quy chuẩn rủi ro 4 mức", "0: Thấp (Low); 1: Trung bình (Medium); 2: Cao (High); 3: Rất cao (Very High - Nguy cơ đuổi học)", "1", "risk_level (0, 1, 2, 3)"],
                [93, "DataMart_Student_Risk_Flat", "target_risk_name", "Tên Mức Rủi Ro", "VARCHAR(30)", "Display Target", "No", "Ánh xạ từ target_risk_level", "Tên gọi hiển thị thân thiện: An toàn / Cảnh báo nhẹ / Nguy cơ cao / Rất nguy cấp", "Trung binh (Medium)", "risk_label (Low, Medium, High, Very High)"]
            ]
        }
    ]
    
    # Render tables with Excel Row Grouping
    current_row = ws2.max_row + 1
    zebra = False
    
    for tbl in tables_data:
        # Group Header Row
        ws2.cell(row=current_row, column=1, value="").fill = group_fill
        ws2.cell(row=current_row, column=2, value=tbl["group_name"]).font = group_header_font
        ws2.cell(row=current_row, column=2).fill = group_fill
        for c_idx in range(3, len(columns_spec) + 1):
            ws2.cell(row=current_row, column=c_idx, value="").fill = group_fill
            ws2.cell(row=current_row, column=c_idx).border = data_border
        ws2.cell(row=current_row, column=1).border = data_border
        ws2.cell(row=current_row, column=2).border = data_border
        ws2.row_dimensions[current_row].height = 26
        
        start_group_row = current_row + 1
        current_row += 1
        
        # Group Data Rows
        for f in tbl["fields"]:
            ws2.append(f)
            r = ws2.max_row
            fill_to_use = zebra_fill if zebra else PatternFill(fill_type=None)
            
            # Special highlighting for target variable
            if f[2] in ["target_risk_level", "target_risk_name"]:
                fill_to_use = accent_orange_fill
            elif f[2] in ["gpa_semester", "cpa_cumulative", "course_score_10", "course_score_4"]:
                fill_to_use = accent_green_fill
            elif f[2] in ["academic_warning_level", "is_barred_from_exam", "is_tuition_debt"]:
                fill_to_use = accent_yellow_fill
                
            for c_idx in range(1, len(f) + 1):
                cell = ws2.cell(row=r, column=c_idx)
                cell.font = bold_data_font if c_idx in [1, 3, 4] else data_font
                if c_idx == 3:
                    cell.font = code_font
                if fill_to_use.fill_type:
                    cell.fill = fill_to_use
                cell.border = data_border
                
                # Alignments
                if c_idx in [1, 5, 6, 7]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c_idx in [8, 9, 10, 11]:
                    cell.alignment = Alignment(vertical="center", wrap_text=True)
                else:
                    cell.alignment = Alignment(vertical="center")
                    
            ws2.row_dimensions[r].height = 24
            zebra = not zebra
            current_row += 1
            
        end_group_row = current_row - 1
        # Set outline/grouping on rows so user can expand/collapse
        ws2.row_dimensions.group(start_group_row, end_group_row, outline_level=1, hidden=False)
        
    # Auto column widths for Sheet 2
    col_widths_2 = {
        "A": 7,    # STT
        "B": 26,   # Nhóm Bảng
        "C": 28,   # Tên Trường
        "D": 28,   # Tên Tiếng Việt
        "E": 16,   # Kiểu DL
        "F": 18,   # Ràng buộc
        "G": 14,   # Cho phép Null
        "H": 36,   # Công thức tính
        "I": 55,   # Mô tả nghiệp vụ VN
        "J": 30,   # Giá trị mẫu
        "K": 35    # Ánh xạ quốc tế
    }
    for col_letter, width in col_widths_2.items():
        ws2.column_dimensions[col_letter].width = width

    # ---------------------------------------------------------
    # SHEET 3: QuyChuan_TinhDiem (QUY CHUẨN TÍNH ĐIỂM & CẢNH BÁO ĐH VN)
    # ---------------------------------------------------------
    ws3 = wb.create_sheet(title="3. QuyChuan_TinhDiem_CanhBao")
    ws3.views.sheetView[0].showGridLines = True
    
    ws3.append(["QUY CHUẨN TÍNH ĐIỂM TÍN CHỈ & TIÊU CHÍ PHÂN TẦNG RỦI RO HỌC VỤ ĐẠI HỌC VIỆT NAM"])
    ws3.append(["Căn cứ theo Điều 9 & Điều 11 Thông tư 08/2021/TT-BGDĐT ban hành Quy chế đào tạo trình độ đại học"])
    ws3.append([])
    
    ws3["A1"].font = title_font
    ws3["A2"].font = subtitle_font
    
    # Table 1: Grading Scale Conversion
    ws3.append(["BẢNG 1: QUY ĐỔI THANG ĐIỂM HỌC PHẦN (10 -> CHỮ -> 4) VÀ ĐÁNH GIÁ ĐẠT/RỚT"])
    ws3.cell(row=ws3.max_row, column=1).font = section_font
    
    t1_headers = ["Thang Điểm 10", "Thang Điểm Chữ", "Thang Điểm 4", "Xếp Loại Học Lực Học Phần", "Trạng Thái Đạt/Không Đạt", "Tác Động Đến Tín Chỉ & Rủi Ro"]
    ws3.append(t1_headers)
    t1_hdr_row = ws3.max_row
    for c_idx in range(1, len(t1_headers) + 1):
        c = ws3.cell(row=t1_hdr_row, column=c_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = header_border
    ws3.row_dimensions[t1_hdr_row].height = 25
    
    t1_data = [
        ["8.5 - 10.0", "A", "4.0", "Giỏi / Xuất sắc", "Đạt (Tích lũy)", "Hoàn thành xuất sắc, không có rủi ro"],
        ["8.0 - 8.4", "B+", "3.5", "Khá giỏi", "Đạt (Tích lũy)", "Học lực tốt, đóng góp kéo CPA lên cao"],
        ["7.0 - 7.9", "B", "3.0", "Khá", "Đạt (Tích lũy)", "Mức an toàn, đạt chuẩn xét tốt nghiệp loại Khá"],
        ["6.5 - 6.9", "C+", "2.5", "Trung bình khá", "Đạt (Tích lũy)", "Mức trung bình khá, cần duy trì"],
        ["5.5 - 6.4", "C", "2.0", "Trung bình", "Đạt (Tích lũy)", "Mức chuẩn tối thiểu để tốt nghiệp (CPA >= 2.0)"],
        ["5.0 - 5.4", "D+", "1.5", "Trung bình yếu", "Đạt (Tích lũy)", "Cảnh báo nhẹ: Tích lũy được tín chỉ nhưng làm tụt CPA chung"],
        ["4.0 - 4.9", "D", "1.0", "Yếu (Điểm vớt)", "Đạt (Tích lũy)", "Cảnh báo cao: Nếu có nhiều điểm D sẽ kéo CPA < 2.0, không đủ điều kiện ra trường"],
        ["< 4.0", "F", "0.0", "Kém (Không đạt)", "Không đạt (Rớt môn)", "RỦI RO RẤT CAO: 0 tín chỉ tích lũy, nợ môn, phải đóng tiền học lại"]
    ]
    for r_data in t1_data:
        ws3.append(r_data)
        r = ws3.max_row
        for c_idx in range(1, len(r_data) + 1):
            cell = ws3.cell(row=r, column=c_idx)
            cell.font = bold_data_font if c_idx in [1, 2, 3] else data_font
            cell.border = data_border
            if c_idx in [1, 2, 3, 5]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if r_data[1] == "F":
                cell.fill = accent_red_fill
            elif r_data[1] in ["D", "D+"]:
                cell.fill = accent_yellow_fill
            elif r_data[1] in ["A", "B+"]:
                cell.fill = accent_green_fill
        ws3.row_dimensions[r].height = 22
        
    ws3.append([])
    ws3.append([])
    
    # Table 2: Official Academic Warning Regulations (Thông tư 08/2021)
    ws3.append(["BẢNG 2: TIÊU CHÍ XỬ LÝ HỌC VỤ & CẢNH BÁO BUỘC THÔI HỌC (ĐIỀU 11 THÔNG TƯ 08/2021)"])
    ws3.cell(row=ws3.max_row, column=1).font = section_font
    
    t2_headers = ["Đối Tượng / Mốc Năm", "Ngưỡng GPA Học Kỳ Bị Cảnh Báo", "Ngưỡng CPA Tích Lũy Bị Cảnh Báo", "Giới Hạn Tín Chỉ Nợ Đọng", "Hậu Quả Pháp Lý & Quy Chế"]
    ws3.append(t2_headers)
    t2_hdr_row = ws3.max_row
    for c_idx in range(1, len(t2_headers) + 1):
        c = ws3.cell(row=t2_hdr_row, column=c_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = header_border
    ws3.row_dimensions[t2_hdr_row].height = 25
    
    t2_data = [
        ["Học kỳ đầu tiên (Năm 1 - HK1)", "GPA < 0.80", "CPA < 1.20", "Nợ > 50% tín chỉ đăng ký", "Cảnh báo học vụ Mức 1 (Gửi thông báo về gia đình)"],
        ["Học kỳ thứ hai (Năm 1 - HK2)", "GPA < 1.00", "CPA < 1.20", "Nợ > 12 tín chỉ", "Cảnh báo học vụ Mức 1 hoặc Mức 2"],
        ["Sinh viên năm 2", "GPA < 1.10", "CPA < 1.40", "Nợ > 16 tín chỉ", "Hạn chế số tín chỉ đăng ký kỳ sau (tối đa 14 TC)"],
        ["Sinh viên năm 3", "GPA < 1.10", "CPA < 1.60", "Nợ > 20 tín chỉ", "Cảnh báo học vụ Mức 2, buộc ký cam kết học tập"],
        ["Sinh viên năm 4 trở đi", "GPA < 1.10", "CPA < 1.80", "Nợ > 24 tín chỉ", "Nguy cơ không kịp thời gian đào tạo tối đa"],
        ["Bị cảnh báo 2 lần liên tiếp", "Tái phạm", "Không cải thiện", "Nợ đọng kéo dài", "CẢNH BÁO HỌC VỤ MỨC 2 - Đình chỉ 1 kỳ hoặc hạn chế đăng ký"],
        ["Bị cảnh báo 3 lần liên tiếp", "Tái phạm liên tục", "CPA không đạt chuẩn", "Vượt quá thời gian tối đa", "BUỘC THÔI HỌC (Đuổi học chính thức theo quy chế)"]
    ]
    for r_data in t2_data:
        ws3.append(r_data)
        r = ws3.max_row
        for c_idx in range(1, len(r_data) + 1):
            cell = ws3.cell(row=r, column=c_idx)
            cell.font = bold_data_font if c_idx == 1 else data_font
            cell.border = data_border
            if c_idx in [2, 3]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if "BUỘC THÔI HỌC" in r_data[4]:
                cell.fill = accent_red_fill
            elif "Mức 2" in r_data[4]:
                cell.fill = accent_orange_fill
        ws3.row_dimensions[r].height = 23
        
    ws3.append([])
    ws3.append([])
    
    # Table 3: 4-Tier Risk Stratification Matrix (Ma trận Phân tầng Rủi ro 4 mức)
    ws3.append(["BẢNG 3: MA TRẬN ĐỊNH LƯỢNG PHÂN TẦNG RỦI RO 4 CẤP ĐỘ (RISK STRATIFICATION MATRIX)"])
    ws3.cell(row=ws3.max_row, column=1).font = section_font
    
    t3_headers = ["Mã Rủi Ro (Code)", "Tên Mức Rủi Ro (Label)", "Màu Chỉ Báo", "Khoảng CPA Tích Lũy", "Tín Chỉ Nợ Kỳ Này", "Tương Tác LMS & Chuyên Cần", "Điểm Rèn Luyện (DRL)", "Học Phí", "Hành Động Can Thiệp Đề Xuất"]
    ws3.append(t3_headers)
    t3_hdr_row = ws3.max_row
    for c_idx in range(1, len(t3_headers) + 1):
        c = ws3.cell(row=t3_hdr_row, column=c_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = header_border
    ws3.row_dimensions[t3_hdr_row].height = 28
    
    t3_data = [
        ["0", "Thấp (Low Risk)", "Xanh lá (Green)", "CPA >= 2.50 (Khá - Giỏi)", "0 tín chỉ nợ", "Clicks LMS cao, không trễ hạn bài tập", "DRL >= 70 (Khá - Tốt)", "Đã hoàn thành", "Khen thưởng, định hướng nghiên cứu khoa học / học bổng"],
        ["1", "Trung bình (Medium Risk)", "Vàng (Yellow)", "2.00 <= CPA < 2.50", "Nợ 1 - 3 tín chỉ (1 môn)", "LMS mức trung bình, có 1-2 lần nộp trễ bài", "50 <= DRL < 70 (Trung bình)", "Đã hoàn thành", "Email nhắc nhở tự động, khuyến nghị ôn tập các môn D/D+"],
        ["2", "Cao (High Risk)", "Cam (Orange)", "1.50 <= CPA < 2.00 HOẶC GPA kỳ < 1.50", "Nợ 4 - 7 tín chỉ (2 môn rớt)", "Ít đăng nhập LMS, vắng học > 15%, nguy cơ cấm thi", "35 <= DRL < 50 (Yếu)", "Có thể chậm nộp", "Cố vấn học tập (CVHT) hẹn gặp trực tiếp, lập kế hoạch trả nợ môn"],
        ["3", "Rất cao (Very High Risk)", "Đỏ (Red)", "CPA < 1.50 HOẶC GPA < 1.00", "Nợ >= 8 tín chỉ (>= 3 môn) HOẶC nợ lũy kế > 20 TC", "Bỏ học LMS, vắng > 25% (bị cấm thi môn chính)", "DRL < 35 (Kém) HOẶC nợ học phí", "Nợ học phí kéo dài", "Can thiệp khẩn cấp: Gửi thông báo phụ huynh, tư vấn tâm lý, nguy cơ thôi học"]
    ]
    for r_data in t3_data:
        ws3.append(r_data)
        r = ws3.max_row
        fill_color = accent_green_fill if r_data[0] == "0" else (
            accent_yellow_fill if r_data[0] == "1" else (
                accent_orange_fill if r_data[0] == "2" else accent_red_fill
            )
        )
        for c_idx in range(1, len(r_data) + 1):
            cell = ws3.cell(row=r, column=c_idx)
            cell.font = bold_data_font if c_idx <= 3 else data_font
            cell.border = data_border
            cell.fill = fill_color
            if c_idx in [1, 2, 3]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in [4, 5, 6, 7, 8, 9]:
                cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws3.row_dimensions[r].height = 36
        
    ws3.column_dimensions["A"].width = 22
    ws3.column_dimensions["B"].width = 28
    ws3.column_dimensions["C"].width = 25
    ws3.column_dimensions["D"].width = 30
    ws3.column_dimensions["E"].width = 24
    ws3.column_dimensions["F"].width = 35
    ws3.column_dimensions["G"].width = 24
    ws3.column_dimensions["H"].width = 20
    ws3.column_dimensions["I"].width = 45

    # ---------------------------------------------------------
    # SHEET 4: DeXuat_CaiTien (ĐỀ XUẤT CẢI TIẾN ĐỀ TÀI SÁT THỰC TẾ)
    # ---------------------------------------------------------
    ws4 = wb.create_sheet(title="4. DeXuat_CaiTien_DeTai")
    ws4.views.sheetView[0].showGridLines = True
    
    ws4.append(["ĐỀ XUẤT CẢI TIẾN HỆ THỐNG STUDENT RISK STRATIFICATION SÁT VỚI THỰC TẾ VIỆT NAM"])
    ws4.append(["Các định hướng nâng cấp kiến trúc, thuật toán và tính năng thực tiễn cho trường đại học / học viện"])
    ws4.append([])
    
    ws4["A1"].font = title_font
    ws4["A2"].font = subtitle_font
    
    proposals_headers = ["STT", "Nhóm Cải Tiến", "Tên Đề Xuất Cải Tiến", "Vấn Đề Thực Tế Cần Giải Quyết", "Giải Pháp Công Nghệ / Thuật Toán", "Lợi Ích Thực Tiễn Cho Nhà Trường & Sinh Viên", "Mức Độ Ưu Tiên"]
    ws4.append(proposals_headers)
    p_hdr_row = ws4.max_row
    for c_idx in range(1, len(proposals_headers) + 1):
        c = ws4.cell(row=p_hdr_row, column=c_idx)
        c.font = table_header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = header_border
    ws4.row_dimensions[p_hdr_row].height = 28
    
    proposals_data = [
        [
            1, "1. Dữ liệu & Tích hợp", "Tích hợp API Đa Nguồn (ERP Đào Tạo + LMS Moodle)", 
            "Hiện tại hệ thống dùng file CSV tĩnh. Trong thực tế, dữ liệu điểm nằm ở cổng Đào tạo (Edusoft, PSC, Daotao.vn), còn hành vi tương tác nằm ở LMS Moodle/Canvas.", 
            "Xây dựng ETL Connector đồng bộ định kỳ qua RESTful API / Webhook từ Moodle và cơ sở dữ liệu quản lý sinh viên SIS/ERP.", 
            "Hệ thống tự động cập nhật dữ liệu hàng đêm; không cần trích xuất file thủ công; dữ liệu luôn tươi mới (near real-time).", 
            "Ưu tiên 1 (Cao)"
        ],
        [
            2, "2. Mô hình & Thuật toán", "Cơ Chế Cảnh Báo Sớm Đa Mốc (Multi-Milestone Early Warning)", 
            "Nếu chỉ dự đoán rủi ro khi kỳ học kết thúc thì đã quá muộn để cứu sinh viên rớt môn hoặc bị cấm thi.", 
            "Chia nhỏ bài toán dự đoán theo 4 mốc: \n- Tuần 4: Dự báo dựa trên Chuyên cần & Tương tác LMS ban đầu\n- Tuần 8: Dự báo sau khi có Điểm giữa kỳ & Bài tập lớn\n- Tuần 12: Dự báo rủi ro Bị cấm thi cuối kỳ\n- Tuần 16: Tổng kết kỳ & Dự báo Cảnh báo học vụ tích lũy", 
            "Giảng viên và Cố vấn học tập (CVHT) có thể can thiệp ngay từ tuần 4-8, giúp sinh viên kịp thời cải thiện trước khi thi.", 
            "Ưu tiên 1 (Cao)"
        ],
        [
            3, "3. Giải thích AI (XAI)", "Tích Hợp SHAP / LIME Giải Thích Rủi Ro Cá Nhân Hóa", 
            "Mô hình Black-box (như LightGBM, XGBoost) chỉ trả về Risk Level 0, 1, 2, 3 nhưng sinh viên và thầy cô không hiểu 'Tại sao tôi lại bị xếp loại rủi ro cao?'.", 
            "Tích hợp thư viện SHAP (SHapley Additive exPlanations) trên giao diện web để trực quan hóa Top 3 yếu tố tiêu cực kéo rủi ro lên (ví dụ: 'Nợ môn Giải tích (-0.3)', 'Vắng 3 buổi học (-0.2)', 'Chưa nộp bài tập tuần 6').", 
            "Tạo sự minh bạch, tăng độ tin cậy của mô hình, giúp sinh viên biết chính xác mình cần sửa đổi hành vi nào.", 
            "Ưu tiên 1 (Cao)"
        ],
        [
            4, "4. Tính năng can thiệp", "Động Cơ Gợi Ý Hành Động Can Thiệp (Prescriptive Analytics Engine)", 
            "Biết sinh viên có rủi ro cao nhưng không có hướng dẫn hành động cụ thể thì hệ thống mới chỉ dừng ở mức 'chẩn đoán' mà chưa 'chữa bệnh'.", 
            "Xây dựng Rule-based Recommender kết hợp phân tích dự đoán để sinh ra khuyến nghị cụ thể: \n- Nếu do nợ học phí -> Gửi link hướng dẫn xin hoãn/miễn giảm học phí\n- Nếu do điểm giữa kỳ < 4.0 -> Gợi ý đăng ký lớp trợ giảng (TA) phụ đạo\n- Nếu vắng học nhiều -> Thông báo tự động gửi SMS/Zalo cho phụ huynh", 
            "Chuyển đổi từ Predictive (dự đoán) sang Prescriptive (đưa ra giải pháp hành động), tăng giá trị ứng dụng thực tiễn của đề tài.", 
            "Ưu tiên 2 (Trung bình)"
        ],
        [
            5, "5. Phân quyền nghiệp vụ", "Giao Diện Chuyên Biệt Cho Cố Vấn Học Tập (CVHT) & Khoa", 
            "Các trường ĐH Việt Nam vận hành theo mô hình Cố vấn học tập (CVHT) quản lý theo Lớp sinh hoạt và Ban Chủ nhiệm Khoa.", 
            "Bổ sung vai trò CVHT trong Role-Based Access Control: CVHT có dashboard riêng xem danh sách sinh viên lớp mình phụ trách, lọc theo mức rủi ro, bấm 1 nút gửi email cảnh báo hàng loạt và lưu nhật ký tư vấn (Counseling Notes).", 
            "Phù hợp trực tiếp với quy trình làm việc thực tế tại các trường đại học tại Việt Nam, tăng tính khả thi khi nghiệm thu đề tài.", 
            "Ưu tiên 2 (Trung bình)"
        ],
        [
            6, "6. So sánh thực nghiệm", "Benchmarking Đa Tập Dữ Liệu (Cross-Dataset Evaluation Protocol)", 
            "Đề tài hiện mới kiểm nghiệm trên OULAD, dễ bị hội đồng đánh giá là phụ thuộc vào một miền dữ liệu cụ thể (chưa chứng minh được tính tổng quát).", 
            "Đưa 3 bộ dữ liệu: OULAD (Online UK), UCI Dropout (Đại học tín chỉ Bồ Đào Nha), và Data Mart Việt Nam vào chung một pipeline thực nghiệm so sánh: LightGBM, XGBoost, Random Forest, CatBoost, Logistic Regression với các độ đo Macro F1, Balanced Accuracy, Recall nhóm Very High.", 
            "Nâng tầm khoa học của đề tài, dễ dàng viết thành bài báo khoa học (Hội nghị / Tạp chí chuyên ngành giáo dục & CNTT).", 
            "Ưu tiên 1 (Cao)"
        ]
    ]
    
    for r_data in proposals_data:
        ws4.append(r_data)
        r = ws4.max_row
        p_prio = r_data[6]
        fill_color = accent_orange_fill if "Ưu tiên 1" in p_prio else accent_yellow_fill
        for c_idx in range(1, len(r_data) + 1):
            cell = ws4.cell(row=r, column=c_idx)
            cell.font = bold_data_font if c_idx in [1, 2, 3] else data_font
            cell.border = data_border
            if c_idx in [1, 7]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.fill = fill_color
            else:
                cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws4.row_dimensions[r].height = 48
        
    ws4.column_dimensions["A"].width = 7
    ws4.column_dimensions["B"].width = 22
    ws4.column_dimensions["C"].width = 32
    ws4.column_dimensions["D"].width = 40
    ws4.column_dimensions["E"].width = 45
    ws4.column_dimensions["F"].width = 42
    ws4.column_dimensions["G"].width = 18

    import os
    out_path_1 = "c:/Nam 4 ki 1/Hoc may/BTL/data/DataMart_ChuanHoa_Student_Risk_VN.xlsx"
    out_path_2 = "c:/Nam 4 ki 1/Hoc may/data/DataMart_ChuanHoa_Student_Risk_VN.xlsx"
    
    os.makedirs(os.path.dirname(out_path_1), exist_ok=True)
    os.makedirs(os.path.dirname(out_path_2), exist_ok=True)
    
    wb.save(out_path_1)
    wb.save(out_path_2)
    print(f"Workbook successfully saved to:\n  1. {out_path_1}\n  2. {out_path_2}")

if __name__ == "__main__":
    build_datamart_workbook()
