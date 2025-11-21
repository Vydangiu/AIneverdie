import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PredictScreen extends StatefulWidget {
  const PredictScreen({super.key});

  @override
  State<PredictScreen> createState() => _PredictScreenState();
}

class _PredictScreenState extends State<PredictScreen> {
  final _formKey = GlobalKey<FormState>();

  // Controllers cho các số
  final _ageCtrl = TextEditingController();
  final _trestbpsCtrl = TextEditingController();
  final _cholCtrl = TextEditingController();
  final _thalachCtrl = TextEditingController();
  final _oldpeakCtrl = TextEditingController();
  final _caCtrl = TextEditingController();

  // Dropdown values
  int? _sex;
  int? _cp;
  int? _fbs;
  int? _restecg;
  int? _exang;
  int? _slope;
  int? _thal;

  bool _loading = false;
  String? _result;
  List<dynamic>? _recommend;

  @override
  void initState() {
    super.initState();
    // Gợi ý giá trị mặc định – nếu user không biết thì cứ để nguyên
    _ageCtrl.text = '50';
    _trestbpsCtrl.text = '130';   // huyết áp
    _cholCtrl.text = '230';       // cholesterol
    _thalachCtrl.text = '140';    // nhịp tim tối đa
    _oldpeakCtrl.text = '1.0';    // ST depression
    _caCtrl.text = '0';           // số mạch lớn nhuộm màu
  }

  @override
  void dispose() {
    _ageCtrl.dispose();
    _trestbpsCtrl.dispose();
    _cholCtrl.dispose();
    _thalachCtrl.dispose();
    _oldpeakCtrl.dispose();
    _caCtrl.dispose();
    super.dispose();
  }

  Future<void> _doPredict() async {
    // Kiểm tra form: ít nhất tuổi không được bỏ trống
    if (!_formKey.currentState!.validate()) return;

    // Bắt buộc user chọn các dropdown (giới tính, cp,...)
    if (_sex == null ||
        _cp == null ||
        _fbs == null ||
        _restecg == null ||
        _exang == null ||
        _slope == null ||
        _thal == null) {
      setState(() => _result = "Vui lòng chọn đầy đủ các mục dạng danh sách (dropdown).");
      return;
    }

    setState(() {
      _loading = true;
      _result = null;
      _recommend = null;
    });

    final payload = {
      "age": int.tryParse(_ageCtrl.text.trim()) ?? 50,
      "sex": _sex!,                       // 0: nữ, 1: nam
      "cp": _cp!,                         // kiểu đau ngực
      "trestbps": double.tryParse(_trestbpsCtrl.text.trim()) ?? 130,
      "chol": double.tryParse(_cholCtrl.text.trim()) ?? 230,
      "fbs": _fbs!,                       // 0 / 1
      "restecg": _restecg!,               // 0 / 1 / 2
      "thalach": double.tryParse(_thalachCtrl.text.trim()) ?? 140,
      "exang": _exang!,                   // 0 / 1
      "oldpeak": double.tryParse(_oldpeakCtrl.text.trim()) ?? 1.0,
      "slope": _slope!,                   // 0 / 1 / 2
      "ca": double.tryParse(_caCtrl.text.trim()) ?? 0,
      "thal": _thal!,                     // 1 / 2 / 3 (UI dễ hiểu)
    };

    final res = await ApiService.predict(payload);

    setState(() => _loading = false);

    if (res["error"] != null) {
      setState(() => _result = res["error"].toString());
    } else {
      final prob = (res["probability"] as num?)?.toDouble() ?? 0.0;
      setState(() {
        _result =
        "Mức nguy cơ: ${res["risk"]} (${(prob * 100).toStringAsFixed(1)}%)";
        _recommend = res["recommendations"] as List<dynamic>? ?? [];
      });
    }
  }

