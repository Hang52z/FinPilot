import { Text, type TextStyle } from 'react-native';

import { formatChangePct } from '@/features/market/format';
import { useTheme } from '@/theme';

/** Percent change with arrow and sign; color only reinforces the direction. */
export function Change({ pct, style }: { pct: number | null; style?: TextStyle }) {
  const { colors } = useTheme();
  if (pct === null) return null;
  const color = pct > 0 ? colors.positive : pct < 0 ? colors.negative : colors.textSecondary;
  return (
    <Text style={[style, { color, fontVariant: ['tabular-nums'] }]}>{formatChangePct(pct)}</Text>
  );
}
