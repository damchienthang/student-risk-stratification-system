import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score, roc_auc_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# 1. Tải và chuẩn bị dữ liệu
data_path = 'data/processed/student_features_labeled.csv'
df = pd.read_csv(data_path)

drop_cols = ['id_student', 'code_module', 'code_presentation', 'final_result', 'risk_label']
X = df.drop(columns=drop_cols)
y = X.pop('risk_level')

# 2. Split dữ liệu
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, stratify=y_temp, random_state=42)

# 3. Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_val_scaled   = pd.DataFrame(scaler.transform(X_val), columns=X_train.columns)

# 4. Điền NaN bằng median
X_train_scaled = X_train_scaled.fillna(X_train_scaled.median())
X_val_scaled   = X_val_scaled.fillna(X_train_scaled.median())

# 5. Tạo dữ liệu SMOTE
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)

# 6. Khởi tạo 3 kịch bản cho LightGBM
comparison_models = {
    'LightGBM (Không xử lý)': LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, random_state=42),
    'LightGBM (Class Weight)': LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, class_weight='balanced', random_state=42),
    'LightGBM (SMOTE)': LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, random_state=42)
}

comparison_results = []

print("Đang huấn luyện và so sánh...")

for name, model in comparison_models.items():
    # Chọn tập dữ liệu huấn luyện tương ứng
    if 'SMOTE' in name:
        model.fit(X_train_smote, y_train_smote)
    else:
        model.fit(X_train_scaled, y_train)
    
    # Dự đoán nhãn và xác suất
    y_pred = model.predict(X_val_scaled)
    y_proba = model.predict_proba(X_val_scaled) # Thêm dòng này để tính AUC
    
    # Tính toán các chỉ số
    f1 = f1_score(y_val, y_pred, average='macro')
    acc = accuracy_score(y_val, y_pred)
    auc = roc_auc_score(y_val, y_proba, multi_class='ovr') # Tính AUC
    
    # Lấy riêng F1-Score của lớp High (Nhãn 2)
    report = classification_report(y_val, y_pred, output_dict=True)
    f1_high = report['2']['f1-score'] 
    
    comparison_results.append({
        'Chiến lược': name,
        'Accuracy': acc,
        'AUC': auc,         
        'F1 Macro': f1,
        'F1 Class High': f1_high
    })


# 7. Hiển thị bảng kết quả
df_compare = pd.DataFrame(comparison_results)
print("\n" + "="*60)
print("KẾT QUẢ SO SÁNH CÁC CHIẾN LƯỢC")
print("="*60)
print(df_compare.to_string(index=False))
print("="*60)
    