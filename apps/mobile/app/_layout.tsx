import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DarkTheme, DefaultTheme, Stack, ThemeProvider } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { restoreLanguage } from '@/i18n'; // also initializes i18next
import { useTheme } from '@/theme';

// Deep links to a modal (e.g. /settings) open with the tabs underneath.
export const unstable_settings = { anchor: '(tabs)' };

export default function RootLayout() {
  const [queryClient] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry: 1 } } }),
  );
  const { t } = useTranslation();
  const { scheme, colors } = useTheme();
  const base = scheme === 'dark' ? DarkTheme : DefaultTheme;

  useEffect(() => {
    void restoreLanguage();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        value={{
          ...base,
          colors: {
            ...base.colors,
            primary: colors.accent,
            background: colors.background,
            card: colors.background,
            text: colors.text,
            border: colors.border,
          },
        }}
      >
        <StatusBar style="auto" />
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen
            name="settings"
            options={{ title: t('settings.title'), presentation: 'modal' }}
          />
        </Stack>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
