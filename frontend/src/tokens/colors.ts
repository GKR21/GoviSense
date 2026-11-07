/**
 * GoviSense Mobile Design System — Smart Color Palette
 *
 * Engineered for high-sunlight outdoor readability in Sri Lankan fields,
 * tactile clarity, and distinct visual separation between brand identity
 * and semantic market risk signals (resolving the brand vs balanced conflict).
 */

export const colors = {
  // Brand Authority & Organic Roots
  brand: {
    primary: "#0A5C36", // Deep forest green - primary actions & header
    primaryHover: "#08492B",
    primaryLight: "#107A48", // Vibrant leaf green
    primaryTint: "#EAF5EF", // Light subtle green surface
    primaryBorder: "#BDE3CE",
    accent: "#E2F163", // Fresh lime accent for high-visibility highlights
    accentDark: "#38470B",
  },

  // Outdoor Friendly Paper & Surface System (Anti-glare warm tones)
  surface: {
    bg: "#F7F9F6", // Calming warm paper background (eliminates harsh glare)
    card: "#FFFFFF", // Elevated crisp card surface
    subtle: "#F0F4EE", // Secondary surfaces & containers
    muted: "#E6ECE4", // Subtle divider and inactive states
    cardHover: "#FAFCF9",
    glass: "rgba(255, 255, 255, 0.88)",
    glassDark: "rgba(10, 33, 20, 0.78)",
    border: "rgba(20, 38, 28, 0.08)",
    borderStrong: "rgba(20, 38, 28, 0.16)",
  },

  // Typography & High Contrast Inks
  ink: {
    title: "#0E1C15", // Ultra deep forest charcoal - 14:1 contrast ratio
    body: "#23332A", // Dark neutral for crisp reading
    secondary: "#506358", // Medium neutral for metadata
    muted: "#7A8C82", // Subtle hints and timestamps
    inverse: "#FFFFFF", // Text on brand/dark surfaces
  },

  // Perspective-Aware Semantic Signals (Reserved exclusively for data & market status)
  semantic: {
    // 1. Balanced Market (Supply matches demand)
    balanced: {
      base: "#168B52",
      text: "#0A502E",
      bg: "#E8F7EE",
      border: "#A6E3BF",
      badge: "#168B52",
    },
    // 2. High Demand / Potential Shortage (Opportunity for farmers)
    opportunity: {
      base: "#D44333", // Distinct coral brick (not muddy brown)
      text: "#8A1C10",
      bg: "#FDF0ED",
      border: "#F7C3BD",
      badge: "#D44333",
    },
    // 3. Oversupply / Price Depressing Risk (Farmer caution)
    caution: {
      base: "#B87300", // Warm amber ochre (clean & visible)
      text: "#6B4300",
      bg: "#FFF7E6",
      border: "#FCE0A6",
      badge: "#B87300",
    },
    // 4. Official Agrarian Advisory / Info
    info: {
      base: "#1E65D6",
      text: "#0D3C8A",
      bg: "#EFF5FF",
      border: "#BBD5FC",
      badge: "#1E65D6",
    },
  },

  // Visual Droplet and Moisture Indicators
  water: {
    low: "#5BB5E8",
    mid: "#2A88D8",
    high: "#0F5BA6",
    track: "#E2EEF8",
  },
} as const

export type ColorTokens = typeof colors

