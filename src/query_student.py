import pandas as pd
import joblib
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

def query_student_risk(student_id):
    # 1. File paths
    data_path = 'data/processed/student_features_labeled.csv'
    model_path = 'notebooks/models/lightgbm.pkl'
    scaler_path = 'notebooks/models/scaler.pkl'

    # Check data file
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return
    
    # 2. Load data and find student
    df = pd.read_csv(data_path)
    student_data = df[df['id_student'] == student_id]

    if student_data.empty:
        print(f"Student ID {student_id} not found.")
        return

    # Get first record (current presentation)
    student_record = student_data.iloc[0]

    # 3. Extract features for model
    drop_cols = ['id_student', 'code_module', 'code_presentation', 'final_result', 'risk_label', 'risk_level']
    features = student_data.drop(columns=drop_cols).iloc[[0]]
    
    # Display information
    print(f"\n=== QUERY STUDENT ID: {student_id} ===")
    print(f"Course: {student_record['code_module']} - {student_record['code_presentation']}")
    print("-" * 40)
    print(f"[*] Demographics:")
    print(f"    - IMD Band: {student_record['imd_band_num']}")
    print(f"    - Education: {student_record['education_num']}")
    print(f"[*] Engagement (VLE):")
    print(f"    - Total clicks: {student_record['total_clicks']}")
    print(f"    - Active days:  {student_record['active_days']}")
    print(f"[*] Performance:")
    print(f"    - Avg Score:    {student_record['avg_score']:.2f}")
    print(f"    - Late submits: {student_record['n_late']}")
    print("-" * 40)
    print(f"[*] Ground Truth: {student_record['final_result']}")

    # 4. Predict using model
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Scale and predict
        features_scaled = scaler.transform(features)
        risk_pred = model.predict(features_scaled)[0]
        risk_proba = model.predict_proba(features_scaled)[0]
        
        levels = ['Low', 'Medium', 'High', 'Very High']
        
        print(f"[*] PREDICTION: {levels[risk_pred]} RISK")
        print(f"[*] Confidence: {risk_proba[risk_pred]*100:.2f}%")
        
        if risk_pred >= 2:
            print(f"\n[!] WARNING: High risk student detected. Needs attention!")
    else:
        print("\n[!] Note: model.pkl or scaler.pkl not found.")

if __name__ == "__main__":
    # Test with sample IDs: 11391 (Pass), 30268 (Withdrawn), 32885 (High Risk)
    test_ids = [11391, 30268, 32885]
    
    for sid in test_ids:
        query_student_risk(sid)
