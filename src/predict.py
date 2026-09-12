import os
import joblib
import pandas as pd

def get_model_pipeline():
    """
    Loads and returns the trained joblib model pipeline.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "models", "salary_model_pipeline.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model pipeline not found at {model_path}. Please run train.py first.")

    return joblib.load(model_path)

def predict_salary(years_of_experience: float, job_title: str, education_level: str, location: str, company_size: str) -> float:
    """
    Predicts annual salary (in INR LPA) for a single candidate profile.
    """
    pipeline = get_model_pipeline()

    input_df = pd.DataFrame([{
        'years_of_experience': years_of_experience,
        'job_title': job_title,
        'education_level': education_level,
        'location': location,
        'company_size': company_size
    }])

    prediction = pipeline.predict(input_df)[0]
    return float(prediction)

def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predicts annual salary for a batch DataFrame of candidates.
    Returns the DataFrame with 'predicted_salary_lpa' and 'predicted_annual_inr'.
    """
    required_cols = ['years_of_experience', 'job_title', 'education_level', 'location', 'company_size']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column: '{col}'")

    pipeline = get_model_pipeline()
    
    # Run pipeline prediction
    predictions = pipeline.predict(df[required_cols])
    
    result_df = df.copy()
    result_df['predicted_salary_lpa'] = np.round(predictions, 2)
    result_df['predicted_annual_inr'] = np.round(predictions * 100000, 0)
    
    return result_df

if __name__ == "__main__":
    import numpy as np
    test_pred = predict_salary(
        years_of_experience=4.5,
        job_title='Data Scientist',
        education_level="Master's",
        location='Bengaluru',
        company_size='Mid-size'
    )
    print(f"Sample Salary Prediction: ₹ {test_pred:.2f} LPA (₹ {test_pred * 100000:,.0f} / year)")
