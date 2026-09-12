import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from src.auth import authenticate_user, register_user_from_gmail, load_users
from src.database import db_save_prediction, db_get_user_predictions, db_load_users

def test():
    print("Testing Auth and DB module...")
    users = load_users()
    print("Loaded users count:", len(users))
    assert len(users) >= 5, "Users should be loaded from DB"

    # Save a test prediction
    ok = db_save_prediction("testuser", {
        "years_of_experience": 5.0,
        "job_title": "Software Engineer",
        "education_level": "Bachelor's",
        "location": "Bengaluru",
        "company_size": "Enterprise",
        "predicted_salary_lpa": 18.5
    })
    print("Prediction save status:", ok)
    assert ok, "Prediction save should succeed"

    preds = db_get_user_predictions("testuser")
    print("Fetched predictions for testuser:", len(preds))
    assert len(preds) > 0, "Should retrieve saved predictions"
    print("First prediction record:", preds[0])
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test()
