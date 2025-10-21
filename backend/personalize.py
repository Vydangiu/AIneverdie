# personalize.py
def risk_tier(p):
    if p < 0.33: return "thấp"
    if p < 0.66: return "trung_binh"
    return "cao"

def personalize_recommendations(x, p=None, shap_top=None):
    recs = []
    # Lipid & đường huyết
    chol = x.get("chol")
    if chol is not None:
        if chol >= 240: recs.append("Cholesterol cao: giảm chất béo bão hòa/chiên xào; tăng cá/hạt/rau ≥400g/ngày.")
        elif chol >= 200: recs.append("Cholesterol cận cao: áp dụng chế độ DASH/Mediterranean, theo dõi định kỳ.")
    if x.get("fbs") == 1:
        recs.append("Đường huyết đói cao: ăn ít đường tinh luyện, tăng chất xơ; vận động 150 phút/tuần.")

    # Huyết áp & gắng sức
    trestbps = x.get("trestbps")
    if trestbps is not None:
        if trestbps >= 140: recs.append("Huyết áp cao: giảm muối <5g/ngày, đi bộ nhanh 30’/ngày, kiểm soát stress.")
        elif trestbps >= 130: recs.append("Huyết áp tăng nhẹ: duy trì vận động đều, hạn chế rượu, theo dõi.")
    if x.get("thalach") is not None and x["thalach"] < 120:
        recs.append("Thể lực thấp: tập nhẹ–vừa 20–30’/ngày, 5 ngày/tuần.")
    if x.get("exang") == 1:
        recs.append("Đau ngực khi gắng sức: chỉ tập cường độ nhẹ–vừa; dừng nếu đau ngực/khó thở/chóng mặt.")

    # ST segment & ECG
    oldpeak = x.get("oldpeak")
    if oldpeak is not None:
        if oldpeak > 2.0: recs.append("Oldpeak >2: giảm căng thẳng, ngủ 7–8h; nên tham khảo bác sĩ.")
        elif oldpeak > 1.0: recs.append("Oldpeak 1–2: điều độ cường độ tập luyện; theo dõi triệu chứng.")
    if x.get("slope") == 2:
        recs.append("Slope downsloping: thận trọng khi gắng sức; ưu tiên bài tập nhịp nhàng.")
    if x.get("restecg") not in (None, 0):
        recs.append("ECG bất thường: theo dõi triệu chứng, tránh tăng cường độ đột ngột.")

    # Mạch vành & thal
    if x.get("ca") is not None and x["ca"] >= 1:
        recs.append("Tổn thương mạch (ca≥1): siết lối sống; theo dõi HA/lipid; thận trọng gắng sức.")
    if x.get("thal") in (6,7):
        recs.append("Thal bất thường (6/7): ưu tiên tập nhẹ–vừa, chú ý dinh dưỡng; theo dõi mệt mỏi/khó thở.")

    # Nhân khẩu & triệu chứng
    if x.get("age") is not None and x["age"] >= 55:
        recs.append("Tuổi ≥55: giữ '3 tốt' (ăn lành mạnh, vận động đều, ngủ đủ); khám định kỳ 6–12 tháng.")
    if x.get("sex") == 1 and x.get("age", 0) >= 45:
        recs.append("Nam ≥45: kiểm soát vòng eo/rượu bia; theo dõi lipid và huyết áp.")
    if x.get("cp") in (0,1):
        recs.append("Có triệu chứng đau ngực: theo dõi khi gắng sức; nếu đau lan tay/hàm/khó thở → đi khám.")

    # Tầng nguy cơ theo xác suất
    if p is not None:
        tier = risk_tier(p)
        if tier == "cao":
            recs.insert(0, "Bạn thuộc nhóm NGUY CƠ CAO: nên tham khảo bác sĩ sớm.")
        elif tier == "trung_binh":
            recs.insert(0, "Nguy cơ TRUNG BÌNH: áp dụng khuyến nghị và tái kiểm tra sau 1–3 tháng.")
        else:
            recs.insert(0, "Nguy cơ THẤP: duy trì lối sống lành mạnh và theo dõi định kỳ.")

    if shap_top:
        recs.append("Yếu tố ảnh hưởng nhiều (SHAP): " + ", ".join(shap_top[:3]))

    # unique & giữ thứ tự
    seen, uniq = set(), []
    for r in recs:
        if r not in seen:
            uniq.append(r); seen.add(r)
    return uniq
