import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import '../data/auth_repository.dart';
import '../../../shared/widgets/brand_mark.dart';
import '../../../shared/widgets/app_card.dart';
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
      }
    } catch (e) {
      if (mounted) setState(() => _error = _messageFor(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Align(
              alignment: Alignment.centerRight,
              child: LanguagePicker(),
            ),
            const BrandMark(),
            const SizedBox(height: 46),
            LocalizedText(
              'Decisions grounded in supply, demand and uncertainty.',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 28),
            AppCard(
              child: Form(
                key: _form,
                child: AutofillGroup(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
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
                      if (_signUp) ...[
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
                              : (v) =>
                                    setState(() => _district = v ?? _district),
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
                            labelText: 'Officer registration code (if issued)',
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
                        label: Text(
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
  );
}
