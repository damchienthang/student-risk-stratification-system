# Multi-Dataset Exploratory Data Analysis (EDA)
# Comparing OULAD, UCI Dropout, and UCI Student Performance in Unified DataMart
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Fix Windows console UTF-8 output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Directory setup
data_path = 'data/processed/DataMart_Student_Risk_Flat_Master.csv'
visuals_dir = 'visuals'
os.makedirs(visuals_dir, exist_ok=True)

# Styling palette
sns.set_theme(style='whitegrid', font='Segoe UI')
risk_palette = {
    0: '#2E7D32', 1: '#F9A825', 2: '#EF6C00', 3: '#C62828',
    '0': '#2E7D32', '1': '#F9A825', '2': '#EF6C00', '3': '#C62828'
}
risk_labels = ['Low (0)', 'Medium (1)', 'High (2)', 'Very High (3)']
source_colors = {'OULAD': '#1F77B4', 'UCI_Dropout': '#FF7F0E', 'UCI_Perf': '#2CA02C'}

print("=" * 80)
print("MULTI-DATASET EXPLORATORY DATA ANALYSIS (EDA) - DATAMART STANDARDIZED")
print("=" * 80)

# 1. Load DataMart Master
df = pd.read_csv(data_path)
print(f"Loaded Master DataMart: {df.shape[0]:,} rows x {df.shape[1]} columns\n")

# 2. Dataset Overview Table
overview = []
for src, g in df.groupby('dataset_source'):
    overview.append({
        'Dataset': src,
        'Count': len(g),
        'Percentage': f"{len(g)/len(df)*100:.1f}%",
        'Low (0)': f"{(g['target_risk_level'] == 0).mean()*100:.1f}%",
        'Medium (1)': f"{(g['target_risk_level'] == 1).mean()*100:.1f}%",
        'High (2)': f"{(g['target_risk_level'] == 2).mean()*100:.1f}%",
        'Very High (3)': f"{(g['target_risk_level'] == 3).mean()*100:.1f}%"
    })
df_overview = pd.DataFrame(overview)
print("TABLE 1: DATASET SIZE & RISK DISTRIBUTION OVERVIEW")
print(df_overview.to_string(index=False))
print("-" * 80)

# 3. Key Academic Metrics by Source and Risk Level
metrics_summary = df.groupby(['dataset_source', 'target_risk_level']).agg({
    'gpa_current_semester': ['mean', 'median', 'std'],
    'cpa_cumulative_score': ['mean', 'median', 'std'],
    'credit_completion_ratio': ['mean', 'median'],
    'failed_courses_count': ['mean', 'max']
}).round(2)
print("\nTABLE 2: ACADEMIC METRICS BY RISK LEVEL ACROSS DATASETS")
print(metrics_summary)
print("-" * 80)

# ==============================================================================
# VISUALIZATION 1: DATASET OVERVIEW & RISK DISTRIBUTION COMPARISON
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

counts = df['dataset_source'].value_counts()
bars = ax1.bar(counts.index, counts.values, color=[source_colors.get(x, '#333') for x in counts.index], width=0.55, edgecolor='black', alpha=0.85)
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f"{yval:,} ({yval/len(df)*100:.1f}%)", ha='center', va='bottom', fontsize=11, fontweight='bold')
ax1.set_title('(A) Quy Mô Mẫu Từng Bộ Dữ Liệu Trong Master DataMart', fontsize=13, fontweight='bold', pad=12)
ax1.set_ylabel('Số lượng bản ghi (sinh viên)', fontsize=11)
ax1.set_ylim(0, max(counts.values) * 1.15)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

