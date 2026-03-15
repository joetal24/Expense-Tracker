import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/theme/app_theme.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/expense_provider.dart';
import 'core/providers/account_provider.dart';
import 'core/screens/login_screen.dart';
import 'core/screens/register_screen.dart';
import 'core/screens/expense_list_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/expenses/add_expense_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ExpenseProvider()),
        ChangeNotifierProvider(create: (_) => AccountProvider()),
      ],
      child: const AkauntiApp(),
    ),
  );
}

class AkauntiApp extends StatefulWidget {
  const AkauntiApp({super.key});

  @override
  State<AkauntiApp> createState() => _AkauntiAppState();
}

class _AkauntiAppState extends State<AkauntiApp> {
  @override
  void initState() {
    super.initState();
    // Try to restore saved session on launch
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await context.read<AuthProvider>().tryRestoreSession();
      _syncTokenToProviders();
    });
  }

  void _syncTokenToProviders() {
    final token = context.read<AuthProvider>().accessToken;
    if (token != null) {
      context.read<ExpenseProvider>().setToken(token);
      context.read<AccountProvider>().setToken(token);
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akaunti UG',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const _RootRouter(),
    );
  }
}

/// Decides whether to show auth or main shell.
class _RootRouter extends StatelessWidget {
  const _RootRouter();

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (ctx, auth, _) {
        if (auth.isLoggedIn) {
          return const MainShell();
        }
        return const _AuthGate();
      },
    );
  }
}

/// Toggles between Login and Register.
class _AuthGate extends StatefulWidget {
  const _AuthGate();

  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  bool _showLogin = true;

  @override
  Widget build(BuildContext context) {
    if (_showLogin) {
      return LoginScreen(
        onGoRegister: () => setState(() => _showLogin = false),
      );
    }
    return RegisterScreen(
      onGoLogin: () => setState(() => _showLogin = true),
    );
  }
}

/// Main app shell: bottom nav + FAB.
class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _tab = 0;

  @override
  void initState() {
    super.initState();
    // Seed token to providers once logged in
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final token = context.read<AuthProvider>().accessToken;
      if (token != null) {
        context.read<ExpenseProvider>().setToken(token);
        context.read<AccountProvider>().setToken(token);
      }
    });
  }

  void _openAddExpense() {
    Navigator.of(context).push(
      MaterialPageRoute(
        fullscreenDialog: true,
        builder: (_) => const AddExpenseScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      const DashboardScreen(),
      const ExpenseListScreen(),
      _ProfileScreen(),
    ];

    return Scaffold(
      body: IndexedStack(index: _tab, children: screens),
      floatingActionButton: FloatingActionButton(
        onPressed: _openAddExpense,
        backgroundColor: const Color(0xFFFFB300),
        foregroundColor: Colors.white,
        child: const Icon(Icons.add, size: 28),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        color: Colors.white,
        elevation: 12,
        child: Row(
          children: [
            _NavItem(
              icon: Icons.dashboard_outlined,
              activeIcon: Icons.dashboard,
              label: 'Home',
              active: _tab == 0,
              onTap: () => setState(() => _tab = 0),
            ),
            _NavItem(
              icon: Icons.receipt_long_outlined,
              activeIcon: Icons.receipt_long,
              label: 'Transactions',
              active: _tab == 1,
              onTap: () => setState(() => _tab = 1),
            ),
            const SizedBox(width: 48), // FAB gap
            _NavItem(
              icon: Icons.person_outline,
              activeIcon: Icons.person,
              label: 'Profile',
              active: _tab == 2,
              onTap: () => setState(() => _tab = 2),
            ),
            _NavItem(
              icon: Icons.settings_outlined,
              activeIcon: Icons.settings,
              label: 'Settings',
              active: false,
              onTap: () {},
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final IconData activeIcon;
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.activeIcon,
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    const blue = Color(0xFF1565C0);
    return Expanded(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                active ? activeIcon : icon,
                color: active ? blue : Colors.grey,
                size: 22,
              ),
              const SizedBox(height: 2),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: active ? blue : Colors.grey,
                  fontWeight:
                      active ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const CircleAvatar(
            radius: 40,
            backgroundColor: Color(0xFFE3F2FD),
            child: Icon(Icons.person, size: 44, color: Color(0xFF1565C0)),
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              auth.username ?? 'User',
              style: const TextStyle(
                  fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 32),
          ListTile(
            leading: const Icon(Icons.logout, color: Color(0xFFC62828)),
            title: const Text('Sign Out',
                style: TextStyle(color: Color(0xFFC62828))),
            onTap: () async {
              await context.read<AuthProvider>().logout();
            },
          ),
        ],
      ),
    );
  }
}

