# ETL — Tài Liệu Ánh Xạ & Hướng Dẫn Thực Hiện

> **Dự án:** Student Risk Stratification System  
> Ba nguồn dữ liệu thô được ánh xạ về chung **22 cột chuẩn** của DataMart Việt Nam,  
> phục vụ bài toán **Học Chéo OOD (Out-Of-Distribution Generalization)**:
>
> - `OULAD` → Tập **Train / Val** (học trọng số mô hình)
> - `UCI Dropout` → Tập **Test độc lập 1** (Blind Predict)
> - `UCI Perf` → Tập **Test độc lập 2** (Blind Predict)

---

## 1. Đặc Trưng Từng Nguồn Dữ Liệu Thô

| Thuộc tính | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Open University UK | Polytechnic Institute Bragança | Cortez & Silva, 2008 |
| **File đầu vào** | `student_features_labeled.csv` (đã qua `01_data_cleaning.ipynb`) | `uci_dropout/data.csv` | `student-mat.csv` + `student-por.csv` |
| **Số dòng** | ~32,593 (sau dedup theo `id_student`) | 4,424 | 649 + 649 = 1,298 |
| **Thang điểm** | 0–100 (`avg_score`) | 0–20 (grade per semester) | 0–20 (G1, G2, G3) |
| **Ngưỡng qua môn** | 40 / 100 | 10 / 20 | 10 / 20 |
| **Có dữ liệu LMS** | ✅ (`total_clicks`, `active_days`, `n_late`, `avg_tma_score`) | ❌ | ❌ |
| **Biến mục tiêu gốc** | `final_result`: Pass/Distinction/Fail/Withdrawn | `Target`: Graduate/Enrolled/Dropout | `G3` (điểm cuối kỳ) |
| **Vai trò OOD** | **TRAIN / VAL** | **TEST 1** | **TEST 2** |

---

## 2. Các Vấn Đề Cần Giải Quyết Trong ETL

Dưới đây là 5 nhóm vấn đề kỹ thuật được xác định và cách xử lý:

### 2.1 Sự Lệch Ngưỡng Qua Môn Giữa Các Hệ Thống Điểm

**Vấn đề:** OULAD và UCI dùng hai thang điểm hoàn toàn khác nhau. Nếu chỉ ánh xạ tuyến tính đơn giản (chia cho max), ngưỡng "qua môn" sẽ rơi vào các giá trị khác nhau trên thang GPA [0, 4]:

| Nguồn | Điểm qua môn gốc | Ánh xạ tuyến tính | Ngưỡng qua môn trên GPA [0,4] |
|---|---|---|---|
| OULAD | 40 / 100 | `score / 100 × 4` | **1.6** ❌ |
| UCI | 10 / 20 | `grade / 20 × 4` | **2.0** |

Khi mô hình học từ OULAD (Train) và dự đoán trên UCI (Test), cây quyết định sẽ học rằng "ngưỡng rủi ro = 1.6 GPA", nhưng trên UCI, sinh viên "sát ngưỡng qua môn" thực sự có GPA = 2.0. Điều này dẫn đến **phân loại sai hệ thống**.

**Giải pháp — Piecewise Linear Alignment:**  
Chia hàm ánh xạ thành 2 đoạn, đảm bảo ngưỡng qua môn **luôn = 2.0** ở cả hai hệ thống:

```
OULAD (score ∈ [0, 100], qua môn = 40):
  score < 40  →  GPA = (score / 40) × 2.0          ← vùng trượt: [0, 40) → [0, 2)
  score ≥ 40  →  GPA = 2.0 + ((score − 40) / 60) × 2.0  ← vùng đạt: [40, 100] → [2, 4]

UCI (grade ∈ [0, 20], qua môn = 10):
  grade < 10  →  GPA = (grade / 10) × 2.0           ← vùng trượt: [0, 10) → [0, 2)
  grade ≥ 10  →  GPA = 2.0 + ((grade − 10) / 10) × 2.0 ← vùng đạt: [10, 20] → [2, 4]
```

### 2.2 Giá Trị Bị Gán Cứng (Hardcoded Constants)

**Vấn đề:** Nhiều cột không có nguồn dữ liệu trực tiếp bị gán một con số cố định (ví dụ: 0.7 cho điểm rèn luyện, 0.5 cho điểm đầu vào, 0 cho nợ tín chỉ). Điều này khiến **phương sai của cột đó = 0** trên tập Train (OULAD) — cây quyết định không thể split trên cột hằng số, và cột đó sẽ bị **bỏ qua hoàn toàn** trong quá trình học, kể cả khi tập Test có dữ liệu thực.

