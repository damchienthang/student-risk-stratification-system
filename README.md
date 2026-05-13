# Student Risk Stratification System

A machine learning system that classifies university students into four risk levels based on their learning behaviour, demographic profile, and assessment performance. Built on the Open University Learning Analytics Dataset (OULAD).

---

## Table of Contents

- [Project Overview](#project-overview)
- [Risk Level Definition](#risk-level-definition)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Pipeline](#pipeline)
- [Model Performance](#model-performance)
- [Key Features Used](#key-features-used)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Visualisations](#visualisations)
- [Technical Notes](#technical-notes)

---

## Project Overview

This system analyses student data and predicts whether a student is at Low, Medium, High, or Very High risk of academic failure. The goal is to help educators identify at-risk students early so that timely interventions can be made.

The system consists of:
- A data processing and feature engineering pipeline
- Exploratory data analysis with 13 generated charts
- A supervised classification model (LightGBM) selected via fair comparison
- A web application built with FastAPI and Jinja2 for student lookup and risk prediction

---

## Risk Level Definition

| Level | Code | Meaning |
|-------|------|---------|
| Low | 0 | Student is performing well with low risk of failure |
| Medium | 1 | Student shows some warning signs |
| High | 2 | Student is at significant risk and requires attention |
| Very High | 3 | Student is at critical risk of failing or withdrawing |

Risk labels are derived from the student's final result combined with their VLE (Virtual Learning Environment) activity level.

---

## Dataset

Source: Open University Learning Analytics Dataset (OULAD)  
URL: https://analyse.kmi.open.ac.uk/open_dataset

The dataset covers students enrolled in Open University (UK) modules between 2013 and 2014. It includes:

- `studentInfo` — demographic information (gender, region, disability, education level, age band)
- `studentRegistration` — module registration and withdrawal dates
- `studentVle` — daily click activity on learning materials
- `studentAssessment` — scores and submission dates for assessments
- `assessments` — assessment type (TMA, CMA, Exam) and weights

After processing, the final dataset contains 32,593 student records with 23 features.

Class distribution before balancing:

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Very High | 17,208 | 52.8% |
| Low | 10,724 | 32.9% |
| Medium | 4,048 | 12.4% |
| High | 613 | 1.9% |

---

## Project Structure

```
.
├── data/
│   ├── raw/                        # Original OULAD CSV files
│   └── processed/
│       └── student_features_labeled.csv   # Final feature table (32,593 rows x 24 cols)
├── notebooks/
│   ├── 01_data_cleaning.ipynb      # Data loading, merging, feature engineering, labelling
│   ├── 02_eda.ipynb                # Exploratory data analysis (13 charts)
│   ├── 03_modeling.py              # Model training, evaluation, and comparison
│   └── models/                    # Saved .pkl model files (excluded from git, regenerate by running 03_modeling.py)
├── src/
│   ├── api/                        # FastAPI route handlers
│   ├── core/                       # Application configuration
│   ├── models/                     # SQLModel database models
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── services/                   # Prediction and database logic
│   ├── utils/                      # Helper utilities
│   └── web/                        # Jinja2 HTML templates and static files
├── visuals/                        # All generated charts (PNG, 150 dpi)
├── main.py                         # FastAPI application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container definition
└── README.md
```

---

## Pipeline

### Step 1 — Data Cleaning and Feature Engineering (`01_data_cleaning.ipynb`)

Raw OULAD tables are merged and transformed into a single flat feature table.

Features created:
- `total_clicks` — total VLE interactions across the module
- `active_days` — number of distinct days with at least one click
- `avg_clicks_day` — average clicks per active day
- `n_resources` — number of distinct VLE resources accessed
- `click_density` — total_clicks divided by days in module
- `avg_score` — mean weighted assessment score
- `avg_tma_score` — mean score on Tutor-Marked Assessments only
- `min_score` — lowest single assessment score
- `std_score` — standard deviation of assessment scores
- `n_late` — number of assessments submitted after the deadline
- `avg_submit_delay` — average days late on submissions
- `gender_num` — binary encoding of gender
- `disability_num` — binary encoding of disability status
- `age_band_num` — ordinal encoding of age band
- `highest_education_num` — ordinal encoding of highest prior education
- `imd_band_num` — ordinal encoding of deprivation index band
- `region_num` — label encoding of UK region
- `studied_credits` — number of credits in the module
- `num_of_prev_attempts` — number of previous attempts at the module
- `reg_days_before` — days between registration and module start
- `unregistered` — binary flag for withdrawal
- `risk_level` — integer target (0=Low, 1=Medium, 2=High, 3=Very High)
- `risk_label` — string label corresponding to risk_level

### Step 2 — Exploratory Data Analysis (`02_eda.ipynb`)

13 charts are generated covering:
- Class imbalance analysis (bar chart, pie chart, imbalance ratio)
- Risk distribution by module and presentation
- Demographic feature distributions by risk level
- VLE behaviour distributions (clicks, active days, resources)
- Assessment score distributions (boxplots with fail threshold at 40)
- Scatter plot of average score vs total clicks coloured by risk
- Pearson correlation with risk_level (bar chart)
- Full correlation heatmap for top 10 features
- IQR-based outlier detection summary

### Step 3 — Model Training and Evaluation (`03_modeling.py`)

Train/Validation/Test split: 60% / 20% / 20% with stratification.

Class imbalance is handled using SMOTE (Synthetic Minority Oversampling Technique) on the training set only. NaN values are filled with the column median before SMOTE.

Four models are trained under identical conditions (same SMOTE data, no class_weight since SMOTE already balances classes):

| Model | n_estimators | learning_rate | Notes |
|-------|-------------|---------------|-------|
| Logistic Regression | — | — | Baseline linear model |
| Random Forest | 300 | — | Bagging ensemble |
| XGBoost | 300 | 0.05 | Gradient boosting |
| LightGBM | 300 | 0.05 | Gradient boosting, num_leaves=31 |

---

## Model Performance

### Validation Set Comparison

| Model | F1 Macro | AUC | Rank (F1) |
|-------|----------|-----|-----------|
| LightGBM | 0.8403 | 0.9868 | 1 — Selected |
| XGBoost | 0.8356 | 0.9872 | 2 |
| Random Forest | 0.8331 | 0.9845 | 3 |
| Logistic Regression | 0.7041 | 0.9624 | 4 |

LightGBM is selected as the final model because it achieves the highest F1 Macro score on the validation set. The AUC difference between LightGBM and XGBoost is 0.0004, which is not meaningful in practice.

F1 Macro is used as the primary selection criterion because it measures actual prediction quality across all four classes equally, and is directly relevant to how the system performs in deployment.

### Test Set Results — LightGBM

```
              precision    recall  f1-score   support

         Low       0.95      0.99      0.97      2145
      Medium       0.80      0.90      0.85       810
        High       0.61      0.66      0.63       122
   Very High       0.96      0.90      0.93      3442

    accuracy                           0.93      6519
   macro avg       0.83      0.86      0.84      6519
weighted avg       0.93      0.93      0.93      6519

Test F1 Macro : 0.844
Test AUC      : 0.989
```

The High risk class (only 1.9% of the dataset) is the hardest to classify, with an F1 of 0.63. This is expected given the low sample count even after SMOTE.

---

## Key Features Used

The top features by importance (from LightGBM):

1. `avg_score` — strongest negative correlation with risk (r = -0.71), the most predictive single feature
2. `min_score` — captures worst-case assessment performance
3. `total_clicks` — overall engagement level
4. `active_days` — consistency of engagement
5. `avg_tma_score` — ongoing assessed work score
6. `n_late` — late submission behaviour
7. `unregistered` — withdrawal flag
8. `reg_days_before` — early registration indicates commitment
9. `std_score` — inconsistency in performance
10. `avg_submit_delay` — habitual lateness

---

## Installation

Requirements: Python 3.11+

```bash
git clone https://github.com/damchienthang/student-risk-stratification-system.git
cd student-risk-stratification-system
pip install -r requirements.txt
```

Model files (`.pkl`) are not included in the repository because they exceed GitHub's file size limit. Regenerate them by running the training script:

```bash
cd student-risk-stratification-system
python notebooks/03_modeling.py
```

This will save all model files to `notebooks/models/`.

---

## Running the Project

### 1. Regenerate the processed dataset (optional — already included)

Open and run `notebooks/01_data_cleaning.ipynb` in Jupyter.

### 2. Run EDA (optional)

Open and run `notebooks/02_eda.ipynb` in Jupyter. Charts are saved to `visuals/`.

### 3. Train models

```bash
python notebooks/03_modeling.py
```

### 4. Start the web application

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

### 5. Docker (optional)

```bash
docker build -t student-risk .
docker run -p 8000:8000 student-risk
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Home page |
| GET | `/student` | Student dashboard |
| GET | `/admin` | Admin dashboard |
| POST | `/predict` | Predict risk level for a student |
| GET | `/about` | About page |

---

## Visualisations

All charts are stored in `visuals/` at 150 dpi.

| File | Description |
|------|-------------|
| `01_class_distribution.png` | Overall class distribution |
| `02_01_imbalance_analysis.png` | Bar, pie, and imbalance ratio charts |
| `02_02_risk_by_module_presentation.png` | Risk breakdown by module and presentation |
| `02_03_demographic_features.png` | Gender, age, region, education, disability by risk |
| `02_04_vle_features.png` | VLE engagement features by risk level |
| `02_05_assessment_features.png` | Assessment score boxplots by risk level |
| `02_06_scatter_score_vle.png` | Score vs clicks scatter coloured by risk |
| `02_07_correlation.png` | Pearson correlation bar chart and heatmap |
| `02_08_outlier_detection.png` | IQR outlier counts per feature |
| `03_confusion_matrix_best.png` | Confusion matrix for LightGBM on test set |
| `03_feature_importance_best.png` | Top 15 feature importances for LightGBM |
| `03_model_comparison.png` | F1, Balanced Accuracy, AUC bar chart for all models |
| `03_roc_curve_ovr.png` | Multi-class ROC curves (One-vs-Rest) for LightGBM |

---

## Technical Notes

**Why SMOTE instead of class_weight?**  
SMOTE generates synthetic samples for minority classes in feature space, giving the model richer training signal. Using both SMOTE and `class_weight='balanced'` at the same time would double-count the imbalance correction and degrade performance.

**Why LightGBM over XGBoost?**  
Both achieve nearly identical AUC (0.987 vs 0.987). LightGBM produces a marginally higher F1 Macro (0.840 vs 0.836). Since F1 Macro is the primary deployment metric, LightGBM is the selected model. LightGBM also trains faster on large datasets due to its histogram-based leaf-wise tree growth.

**Why are .pkl files excluded from git?**  
The Random Forest model file is 117 MB, exceeding GitHub's 100 MB limit. All model files are excluded via `.gitignore`. Run `python notebooks/03_modeling.py` to regenerate them locally.

**matplotlib backend**  
The training script uses `matplotlib.use('Agg')` to avoid Qt display warnings on Windows when running headless (no GUI needed since all charts are saved to files).
