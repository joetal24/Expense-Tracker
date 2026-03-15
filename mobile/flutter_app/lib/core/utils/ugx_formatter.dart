import 'package:intl/intl.dart';

class UGXFormatter {
  static final _full = NumberFormat('#,###', 'en_UG');

  /// e.g. UGX 45,000
  static String format(double amount) => 'UGX ${_full.format(amount.round())}';

  /// Compact: 1.2M, 450K, 45K
  static String compact(double amount) {
    if (amount >= 1000000) {
      return 'UGX ${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return 'UGX ${(amount / 1000).toStringAsFixed(0)}K';
    }
    return format(amount);
  }

  /// Without currency prefix
  static String raw(double amount) => _full.format(amount.round());
}
