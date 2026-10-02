import pandas as pd
import numpy as np
import os

print("Starting Optimized OOD ETL Process...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def load_data():
    print("Loading OULAD...")
    info = pd.read_csv(f"{RAW_DIR}/studentInfo.csv")
    assess = pd.read_csv(f"{RAW_DIR}/studentAssessment.csv")
    reg = pd.read_csv(f"{RAW_DIR}/studentRegistration.csv")
    
    print("Loading UCI Dropout...")
    uci_d = pd.read_csv(f"{RAW_DIR}/uci_dropout/data.csv", sep=";")
    
    print("Loading UCI Performance...")
    uci_p_mat = pd.read_csv(f"{RAW_DIR}/uci_student_performance/student-mat.csv", sep=";")
    uci_p_por = pd.read_csv(f"{RAW_DIR}/uci_student_performance/student-por.csv", sep=";")
    uci_p = pd.concat([uci_p_mat, uci_p_por], ignore_index=True)
    
    return info, assess, reg, uci_d, uci_p

# MAPPING TỐI ƯU OOD: Cân bằng ranh giới qua môn (Piecewise Linear Alignment)
# Giúp mô hình học được "Khoảng cách đến điểm đỗ" thay vì giá trị tuyệt đối.
def map_oulad_gpa(s):
    if pd.isna(s): return 0.0
    if s < 40: return (s / 40.0) * 2.0
    return 2.0 + ((s - 40) / 60.0) * 2.0

def map_uci_gpa(g):
    if pd.isna(g): return 0.0
    if g < 10: return (g / 10.0) * 2.0
    return 2.0 + ((g - 10) / 10.0) * 2.0

def process_oulad(info, assess, reg):
    print("Processing OULAD (Train Set)...")
    avg_score = assess.groupby("id_student")["score"].mean().reset_index()
    avg_score["gpa_current_semester"] = avg_score["score"].apply(map_oulad_gpa)
    
    df = info.merge(avg_score, on="id_student", how="left")
    df["gpa_current_semester"] = df["gpa_current_semester"].fillna(0.0)
    
    out = pd.DataFrame()
    out["student_code"] = "OU_" + df["id_student"].astype(str)
    out["academic_year_order"] = df["num_of_prev_attempts"] + 1
    
    # Proxy cho Admission Score bằng trình độ học vấn
    ed_map = {'No Formal quals': 0.2, 'Lower Than A Level': 0.4, 'A Level or Equivalent': 0.6, 'HE Qualification': 0.8, 'Post Graduate': 1.0}
    out["admission_score_norm"] = df["highest_education"].map(ed_map).fillna(0.5)
    
    out["priority_flag"] = df["disability"].apply(lambda x: 1 if x == "Y" else 0)
    out["credits_registered"] = df["studied_credits"]
    out["credit_completion_ratio"] = df["final_result"].apply(lambda x: 1.0 if x in ["Pass", "Distinction"] else 0.0)
    out["cumulative_credit_debt"] = 0
    out["gpa_current_semester"] = df["gpa_current_semester"]
    out["cpa_cumulative_score"] = df["gpa_current_semester"]
    out["cpa_growth_delta"] = 0.0
    out["failed_courses_count"] = df["final_result"].apply(lambda x: 1 if x == "Fail" else 0)
    out["training_point_norm"] = 0.7
    out["tuition_debt_flag"] = 0
    
    # Lấy LMS features từ master file cũ (vì VLE quá lớn để đọc trong script nhẹ)
    old_dm_path = f"{PROCESSED_DIR}/DataMart_Student_Risk_Flat_Master.csv"
    if os.path.exists(old_dm_path):
        old_dm = pd.read_csv(old_dm_path)
        old_oulad = old_dm[old_dm['dataset_source'] == 'OULAD']
        lms_cols = ['student_code', 'lms_total_clicks', 'lms_active_days', 'lms_late_submits', 'lms_avg_quiz']
        out = out.merge(old_oulad[lms_cols], on='student_code', how='left')
        out['lms_total_clicks'] = out['lms_total_clicks'].fillna(1200)
        out['lms_active_days'] = out['lms_active_days'].fillna(60)
        out['lms_late_submits'] = out['lms_late_submits'].fillna(1)
        out['lms_avg_quiz'] = out['lms_avg_quiz'].fillna(7.0)
    else:
        out["lms_total_clicks"] = 1200
        out["lms_active_days"] = 60
        out["lms_late_submits"] = 1
        out["lms_avg_quiz"] = 7.0
        
    out["previous_academic_warnings"] = df["num_of_prev_attempts"]
    out["risk_score_continuous"] = 0.0
    
    def get_target(row):
        res = row["final_result"]
        gpa = row["gpa_current_semester"]
        if res == "Withdrawn": return 3
        if res == "Fail": return 2
        if gpa >= 3.2: return 0
        if gpa >= 2.5: return 1
        return 2
        
    out["target_risk_level"] = df.apply(get_target, axis=1)
    name_map = {0: "Low", 1: "Medium", 2: "High", 3: "Very High"}
    out["target_risk_name"] = out["target_risk_level"].map(name_map)
    out["dataset_source"] = "OULAD"
    out = out.drop_duplicates(subset=["student_code"])
    
    return out

def process_uci_dropout(df):
    print("Processing UCI Dropout (Test Set 1)...")
    out = pd.DataFrame()
    out["student_code"] = "UD_" + df.index.astype(str)
    out["academic_year_order"] = 1
    out["admission_score_norm"] = df["Admission grade"] / 200.0
    out["priority_flag"] = df["Educational special needs"]
    
    enrolled = df["Curricular units 2nd sem (enrolled)"]
    approved = df["Curricular units 2nd sem (approved)"]
    out["credits_registered"] = enrolled * 3
    out["credit_completion_ratio"] = np.where(enrolled > 0, approved / enrolled, 0.0)
    out["cumulative_credit_debt"] = (enrolled - approved).clip(lower=0) * 3
    
    grade2 = df["Curricular units 2nd sem (grade)"]
    grade1 = df["Curricular units 1st sem (grade)"]
    
    out["gpa_current_semester"] = grade2.apply(map_uci_gpa)
    out["cpa_cumulative_score"] = ((grade1 + grade2) / 2.0).apply(map_uci_gpa)
    out["cpa_growth_delta"] = out["gpa_current_semester"] - grade1.apply(map_uci_gpa)
    
    out["failed_courses_count"] = (enrolled - approved).clip(lower=0)
    out["training_point_norm"] = 0.7
    out["tuition_debt_flag"] = 1 - df["Tuition fees up to date"]
    
    # NaN MASKING CHO OOD: Đảm bảo model học chéo không bị chệch hướng
    out["lms_total_clicks"] = np.nan
    out["lms_active_days"] = np.nan
    out["lms_late_submits"] = np.nan
    out["lms_avg_quiz"] = np.nan
    
    out["previous_academic_warnings"] = 0
    out["risk_score_continuous"] = 0.0
    
    target_map = {"Graduate": 0, "Enrolled": 1, "Dropout": 3}
    out["target_risk_level"] = df["Target"].map(target_map).fillna(2)
    name_map = {0: "Low", 1: "Medium", 2: "High", 3: "Very High"}
    out["target_risk_name"] = out["target_risk_level"].map(name_map)
    out["dataset_source"] = "UCI_Dropout"
    
    return out

def process_uci_perf(df):
    print("Processing UCI Perf (Test Set 2)...")
    out = pd.DataFrame()
    out["student_code"] = "UP_" + df.index.astype(str)
    out["academic_year_order"] = 1
    # Proxy admission bằng trình độ học vấn của bố mẹ
    out["admission_score_norm"] = (df["Medu"] + df["Fedu"]) / 8.0 
    out["priority_flag"] = 0
    out["credits_registered"] = 6
    
    g3, g2, g1 = df["G3"], df["G2"], df["G1"]
    out["credit_completion_ratio"] = np.where(g3 >= 10, 1.0, 0.0)
    out["cumulative_credit_debt"] = df["failures"] * 6
    
    out["gpa_current_semester"] = g3.apply(map_uci_gpa)
    out["cpa_cumulative_score"] = ((g1 + g2 + g3) / 3.0).apply(map_uci_gpa)
    out["cpa_growth_delta"] = out["gpa_current_semester"] - g1.apply(map_uci_gpa)
    
    out["failed_courses_count"] = df["failures"]
    out["training_point_norm"] = (1.0 - df["absences"]/93.0).clip(lower=0, upper=1)
    out["tuition_debt_flag"] = 0
    
    # NaN MASKING CHO OOD
    out["lms_total_clicks"] = np.nan
    out["lms_active_days"] = np.nan
    out["lms_late_submits"] = np.nan
    out["lms_avg_quiz"] = np.nan
    
    out["previous_academic_warnings"] = df["failures"]
    out["risk_score_continuous"] = 0.0
    
    def get_target(g):
        if g < 10: return 3
        if g < 12: return 2
        if g < 14: return 1
        return 0
        
    out["target_risk_level"] = g3.apply(get_target)
    name_map = {0: "Low", 1: "Medium", 2: "High", 3: "Very High"}
    out["target_risk_name"] = out["target_risk_level"].map(name_map)
    out["dataset_source"] = "UCI_Perf"
    
    return out

def main():
    info, assess, reg, uci_d, uci_p = load_data()
    
    df_oulad = process_oulad(info, assess, reg)
    df_uci_d = process_uci_dropout(uci_d)
    df_uci_p = process_uci_perf(uci_p)
    
    master_df = pd.concat([df_oulad, df_uci_d, df_uci_p], ignore_index=True)
    
    print(f"Total rows: {len(master_df)}")
    print(master_df["dataset_source"].value_counts())
    
    out_path = os.path.join(PROCESSED_DIR, "DataMart_Student_Risk_Flat_Master.csv")
    master_df.to_csv(out_path, index=False)
    print(f"✅ OOD Optimized ETL Completed! Saved to: {out_path}")

if __name__ == "__main__":
    main()
