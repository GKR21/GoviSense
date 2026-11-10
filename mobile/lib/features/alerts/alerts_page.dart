import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/localization/app_translations.dart';
import '../farmer/data/farmer_repository.dart';
import '../farmer/models/farmer_alert.dart';

class AlertsPage extends StatefulWidget {
  const AlertsPage({
    super.key,
    this.initialLanguage = AppLanguage.en,
    this.repository,
  });

  final AppLanguage initialLanguage;
  final FarmerRepository? repository;

  @override
  State<AlertsPage> createState() => _AlertsPageState();
}

class _AlertsPageState extends State<AlertsPage> {
  late final FarmerRepository _repo;
  late AppLanguage _language;
  String _filter = 'all';

  @override
  void initState() {
    super.initState();
    _repo = widget.repository ?? FarmerRepository.instance;
    _language = widget.initialLanguage;
    _repo.addListener(_onUpdated);
  }

  @override
  void dispose() {
    _repo.removeListener(_onUpdated);
    super.dispose();
  }

  void _onUpdated() {
    if (mounted) setState(() {});
  }

  void _showAskOfficerDialog(FarmerAlert alert) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(AppTranslations.t(_language, 'askOfficerDialogTitle')),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              alert.localizedTitle(_language),
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: controller,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: AppTranslations.t(_language, 'askOfficerHint'),
                border: const OutlineInputBorder(),
                isDense: true,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(AppTranslations.t(_language, 'cancelBtn')),
          ),
          ElevatedButton(
            onPressed: () {
              final text = controller.text.trim();
              if (text.isNotEmpty) {
                _repo.askOfficer(alert.id, text);
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(AppTranslations.t(_language, 'questionSent'))),
                );
              }
            },
            child: Text(AppTranslations.t(_language, 'sendQuestionBtn')),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final allAlerts = _repo.alerts;
    final filtered = allAlerts.where((a) {
      if (_filter == 'unread') return !a.isRead;
      if (_filter == 'market') return a.type == AlertType.market;
      if (_filter == 'weather') return a.type == AlertType.weather;
      return true;
    }).toList();

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(AppTranslations.t(_language, 'alertsInboxTitle')),
        actions: [
          DropdownButton<AppLanguage>(
            value: _language,
            underline: const SizedBox.shrink(),
            onChanged: (lang) {
              if (lang != null) setState(() => _language = lang);
            },
            items: AppLanguage.values.map((l) {
              return DropdownMenuItem(
                value: l,
                child: Text(l.nativeLabel, style: const TextStyle(fontSize: 12)),
              );
            }).toList(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        children: [
          Text(
            AppTranslations.t(_language, 'alertsInboxSub'),
            style: const TextStyle(fontSize: 11, color: AppTheme.neutral600),
          ),
          const SizedBox(height: 12),

          // Filters
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip(AppTranslations.t(_language, 'filterAll'), 'all', allAlerts.length),
                _buildFilterChip(AppTranslations.t(_language, 'filterUnread'), 'unread', _repo.unreadAlertsCount),
                _buildFilterChip(AppTranslations.t(_language, 'filterMarket'), 'market', null),
                _buildFilterChip(AppTranslations.t(_language, 'filterWeather'), 'weather', null),
              ],
            ),
          ),
          const SizedBox(height: 14),

          if (filtered.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Text(AppTranslations.t(_language, 'noAlerts')),
              ),
            )
          else
            ...filtered.map((alert) => _buildCard(alert)),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, String key, int? count) {
    final isSelected = _filter == key;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ChoiceChip(
        label: Text(count != null ? '$label ($count)' : label),
        selected: isSelected,
        onSelected: (_) => setState(() => _filter = key),
        selectedColor: AppTheme.primary,
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : AppTheme.ink,
          fontWeight: FontWeight.bold,
          fontSize: 11,
        ),
      ),
    );
  }

  Widget _buildCard(FarmerAlert alert) {
    final iconData = alert.type == AlertType.weather
        ? Icons.cloudy_snowing
        : alert.type == AlertType.market
            ? Icons.trending_up_rounded
            : alert.type == AlertType.success
                ? Icons.check_circle_outline
                : Icons.campaign_rounded;

    final color = alert.type == AlertType.weather
        ? const Color(0xFF2563EB)
        : alert.type == AlertType.market
            ? AppTheme.oversupply
            : alert.type == AlertType.success
                ? AppTheme.balanced
                : AppTheme.primary;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: alert.isRead ? AppTheme.background : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: alert.isRead ? AppTheme.cardBorder : AppTheme.primary.withValues(alpha: 0.4),
          width: alert.isRead ? 1 : 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(iconData, color: color, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  alert.localizedTitle(_language),
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: alert.isRead ? FontWeight.w600 : FontWeight.bold,
                    color: AppTheme.ink,
                  ),
                ),
              ),
              if (!alert.isRead)
                Container(
                  height: 8,
                  width: 8,
                  decoration: const BoxDecoration(
                    color: AppTheme.primary,
                    shape: BoxShape.circle,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            alert.localizedMessage(_language),
            style: const TextStyle(fontSize: 11, color: AppTheme.neutral600, height: 1.4),
          ),
          if (alert.questionAsked != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFCBD5E1)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.help_outline_rounded, size: 12, color: AppTheme.primary),
                      const SizedBox(width: 4),
                      Text(
                        _language == AppLanguage.si ? 'ඔබගේ විමසීම:' : _language == AppLanguage.ta ? 'உங்கள் கேள்வி:' : 'Your Inquiry:',
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.primary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(alert.questionAsked!, style: const TextStyle(fontSize: 11, color: AppTheme.ink)),
                  if (alert.officerResponse != null) ...[
                    const Divider(height: 12),
                    Text(
                      _language == AppLanguage.si ? 'නිලධාරී පිළිතුර:' : _language == AppLanguage.ta ? 'அதிகாரியின் பதில்:' : 'Officer Response:',
                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.balanced),
                    ),
                    const SizedBox(height: 2),
                    Text(alert.officerResponse!, style: const TextStyle(fontSize: 11, color: AppTheme.balanced)),
                  ],
                ],
              ),
            ),
          ],
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(alert.timestamp, style: const TextStyle(fontSize: 10, color: AppTheme.neutral400)),
              Wrap(
                spacing: 6,
                children: [
                  if (alert.isAcknowledged)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.balancedTint,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppTheme.balanced.withValues(alpha: 0.3)),
                      ),
                      child: Text(
                        AppTranslations.t(_language, 'acknowledgedBadge'),
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.balanced),
                      ),
                    )
                  else
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                      ),
                      onPressed: () => _repo.acknowledgeAlert(alert.id),
                      icon: const Icon(Icons.check, size: 12),
                      label: Text(
                        AppTranslations.t(_language, 'acknowledgeBtn'),
                        style: const TextStyle(fontSize: 11),
                      ),
                    ),
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      visualDensity: VisualDensity.compact,
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                    ),
                    onPressed: () => _showAskOfficerDialog(alert),
                    icon: const Icon(Icons.chat_bubble_outline_rounded, size: 12),
                    label: Text(
                      AppTranslations.t(_language, 'askOfficerBtn'),
                      style: const TextStyle(fontSize: 11),
                    ),
                  ),
                  if (alert.officerPhone != null)
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        padding: const EdgeInsets.symmetric(horizontal: 8),
                      ),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Calling officer at ${alert.officerPhone}')),
                        );
                      },
                      icon: const Icon(Icons.phone, size: 12),
                      label: Text(
                        AppTranslations.t(_language, 'callOfficerBtn'),
                        style: const TextStyle(fontSize: 11),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
