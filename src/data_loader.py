# Used to read the raw CSV file and convert it into a structured table that Python can understand 
import pandas as pd
# For handling file paths dynamically, ensuring the code works flawlessly whether it's run on any OS
import os

# pd.DataFrame is a "type hint" indicating that whenever this function finishes, it will return a Pandas DataFrame
def load_salary_data(data_path: str = None) -> pd.DataFrame:
    """
    Loads and validates the salary dataset (salaries in INR LPA).
    """
    if data_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "salary_data_multifeature.csv")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset file not found at: {data_path}")
    
    df = pd.read_csv(data_path)
    
    required_cols = [
        'years_of_experience', 'job_title', 'education_level',
        'location', 'company_size', 'salary_in_lpa'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' in dataset.")
            
    return df

if __name__ == "__main__":
    df = load_salary_data()
    print("Dataset Loaded Successfully!")
    print(f"Shape: {df.shape}")
    print("\nSample Data (Salaries in ₹ LPA):")
    print(df.head())
