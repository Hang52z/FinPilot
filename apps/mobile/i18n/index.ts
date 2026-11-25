import AsyncStorage from '@react-native-async-storage/async-storage';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './en';
import zh from './zh';

export const languages = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' },
] as const;

export type Language = (typeof languages)[number]['code'];

const STORAGE_KEY = 'language';
const DEFAULT_LANGUAGE: Language = 'en';

function isLanguage(value: unknown): value is Language {
  return languages.some((l) => l.code === value);
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, zh: { translation: zh } },
  lng: DEFAULT_LANGUAGE,
  fallbackLng: DEFAULT_LANGUAGE,
  interpolation: { escapeValue: false },
});

/** Restores the saved language. Falls back to English if storage is empty or unreadable. */
export async function restoreLanguage(): Promise<void> {
  try {
    const saved = await AsyncStorage.getItem(STORAGE_KEY);
    if (isLanguage(saved)) await i18n.changeLanguage(saved);
  } catch {
    // Storage failure is non-fatal: keep the default language.
  }
}

export async function setLanguage(language: Language): Promise<void> {
  await i18n.changeLanguage(language);
  await AsyncStorage.setItem(STORAGE_KEY, language);
}

export default i18n;
