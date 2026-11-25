import { Link } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { ErrorRow } from '@/components/ErrorRow';
import { Screen } from '@/components/Screen';
import { errorKey } from '@/features/market/format';
import { useSearch } from '@/hooks/useMarket';
import { useTheme } from '@/theme';

export default function ResearchScreen() {
  const { t } = useTranslation();
  const { colors, spacing, radius, typography } = useTheme();
  const [query, setQuery] = useState('');
  const search = useSearch(query);
  const results = search.data ?? [];

  return (
    <Screen>
      <TextInput
        accessibilityLabel={t('search.placeholder')}
        autoCapitalize="characters"
        autoCorrect={false}
        autoFocus
        clearButtonMode="while-editing"
        onChangeText={setQuery}
        placeholder={t('search.placeholder')}
        placeholderTextColor={colors.textSecondary}
        returnKeyType="search"
        value={query}
        style={[
          typography.body,
          {
            backgroundColor: colors.surface,
            borderRadius: radius.md,
            color: colors.text,
            paddingHorizontal: spacing.md,
            paddingVertical: spacing.sm + 2,
            marginBottom: spacing.sm,
          },
        ]}
      />
      {search.isError ? (
        <ErrorRow
          message={t(errorKey(search.error))}
          onRetry={() => void search.refetch()}
          retrying={search.isFetching}
        />
      ) : null}
      {search.isSuccess && results.length === 0 ? (
        <Text style={[typography.body, { color: colors.textSecondary, marginTop: spacing.md }]}>
          {t('search.noResults')}
        </Text>
      ) : null}
      <FlatList
        data={results}
        keyboardShouldPersistTaps="handled"
        keyExtractor={(r) => r.symbol}
        renderItem={({ item }) => (
          <Link href={{ pathname: '/stock/[symbol]', params: { symbol: item.symbol } }} asChild>
            <Pressable
              accessibilityRole="link"
              style={StyleSheet.flatten([styles.row, { paddingVertical: spacing.sm + 4 }])}
            >
              <Text style={[typography.heading, styles.symbol, { color: colors.text }]}>
                {item.symbol}
              </Text>
              <Text
                numberOfLines={1}
                style={[typography.body, styles.name, { color: colors.textSecondary }]}
              >
                {item.name}
              </Text>
              {item.asset_type === 'etf' ? (
                <Text style={[typography.caption, { color: colors.textSecondary }]}>
                  {t('search.etf')}
                </Text>
              ) : null}
            </Pressable>
          </Link>
        )}
        ItemSeparatorComponent={() => (
          <View style={{ height: StyleSheet.hairlineWidth, backgroundColor: colors.border }} />
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  symbol: { minWidth: 64 },
  name: { flex: 1 },
});