  Widget _buildCard(String title, List<Widget> children) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style:
              const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildNumberField({
    required TextEditingController controller,
    required String label,
    String? hint,
    String? helper,
    bool required = false,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        helperText: helper,
      ),
      validator: (v) {
        if (required && (v == null || v.trim().isEmpty)) {
          return 'Không được để trống';
        }
        return null; // cho phép bỏ trống, sẽ dùng giá trị gợi ý
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Dự đoán nguy cơ tim mạch")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildCard("Thông tin lâm sàng", [
                _buildNumberField(
                  controller: _ageCtrl,
                  label: "Tuổi (age)",
                  hint: "Ví dụ: 45 – 80",
                  helper: "Bắt buộc nhập. Nếu không rõ, 50 là giá trị trung bình.",
                  required: true,
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Giới tính (sex)",
                    helperText: "0 = Nữ (female), 1 = Nam (male)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 0, child: Text("0 - Nữ (female)")),
                    DropdownMenuItem(value: 1, child: Text("1 - Nam (male)")),
                  ],
                  value: _sex,
                  onChanged: (v) => setState(() => _sex = v),
                  validator: (v) =>
                  v == null ? "Chọn giới tính" : null,
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Kiểu đau ngực (chest pain - cp)",
                    helperText:
                    "Nếu không rõ: chọn '3 - Ít/không triệu chứng'",
                  ),
                  items: const [
                    DropdownMenuItem(
                        value: 0, child: Text("0 - Đau thắt điển hình (typical)")),
                    DropdownMenuItem(
                        value: 1, child: Text("1 - Đau không điển hình (atypical)")),
                    DropdownMenuItem(
                        value: 2, child: Text("2 - Không phải đau tim (non-anginal)")),
                    DropdownMenuItem(
                        value: 3, child: Text("3 - Ít/không triệu chứng (asymptomatic)")),
                  ],
                  value: _cp,
                  onChanged: (v) => setState(() => _cp = v),
                  validator: (v) =>
                  v == null ? "Chọn kiểu đau ngực" : null,
                ),
              ]),

              const SizedBox(height: 16),

              _buildCard("Chỉ số xét nghiệm", [
                _buildNumberField(
                  controller: _trestbpsCtrl,
                  label: "Huyết áp lúc nghỉ (resting BP - trestbps)",
                  hint: "Ví dụ: 110 – 160",
                  helper: "Đơn vị: mmHg. Nếu không rõ, để 130.",
                ),
                const SizedBox(height: 10),

                _buildNumberField(
                  controller: _cholCtrl,
                  label: "Cholesterol toàn phần (chol, mg/dl)",
                  hint: "Ví dụ: 180 – 300",
                  helper: "Nếu không rõ, để 230.",
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Đường huyết đói >120 mg/dl? (fbs)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 0, child: Text("0 - Không (No)")),
                    DropdownMenuItem(value: 1, child: Text("1 - Có (Yes)")),
                  ],
                  value: _fbs,
                  onChanged: (v) => setState(() => _fbs = v),
                  validator: (v) =>
                  v == null ? "Chọn trạng thái đường huyết" : null,
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Điện tâm đồ lúc nghỉ (restecg)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 0, child: Text("0 - Bình thường")),
                    DropdownMenuItem(
                        value: 1,
                        child: Text("1 - Bất thường ST-T (ST-T abnormality)")),
                    DropdownMenuItem(
                        value: 2,
                        child: Text("2 - Phì đại thất trái (LV hypertrophy)")),
                  ],
                  value: _restecg,
                  onChanged: (v) => setState(() => _restecg = v),
                  validator: (v) =>
                  v == null ? "Chọn kết quả ECG" : null,
                ),
                const SizedBox(height: 10),

                _buildNumberField(
                  controller: _thalachCtrl,
                  label: "Nhịp tim tối đa khi gắng sức (thalach)",
                  hint: "Ví dụ: 120 – 180",
                  helper: "Nếu không rõ, để 140.",
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Đau ngực khi gắng sức (exang)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 0, child: Text("0 - Không (No)")),
                    DropdownMenuItem(value: 1, child: Text("1 - Có (Yes)")),
                  ],
                  value: _exang,
                  onChanged: (v) => setState(() => _exang = v),
                  validator: (v) =>
                  v == null ? "Chọn tình trạng khi gắng sức" : null,
                ),
                const SizedBox(height: 10),

                _buildNumberField(
                  controller: _oldpeakCtrl,
                  label: "ST depression (oldpeak)",
                  hint: "Thường 0.0 – 4.0",
                  helper: "Nếu không rõ, để 1.0.",
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Độ dốc ST (slope)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 0, child: Text("0 - Tăng (upsloping)")),
                    DropdownMenuItem(value: 1, child: Text("1 - Phẳng (flat)")),
                    DropdownMenuItem(
                        value: 2, child: Text("2 - Giảm (downsloping)")),
                  ],
                  value: _slope,
                  onChanged: (v) => setState(() => _slope = v),
                  validator: (v) =>
                  v == null ? "Chọn slope" : null,
                ),
                const SizedBox(height: 10),

                _buildNumberField(
                  controller: _caCtrl,
                  label: "Số mạch vành lớn nhuộm màu (ca: 0–4)",
                  hint: "0 nếu không rõ",
                  helper: "0–4, nếu không biết để 0.",
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<int>(
                  isExpanded: true,
                  decoration: const InputDecoration(
                    labelText: "Thalassemia (thal)",
                  ),
                  items: const [
                    DropdownMenuItem(value: 1, child: Text("1 - Bình thường (normal)")),
                    DropdownMenuItem(value: 2, child: Text("2 - Tổn thương cố định (fixed)")),
                    DropdownMenuItem(
                        value: 3,
                        child: Text("3 - Tổn thương hồi phục (reversible)")),
                  ],
                  value: _thal,
                  onChanged: (v) => setState(() => _thal = v),
                  validator: (v) =>
                  v == null ? "Chọn thalassemia" : null,
                ),
              ]),

              const SizedBox(height: 16),

              ElevatedButton(
                onPressed: _loading ? null : _doPredict,
                child: _loading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text("Dự đoán"),
              ),

              if (_result != null) ...[
                const SizedBox(height: 20),
                Text(
                  _result!,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],

              if (_recommend != null && _recommend!.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Text(
                  "Khuyến nghị cá nhân hoá:",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ..._recommend!.map((e) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text("• "),
                      Expanded(child: Text(e.toString())),
                    ],
                  ),
                )),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
