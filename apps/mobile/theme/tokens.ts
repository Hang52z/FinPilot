// Design tokens. The single source for color, spacing, radius and type.
// Color is reserved for state, risk and interaction feedback.

const palette = {
  light: {
    background: '#FFFFFF',
    surface: '#F6F6F7',
    text: '#111113',
    textSecondary: '#6B6B72',
    border: '#E4E4E7',
    accent: '#3E63DD',
    positive: '#1A7F4B',
    negative: '#C62A2F',
  },
  dark: {
    background: '#0E0E10',
    surface: '#18181B',
    text: '#EDEDEF',
    textSecondary: '#8F8F96',
    border: '#2A2A2E',
    accent: '#7B93FF',
    positive: '#3DD68C',
    negative: '#FF6369',
  },
} as const;

export type ColorScheme = keyof typeof palette;
export type Colors = { [K in keyof (typeof palette)['light']]: string };

export const colors: Record<ColorScheme, Colors> = palette;

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;

export const radius = { sm: 6, md: 10, lg: 14 } as const;

export const typography = {
  title: { fontSize: 28, fontWeight: '700' },
  heading: { fontSize: 17, fontWeight: '600' },
  body: { fontSize: 17, fontWeight: '400' },
  caption: { fontSize: 13, fontWeight: '400' },
} as const;
