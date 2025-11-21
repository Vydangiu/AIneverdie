
class ApiConfig {
  static const String baseUrl = 'http://192.168.1.13:8000/api';

  static String get register => '$baseUrl/register/';
  static String get login => '$baseUrl/login/';
  static String get predict => '$baseUrl/predict/';
  static String get history => '$baseUrl/history/';
}