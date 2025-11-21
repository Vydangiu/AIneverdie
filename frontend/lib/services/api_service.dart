import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../api_config.dart';

class ApiService {
  static Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
  static const String _kAccessTokenKey = 'access_token';

  // Lưu token
  static Future<void> saveAccessToken(String token) async {
    final prefs = await _prefs;
    await prefs.setString(_kAccessTokenKey, token);
  }

  static Future<String?> getAccessToken() async {
    final prefs = await _prefs;
    return prefs.getString(_kAccessTokenKey);
  }

  static Future<void> clearToken() async {
    final prefs = await _prefs;
    await prefs.remove(_kAccessTokenKey);
  }

  // Đăng ký
  static Future<String?> register({
    required String username,
    required String password,
    required String fullName,
  }) async {
    final uri = Uri.parse(ApiConfig.register);

    try {
      final res = await http
          .post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
          'full_name': fullName,
        }),
      )
          .timeout(const Duration(seconds: 3));

      if (res.statusCode == 200 || res.statusCode == 201) {
        return null;
      } else {
        return "Đăng ký thất bại: ${res.statusCode} - ${res.body}";
      }
    } catch (e) {
      return "Lỗi kết nối: $e";
    }
  }

  // Đăng nhập
  static Future<String?> login({
    required String username,
    required String password,
  }) async {
    final uri = Uri.parse(ApiConfig.login);

    try {
      final res = await http
          .post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      )
          .timeout(const Duration(seconds: 3));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        await saveAccessToken(data['access']);
        return null;
      } else {
        return "Sai tài khoản hoặc mật khẩu";
      }
    } catch (e) {
      return "Lỗi kết nối: $e";
    }
  }

  // Predict
  static Future<Map<String, dynamic>> predict(Map<String, dynamic> payload) async {
    final token = await getAccessToken();
    if (token == null) {
      throw Exception('Chưa đăng nhập');
    }

    final uri = Uri.parse(ApiConfig.predict);
    final res = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(payload),
    );

    if (res.statusCode == 200) {
      return jsonDecode(res.body) as Map<String, dynamic>;
    } else if (res.statusCode == 401) {
      throw Exception('Token hết hạn hoặc không hợp lệ');
    } else {
      throw Exception('Lỗi dự đoán: ${res.statusCode} - ${res.body}');
    }
  }

  // History
  static Future<List<dynamic>> fetchHistory() async {
    final token = await getAccessToken();
    if (token == null) {
      throw Exception('Chưa đăng nhập');
    }

    final uri = Uri.parse(ApiConfig.history);
    final res = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List<dynamic>;
    } else if (res.statusCode == 401) {
      throw Exception('Token hết hạn hoặc không hợp lệ');
    } else {
      throw Exception('Lỗi lấy lịch sử: ${res.statusCode} - ${res.body}');
    }
  }
}
