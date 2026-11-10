import '../../../core/localization/app_locale.dart';
import '../../../core/localization/localized_text.dart';

import 'package:flutter/material.dart';

import '../data/auth_repository.dart';
import '../../../shared/widgets/brand_mark.dart';
import '../../../shared/widgets/app_card.dart';

class AuthPage extends StatefulWidget {
  const AuthPage({super.key});
  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final _form = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  bool _obscure = true;
  String? _error;
  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (_loading || !_form.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await AuthRepository.instance.login(_username.text, _password.text);
    } catch (_) {
      if (mounted) {
        setState(
          () => _error =
              'Unable to sign in. Check your credentials and connection.',
        );
      }
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
                      LocalizedText(
                        'Welcome back',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 6),
                      const LocalizedText(
                        'Sign in with your GoviSense account.',
                      ),
                      const SizedBox(height: 20),
                      TextFormField(
                        controller: _username,
                        enabled: !_loading,
                        autocorrect: false,
                        autofillHints: const [AutofillHints.username],
                        decoration: InputDecoration(
                          labelText: context.tr('Username / email'),
                          prefixIcon: Icon(Icons.person_outline),
                        ),
                        validator: (v) => v == null || v.trim().isEmpty
                            ? context.tr('Enter your username')
                            : null,
                      ),
                      const SizedBox(height: 14),
                      TextFormField(
                        controller: _password,
                        enabled: !_loading,
                        obscureText: _obscure,
                        autofillHints: const [AutofillHints.password],
                        onFieldSubmitted: (_) => _login(),
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
                        validator: (v) => v == null || v.isEmpty
                            ? context.tr('Enter your password')
                            : null,
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton.icon(
                        onPressed: _loading ? null : _login,
                        icon: const Icon(Icons.login_rounded),
                        label: LocalizedText(
                          _loading ? 'Signing in...' : 'Sign in',
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
