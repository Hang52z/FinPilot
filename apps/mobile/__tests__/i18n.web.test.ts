jest.mock('react-native', () => ({ Platform: { OS: 'web' } }));

it('keeps the page language in step on web', async () => {
  const documentElement = { lang: 'en' };
  Object.assign(global, { document: { documentElement } });
  const { setLanguage } = require('@/i18n') as typeof import('@/i18n');

  await setLanguage('zh');
  expect(documentElement.lang).toBe('zh-Hans');

  await setLanguage('en');
  expect(documentElement.lang).toBe('en');
});
