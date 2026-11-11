import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../data/auth_repository.dart';
import '../../../shared/widgets/brand_mark.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/localization/app_locale.dart';
import '../../../core/localization/localized_text.dart';

const _districts = [
  'Anuradhapura',
  'Polonnaruwa',
  'Kurunegala',
  'Matale',
  'Kandy',
  'Puttalam',
  'Ampara',
  'Hambantota',
  'Badulla',
  'Monaragala',
  'Vavuniya',
  'Colombo',
];

class AuthPage extends StatefulWidget {
  const AuthPage({super.key});
  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final _form = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  final _fullName = TextEditingController();
  final _officerCode = TextEditingController();
  bool _signUp = false;
  String _role = 'farmer';
  String _district = 'Anuradhapura';
  bool _loading = false;
  bool _obscure = true;
  String? _error;
  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    _fullName.dispose();
    _officerCode.dispose();
    super.dispose();
  }

  void _toggleMode() => setState(() {
    _signUp = !_signUp;
    _error = null;
  });

  String _messageFor(Object e) {
    if (e is StateError) return e.message.toString();
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map && data['detail'] is String) {
        return data['detail'] as String;
      }
      if (e.response == null) {
        return 'Cannot reach the server. Check your connection and API address.';
      }
    }
    return _signUp
        ? 'Unable to create account. Please try again.'
        : 'Unable to sign in. Check your credentials and connection.';
  }

  Future<void> _submit() async {
    if (_loading || !_form.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      if (_signUp) {
        await AuthRepository.instance.register(
          username: _username.text,
          password: _password.text,
          fullName: _fullName.text,
          role: _role,
          district: _district,
          officerCode: _role == 'officer' ? _officerCode.text : null,
        );
      } else {
        await AuthRepository.instance.login(_username.text, _password.text);
        if (AuthRepository.instance.role != _role) {
          final verifiedRole = AuthRepository.instance.role;
          await AuthRepository.instance.logout();
          throw StateError(
            'This account belongs to the $verifiedRole workspace.',
          );
        }
      }
      if (mounted) {
        context.go(AuthRepository.instance.home);
      }
    } catch (e) {
      if (mounted) setState(() => _error = _messageFor(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFFEAF5EF), AppTheme.background],
          stops: [0, 0.42],
        ),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const BrandMark(),
                  DecoratedBox(
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.8),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.cardBorder),
                    ),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                      child: LanguagePicker(),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 34),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  color: AppTheme.primary,
                  borderRadius: BorderRadius.circular(26),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primary.withValues(alpha: 0.22),
                      blurRadius: 22,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.14),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.auto_awesome_rounded,
                        color: AppTheme.accent,
                        size: 22,
                      ),
                    ),
                    const SizedBox(height: 18),
                    const LocalizedText(
                      'Smarter decisions for every season.',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        height: 1.15,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.4,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const LocalizedText(
                      'Live market intelligence, trusted forecasts and practical guidance for Sri Lankan agriculture.',
                      style: TextStyle(
                        color: Color(0xFFD8EDE0),
                        fontSize: 13,
                        height: 1.45,
                      ),
                    ),
                    const SizedBox(height: 18),
                    const Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _TrustBadge(
                          icon: Icons.insights_rounded,
                          label: 'AI insights',
                        ),
                        _TrustBadge(
                          icon: Icons.storefront_rounded,
                          label: 'Live prices',
                        ),
                        _TrustBadge(
                          icon: Icons.verified_user_outlined,
                          label: 'Secure access',
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 22),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppTheme.cardBorder),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x0A14211B),
                      blurRadius: 18,
                      offset: Offset(0, 7),
                    ),
                  ],
                ),
                child: Form(
                  key: _form,
                  child: AutofillGroup(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        LocalizedText(
                          _signUp ? 'Create your account' : 'Welcome back',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _signUp
                              ? 'Join GoviSense as a farmer or an officer.'
                              : 'Sign in with your GoviSense account.',
                        ),
                        const SizedBox(height: 20),
                        SegmentedButton<String>(
                          segments: const [
                            ButtonSegment(
                              value: 'farmer',
                              icon: Icon(Icons.agriculture_outlined),
                              label: Text('Farmer'),
                            ),
                            ButtonSegment(
                              value: 'officer',
                              icon: Icon(Icons.badge_outlined),
                              label: Text('Officer'),
                            ),
                          ],
                          selected: {_role},
                          onSelectionChanged: _loading
                              ? null
                              : (s) => setState(() => _role = s.first),
                        ),
                        if (_signUp) ...[
                          const SizedBox(height: 14),
                          TextFormField(
                            controller: _fullName,
                            enabled: !_loading,
                            textCapitalization: TextCapitalization.words,
                            autofillHints: const [AutofillHints.name],
                            decoration: const InputDecoration(
                              labelText: 'Full name',
                              prefixIcon: Icon(Icons.badge_outlined),
                            ),
                            validator: (v) => v == null || v.trim().length < 2
                                ? 'Enter your name'
                                : null,
                          ),
                          const SizedBox(height: 14),
                          DropdownButtonFormField<String>(
                            initialValue: _district,
                            decoration: const InputDecoration(
                              labelText: 'District',
                              prefixIcon: Icon(Icons.location_on_outlined),
                            ),
                            items: [
                              for (final d in _districts)
                                DropdownMenuItem(value: d, child: Text(d)),
                            ],
                            onChanged: _loading
                                ? null
                                : (v) => setState(
                                    () => _district = v ?? _district,
                                  ),
                          ),
                          const SizedBox(height: 14),
                        ],
                        TextFormField(
                          controller: _username,
                          enabled: !_loading,
                          autocorrect: false,
                          autofillHints: const [AutofillHints.username],
                          decoration: InputDecoration(
                            labelText: context.tr('Username / email'),
                            prefixIcon: Icon(Icons.person_outline),
                          ),
                          validator: (v) {
                            final t = v?.trim() ?? '';
                            if (t.isEmpty) return 'Enter your username';
                            if (_signUp && t.length < 3) {
                              return 'At least 3 characters';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),
                        TextFormField(
                          controller: _password,
                          enabled: !_loading,
                          obscureText: _obscure,
                          autofillHints: [
                            _signUp
                                ? AutofillHints.newPassword
                                : AutofillHints.password,
                          ],
                          onFieldSubmitted: (_) => _submit(),
                          decoration: InputDecoration(
                            labelText: context.tr('Password'),
                            prefixIcon: const Icon(Icons.lock_outline),
                            suffixIcon: IconButton(
                              tooltip: context.tr(
                                _obscure ? 'Show password' : 'Hide password',
                              ),
                              onPressed: () =>
                                  setState(() => _obscure = !_obscure),
                              icon: Icon(
                                _obscure
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                            ),
                          ),
                          validator: (v) {
                            if (v == null || v.isEmpty) {
                              return 'Enter your password';
                            }
                            if (_signUp && v.length < 8) {
                              return 'At least 8 characters';
                            }
                            return null;
                          },
                        ),
                        if (_signUp && _role == 'officer') ...[
                          const SizedBox(height: 14),
                          TextFormField(
                            controller: _officerCode,
                            enabled: !_loading,
                            decoration: const InputDecoration(
                              labelText:
                                  'Officer registration code (if issued)',
                              prefixIcon: Icon(Icons.vpn_key_outlined),
                            ),
                          ),
                        ],
                        const SizedBox(height: 20),
                        ElevatedButton.icon(
                          onPressed: _loading ? null : _submit,
                          icon: Icon(
                            _signUp
                                ? Icons.person_add_alt_1_rounded
                                : Icons.login_rounded,
                          ),
                          label: LocalizedText(
                            _loading
                                ? (_signUp
                                      ? 'Creating account...'
                                      : 'Signing in...')
                                : (_signUp ? 'Create account' : 'Sign in'),
                          ),
                        ),
                        if (_error != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 12),
                            child: LocalizedText(
                              _error!,
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.error,
                              ),
                            ),
                          ),
                        const SizedBox(height: 8),
                        Center(
                          child: TextButton(
                            onPressed: _loading ? null : _toggleMode,
                            child: Text(
                              _signUp
                                  ? 'Already have an account? Sign in'
                                  : "New to GoviSense? Sign up",
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class _TrustBadge extends StatelessWidget {
  const _TrustBadge({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.16)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppTheme.accent),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
