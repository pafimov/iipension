import { expect, test } from '@playwright/test';

test('save and review a pension plan with keyboard navigation on desktop and mobile', async ({
  page,
}) => {
  const username = process.env['E2E_USERNAME'];
  const password = process.env['E2E_PASSWORD'];
  if (!username || !password)
    throw new Error('Set E2E_USERNAME and E2E_PASSWORD for an isolated test account');
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`${message.text()} (${message.location().url})`);
  });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Спланируйте личную пенсию' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Вход в личный кабинет' })).toBeVisible();
  await page.screenshot({ path: 'test-results/welcome.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'К содержимому' })).toBeFocused();
  await page.keyboard.press('Enter');
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Имя пользователя')).toBeFocused();
  await page.getByLabel('Имя пользователя').fill(username);
  await page.getByLabel('Пароль', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Войти', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Параметры пенсии' })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  const marker = `E2E-${String(Date.now())}`;
  await page.getByLabel('Сколько хотите получать в месяц?').fill('30000.50');
  await page.getByLabel('Месяц начала выплат').fill('2090-01');
  await page.getByLabel('Срок выплат, месяцев').fill('120');
  const capital = page.getByLabel('Уже накоплено, ₽');
  await capital.fill('-1');
  await page.getByLabel('Могу откладывать в месяц, ₽').fill('8000');
  await page.getByLabel('Ограничения риска').fill(`${marker} ${'длинныйтекст'.repeat(12)}`);
  await page.getByRole('button', { name: 'Сохранить черновик' }).click();
  await expect(capital).toBeFocused();
  expect(await capital.evaluate((input: HTMLInputElement) => input.validity.rangeUnderflow)).toBe(
    true,
  );
  await capital.fill('99999999999999.99');
  await page.getByRole('button', { name: 'Сохранить черновик' }).press('Enter');
  const goal = page.getByRole('listitem').filter({ hasText: marker });
  await expect(goal).toBeVisible();
  const amount = goal.getByRole('heading', { name: '30 000,50 ₽ в месяц' });
  await expect(amount).toBeFocused();
  await expect(goal.getByText('99 999 999 999 999,99 ₽', { exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await page.screenshot({ path: 'test-results/mobile.png', fullPage: true });
  await page.keyboard.press('Tab');
  await expect(goal.getByRole('button', { name: 'Подтвердить параметры' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(goal.getByText('Параметры подтверждены')).toBeVisible();
  await expect(amount).toBeFocused();
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.reload();
  await expect(goal.getByText('Параметры подтверждены')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await page.screenshot({ path: 'test-results/desktop.png', fullPage: true });
  await page.getByRole('button', { name: 'Выйти', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Войти', exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});
