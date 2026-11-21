import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import { api } from '../../shared/api/client';
import { GoalForm } from './GoalForm';

afterEach(() => vi.restoreAllMocks());
it('sends money as strings and keeps input on failed save', async () => {
  const save = vi.spyOn(api, 'saveGoal').mockRejectedValue(new Error('Нет соединения'));
  const onSaved = vi.fn();
  const user = userEvent.setup();
  render(<GoalForm onSaved={onSaved} />);
  await user.type(screen.getByLabelText('Сколько хотите получать в месяц?'), '30000.50');
  await user.type(screen.getByLabelText('Месяц начала выплат'), '2090-01');
  await user.type(screen.getByLabelText('Срок выплат, месяцев'), '120');
  await user.type(screen.getByLabelText('Уже накоплено, ₽'), '0');
  await user.type(screen.getByLabelText('Могу откладывать в месяц, ₽'), '8000');
  await user.type(screen.getByLabelText('Ограничения риска'), 'Уточнить риск');
  await user.click(screen.getByRole('button', { name: 'Сохранить черновик' }));
  await waitFor(() => {
    expect(save).toHaveBeenCalledWith(
      expect.objectContaining({
        monthly_income: '30000.50',
        initial_capital: '0',
        monthly_contribution: '8000',
        payout_months: 120,
      }),
    );
  });
  expect(await screen.findByRole('alert')).toHaveTextContent('Нет соединения');
  expect(screen.getByLabelText('Сколько хотите получать в месяц?')).toHaveValue(30000.5);
  expect(onSaved).not.toHaveBeenCalled();
});
