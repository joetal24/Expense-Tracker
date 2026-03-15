import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/expense_provider.dart';
import '../providers/auth_provider.dart';
import '../models/expense_model.dart';
import '../utils/ugx_formatter.dart';
import '../widgets/loading_shimmer.dart';

class ExpenseListScreen extends StatefulWidget {
  const ExpenseListScreen({super.key});

  @override
  State<ExpenseListScreen> createState() => _ExpenseListScreenState();
}

class _ExpenseListScreenState extends State<ExpenseListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final token = context.read<AuthProvider>().accessToken;
      context.read<ExpenseProvider>().loadExpenses(token: token);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Transactions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {},
          ),
        ],
      ),
      body: Consumer<ExpenseProvider>(
        builder: (ctx, provider, _) {
          if (provider.isLoading) {
            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: 5,
              itemBuilder: (_, __) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: LoadingShimmer(height: 64, borderRadius: BorderRadius.circular(12)),
              ),
            );
          }

          final expenses = provider.recentExpenses;
          if (expenses.isEmpty) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.receipt_long_outlined,
                      size: 64, color: Colors.grey),
                  SizedBox(height: 12),
                  Text('No transactions yet',
                      style: TextStyle(color: Colors.grey, fontSize: 16)),
                  SizedBox(height: 4),
                  Text('Tap + to add your first transaction',
                      style: TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
            );
          }

          // Group by date
          final grouped = <String, List<ExpenseModel>>{};
          for (final e in expenses) {
            final key = DateFormat('d MMM yyyy').format(e.date);
            grouped.putIfAbsent(key, () => []).add(e);
          }

          return RefreshIndicator(
            onRefresh: () async {
              final token = context.read<AuthProvider>().accessToken;
              await context
                  .read<ExpenseProvider>()
                  .loadExpenses(token: token);
            },
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              itemCount: grouped.length,
              itemBuilder: (ctx, i) {
                final date = grouped.keys.elementAt(i);
                final items = grouped[date]!;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(
                        date,
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                    ...items.map((e) => _ExpenseTile(expense: e)),
                  ],
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _ExpenseTile extends StatelessWidget {
  final ExpenseModel expense;
  const _ExpenseTile({required this.expense});

  @override
  Widget build(BuildContext context) {
    final isExpense = expense.type != 'income';
    final color =
        isExpense ? const Color(0xFFC62828) : const Color(0xFF2E7D32);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.1),
          child: Icon(
            isExpense ? Icons.arrow_upward : Icons.arrow_downward,
            color: color,
            size: 18,
          ),
        ),
        title: Text(
          expense.category?.name ?? (isExpense ? 'Expense' : 'Income'),
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        subtitle: Text(
          expense.note?.isNotEmpty == true
              ? expense.note!
              : DateFormat('h:mm a').format(expense.date),
          style: const TextStyle(fontSize: 12, color: Colors.grey),
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Text(
          '${isExpense ? '-' : '+'}${UGXFormatter.format(expense.amount)}',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
      ),
    );
  }
}