risk_pct = pd.crosstab(df['dataset_source'], df['target_risk_level'], normalize='index') * 100
bottom = np.zeros(len(risk_pct))
for lvl in [0, 1, 2, 3]:
    vals = risk_pct[lvl].values if lvl in risk_pct.columns else np.zeros(len(risk_pct))
    ax2.bar(risk_pct.index, vals, bottom=bottom, color=risk_palette[lvl], label=risk_labels[lvl], width=0.55, edgecolor='black', alpha=0.85)
    for i, v in enumerate(vals):
        if v >= 6:
            ax2.text(i, bottom[i] + v/2.0, f"{v:.1f}%", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    bottom += vals

ax2.set_title('(B) Tỷ Lệ Phân Phối 4 Mức Rủi Ro Theo Từng Bộ Dữ Liệu', fontsize=13, fontweight='bold', pad=12)
ax2.set_ylabel('Tỷ lệ phần trăm (%)', fontsize=11)
ax2.set_ylim(0, 105)
ax2.legend(title='Mức Rủi Ro', title_fontsize='10', loc='upper right', frameon=True)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
p1 = os.path.join(visuals_dir, 'eda_01_multidataset_overview_and_risk.png')
plt.savefig(p1, dpi=200)
plt.close()
print(f"[Saved] {p1}")

# ==============================================================================
# VISUALIZATION 2: GPA & CPA DISTRIBUTION BY RISK LEVEL
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

sns.boxplot(
    data=df, x='target_risk_level', y='gpa_current_semester', hue='dataset_source',
    palette=source_colors, ax=ax1, boxprops=dict(alpha=0.85), fliersize=2
)
ax1.set_title('(A) Phân Phối Điểm GPA Học Kỳ Theo 4 Mức Rủi Ro', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Mức Rủi Ro (0: Low, 1: Medium, 2: High, 3: Very High)', fontsize=11)
ax1.set_ylabel('Điểm GPA Học Kỳ (Thang 4 chuẩn hóa)', fontsize=11)
ax1.set_xticks(range(4))
ax1.set_xticklabels(risk_labels)
ax1.set_ylim(-0.2, 4.3)
ax1.legend(title='Nguồn Dữ Liệu', loc='upper right')

sns.boxplot(
    data=df, x='target_risk_level', y='cpa_cumulative_score', hue='dataset_source',
    palette=source_colors, ax=ax2, boxprops=dict(alpha=0.85), fliersize=2
)
ax2.set_title('(B) Phân Phối Điểm CPA Tích Lũy Theo 4 Mức Rủi Ro', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Mức Rủi Ro (0: Low, 1: Medium, 2: High, 3: Very High)', fontsize=11)
ax2.set_ylabel('Điểm CPA Tích Lũy (Thang 4 chuẩn hóa)', fontsize=11)
ax2.set_xticks(range(4))
ax2.set_xticklabels(risk_labels)
ax2.set_ylim(-0.2, 4.3)
ax2.legend(title='Nguồn Dữ Liệu', loc='upper right')

plt.tight_layout()
p2 = os.path.join(visuals_dir, 'eda_02_multidataset_academic_performance.png')
plt.savefig(p2, dpi=200)
plt.close()
print(f"[Saved] {p2}")

# ==============================================================================
# VISUALIZATION 3: CREDIT COMPLETION RATIO & FAILED COURSES COUNT
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

sns.barplot(
    data=df, x='target_risk_level', y='credit_completion_ratio', hue='dataset_source',
    palette=source_colors, ax=ax1, errorbar=None, edgecolor='black', alpha=0.85
)
for p in ax1.patches:
    h = p.get_height()
    if h > 0.05:
        ax1.annotate(f"{h:.2f}", (p.get_x() + p.get_width() / 2., h),
                     ha='center', va='bottom', fontsize=9, fontweight='bold', xytext=(0, 3),
                     textcoords='offset points')
ax1.set_title('(A) Tỷ Lệ Hoàn Thành Tín Chỉ (Completion Ratio) Theo Mức Rủi Ro', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Mức Rủi Ro', fontsize=11)
ax1.set_ylabel('Tỷ lệ hoàn thành tín chỉ (0.0 -> 1.0)', fontsize=11)
ax1.set_xticks(range(4))
ax1.set_xticklabels(risk_labels)
ax1.set_ylim(0, 1.15)
ax1.legend(title='Nguồn Dữ Liệu', loc='upper right')

sns.barplot(
    data=df, x='target_risk_level', y='failed_courses_count', hue='dataset_source',
    palette=source_colors, ax=ax2, errorbar=None, edgecolor='black', alpha=0.85
)
for p in ax2.patches:
    h = p.get_height()
    if h > 0.02:
        ax2.annotate(f"{h:.2f}", (p.get_x() + p.get_width() / 2., h),
                     ha='center', va='bottom', fontsize=9, fontweight='bold', xytext=(0, 3),
                     textcoords='offset points')
ax2.set_title('(B) Số Môn Từng Rớt / Thất Bại Theo Mức Rủi Ro', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('Mức Rủi Ro', fontsize=11)
ax2.set_ylabel('Số môn rớt trung bình', fontsize=11)
ax2.set_xticks(range(4))
ax2.set_xticklabels(risk_labels)
ax2.legend(title='Nguồn Dữ Liệu', loc='upper left')

plt.tight_layout()
p3 = os.path.join(visuals_dir, 'eda_03_multidataset_credit_and_failure.png')
plt.savefig(p3, dpi=200)
plt.close()
print(f"[Saved] {p3}")

# ==============================================================================
# VISUALIZATION 4: CROSS-DATASET CORRELATION HEATMAP
# ==============================================================================
common_cols = [
    'admission_score_norm', 'credits_registered', 'credit_completion_ratio',
    'cumulative_credit_debt', 'gpa_current_semester', 'cpa_cumulative_score',
    'cpa_growth_delta', 'failed_courses_count', 'tuition_debt_flag',
    'target_risk_level'
]
col_labels_vn = [
    'Điểm tuyển sinh', 'Tín chỉ đăng ký', 'Tỷ lệ đậu tín chỉ',
    'Tín chỉ nợ', 'GPA học kỳ', 'CPA tích lũy',
    'Độ dốc CPA', 'Số môn rớt', 'Cờ nợ học phí',
    'MỨC RỦI RO (Target)'
]

corr = df[common_cols].corr()

plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1,
    square=True, linewidths=0.8, cbar_kws={"shrink": 0.8},
    xticklabels=col_labels_vn, yticklabels=col_labels_vn
)
plt.title('Ma Trận Tương Quan (Correlation Heatmap) Giữa Các Đặc Trưng Chuẩn Hóa Với Mức Rủi Ro', fontsize=13, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()
p4 = os.path.join(visuals_dir, 'eda_04_multidataset_correlation_matrix.png')
plt.savefig(p4, dpi=200)
plt.close()
print(f"[Saved] {p4}")

# ==============================================================================
# VISUALIZATION 5: DOMAIN-SPECIFIC RISK DRIVERS (OULAD LMS vs UCI Dropout Debt vs UCI Perf Failures)
# ==============================================================================
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5))

# Subplot 1: OULAD LMS Clicks
oulad_df = df[df['dataset_source'] == 'OULAD'].dropna(subset=['lms_total_clicks'])
oulad_mean_clicks = oulad_df.groupby('target_risk_level')['lms_total_clicks'].mean()
bars1 = ax1.bar(oulad_mean_clicks.index, oulad_mean_clicks.values, color=[risk_palette[i] for i in oulad_mean_clicks.index], edgecolor='black', alpha=0.85, width=0.6)
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, h + 30, f"{int(h):,}", ha='center', va='bottom', fontsize=9.5, fontweight='bold')
ax1.set_title('OULAD (E-learning):\nClicks LMS Trung Bình Theo Rủi Ro', fontsize=11.5, fontweight='bold', pad=10)
ax1.set_xlabel('Mức Rủi Ro', fontsize=10)
ax1.set_ylabel('Tổng clicks LMS trung bình', fontsize=10)
ax1.set_xticks(range(4))
ax1.set_xticklabels(risk_labels, rotation=15)

# Subplot 2: UCI Dropout - Tuition Debt Rate
uci_df = df[df['dataset_source'] == 'UCI_Dropout']
debt_rate = uci_df.groupby('target_risk_level')['tuition_debt_flag'].mean() * 100
bars2 = ax2.bar(debt_rate.index, debt_rate.values, color=[risk_palette[i] for i in debt_rate.index], edgecolor='black', alpha=0.85, width=0.6)
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, h + 1.5, f"{h:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_title('UCI Dropout (Đại Học Tín Chỉ):\nTỷ Lệ Nợ Học Phí Theo Rủi Ro', fontsize=11.5, fontweight='bold', pad=10)
ax2.set_xlabel('Mức Rủi Ro', fontsize=10)
ax2.set_ylabel('Tỷ lệ sinh viên nợ học phí (%)', fontsize=10)
ax2.set_xticks([0, 1, 3])
ax2.set_xticklabels(['Low (0)', 'Medium (1)', 'Very High (3)'], rotation=15)
ax2.set_ylim(0, max(debt_rate.values) * 1.25)

# Subplot 3: UCI Perf - Previous Failures
perf_df = df[df['dataset_source'] == 'UCI_Perf']
perf_mean_failures = perf_df.groupby('target_risk_level')['failed_courses_count'].mean()
bars3 = ax3.bar(perf_mean_failures.index, perf_mean_failures.values, color=[risk_palette[i] for i in perf_mean_failures.index], edgecolor='black', alpha=0.85, width=0.6)
for bar in bars3:
    h = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, h + 0.05, f"{h:.2f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
ax3.set_title('UCI Perf (Phổ Thông K-12):\nSố Môn Từng Trượt Theo Rủi Ro', fontsize=11.5, fontweight='bold', pad=10)
ax3.set_xlabel('Mức Rủi Ro', fontsize=10)
ax3.set_ylabel('Số môn trượt trung bình', fontsize=10)
ax3.set_xticks(range(4))
ax3.set_xticklabels(risk_labels, rotation=15)

plt.tight_layout()
p5 = os.path.join(visuals_dir, 'eda_05_multidataset_domain_drivers.png')
plt.savefig(p5, dpi=200)
plt.close()
print(f"[Saved] {p5}")

print("\n" + "=" * 80)
print("MULTI-DATASET EDA COMPLETE! ALL CHARTS GENERATED IN visuals/")
print("=" * 80)
