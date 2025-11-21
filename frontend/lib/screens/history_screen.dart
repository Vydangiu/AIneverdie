import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _loading = true;
  String? _error;
  List<dynamic> _items = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await ApiService.fetchHistory();
      setState(() => _items = data);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    if (_items.isEmpty) {
      return const Center(child: Text('Chưa có lịch sử dự đoán.'));
    }

    return RefreshIndicator(
      onRefresh: _loadHistory,
      child: ListView.builder(
        itemCount: _items.length,
        itemBuilder: (ctx, i) {
          final item = _items[i] as Map<String, dynamic>;
          final prob = (item['probability'] as num?)?.toDouble() ?? 0.0;
          final risk = item['risk'] ?? item['risk_level'] ?? '';
          final createdAt = item['created_at'] ?? '';
          final recs = (item['recommendations'] as List<dynamic>? ?? [])
              .map((e) => e.toString())
              .toList();

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Nguy cơ: $risk',
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16)),
                  Text('Xác suất: ${(prob * 100).toStringAsFixed(1)}%'),
                  Text('Thời gian: $createdAt'),
                  const SizedBox(height: 8),
                  const Text('Khuyến nghị:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  for (int j = 0; j < recs.length && j < 3; j++)
                    Text('- ${recs[j]}'),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
