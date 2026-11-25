import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useTheme } from '@/theme';

type Props = { message: string; onRetry?: () => void; retrying?: boolean };

/** One-line error with an optional Retry. The standard error presentation for every screen. */
export function ErrorRow({ message, onRetry, retrying = false }: Props) {
  const { t } = useTranslation();
  const { colors, spacing, radius, typography } = useTheme();

  return (
    <View
      accessibilityRole="alert"
      style={[
        styles.row,
        { backgroundColor: colors.surface, borderRadius: radius.md, padding: spacing.md },
      ]}
    >
      <Text style={[typography.body, styles.message, { color: colors.negative }]}>{message}</Text>
      {onRetry && (
        <Pressable
          accessibilityRole="button"
          disabled={retrying}
          hitSlop={spacing.sm}
          onPress={onRetry}
        >
          <Text style={[typography.body, { color: colors.accent, opacity: retrying ? 0.4 : 1 }]}>
            {t('errors.retry')}
          </Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12 },
  message: { flexShrink: 1 },
});
