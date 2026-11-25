import type { ReactNode } from 'react';
import { StyleSheet, View } from 'react-native';

import { useTheme } from '@/theme';

export function Screen({ children }: { children?: ReactNode }) {
  const { colors, spacing } = useTheme();
  return (
    <View style={[styles.root, { backgroundColor: colors.background, padding: spacing.md }]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({ root: { flex: 1 } });
