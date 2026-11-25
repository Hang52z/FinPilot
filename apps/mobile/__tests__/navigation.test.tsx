import { userEvent } from '@testing-library/react-native';
import { renderRouter, screen, testRouter, waitFor } from 'expo-router/testing-library';

import i18n from '@/i18n';

beforeEach(async () => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({ status: 'ok', database: 'ok', version: '0.1.0' }),
  });
  await i18n.changeLanguage('en');
});

it('shows the four main tabs', async () => {
  await renderRouter('./app');

  for (const name of ['Home', 'Research', 'AI', 'Portfolio']) {
    expect(screen.getByRole('button', { name: new RegExp(name) })).toBeOnTheScreen();
  }
});

it('switches the interface to Chinese from Settings', async () => {
  await renderRouter('./app', { initialUrl: '/settings' });

  await userEvent.setup().press(screen.getByRole('radio', { name: '中文' }));

  await waitFor(() => expect(screen.getByRole('radio', { name: '中文' })).toBeChecked());
  expect(i18n.language).toBe('zh');

  await testRouter.navigate('/');
  expect(screen.getByRole('button', { name: /首页/ })).toBeOnTheScreen();
});