**Nguyên tắc chung:** Bất kỳ cột nào bị gán cứng cần được thay thế bằng **biến đại diện (Proxy)** có phương sai thực, hoặc bị gán `NaN` để thuật toán tự xử lý, hoặc nếu không có proxy hợp lý thì phải được ghi nhận rõ ràng là "thiếu thông tin — không đưa vào mô hình".

### 2.3 Feature Leakage Ngữ Nghĩa Tại Cột LMS (Vấn Đề OOD Nghiêm Trọng Nhất)

**Vấn đề:** OULAD (Train) có dữ liệu LMS đầy đủ. UCI (Test) hoàn toàn không có. Code cũ đang lấy **median từ OULAD (Train) đắp vào UCI (Test)**. Điều này gây ra "Feature Leakage Ngữ nghĩa": mô hình LightGBM học rằng "LMS ở mức median thì rủi ro X", nhưng trên thực tế median của OULAD và "không có LMS" là hai tình huống hoàn toàn khác nhau. Kết quả: **Model tự tin sai khi Blind Predict trên UCI**.

**Giải pháp — NaN Masking:** Gán `NaN` cho toàn bộ cột LMS của tập UCI.

| Cột | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| `lms_total_clicks` | Từ `total_clicks` (đã xử lý) | `NaN` ✅ | `NaN` ✅ |
| `lms_active_days` | Từ `active_days` | `NaN` ✅ | `NaN` ✅ |
| `lms_late_submits` | Từ `n_late` | `NaN` ✅ | `NaN` ✅ |
| `lms_avg_quiz` | Từ `avg_tma_score / 10` | `NaN` ✅ | `NaN` ✅ |

**Lý do dùng `NaN` thay vì Median:**
- LightGBM, XGBoost, CatBoost đều hỗ trợ xử lý `NaN` native — chúng sẽ học cách rẽ nhánh "dự phòng" (fallback branch) vào các biến GPA/Academic/Demographic khi không có LMS.
- Nếu dùng Median OULAD, mô hình sẽ tưởng rằng "học sinh UCI học trực tuyến ở mức trung bình" → sai lệch tín hiệu.

**⚠️ Lưu ý với Random Forest & Logistic Regression:**  
Random Forest và Logistic Regression **không xử lý `NaN` native**. Cần thêm bước preprocessing trong pipeline Modeling:
```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')   # áp dụng RIÊNG trên tập Train, rồi transform Test
```
Không thực hiện bước này trong ETL để tránh Data Leakage từ Test vào Train.

### 2.4 Thiếu Proxy Cho Các Cột Không Có Nguồn Tương Đương

Một số cột của DataMart VN không có trường dữ liệu tương ứng trong tập nguồn. Thay vì gán hằng số, ta dùng biến đại diện có tương quan:

| Cột DataMart | Thiếu ở nguồn | Proxy được dùng | Lý do |
|---|---|---|---|
| `admission_score_norm` | OULAD không có điểm tuyển sinh | `education_num / 4.0` (trình độ học vấn đã mã hóa từ `01_data_cleaning`) | Trình độ học vấn tương quan với năng lực đầu vào |
| `admission_score_norm` | UCI Perf không có điểm tuyển sinh | `(Medu + Fedu) / 8.0` | Nghiên cứu giáo dục học xác nhận học vấn phụ huynh tương quan với đầu vào |
| `training_point_norm` | UCI Perf không có điểm rèn luyện | `(1 − absences / 93).clip(0, 1)` | Vắng mặt nhiều → điểm rèn luyện thấp; 93 là giá trị max của absences |
| `cumulative_credit_debt` | OULAD không track nợ tín chỉ từng môn | `0` (hằng số) | Không có proxy hợp lý — ghi nhận là missing semantic |

### 2.5 Nhãn Mục Tiêu Không Có Mức "High (2)" Trong UCI Dropout

**Vấn đề:** UCI Dropout chỉ có 3 nhãn gốc: Graduate (→0), Enrolled (→1), Dropout (→3). Mức 2 (High) bị bỏ trống.

**Quyết định:** Giữ nguyên. Mức "High" trong UCI Dropout được dùng cho các trường hợp Target bị thiếu/null (`fillna(2)`). Trong mô hình OOD, sự bất đối xứng này là thực tế của dữ liệu thực tế và nên được phản ánh trung thực.

---

## 3. Bảng Mapping 22 Cột Chi Tiết

### Cột 1: `student_code`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `id_student` | index | index |
| **Công thức** | `"OU_" + str(id_student)` | `"UD_" + str(index)` | `"UP_" + str(index)` |
| **Ghi chú** | Prefix để tránh trùng ID giữa 3 tập khi concat | — | — |

