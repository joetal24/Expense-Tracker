import 'package:flutter/material.dart';
import '../utils/ugx_formatter.dart';

class BudgetAlertCard extends StatelessWidget {
  final Map<String, dynamic> alert;

  const BudgetAlertCard({super.key, required this.alert});

  @override
  Widget build(BuildContext context) {
    final name = alert['name']?.toString() ?? 'Budget';
    final spent = (alert['spent'] as num?)?.toDouble() ?? 0;
    final limit = (alert['limit'] as num?)?.toDouble() ?? 1;
    final pct = (spent / limit).clamp(0.0, 1.0);
    final isOver = pct >= 1.0;
    final isDanger = pct >= 0.85;

    final color = isOver
        ? const Color(0xFFC62828)
        : isDanger
            ? const Color(0xFFF57C00)
            : const Color(0xFF2E7D32);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.06),
        border: Border.all(color: color.withOpacity(0.3)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(name,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600, fontSize: 13)),
              Text(
                isOver ? 'Over budget!' : '${(pct * 100).toStringAsFixed(0)}%',
                style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                    fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 6,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            '${UGXFormatter.compact(spent)} of ${UGXFormatter.compact(limit)}',
            style: const TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
