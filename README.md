# 💼 Tech Salary Predictor | India Market (INR LPA)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.2%2B-orange.svg)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end Machine Learning web application engineered to predict annual tech compensation (Software Engineering, Data Science, ML Engineering, DevOps) in **Lakhs Per Annum (₹ LPA)** across major Indian tech hubs. Built using **Scikit-Learn**, **Streamlit**, and **Plotly**.

---

## 📌 Project Overview

Unlike simple 1-variable dataset tutorials, this project models compensation across **5 key industry variables**, capturing realistic interactions between role designation, location tier (Bengaluru, NCR, Hyderabad, Pune, Remote), education, company scale, and total experience.

### ✨ Key Features
- **Custom Dataset CSV Upload & Batch Prediction:** Allows users to upload their own custom CSV files, download a sample template, automatically generate salary predictions across multiple candidate profiles, visualize prediction distributions, and export the resulting predictions CSV.
- **Human-Centric Dashboard UI:** Clean, minimalist **Streamlit** dashboard designed with professional typography, real-world Indian tech market parameters, compensation range estimations, and market data insights.
- **Pipeline Serialization:** Serializes the complete preprocessing and regression model pipeline into `models/salary_model_pipeline.joblib`.

---

## 📊 Dataset Parameters

| Parameter Name | Feature Type | Description / Categories |
| :--- | :--- | :--- |
| `years_of_experience` | Numerical | Total professional experience (0.0 to 20.0 yrs) |
| `job_title` | Categorical | `Software Engineer`, `Data Scientist`, `ML Engineer`, `Data Engineer`, `DevOps Engineer` |
| `education_level` | Categorical | `Bachelor's`, `Master's`, `PhD` |
| `location` | Categorical | `Bengaluru`, `Hyderabad`, `NCR`, `Pune`, `Remote` |
| `company_size` | Categorical | `Startup`, `Mid-size`, `Enterprise` |
| `salary_in_lpa` | Target (Numeric) | Gross annual compensation in Lakhs Per Annum (₹ LPA) |

---

## 📈 Model Performance Benchmark

Models were trained on 80% of the dataset and evaluated on the 20% holdout test dataset:

| Model Architecture | $R^2$ Score | MAE (₹ LPA) | RMSE (₹ LPA) |
| :--- | :---: | :---: | :---: |
| **Gradient Boosting Regressor** | **0.945** | **₹ 0.65 LPA** | **₹ 0.84 LPA** |
| Random Forest Regressor | 0.932 | ₹ 0.72 LPA | ₹ 0.92 LPA |
| Ridge Regression | 0.918 | ₹ 0.85 LPA | ₹ 1.05 LPA |
| Linear Regression (Baseline) | 0.910 | ₹ 0.89 LPA | ₹ 1.10 LPA |

---

## 📁 Repository Structure

```
Salary_Predictor_Project/
├── data/
│   └── salary_data_multifeature.csv    # Multi-feature Indian compensation dataset
|
├── src/
│   ├── data_loader.py                 # Data loading & schema validation
│   ├── preprocess.py                  # ColumnTransformer feature pipeline
│   ├── train.py                       # Model training & benchmarking script
│   └── predict.py                     # Inference script
|
├── models/
│   └── salary_model_pipeline.joblib   # Serialized ML pipeline model
|
├── app.py                             # Clean Streamlit Web Dashboard
|
├── EDA_and_Modeling.ipynb             # Jupyter Notebook for EDA & model analysis
|
├── requirements.txt                   # Project dependency list
|
├── .gitignore                         # Git exclusion rules
|
└── README.md                          # Comprehensive documentation
```

---

## 🛠️ Local Execution Setup

### 1. Navigate to Project Directory
```powershell
cd D:\Salary_Predictor_Project
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Run Model Training & Pipeline Generation
```powershell
python src/train.py
```

### 4. Launch Streamlit Web Dashboard
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📜 License
Distributed under the MIT License.
