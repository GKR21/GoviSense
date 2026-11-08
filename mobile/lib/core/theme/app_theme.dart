import 'package:flutter/material.dart';

class AppTheme {
  const AppTheme._();

  // Brand Palette
  static const primary = Color(0xFF0A5C36); // Deep forest green
  static const primaryLight = Color(0xFF168B52); // Leaf green
  static const primaryDark = Color(0xFF08492B);
  static const primaryTint = Color(0xFFEAF5EF);
  static const accent = Color(0xFFE2F163); // Fresh lime accent
  static const accentDark = Color(0xFF38470B);

  // Surface & Inks (Outdoor Sunlight Optimized)
  static const ink = Color(0xFF0E1C15); // High contrast dark
  static const background = Color(0xFFF7F9F6); // Anti-glare warm paper
  static const surface = Colors.white;
  static const cardBorder = Color(0xFFE3EAE4);
  static const neutral800 = Color(0xFF16241D);
  static const neutral700 = Color(0xFF23332A);
  static const neutral600 = Color(0xFF506358);
  static const neutral400 = Color(0xFF7A8C82);
  static const neutral200 = Color(0xFFDFE6E2);
  static const neutral100 = Color(0xFFF0F4EE);

  // Semantic Data Risk Signals (Separated from Brand Green)
  static const balanced = Color(0xFF168B52);
  static const balancedTint = Color(0xFFE8F7EE);
  static const balancedBorder = Color(0xFFA6E3BF);

  static const shortage = Color(0xFFD44333); // High demand / shortage
  static const shortageTint = Color(0xFFFDF0ED);
  static const shortageBorder = Color(0xFFF7C3BD);

  static const oversupply = Color(0xFFB87300); // Market glut risk
  static const oversupplyTint = Color(0xFFFFF7E6);
  static const oversupplyBorder = Color(0xFFFCE0A6);

  static const info = Color(0xFF1E65D6);
  static const infoTint = Color(0xFFEFF5FF);
  static const infoBorder = Color(0xFFBBD5FC);

  static ThemeData light() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        surface: surface,
      ),
      scaffoldBackgroundColor: background,
      useMaterial3: true,
      fontFamily: 'Inter',
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          color: ink,
          fontSize: 28,
          fontWeight: FontWeight.w800,
          height: 1.2,
          letterSpacing: -0.5,
        ),
        headlineSmall: TextStyle(
          color: ink,
          fontSize: 20,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.3,
        ),
        titleLarge: TextStyle(
          color: ink,
          fontSize: 18,
          fontWeight: FontWeight.w700,
        ),
        titleMedium: TextStyle(
          color: ink,
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(color: neutral700, fontSize: 15, height: 1.5),
        bodyMedium: TextStyle(color: neutral600, fontSize: 13, height: 1.45),
        labelLarge: TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: ink,
        elevation: 0,
        centerTitle: false,
        scrolledUnderElevation: 1,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 16,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: cardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          minimumSize: const Size.fromHeight(50),
          elevation: 2,
          shadowColor: primary.withOpacity(0.3),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
