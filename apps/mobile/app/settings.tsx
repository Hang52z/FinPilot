import Ionicons from '@expo/vector-icons/Ionicons';
import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Screen } from '@/components/Screen';
import { languages, setLanguage } from '@/i18n';
import { useTheme } from '@/theme';

export default function SettingsScreen() {
  const { t, i18n } = useTranslation();
  const { colors, spacing, radius, typography } = useTheme();

  return (
    <Screen>
      <Text
        accessibilityRole="header"
        style={[typography.caption, { color: colors.textSecondary, marginBottom: spacing.sm }]}
      >
        {t('settings.language')}
      </Text>
      <View style={{ backgroundColor: colors.surface, borderRadius: radius.md }}>
        {languages.map(({ code, label }, index) => {
          const selected = i18n.language === code;
          return (
            <Pressable
              key={code}
              accessibilityLabel={label}
              accessibilityRole="radio"
              accessibilityState={{ checked: selected }}
              onPress={() => void setLanguage(code)}
              style={[
                styles.row,
                { padding: spacing.md },
                index > 0 && {
                  borderTopWidth: StyleSheet.hairlineWidth,
                  borderColor: colors.border,
                },
              ]}
            >
              <Text style={[typography.body, { color: colors.text }]}>{label}</Text>
              {selected && <Ionicons name="checkmark" size={20} color={colors.accent} />}
            </Pressable>
          );
        })}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
});
