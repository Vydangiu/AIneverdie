import json
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Tạo email test random để tránh trùng
import uuid
test_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
test_password = "123456"

def test_register():
    """Đăng ký tài khoản mới"""
    resp = client.post("/auth/register", json={
        "email": test_email,
        "password": test_password,
        "name": "Test User"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data

def test_login():
    """Đăng nhập với email/password đã đăng ký"""
    resp = client.post("/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    global access_token
    access_token = data["access_token"]

def test_predict():
    """Gọi API /predict để dự đoán"""
    headers = {"Authorization": f"Bearer {access_token}"}
    features = {
        "age": 58, "sex": 1, "cp": 1,
        "trestbps": 148, "chol": 252, "fbs": 1,
        "restecg": 1, "thalach": 112, "exang": 1,
        "oldpeak": 2.3, "slope": 2, "ca": 1, "thal": 7
    }
    resp = client.post("/predict", json={"features": features}, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "probability" in data
    assert "recommendations" in data

def test_history():
    """Kiểm tra lịch sử đã được lưu"""
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.get("/history", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
