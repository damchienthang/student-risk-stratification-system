import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score, accuracy_score, balanced_accuracy_score, roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from imblearn.over_sampling import SMOTE

# Ensure visuals dir exists
visuals_dir = 'visuals'
os.makedirs(visuals_dir, exist_ok=True)
models_dir = 'notebooks/models'
os.makedirs(models_dir, exist_ok=True)

# 1. Tải dữ liệu
data_path = 'data/processed/student_features_labeled.csv'
df = pd.read_csv(data_path)

# Drop ID columns and Final result (we use risk_label or risk_level as target)
drop_cols = ['id_student', 'code_module', 'code_presentation', 'final_result', 'risk_label']
X = df.drop(columns=drop_cols)
# Chuyển đổi target thành risk_level (0: Low, 1: Medium, 2: High, 3: Very High)
y = X.pop('risk_level')

print("Phân phối nhãn ban đầu:")
print(y.value_counts())

# 2. Train / Validation / Test split (60/20/20)
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, stratify=y_temp, random_state=42) # 0.25 * 0.8 = 0.2

print(f"\nKích thước tập Train: {X_train.shape}")
print(f"Kích thước tập Validation: {X_val.shape}")
print(f"Kích thước tập Test: {X_test.shape}")

# 3. Chuẩn hóa dữ liệu (StandardScaler)
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_val_scaled = pd.DataFrame(scaler.transform(X_val), columns=X_val.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))

# 4. Xử lý mất cân bằng dữ liệu với SMOTE cho tập train
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

print(f"\nPhân phối nhãn sau SMOTE:")
print(pd.Series(y_train_resampled).value_counts())

# 5. Huấn luyện mô hình
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'XGBoost': XGBClassifier(n_estimators=300, learning_rate=0.05, random_state=42),
    'LightGBM': LGBMClassifier(class_weight='balanced', random_state=42)
}

results = {}

for name, model in models.items():
    print(f"\n--- Training {name} ---")
    # dùng cùng data SMOTE cho tất cả
    model.fit(X_train_resampled, y_train_resampled)

    y_val_pred = model.predict(X_val_scaled)
    y_val_proba = model.predict_proba(X_val_scaled)

    macro_f1 = f1_score(y_val, y_val_pred, average='macro')
    acc = accuracy_score(y_val, y_val_pred)
    b_acc = balanced_accuracy_score(y_val, y_val_pred)

    # THÊM AUC
    auc_score = roc_auc_score(y_val, y_val_proba, multi_class='ovr')

    print(f"F1: {macro_f1:.4f} | AUC: {auc_score:.4f}")

    results[name] = {
        'model': model,
        'f1_macro': macro_f1,
        'acc': acc,
        'b_acc': b_acc,
        'auc': auc_score
    }

    joblib.dump(model, os.path.join(models_dir, f'{name.replace(" ", "_").lower()}.pkl'))

# 6. Đánh giá chi tiết mô hình tốt nhất (XGBoost) trên tập Test
best_model_name = 'XGBoost'
best_model = results[best_model_name]['model']

y_test_pred = best_model.predict(X_test_scaled)


print(f"\n=== ĐÁNH GIÁ TRÊN TẬP TEST ({best_model_name}) ===")
print(classification_report(y_test, y_test_pred, target_names=['Low', 'Medium', 'High', 'Very High']))

y_test_proba = best_model.predict_proba(X_test_scaled)

print("Test F1:", f1_score(y_test, y_test_pred, average='macro'))
print("Test AUC:", roc_auc_score(y_test, y_test_proba, multi_class='ovr'))

# Confusion Matrix
cm = confusion_matrix(y_test, y_test_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Low', 'Medium', 'High', 'Very High'], yticklabels=['Low', 'Medium', 'High', 'Very High'])
plt.title(f'Confusion Matrix - {best_model_name}')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig(os.path.join(visuals_dir, '03_confusion_matrix_best.png'))
plt.close()

# ROC Curve (One-vs-Rest)
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3])
y_score = best_model.predict_proba(X_test_scaled)
n_classes = 4

plt.figure(figsize=(10, 8))
colors = ['green', 'blue', 'orange', 'red']
labels = ['Low', 'Medium', 'High', 'Very High']
for i in range(n_classes):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, color=colors[i], lw=2, label=f'ROC curve of class {labels[i]} (area = {roc_auc:.2f})')

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title(f'Multi-class ROC (One-vs-Rest) - {best_model_name}')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(visuals_dir, '03_roc_curve_ovr.png'))
plt.close()

# Feature Importance
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    features = X.columns
    
    plt.figure(figsize=(10,8))
    sns.barplot(x=importances[indices][:15], y=[features[i] for i in indices][:15])
    plt.title(f'Top 15 Feature Importances - {best_model_name}')
    plt.tight_layout()
    plt.savefig(os.path.join(visuals_dir, '03_feature_importance_best.png'))
    plt.close()

import pandas as pd
df_results = pd.DataFrame(results).T.drop(columns=['model'])
print("\nSo sánh các mô hình:")
print(df_results)
df_results.plot(kind='bar', y=['f1_macro', 'b_acc', 'auc'], figsize=(10,6), colormap='viridis')
plt.title('So sánh hiệu suất các mô hình trên tập Validation')
plt.ylabel('Score')
plt.ylim([0, 1])
plt.xticks(rotation=0)
plt.legend(['F1 Macro', 'Balanced Accuracy', 'AUC'])
plt.tight_layout()
plt.savefig(os.path.join(visuals_dir, '03_model_comparison.png'))
plt.close()

print("\nĐã lưu các biểu đồ vào thư mục visuals/ và mô hình vào notebooks/models/.")
