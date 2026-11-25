import Ionicons from '@expo/vector-icons/Ionicons';
import { Link } from 'expo-router';
import { Tabs } from 'expo-router/js-tabs';
import type { ComponentProps } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable } from 'react-native';

import { useTheme } from '@/theme';

type IconName = ComponentProps<typeof Ionicons>['name'];

function SettingsButton() {
  const { t } = useTranslation();
  const { colors, spacing } = useTheme();
  return (
    <Link href="/settings" asChild>
      <Pressable
        accessibilityLabel={t('settings.title')}
        hitSlop={spacing.sm}
        style={{ marginHorizontal: spacing.md }}
      >
        <Ionicons name="settings-outline" size={22} color={colors.text} />
      </Pressable>
    </Link>
  );
}

export default function TabsLayout() {
  const { t } = useTranslation();
  const { colors } = useTheme();

  const tab = (title: string, icon: IconName) => ({
    title,
    tabBarIcon: ({ focused, size }: { focused: boolean; size: number }) => (
      <Ionicons name={icon} color={focused ? colors.text : colors.textSecondary} size={size} />
    ),
  });

  return (
    <Tabs
      screenOptions={{
        headerRight: () => <SettingsButton />,
        headerShadowVisible: false,
        tabBarActiveTintColor: colors.text,
        tabBarInactiveTintColor: colors.textSecondary,
      }}
    >
      <Tabs.Screen name="index" options={tab(t('tabs.home'), 'home-outline')} />
      <Tabs.Screen name="research" options={tab(t('tabs.research'), 'search-outline')} />
      <Tabs.Screen name="ai" options={tab(t('tabs.ai'), 'chatbubble-outline')} />
      <Tabs.Screen name="portfolio" options={tab(t('tabs.portfolio'), 'pie-chart-outline')} />
    </Tabs>
  );
}
