import { useColorScheme } from 'react-native';

import { colors, radius, spacing, typography, type Colors } from './tokens';

export { colors, radius, spacing, typography };
export type { Colors };

export function useTheme() {
  const scheme = useColorScheme() === 'dark' ? 'dark' : 'light';
  return { scheme, colors: colors[scheme], spacing, radius, typography } as const;
}
