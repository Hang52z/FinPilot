import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useHealth } from '@/hooks/useHealth';
import { useTheme } from '@/theme';

/** Renders nothing while the server is healthy or loading; a single error row otherwise. */
export function ServerStatus() {
  const { t } = useTranslation();
  const { colors, spacing, radius, typography } = useTheme();
  const { isError, data, refetch, isFetching } = useHealth();

  if (!isError && data?.status !== 'degraded') return null;

  return (
    <View
      accessibilityRole="alert"
      style={[
        styles.row,
        { backgroundColor: colors.surface, borderRadius: radius.md, padding: spacing.md },
      ]}
    >
      <Text style={[typography.body, { color: colors.negative }]}>
        {t('errors.serverUnreachable')}
      </Text>
      <Pressable
        accessibilityRole="button"
        disabled={isFetching}
        hitSlop={spacing.sm}
        onPress={() => void refetch()}
      >
        <Text style={[typography.body, { color: colors.accent, opacity: isFetching ? 0.4 : 1 }]}>
          {t('errors.retry')}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
});
