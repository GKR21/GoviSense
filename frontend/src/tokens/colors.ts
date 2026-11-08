/**
 * GoviSense Mobile & Desktop Design System — Smart Color Palette
 *
 * Engineered for high-sunlight outdoor readability in Sri Lankan fields,
 * tactile clarity, and distinct visual separation between brand identity
 * and semantic market risk signals (resolving the brand vs balanced conflict).
 *
 * Supports both high-contrast Light (warm paper anti-glare) and Dark (deep obsidian forest) themes.
 */

export const colors = {
  // Dual-Theme Palette
  light: {
    brand: {
      primary: "#0A5C36", // Deep forest green - authority & institutional trust
      primaryHover: "#08492B",
      primaryDark: "#073B23",
      primaryLight: "#107A48", // Vibrant leaf green
      primaryTint: "#EAF5EF",
      primaryBorder: "#BDE3CE",
      accent: "#E2F163", // Fresh high-visibility lime
      accentContrast: "#1C2600",
      accentDark: "#38470B",
    },
    surface: {
      bg: "#F7F9F6", // Calming warm paper (anti-glare)
      card: "#FFFFFF",
      subtle: "#F0F4EE",
      muted: "#E6ECE4",
      cardHover: "#FAFCF9",
      glass: "rgba(255, 255, 255, 0.92)",
      border: "rgba(20, 38, 28, 0.08)",
      borderStrong: "rgba(20, 38, 28, 0.16)",
    },
    ink: {
      title: "#0E1C15", // 14:1 ultra-high contrast charcoal
      body: "#23332A",
      secondary: "#506358",
      muted: "#7A8C82",
      inverse: "#FFFFFF",
    },
    semantic: {
      balanced: {
        base: "#168B52",
        text: "#0A502E",
        bg: "#E8F7EE",
        border: "#A6E3BF",
      },
      opportunity: {
        base: "#D44333",
        text: "#8A1C10",
        bg: "#FDF0ED",
        border: "#F7C3BD",
      },
      caution: {
        base: "#B87300",
        text: "#6B4300",
        bg: "#FFF7E6",
        border: "#FCE0A6",
      },
      info: {
        base: "#1E65D6",
        text: "#0D3C8A",
        bg: "#EFF5FF",
        border: "#BBD5FC",
      },
    },
    water: {
      low: "#5BB5E8",
      mid: "#2A88D8",
      high: "#0F5BA6",
      track: "#E2EEF8",
    },
  },
  dark: {
    brand: {
      primary: "#1EB96C", // Luminous botanical emerald for dark theme
      primaryHover: "#27D47E",
      primaryDark: "#14854C",
      primaryLight: "#35E087",
      primaryTint: "rgba(30, 185, 108, 0.14)",
      primaryBorder: "rgba(30, 185, 108, 0.3)",
      accent: "#E2F163",
      accentContrast: "#101900",
      accentDark: "#C5D83A",
    },
    surface: {
      bg: "#0B130E", // Deep obsidian forest (not harsh cold grey)
      card: "#121C16",
      subtle: "#17241C",
      muted: "#233229",
      cardHover: "#192720",
      glass: "rgba(18, 28, 22, 0.92)",
      border: "rgba(255, 255, 255, 0.08)",
      borderStrong: "rgba(255, 255, 255, 0.16)",
    },
    ink: {
      title: "#F1F7F4", // Crisp 15:1 soft white
      body: "#D6E2DB",
      secondary: "#A3B8AD",
      muted: "#6E8477",
      inverse: "#0E1C15",
    },
    semantic: {
      balanced: {
        base: "#2BD482",
        text: "#96F0C2",
        bg: "rgba(43, 212, 130, 0.15)",
        border: "rgba(43, 212, 130, 0.35)",
      },
      opportunity: {
        base: "#FF6B6B",
        text: "#FFB8B8",
        bg: "rgba(255, 107, 107, 0.15)",
        border: "rgba(255, 107, 107, 0.35)",
      },
      caution: {
        base: "#F5A623",
        text: "#FFDEB0",
        bg: "rgba(245, 166, 35, 0.15)",
        border: "rgba(245, 166, 35, 0.35)",
      },
      info: {
        base: "#5995FF",
        text: "#BDD6FF",
        bg: "rgba(89, 149, 255, 0.15)",
        border: "rgba(89, 149, 255, 0.35)",
      },
    },
    water: {
      low: "#72C6F5",
      mid: "#459DE8",
      high: "#2579CC",
      track: "rgba(69, 157, 232, 0.15)",
    },
  },

  // Backward-compatible direct bindings (maps to light by default)
  brand: {
    primary: "#0A5C36",
    primaryHover: "#08492B",
    primaryLight: "#107A48",
    primaryTint: "#EAF5EF",
    primaryBorder: "#BDE3CE",
    accent: "#E2F163",
    accentContrast: "#1C2600",
    accentDark: "#38470B",
  },
  surface: {
    bg: "#F7F9F6",
    card: "#FFFFFF",
    subtle: "#F0F4EE",
    muted: "#E6ECE4",
    cardHover: "#FAFCF9",
    glass: "rgba(255, 255, 255, 0.88)",
    glassDark: "rgba(10, 33, 20, 0.78)",
    border: "rgba(20, 38, 28, 0.08)",
    borderStrong: "rgba(20, 38, 28, 0.16)",
  },
  ink: {
    title: "#0E1C15",
    body: "#23332A",
    secondary: "#506358",
    muted: "#7A8C82",
    inverse: "#FFFFFF",
  },
  semantic: {
    balanced: {
      base: "#168B52",
      text: "#0A502E",
      bg: "#E8F7EE",
      border: "#A6E3BF",
      badge: "#168B52",
    },
    opportunity: {
      base: "#D44333",
      text: "#8A1C10",
      bg: "#FDF0ED",
      border: "#F7C3BD",
      badge: "#D44333",
    },
    caution: {
      base: "#B87300",
      text: "#6B4300",
      bg: "#FFF7E6",
      border: "#FCE0A6",
      badge: "#B87300",
    },
    info: {
      base: "#1E65D6",
      text: "#0D3C8A",
      bg: "#EFF5FF",
      border: "#BBD5FC",
      badge: "#1E65D6",
    },
  },
  water: {
    low: "#5BB5E8",
    mid: "#2A88D8",
    high: "#0F5BA6",
    track: "#E2EEF8",
  },
} as const

export type ColorTokens = typeof colors
