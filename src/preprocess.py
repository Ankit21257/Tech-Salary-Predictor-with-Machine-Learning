from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def get_preprocessing_pipeline():
    """
    Returns a Scikit-Learn ColumnTransformer for numerical scaling and categorical encoding.
    """
    num_features = ['years_of_experience']
    cat_features = ['job_title', 'education_level', 'location', 'company_size']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ],
        remainder='drop'
    )
    
    return preprocessor

if __name__ == "__main__":
    from data_loader import load_salary_data
    df = load_salary_data()
    X = df.drop(columns=['salary_in_lpa'])
    y = df['salary_in_lpa']
    
    preprocessor = get_preprocessing_pipeline()
    X_trans = preprocessor.fit_transform(X)
    print("Preprocessing successful!")
    print(f"Transformed Feature Matrix Shape: {X_trans.shape}")
