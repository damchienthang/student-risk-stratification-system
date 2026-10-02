# ETL Summary Report

> **Dự án:** Student Risk Stratification System  
> Ba nguồn dữ liệu được ETL về 22 cột chuẩn để phục vụ bài toán **Học Chéo OOD** với 5 mô hình.

---

## 1. Quy Mô Dữ Liệu

| Nguồn | Dòng gốc | Dòng sau ETL | Vai trò |
|---|---|---|---|
| OULAD (`student_features_labeled.csv`) | 32,593 | ~32,593 (dedup `id_student`) | Train / Val |
| UCI Dropout (`data.csv`) | 4,424 | 4,424 | Test độc lập 1 |
| UCI Perf (`student-mat.csv` + `student-por.csv`) | 1,298 | 1,298 | Test độc lập 2 |
| **Tổng Master** | — | **~38,315** | — |

---

## 2. Cấu Trúc 22 Cột DataMart Chuẩn Hóa

| # | Tên cột | Kiểu | Phạm vi | Trạng thái NaN |
|---|---|---|---|---|
| 1 | `student_code` | str | — | Không |
| 2 | `academic_year_order` | int | 1–4 | Không |
| 3 | `admission_score_norm` | float | [0, 1] | Không (có proxy) |
| 4 | `priority_flag` | int | {0, 1} | Không |
| 5 | `credits_registered` | int | 0–∞ | Không |
| 6 | `credit_completion_ratio` | float | [0, 1] | Không |
| 7 | `cumulative_credit_debt` | int | 0–∞ | Không |
| 8 | `gpa_current_semester` | float | [0, 4] | Không |
| 9 | `cpa_cumulative_score` | float | [0, 4] | Không |
| 10 | `cpa_growth_delta` | float | [-4, 4] | Không |
| 11 | `failed_courses_count` | int | 0–∞ | Không |
| 12 | `training_point_norm` | float | [0, 1] / NaN | **NaN ở OULAD & UCI Dropout** |
| 13 | `tuition_debt_flag` | int | {0, 1} | Không |
| 14 | `lms_total_clicks` | float | [0, ∞) / NaN | **NaN ở UCI_*** |
| 15 | `lms_active_days` | float | [0, ∞) / NaN | **NaN ở UCI_*** |
| 16 | `lms_late_submits` | float | [0, ∞) / NaN | **NaN ở UCI_*** |
| 17 | `lms_avg_quiz` | float | [0, 10] / NaN | **NaN ở UCI_*** |
| 18 | `previous_academic_warnings` | int | 0–∞ | Không |
| 19 | `risk_score_continuous` | float | [0, 1] | Không (= 0.0 placeholder) |
| 20 | `target_risk_level` | int | {0, 1, 2, 3} | Không |
| 21 | `target_risk_name` | str | Low/Medium/High/Very High | Không |
| 22 | `dataset_source` | str | OULAD/UCI_Dropout/UCI_Perf | Không |

---

## 3. Phân Phối Nhãn Target (Ước Lượng)

| Nhãn | Mức | OULAD | UCI Dropout | UCI Perf | Tổng ước lượng |
|---|---|---|---|---|---|
| Low | 0 | ~25% | ~50% | ~35% | ~30% |
| Medium | 1 | ~20% | ~18% | ~20% | ~20% |
| High | 2 | ~30% | ~5% | ~25% | ~25% |
| Very High | 3 | ~25% | ~27% | ~20% | ~25% |

> **Lưu ý:** Mất cân bằng nhãn cần xử lý ở bước Modeling bằng `class_weight='balanced'` (Logistic Regression, Random Forest) hoặc `scale_pos_weight` (XGBoost, LightGBM).

---

## 4. Ba Quyết Định Kỹ Thuật OOD Cốt Lõi

### 4.1 Piecewise Linear GPA Alignment
Đảm bảo ngưỡng "qua môn" = **GPA 2.0** ở cả OULAD (40/100) và UCI (10/20). Cây quyết định học được biên giới Pass/Fail chung, có thể áp dụng trực tiếp trên tập Test mà không cần điều chỉnh.

### 4.2 NaN Masking (không dùng Median Imputation trong ETL)
Cột LMS của UCI giữ nguyên `NaN`. Các thuật toán Boosting (LightGBM, XGBoost, CatBoost) học cách rẽ nhánh "dự phòng" tự nhiên. Với Random Forest và Logistic Regression, `SimpleImputer` được áp dụng **trong pipeline Modeling** (không trong ETL) để tránh Data Leakage từ Test vào Train.

### 4.3 Proxy Variables thay thế Hardcoded Constants
Các cột không có nguồn dữ liệu thực được thay thế bằng biến đại diện có tương quan thực nghiệm, đảm bảo phương sai > 0 trên tập Train để thuật toán có thể khai thác thông tin.

---

## 5. Checklist Trước Khi Sang Modeling

- [x] File `DataMart_Student_Risk_Flat_Master.csv` tồn tại trong `data/processed/`
- [x] Cột `dataset_source` phân biệt OULAD (Train) và UCI_* (Test)
- [x] Cột LMS của UCI_* là `NaN` (không phải 0 hay median)
- [x] Cột `training_point_norm` của OULAD và UCI_Dropout là `NaN`
- [x] GPA/CPA dùng Piecewise Alignment (ngưỡng = 2.0 nhất quán)
- [x] `admission_score_norm` có phương sai > 0 ở cả 3 nguồn
- [x] `credit_completion_ratio` UCI Perf dùng ngưỡng `G3 ≥ 10`
- [ ] **Cần làm:** Kiểm tra phân phối GPA và NaN trong notebook 01B_ETL_DataMart
- [ ] **Cần làm:** Xây dựng `SimpleImputer` trong pipeline của Random Forest & Logistic Regression
- [ ] **Cần làm:** Đánh giá Feature Importance sau training để xác nhận các Proxy Variables có đóng góp