### Cột 2: `academic_year_order`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `num_of_prev_attempts` | Không có | Không có |
| **Công thức** | `num_of_prev_attempts + 1` | `1` | `1` |
| **Ghi chú** | Hằng số 1 cho UCI vì không có thông tin năm học | — | — |

### Cột 3: `admission_score_norm` ∈ [0, 1]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn thô** | `education_num` (0–4, từ `01_data_cleaning`) | `Admission grade` (0–200) | `Medu`, `Fedu` (0–4 mỗi cột) |
| **Công thức** | `education_num / 4.0` | `Admission grade / 200.0` | `(Medu + Fedu) / 8.0` |
| **Vấn đề cũ** | Gán `0.5` → phương sai = 0 → biến chết ❌ | Đúng ✅ | Gán `0.5` → phương sai = 0 → biến chết ❌ |

### Cột 4: `priority_flag` ∈ {0, 1}
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `disability_num` (0/1 từ `01_data_cleaning`) | `Educational special needs` (0/1) | Không có |
| **Công thức** | `disability_num` trực tiếp | `Educational special needs` | `0` |

### Cột 5: `credits_registered`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `studied_credits` | `Curricular units 2nd sem (enrolled)` | Không có |
| **Công thức** | `studied_credits` | `enrolled_2nd × 3` (ECTS: 1 môn ≈ 3 tín chỉ) | `6` (2 môn × 3TC) |

### Cột 6: `credit_completion_ratio` ∈ [0, 1]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `final_result` | `enrolled`, `approved` (kỳ 2) | `G3` |
| **Công thức** | `1.0 if Pass/Distinction else 0.0` | `approved / enrolled` (guard chia 0) | `1.0 if G3 ≥ 10 else 0.0` |
| **Vấn đề cũ** | — | — | Dùng `G3 ≥ 5` → sai ngưỡng qua môn ❌ |

### Cột 7: `cumulative_credit_debt`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Không có | `enrolled - approved` (kỳ 2) | `failures` |
| **Công thức** | `0` | `(enrolled − approved).clip(0) × 3` | `failures × 6` |

### Cột 8: `gpa_current_semester` ∈ [0, 4]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `avg_score` (0–100) | `Curricular units 2nd sem (grade)` (0–20) | `G3` (0–20) |
| **Công thức (Piecewise)** | Xem §2.1 | Xem §2.1 | Xem §2.1 |
| **Ngưỡng qua môn → GPA** | 40 → **2.0** ✅ | 10 → **2.0** ✅ | 10 → **2.0** ✅ |

### Cột 9: `cpa_cumulative_score` ∈ [0, 4]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Không có lịch sử đa kỳ | Grade kỳ 1 + kỳ 2 | G1, G2, G3 |
| **Công thức** | `gpa_current_semester` (proxy) | `piecewise((grade1 + grade2) / 2)` | `piecewise((G1+G2+G3) / 3)` |

### Cột 10: `cpa_growth_delta` ∈ [-4, 4]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Không có | Grade kỳ 1 và kỳ 2 | G1 và G3 |
| **Công thức** | `0.0` | `piecewise(grade2) − piecewise(grade1)` | `piecewise(G3) − piecewise(G1)` |

### Cột 11: `failed_courses_count`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `final_result` | `enrolled − approved` (kỳ 2) | `failures` |
| **Công thức** | `1 if Fail else 0` | `(enrolled − approved).clip(0)` | `failures` |

### Cột 12: `training_point_norm` ∈ [0, 1]
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Không có | Không có | `absences` (0–93) |
| **Công thức** | `NaN` | `NaN` | `(1 − absences / 93).clip(0, 1)` |
| **Ghi chú** | Gán `NaN` thay vì `0.7` cứng; xử lý ở bước Modeling | — | 93 là giá trị `absences.max()` thực tế |

### Cột 13: `tuition_debt_flag` ∈ {0, 1}
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | Không có | `Tuition fees up to date` (1=đã nộp) | Không có |
| **Công thức** | `0` | `1 − Tuition fees up to date` | `0` |

### Cột 14–17: Nhóm LMS (xem §2.3 và bảng NaN Masking phía trên)

### Cột 18: `previous_academic_warnings`
| | OULAD | UCI Dropout | UCI Perf |
|---|---|---|---|
| **Nguồn** | `num_of_prev_attempts` | Không có | `failures` |
| **Công thức** | `num_of_prev_attempts` | `0` | `failures` |

### Cột 19: `risk_score_continuous` ∈ [0, 1]
Placeholder. Được sinh ra bởi mô hình ML ở chặng 2. Mặc định `0.0`.

