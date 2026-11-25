import AsyncStorage from '@react-native-async-storage/async-storage';

import i18n, { restoreLanguage, setLanguage } from '@/i18n';
import en from '@/i18n/en';
import zh from '@/i18n/zh';

function keys(value: object, prefix = ''): string[] {
  return Object.entries(value).flatMap(([k, v]) =>
    typeof v === 'object' && v !== null ? keys(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  );
}

describe('i18n', () => {
  beforeEach(async () => {
    await AsyncStorage.clear();
    await i18n.changeLanguage('en');
  });

  it('has the same keys in every language', () => {
    expect(keys(zh).sort()).toEqual(keys(en).sort());
  });

  it('defaults to English', () => {
    expect(i18n.language).toBe('en');
    expect(i18n.t('tabs.home')).toBe('Home');
  });

  it('switches to Chinese and remembers the choice', async () => {
    await setLanguage('zh');
    expect(i18n.t('tabs.home')).toBe('首页');

    await i18n.changeLanguage('en');
    await restoreLanguage();
    expect(i18n.language).toBe('zh');
  });

  it('ignores an unknown saved language', async () => {
    await AsyncStorage.setItem('language', 'xx');
    await restoreLanguage();
    expect(i18n.language).toBe('en');
  });
});
