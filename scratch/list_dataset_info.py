import pandas as pd
import os

def list_info():
    data_path = 'data/processed/student_features_labeled.csv'
    if not os.path.exists(data_path):
        print("Data file not found.")
        return
        
    df = pd.read_csv(data_path)
    
    print("\n--- MODULES (COURSES) ---")
    print(df['code_module'].unique().tolist())
    
    print("\n--- PRESENTATIONS (SEMESTERS) ---")
    print(df['code_presentation'].unique().tolist())
    
    print("\n--- STUDENT COUNT PER MODULE ---")
    print(df['code_module'].value_counts().to_string())
    
    print("\n--- TOTAL RECORDS ---")
    print(len(df))

if __name__ == "__main__":
    list_info()
