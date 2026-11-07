/**
 * GoviSense Mobile Design System — Spacing, Elevation & Motion
 *
 * Strict 8pt grid with 48px minimum touch targets for one-handed mobile use.
 */

export const spacing = {
  grid: {
    1: "4px",
    2: "8px",
    3: "12px",
    4: "16px",
    5: "20px",
    6: "24px",
    8: "32px",
    10: "40px",
    12: "48px",
    16: "64px",
  },
  radii: {
    xs: "6px",
    sm: "10px",
    md: "14px",
    lg: "20px",
    xl: "26px",
    full: "9999px",
  },
  shadows: {
    sm: "0 1px 3px rgba(14, 28, 21, 0.05)",
    md: "0 6px 16px -2px rgba(14, 28, 21, 0.07), 0 2px 6px -1px rgba(14, 28, 21, 0.04)",
    lg: "0 12px 28px -4px rgba(14, 28, 21, 0.1), 0 4px 10px -2px rgba(14, 28, 21, 0.05)",
    glow: "0 4px 20px rgba(10, 92, 54, 0.18)",
    floatingNav: "0 8px 32px rgba(10, 30, 20, 0.12)",
  },
  touchTarget: "48px", // Minimum tap target
} as const

