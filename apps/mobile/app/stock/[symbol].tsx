import Ionicons from '@expo/vector-icons/Ionicons';
import { Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Change } from '@/components/Change';
import { ErrorRow } from '@/components/ErrorRow';
import { PriceChart } from '@/components/PriceChart';
import { rangeChangePct } from '@/features/market/chart';
import {
  errorKey,
  formatChangePct,
  formatMarketDate,
  formatPrice,
  sourceName,
} from '@/features/market/format';
import { useHistory, useStock, useWatchlistToggle } from '@/hooks/useMarket';
import { RANGES, type Range } from '@/services/market';
import { useTheme } from '@/theme';

function WatchButton({ symbol }: { symbol: string }) {
  const { t } = useTranslation();
  const { colors, spacing } = useTheme();
  const { watched, ready, toggle, mutation } = useWatchlistToggle(symbol);
  if (!ready) return null;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={t(watched ? 'watchlist.remove' : 'watchlist.add')}
      accessibilityState={{ selected: watched, busy: mutation.isPending }}
      disabled={mutation.isPending}
      hitSlop={spacing.sm}
      onPress={() => toggle()}
      style={{ marginHorizontal: spacing.md }}
    >
      <Ionicons
        name={watched ? 'star' : 'star-outline'}
        size={22}
        color={watched ? colors.accent : colors.text}
      />
    </Pressable>
  );
}

export default function StockScreen() {
  const { symbol: raw } = useLocalSearchParams<{ symbol: string }>();
  const symbol = String(raw).toUpperCase();
  const { t, i18n } = useTranslation();
  const { colors, spacing, radius, typography } = useTheme();
  const [range, setRange] = useState<Range>('1Y');
  const stock = useStock(symbol);
  const history = useHistory(symbol, range);

  const values = history.data?.bars.map((b) => Number(b.adj_close)) ?? [];
  const rangePct = rangeChangePct(values);
  const last = stock.data?.last_close;

  return (
    <>
      <Stack.Screen
        options={{ title: symbol, headerRight: () => <WatchButton symbol={symbol} /> }}
      />
      <ScrollView
        style={{ backgroundColor: colors.background }}
        contentContainerStyle={{ padding: spacing.md, gap: spacing.md }}
      >
        {stock.isError ? (
          <ErrorRow
            message={t(errorKey(stock.error))}
            onRetry={() => void stock.refetch()}
            retrying={stock.isFetching}
          />
        ) : null}
        {stock.isPending ? <ActivityIndicator /> : null}

        {stock.data ? (
          <View>
            <Text style={[typography.body, { color: colors.textSecondary }]}>
              {stock.data.name}
            </Text>
            {last ? (
              <View style={styles.priceRow}>
                <Text style={[typography.title, styles.numbers, { color: colors.text }]}>
                  {formatPrice(last.close, stock.data.currency, i18n.language)}
                </Text>
                <Change
                  pct={last.change_pct === null ? null : Number(last.change_pct)}
                  style={typography.body}
                />
              </View>
            ) : (
              <Text style={[typography.body, { color: colors.textSecondary }]}>
                {t('market.noPrices')}
              </Text>
            )}
          </View>
        ) : null}

        {values.length > 1 ? (
          <PriceChart
            values={values}
            label={`${symbol} ${t(`market.ranges.${range}`)} ${
              rangePct === null ? '' : formatChangePct(rangePct)
            }`}
          />
        ) : history.isPending ? (
          <View style={styles.chartPlaceholder} />
        ) : null}

        <View style={styles.rangeRow}>
          <View
            accessibilityRole="tablist"
            style={[styles.ranges, { backgroundColor: colors.surface, borderRadius: radius.md }]}
          >
            {RANGES.map((r) => {
              const selected = r === range;
              return (
                <Pressable
                  key={r}
                  accessibilityRole="tab"
                  accessibilityState={{ selected }}
                  onPress={() => setRange(r)}
                  style={[
                    styles.range,
                    { borderRadius: radius.sm },
                    selected && { backgroundColor: colors.background },
                  ]}
                >
                  <Text
                    style={[
                      typography.caption,
                      { color: selected ? colors.text : colors.textSecondary },
                    ]}
                  >
                    {t(`market.ranges.${r}`)}
                  </Text>
                </Pressable>
              );
            })}
          </View>
          <Change pct={rangePct} style={typography.caption} />
        </View>

        {last && stock.data ? (
          <Text style={[typography.caption, { color: colors.textSecondary }]}>
            {t('market.dailyClose', {
              date: formatMarketDate(last.date, i18n.language),
              source: sourceName(stock.data.source),
            })}
          </Text>
        ) : null}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  priceRow: { flexDirection: 'row', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' },
  numbers: { fontVariant: ['tabular-nums'] },
  chartPlaceholder: { height: 200 },
  rangeRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  ranges: { flexDirection: 'row', padding: 2 },
  range: { paddingHorizontal: 12, paddingVertical: 6 },
});
