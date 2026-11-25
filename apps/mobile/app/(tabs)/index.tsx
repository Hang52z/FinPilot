import { Link, router } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';

import { Change } from '@/components/Change';
import { ErrorRow } from '@/components/ErrorRow';
import { Screen } from '@/components/Screen';
import { ServerStatus } from '@/components/ServerStatus';
import { errorKey, formatMarketDate, formatPrice, sourceName } from '@/features/market/format';
import { useWatchlist } from '@/hooks/useMarket';
import type { WatchlistItem } from '@/services/market';
import { useTheme } from '@/theme';

export default function HomeScreen() {
  const { t, i18n } = useTranslation();
  const { colors, spacing, typography } = useTheme();
  const watchlist = useWatchlist();
  const items = watchlist.data?.items ?? [];
  const latest = items
    .map((i) => i.last_close?.date)
    .filter((d): d is string => !!d)
    .sort()
    .at(-1);

  const row = ({ item }: { item: WatchlistItem }) => {
    const last = item.last_close;
    return (
      <Link href={{ pathname: '/stock/[symbol]', params: { symbol: item.symbol } }} asChild>
        <Pressable
          accessibilityRole="link"
          style={StyleSheet.flatten([styles.row, { paddingVertical: spacing.md }])}
        >
          <View style={styles.name}>
            <Text style={[typography.heading, { color: colors.text }]}>{item.symbol}</Text>
            <Text numberOfLines={1} style={[typography.caption, { color: colors.textSecondary }]}>
              {item.name}
            </Text>
          </View>
          {last ? (
            <View style={styles.price}>
              <Text style={[typography.body, styles.numbers, { color: colors.text }]}>
                {formatPrice(last.close, 'USD', i18n.language)}
              </Text>
              <Change
                pct={last.change_pct === null ? null : Number(last.change_pct)}
                style={typography.caption}
              />
            </View>
          ) : (
            <Text style={[typography.caption, { color: colors.textSecondary }]}>
              {t('market.noPrices')}
            </Text>
          )}
        </Pressable>
      </Link>
    );
  };

  return (
    <Screen>
      <ServerStatus />
      {watchlist.isError && !watchlist.data ? (
        <ErrorRow
          message={t(errorKey(watchlist.error))}
          onRetry={() => void watchlist.refetch()}
          retrying={watchlist.isFetching}
        />
      ) : null}
      {watchlist.isSuccess && items.length === 0 ? (
        <View style={styles.empty}>
          <Text style={[typography.body, { color: colors.textSecondary }]}>
            {t('watchlist.empty')}
          </Text>
          <Pressable
            accessibilityRole="button"
            hitSlop={spacing.sm}
            onPress={() => router.navigate('/research')}
            style={{ marginTop: spacing.sm }}
          >
            <Text style={[typography.body, { color: colors.accent }]}>{t('watchlist.search')}</Text>
          </Pressable>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(i) => i.symbol}
          renderItem={row}
          ItemSeparatorComponent={() => (
            <View style={{ height: StyleSheet.hairlineWidth, backgroundColor: colors.border }} />
          )}
          refreshControl={
            <RefreshControl
              refreshing={watchlist.isRefetching}
              onRefresh={() => void watchlist.refetch()}
            />
          }
          ListFooterComponent={
            latest && watchlist.data ? (
              <Text
                style={[typography.caption, { color: colors.textSecondary, marginTop: spacing.md }]}
              >
                {t('market.dailyClose', {
                  date: formatMarketDate(latest, i18n.language),
                  source: sourceName(watchlist.data.source),
                })}
              </Text>
            ) : undefined
          }
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 16 },
  name: { flex: 1 },
  price: { alignItems: 'flex-end' },
  numbers: { fontVariant: ['tabular-nums'] },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
