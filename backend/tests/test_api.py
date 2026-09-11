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


def test_calorie_budget_calculate_endpoint():
    payload = {
        "weight_kg": 70.0,
        "height_cm": 175.0,
        "age": 25,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "lose",
        "goal_delta_kcal": 500.0,
    }
    resp = client.post("/calorie-budget/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "target_calories" in data
    assert "slot_targets" in data
    slot_targets = data["slot_targets"]
    assert "breakfast" in slot_targets
    assert "lunch" in slot_targets
    assert "snack" in slot_targets
    assert "dinner" in slot_targets
    # Confirm slot_targets sum matches target_calories (within floating point rounding)
    sum_slots = sum(slot_targets.values())
    assert abs(sum_slots - data["target_calories"]) <= 1.0


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


def test_stage2_manual_meal_logging_checkpoint():
    # 1. Signup user
    unique_email = f"stage2_user_{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "email": unique_email,
        "password": "stage2password",
        "age": 30,
        "weight": 75.0,
        "height": 180.0,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "maintain",
    }
    resp = client.post("/auth/signup", json=signup_payload)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get initial dashboard
    dash_resp = client.get("/dashboard/today", headers=headers)
    assert dash_resp.status_code == 200
    d_data = dash_resp.json()
    target_cals = d_data["target_calories"]
    assert d_data["consumed_calories"] == 0.0
    assert d_data["remaining_calories"] == target_cals

    # 3. Log meal 1: Breakfast (Oatmeal 200g)
    log1 = client.post("/meals/manual", json={"meal_slot": "breakfast", "food_name": "Oatmeal", "quantity_g": 200.0}, headers=headers)
    assert log1.status_code == 200

    # 4. Log meal 2: Lunch (Grilled Chicken Breast 150g)
    log2 = client.post("/meals/manual", json={"meal_slot": "lunch", "food_name": "Grilled Chicken Breast", "quantity_g": 150.0}, headers=headers)
    assert log2.status_code == 200

    # 5. Log meal 3: Snack (Banana 120g)
    log3 = client.post("/meals/manual", json={"meal_slot": "snacks", "food_name": "Banana", "quantity_g": 120.0}, headers=headers)
    assert log3.status_code == 200

    # 6. Verify dashboard
    dash_updated = client.get("/dashboard/today", headers=headers).json()
    consumed = dash_updated["consumed_calories"]
    remaining = dash_updated["remaining_calories"]

    assert consumed > 0
    assert remaining < target_cals
    # Confirm remaining_calories == target_calories - consumed_calories
    assert abs(remaining - (target_cals - consumed)) <= 0.1


def test_stage4_photo_food_recognition_checkpoint():
    import io
    from PIL import Image

    # 1. Signup user
    unique_email = f"stage4_user_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/auth/signup", json={
        "email": unique_email,
        "password": "stage4password",
        "age": 26,
        "weight": 68.0,
        "height": 172.0,
        "gender": "female",
        "activity_level": "active",
        "goal": "lose",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate dummy test image bytes
    img = Image.new("RGB", (200, 200), color=(255, 100, 100))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    # 3. Post photo to /meals/photo
    files = {"file": ("test_pizza.jpg", img_bytes, "image/jpeg")}
    photo_resp = client.post("/meals/photo", files=files, headers=headers)
    assert photo_resp.status_code == 200
    p_data = photo_resp.json()

    assert "detected_food" in p_data
    assert "confidence" in p_data
    assert "uncertain" in p_data
    assert "calories" in p_data
    assert p_data["calories"] > 0
    assert p_data["portion_g"] > 0


def test_stage5_recommendation_engine_allergen_filter_checkpoint():
    # Signup user with allergy to nuts and dairy
    unique_email = f"allergy_user_{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "email": unique_email,
        "password": "allergypassword",
        "age": 32,
        "weight": 70.0,
        "height": 170.0,
        "gender": "female",
        "activity_level": "moderate",
        "goal": "lose",
        "dietary_preferences": "balanced",
        "allergies": "nuts,dairy",
    }
    resp = client.post("/auth/signup", json=signup_payload)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch recommendations
    rec_resp = client.get("/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    suggestions = rec_resp.json()["suggestions"]
    assert len(suggestions) > 0

    # Verify no suggested item contains nuts or dairy
    for item in suggestions:
        fname = item["food_name"].lower()
        cat = item["category"].lower()
        assert "nut" not in fname
        assert "almond" not in fname
        assert "walnut" not in fname
        assert "cheese" not in fname
        assert "yogurt" not in fname
        assert "milk" not in fname
