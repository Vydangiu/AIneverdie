# ===============================
# personalize.py – AI recommendation logic
# ===============================

def risk_tier(p):
    """Phân loại mức độ nguy cơ dựa vào xác suất p"""
    if p < 0.33:
        return "thấp"
    if p < 0.66:
        return "trung_binh"
    return "cao"


def personalize_recommendations(x, p=None, shap_top=None):
    """
    x: dict input gồm các biến Cleveland dataset
    p: xác suất dự đoán (0..1)
    shap_top: top features từ SHAP (tùy chọn)
    Trả về list[str] khuyến nghị cá nhân hóa.
    """

    recs = []

    # -------------------------------
    # 1. Lipid & đường huyết
    # -------------------------------
    if x.get("chol") is not None:
        if x["chol"] >= 240:
            recs.append("Cholesterol cao: giảm chất béo bão hoà/chiên xào; tăng cá, hạt, rau ≥400g/ngày.")
        elif x["chol"] >= 200:
            recs.append("Cholesterol cận cao: duy trì chế độ DASH/Mediterranean và theo dõi định kỳ.")

    if x.get("fbs") == 1:
        recs.append("Đường huyết đói cao: ăn ít đường tinh luyện, tăng chất xơ; vận động 150 phút/tuần.")

    # -------------------------------
    # 2. Huyết áp & gắng sức
    # -------------------------------
    if x.get("trestbps") is not None:
        if x["trestbps"] >= 140:
            recs.append("Huyết áp cao: giảm muối <5g/ngày, đi bộ nhanh 30 phút/ngày, kiểm soát stress.")
        elif x["trestbps"] >= 130:
            recs.append("Huyết áp tăng nhẹ: duy trì vận động đều, hạn chế rượu bia, theo dõi huyết áp.")

    if x.get("thalach") is not None and x["thalach"] < 120:
        recs.append("Thể lực thấp (thalach <120): bắt đầu tập nhẹ–vừa 20–30 phút, 5 ngày/tuần.")

    if x.get("exang") == 1:
        recs.append("Đau ngực khi gắng sức: tập mức nhẹ, ngừng lại nếu đau hoặc khó thở.")

    # -------------------------------
    # 3. ST segment & ECG
    # -------------------------------
    if x.get("oldpeak") is not None:
        if x["oldpeak"] > 2.0:
            recs.append("Oldpeak >2: giảm căng thẳng, ngủ đủ 7–8h; nên tham khảo bác sĩ.")
        elif x["oldpeak"] > 1.0:
            recs.append("Oldpeak 1–2: điều độ cường độ tập luyện, theo dõi triệu chứng.")

    if x.get("slope") == 2:
        recs.append("Slope downsloping: thận trọng khi gắng sức; ưu tiên bài tập nhịp nhàng.")

    if x.get("restecg") not in (None, 0):
        recs.append("Điện tâm đồ có bất thường: tránh tăng gắng sức đột ngột, theo dõi triệu chứng.")

    # -------------------------------
    # 4. Mạch vành & thal
    # -------------------------------
    if x.get("ca") is not None and x["ca"] >= 1:
        recs.append("Có dấu hiệu tổn thương mạch (ca≥1): siết chặt lối sống; theo dõi HA/lipid.")

    if x.get("thal") in (6, 7):
        recs.append("Thal bất thường (6/7): tập nhẹ–vừa, theo dõi khó thở/mệt mỏi.")

    # -------------------------------
    # 5. Nhân khẩu học & triệu chứng
    # -------------------------------
    if x.get("age") is not None and x["age"] >= 55:
        recs.append("Tuổi ≥55: duy trì ăn lành mạnh, vận động đều, khám 6–12 tháng/lần.")

    if x.get("sex") == 1 and x.get("age", 0) >= 45:
        recs.append("Nam ≥45 tuổi: kiểm soát vòng eo, hạn chế rượu bia, theo dõi lipid.")

    if x.get("cp") in (0, 1):
        recs.append("Có triệu chứng đau ngực: nếu đau lan tay/hàm hoặc khó thở → đi khám ngay.")

    # -------------------------------
    # 6. Nguy cơ tổng quát (từ mô hình)
    # -------------------------------
    if p is not None:
        tier = risk_tier(p)
        if tier == "cao":
            recs.insert(0, "Bạn thuộc nhóm NGUY CƠ CAO: nên tham khảo bác sĩ sớm.")
        elif tier == "trung_binh":
            recs.insert(0, "Nguy cơ TRUNG BÌNH: áp dụng khuyến nghị và tái kiểm tra sau 1–3 tháng.")
        else:
            recs.insert(0, "Nguy cơ THẤP: duy trì lối sống lành mạnh và theo dõi định kỳ.")

    # -------------------------------
    # 7. SHAP feature explanation (tuỳ chọn)
    # -------------------------------
    if shap_top:
        recs.append(f"Yếu tố ảnh hưởng nhiều (SHAP): {', '.join(shap_top[:3])}.")

    # -------------------------------
    # 8. Loại trùng lặp
    # -------------------------------
    seen = set()
    unique_recs = []
    for r in recs:
        if r not in seen:
            unique_recs.append(r)
            seen.add(r)

    return unique_recs
