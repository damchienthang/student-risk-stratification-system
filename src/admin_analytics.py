import pandas as pd
import joblib
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

def generate_admin_report(module_code, presentation_code):
    # 1. File paths
    data_path = 'data/processed/student_features_labeled.csv'
    model_path = 'notebooks/models/lightgbm.pkl'
    scaler_path = 'notebooks/models/scaler.pkl'

    if not os.path.exists(data_path):
        print("Error: Processed data file not found.")
        return

    # 2. Load data and filter by module/presentation
    df = pd.read_csv(data_path)
    class_df = df[(df['code_module'] == module_code) & 
                  (df['code_presentation'] == presentation_code)]

    if class_df.empty:
        print(f"No data found for Module {module_code} - {presentation_code}")
        return

    total_students = len(class_df)
    
    # 3. Predict risk for the entire class
    drop_cols = ['id_student', 'code_module', 'code_presentation', 'final_result', 'risk_label', 'risk_level']
    X_class = class_df.drop(columns=drop_cols)
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        X_scaled = scaler.transform(X_class)
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)
        
        # Add predictions to dataframe for analysis
        class_df['pred_risk_level'] = predictions
        class_df['confidence'] = [probabilities[i][predictions[i]] for i in range(len(predictions))]
    else:
        # Fallback to ground truth if model missing
        class_df['pred_risk_level'] = class_df['risk_level']
        class_df['confidence'] = 1.0
        print("(!) Warning: Using ground truth labels (Model not found).")

    # 4. Statistical Summary
    risk_counts = class_df['pred_risk_level'].value_counts().sort_index()
    risk_labels = ['Low', 'Medium', 'High', 'Very High']
    
    print(f"\n" + "="*60)
    print(f"ADMIN RISK MANAGEMENT REPORT - MODULE {module_code} ({presentation_code})")
    print(f"Total Students: {total_students}")
    print("="*60)

    print("\n[1] RISK STRATIFICATION DISTRIBUTION:")
    for i, label in enumerate(risk_labels):
        count = risk_counts.get(i, 0)
        percentage = (count / total_students) * 100
        print(f"    - {label:10s}: {count:4d} Students ({percentage:.1f}%)")

    # 5. Urgent Intervention List (Top 10 Very High Risk)
    emergency_list = class_df[class_df['pred_risk_level'] == 3].sort_values(by='confidence', ascending=False).head(10)

    print("\n[2] TOP 10 STUDENTS FOR URGENT INTERVENTION (VERY HIGH RISK):")
    if not emergency_list.empty:
        print(f"    {'Student ID':<12} | {'Confidence':<12} | {'Avg Score':<10} | {'Total Clicks'}")
        print("    " + "-"*55)
        for _, row in emergency_list.iterrows():
            print(f"    {int(row['id_student']):<12} | {row['confidence']*100:>10.2f}% | {row['avg_score']:>10.2f} | {int(row['total_clicks']):>10}")
    else:
        print("    (No Very High Risk students found)")

    # 6. Class Benchmarks
    avg_clicks = class_df['total_clicks'].mean()
    avg_score = class_df['avg_score'].mean()
    print(f"\n[3] CLASS PERFORMANCE BENCHMARKS:")
    print(f"    - Avg Engagement (Clicks): {avg_clicks:.1f}")
    print(f"    - Avg Academic Score:      {avg_score:.2f}")
    print("="*60)

if __name__ == "__main__":
    # Test with Module BBB (Large) and Semester 2014J
    generate_admin_report('BBB', '2014J')
