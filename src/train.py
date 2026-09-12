import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from data_loader import load_salary_data
from preprocess import get_preprocessing_pipeline

def train_and_evaluate():
    """
    Trains multiple models on Indian Salary Data (₹ LPA), evaluates performance,
    selects the best model, and serializes the pipeline.
    """
    # 1. Load Data
    df = load_salary_data()
    X = df.drop(columns=['salary_in_lpa'])
    y = df['salary_in_lpa']

    # 2. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 3. Preprocessor
    preprocessor = get_preprocessing_pipeline()

    # 4. Candidate Models
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }

    results = []
    best_r2 = -float('inf')
    best_pipeline = None
    best_model_name = ""

    print("=" * 65)
    print("      Salary Predictor - Model Benchmarking & Evaluation (INR LPA)")
    print("=" * 65)

    for name, model in models.items():
        # Build Pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        # Fit
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        results.append({
            'Model': name,
            'R2 Score': r2,
            'MAE (₹ LPA)': mae,
            'RMSE (₹ LPA)': rmse
        })

        print(f"[{name}]")
        print(f"   R² Score  : {r2:.4f}")
        print(f"   MAE (LPA) : ₹ {mae:.2f} LPA")
        print(f"   RMSE (LPA): ₹ {rmse:.2f} LPA")
        print("-" * 65)

        if r2 > best_r2:
            best_r2 = r2
            best_pipeline = pipeline
            best_model_name = name

    # Results DataFrame
    results_df = pd.DataFrame(results).sort_values(by='R2 Score', ascending=False)
    print("\nFinal Model Comparison:")
    print(results_df.to_string(index=False))

    # Save Best Model
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)
    
    saved_model_path = os.path.join(model_dir, "salary_model_pipeline.joblib")
    joblib.dump(best_pipeline, saved_model_path)
    
    print(f"\nBest Model Selected: '{best_model_name}' with R² = {best_r2:.4f}")
    print(f"Saved trained pipeline to: {saved_model_path}")

    return results_df, best_model_name, saved_model_path

if __name__ == "__main__":
    train_and_evaluate()
