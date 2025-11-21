import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _nameCtrl = TextEditingController();
  bool _loading = false;
  String? _msg;

  Future<void> _doRegister() async {
    setState(() {
      _loading = true;
      _msg = null;
    });

    final err = await ApiService.register(
      username: _userCtrl.text.trim(),
      password: _passCtrl.text.trim(),
      fullName: _nameCtrl.text.trim(),
    );

    setState(() => _loading = false);

    if (err == null) {

      if (!mounted) return;
      Navigator.pop(context); // quay lại LoginScreen
    } else {
      setState(() => _msg = err);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Đăng ký')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _userCtrl,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passCtrl,
              decoration: const InputDecoration(labelText: 'Mật khẩu'),
              obscureText: true,
            ),
            TextField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Họ tên'),
            ),
            const SizedBox(height: 12),
            if (_msg != null) Text(_msg!),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _loading ? null : _doRegister,
              child: _loading
                  ? const CircularProgressIndicator()
                  : const Text('Đăng ký'),
            ),
          ],
        ),
      ),
    );
  }
}
