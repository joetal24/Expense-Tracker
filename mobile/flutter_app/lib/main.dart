import 'dart:convert';

import 'package:flutter/material.dart';

import 'core/config/api_config.dart';
import 'core/services/backend_api_service.dart';

void main() {
  runApp(const AkauntiWireApp());
}

class AkauntiWireApp extends StatelessWidget {
  const AkauntiWireApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akaunti UG Wiring',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
      ),
      home: const WiringHomeScreen(),
    );
  }
}

class WiringHomeScreen extends StatefulWidget {
  const WiringHomeScreen({super.key});

  @override
  State<WiringHomeScreen> createState() => _WiringHomeScreenState();
}

class _WiringHomeScreenState extends State<WiringHomeScreen> {
  final _usernameController = TextEditingController(text: 'release_user');
  final _passwordController = TextEditingController(text: 'StrongPass123!');
  final _api = BackendApiService();

  bool _loading = false;
  String _status = 'Ready';
  String? _accessToken;
  Map<String, dynamic>? _dashboard;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _runAction(Future<void> Function() action) async {
    if (_loading) return;
    setState(() => _loading = true);
    try {
      await action();
    } catch (error) {
      setState(() => _status = 'Error: $error');
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _register() async {
    await _runAction(() async {
      final response = await _api.register(
        username: _usernameController.text.trim(),
        password: _passwordController.text,
      );
      setState(() => _status = 'Register response: ${jsonEncode(response)}');
    });
  }

  Future<void> _login() async {
    await _runAction(() async {
      final token = await _api.login(
        username: _usernameController.text.trim(),
        password: _passwordController.text,
      );
      setState(() {
        _accessToken = token;
        _status = 'Login success. Token stored in memory.';
      });
    });
  }

  Future<void> _loadDashboard() async {
    await _runAction(() async {
      if (_accessToken == null || _accessToken!.isEmpty) {
        throw 'Login first to fetch dashboard.';
      }
      final dashboard = await _api.getDashboard(_accessToken!);
      setState(() {
        _dashboard = dashboard;
        _status = 'Dashboard loaded successfully.';
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Akaunti APK Wiring'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'API Base URL: ${ApiConfig.apiBaseUrl}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(
                labelText: 'Username',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                ElevatedButton(
                  onPressed: _loading ? null : _register,
                  child: const Text('Register'),
                ),
                ElevatedButton(
                  onPressed: _loading ? null : _login,
                  child: const Text('Login'),
                ),
                ElevatedButton(
                  onPressed: _loading ? null : _loadDashboard,
                  child: const Text('Fetch Dashboard'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Status: $_status',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: SingleChildScrollView(
                  child: Text(
                    const JsonEncoder.withIndent('  ').convert(_dashboard ?? {}),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
