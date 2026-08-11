import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_nutrition_database
from backend.app.budget_engine import calculate_bmr, calculate_daily_calorie_target, calculate_bmi
from backend.app.redistribution import recalculate_and_redistribute_daily_target


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_nutrition_database(db)
    finally:
        db.close()


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_budget_engine_mifflin_st_jeor():
    # Male: (10 * 75) + (6.25 * 175) - (5 * 30) + 5 = 750 + 1093.75 - 150 + 5 = 1698.75
    bmr_male = calculate_bmr(75.0, 175.0, 30, "male")
    assert bmr_male == 1698.75

    # Female: (10 * 60) + (6.25 * 160) - (5 * 25) - 161 = 600 + 1000 - 125 - 161 = 1314.0
    bmr_female = calculate_bmr(60.0, 160.0, 25, "female")
    assert bmr_female == 1314.0

    target_data = calculate_daily_calorie_target(75.0, 175.0, 30, "male", "moderate", "lose")
    assert target_data["target_calories"] == 2133.1


def test_bmi_calculator():
    bmi_info = calculate_bmi(70.0, 175.0)  # 70 / 1.75^2 = 22.86 -> Normal
    assert bmi_info["bmi"] == 22.9
    assert bmi_info["category"] == "Normal"


import uuid

def test_auth_and_meal_logging_flow():
    # 1. Signup user
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "email": unique_email,
        "password": "secretpassword123",
        "age": 28,
        "weight": 70.0,
        "height": 175.0,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "maintain",
        "dietary_preferences": "balanced",
        "allergies": "",
    }
    resp = client.post("/api/auth/signup", json=signup_payload)
    assert resp.status_code == 201
    data = resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get today's initial target
    target_resp = client.get("/api/targets/today", headers=headers)
    assert target_resp.status_code == 200
    t_data = target_resp.json()
    init_target_cals = t_data["target_calories"]
    assert t_data["consumed_calories"] == 0.0
    assert t_data["remaining_calories"] == init_target_cals

    # 3. Log a manual breakfast meal (Apple)
    meal_payload = {
        "meal_slot": "breakfast",
        "food_name": "Apple",
        "quantity_g": 150.0,
        "source": "manual",
    }
    log_resp = client.post("/api/meals/manual", json=meal_payload, headers=headers)
    assert log_resp.status_code == 200
    log_json = log_resp.json()
    assert log_json["meal_log"]["food_name"] == "Apple"

    # 4. Check adaptive target redistribution
    updated_target = log_json["updated_target"]
    assert updated_target["consumed_calories"] > 0
    assert updated_target["remaining_calories"] < init_target_cals
    assert updated_target["breakfast"]["consumed"] > 0

    # 5. Fetch recommendations
    rec_resp = client.get("/api/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    recs = rec_resp.json()["suggestions"]
    assert len(recs) > 0

    # 6. Fetch accuracy evaluation report
    acc_resp = client.get("/api/analytics/accuracy", headers=headers)
    assert acc_resp.status_code == 200
    acc_json = acc_resp.json()
    assert acc_json["total_users"] > 0
    assert "overall_mae" in acc_json
