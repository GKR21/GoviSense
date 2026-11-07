/**
 * GoviSense Mobile Design System — Typography Tokens
 *
 * Tailored for tri-lingual display:
 * - English: Inter (clean, compact, tabular numerals for monetary ranges)
 * - Sinhala: Noto Sans Sinhala with enhanced line-height 1.6-1.7 to prevent diacritic clipping
 * - Tamil: Noto Sans Tamil with optimized glyph heights
 */

export const typography = {
  fontFamilies: {
    en: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    si: "'Noto Sans Sinhala', 'Inter', sans-serif",
    ta: "'Noto Sans Tamil', 'Inter', sans-serif",
  },
  sizes: {
    xs: { fontSize: "0.75rem", lineHeight: "1.4" },      // 12px
    sm: { fontSize: "0.875rem", lineHeight: "1.45" },    // 14px
    base: { fontSize: "1rem", lineHeight: "1.55" },      // 16px (minimum readable body)
    lg: { fontSize: "1.125rem", lineHeight: "1.5" },     // 18px
    xl: { fontSize: "1.25rem", lineHeight: "1.4" },      // 20px
    "2xl": { fontSize: "1.5rem", lineHeight: "1.3" },    // 24px
    "3xl": { fontSize: "1.875rem", lineHeight: "1.2" },  // 30px
    display: { fontSize: "2.25rem", lineHeight: "1.15" } // 36px
  },
  weights: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const

