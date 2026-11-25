import { useState } from 'react';
import { View } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import { linePath } from '@/features/market/chart';
import { useTheme } from '@/theme';

const HEIGHT = 200;

export function PriceChart({ values, label }: { values: number[]; label: string }) {
  const { colors } = useTheme();
  const [width, setWidth] = useState(0);
  const first = values[0] ?? 0;
  const last = values[values.length - 1] ?? 0;
  const stroke = last > first ? colors.positive : last < first ? colors.negative : colors.text;
  const d = linePath(values, { width, height: HEIGHT, padding: 8 });

  return (
    <View
      accessible
      accessibilityRole="image"
      accessibilityLabel={label}
      style={{ height: HEIGHT }}
      onLayout={(e) => setWidth(e.nativeEvent.layout.width)}
    >
      {width > 0 && d !== '' && (
        <Svg width={width} height={HEIGHT}>
          <Path d={d} stroke={stroke} strokeWidth={1.5} fill="none" strokeLinejoin="round" />
        </Svg>
      )}
    </View>
  );
}