### Cột 20–22: Nhóm Target

**Phân loại rủi ro 4 mức:**

| Mức | Nhãn | Ý nghĩa |
|---|---|---|
| 0 | Low | Đạt tốt, GPA cao |
| 1 | Medium | Có dấu hiệu cần theo dõi |
| 2 | High | Đang gặp khó khăn học vụ |
| 3 | Very High | Bỏ học / Rút môn / Trượt nặng |

**Quy tắc gán nhãn theo nguồn:**

| OULAD (`final_result` + `gpa`) | → `target_risk_level` |
|---|---|
| `Withdrawn` (bất kể GPA) | → 3 |
| `Fail` (bất kể GPA) | → 2 |
| `Pass/Distinction` và GPA ≥ 3.2 | → 0 |
| `Pass/Distinction` và GPA ≥ 2.5 | → 1 |
| `Pass/Distinction` và GPA < 2.5 | → 2 |

| UCI Dropout (`Target`) | → `target_risk_level` |
|---|---|
| `Graduate` | → 0 |
| `Enrolled` | → 1 |
| `Dropout` | → 3 |
| `(null)` | → 2 |

| UCI Perf (`G3`) | → `target_risk_level` |
|---|---|
| G3 < 10 | → 3 |
| 10 ≤ G3 < 12 | → 2 |
| 12 ≤ G3 < 14 | → 1 |
| G3 ≥ 14 | → 0 |

---

## 4. Tổng Hợp Vấn Đề & Trạng Thái

| # | Vấn đề | Mức độ | Trạng thái |
|---|---|---|---|
| 1 | GPA ánh xạ tuyến tính → ngưỡng qua môn lệch OOD | 🔴 Nghiêm trọng | ✅ Piecewise Alignment |
| 2 | LMS của UCI điền bằng Median → Feature Leakage ngữ nghĩa | 🔴 Nghiêm trọng | ✅ NaN Masking |
| 3 | `admission_score_norm` = 0.5 cứng → biến chết (phương sai = 0) | 🔴 Nghiêm trọng | ✅ Proxy từ education_num / Medu+Fedu |
| 4 | `credit_completion_ratio` UCI Perf dùng ngưỡng 5 (sai, đúng phải là 10) | 🟡 Vừa | ✅ Sửa `G3 ≥ 10` |
| 5 | `training_point_norm` = 0.7 cứng → biến chết ở Train | 🟡 Vừa | ✅ NaN (OULAD/UCI Drop), Proxy absences (UCI Perf) |
| 6 | `cpa_growth_delta` UCI tính tuyến tính thay vì piecewise | 🟡 Vừa | ✅ Piecewise |
| 7 | Đường dẫn hardcoded `D:/Study/School/kì_7/...` | 🔴 Nghiêm trọng | ✅ Dynamic `BASE_DIR` |
| 8 | Random Forest & Logistic Regression không xử lý NaN | 🟡 Vừa | ⚠️ Xử lý ở bước Modeling bằng `SimpleImputer` |

---

## 5. Cấu Trúc Notebook ETL

| Notebook | Nội dung | Output |
|---|---|---|
| `notebooks/01B_ETL_OULAD.ipynb` | Đọc `student_features_labeled.csv` → ánh xạ 22 cột | `oulad_datamart.csv` (tạm) |
| `notebooks/01C_ETL_UCI_Dropout.ipynb` | Đọc `uci_dropout/data.csv` → ánh xạ 22 cột | `uci_dropout_datamart.csv` (tạm) |
| `notebooks/01D_ETL_UCI_Perf.ipynb` | Đọc `student-mat/por.csv` → ánh xạ 22 cột | `uci_perf_datamart.csv` (tạm) |
| `notebooks/01B_ETL_DataMart.ipynb` | Đọc 3 file tạm → concat → QA → lưu Master | `DataMart_Student_Risk_Flat_Master.csv` |

---

## 6. Hướng Dẫn Chạy ETL

```bash
# Cách 1: Chạy qua Python script (nhanh hơn)
cd d:\Study\School\k7\new
python run_etl.py

# Cách 2: Chạy từng notebook theo thứ tự
# 01B_ETL_OULAD.ipynb  →  01C_ETL_UCI_Dropout.ipynb  →  01D_ETL_UCI_Perf.ipynb  →  01B_ETL_DataMart.ipynb
```

**Output cuối:** `data/processed/DataMart_Student_Risk_Flat_Master.csv`  
Phân biệt nguồn bằng cột `dataset_source`: `OULAD` | `UCI_Dropout` | `UCI_Perf`
