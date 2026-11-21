import { formValue } from '../../shared/ui/formValue';
import { useState } from 'react';
import { api } from '../../shared/api/client';
import type { Goal, GoalInput } from '../../shared/api/client';
import { Feedback } from '../../shared/ui/Feedback';
export function GoalForm({ onSaved }: { onSaved: (goal: Goal) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const now = new Date();
  const currentMonth = `${String(now.getUTCFullYear())}-${String(now.getUTCMonth() + 1).padStart(2, '0')}`;
  async function submit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const basis = data.get('money_basis');
    if (basis !== 'today' && basis !== 'future') return;
    const payload: GoalInput = {
      monthly_income: formValue(data, 'monthly_income'),
      money_basis: basis,
      payout_start: `${formValue(data, 'payout_start')}-01`,
      payout_months: Number(data.get('payout_months')),
      initial_capital: formValue(data, 'initial_capital'),
      monthly_contribution: formValue(data, 'monthly_contribution'),
      risk_notes: formValue(data, 'risk_notes'),
    };
    setBusy(true);
    setError('');
    try {
      onSaved(await api.saveGoal(payload));
      form.reset();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось сохранить');
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="card" aria-labelledby="goal-title">
      <h2 id="goal-title">Параметры пенсии</h2>
      <form
        onSubmit={(event) => {
          void submit(event);
        }}
      >
        <div className="income-field">
          <label htmlFor="monthly-income">Сколько хотите получать в месяц?</label>
          <p id="income-example" className="hint">
            Например, 30 000 ₽.
          </p>
          <div className="income-input">
            <input
              id="monthly-income"
              name="monthly_income"
              type="number"
              inputMode="decimal"
              min="0.01"
              step="0.01"
              aria-describedby="income-example"
              required
            />
            <span aria-hidden="true">₽</span>
          </div>
        </div>
        <div className="field">
          <label htmlFor="money-basis">В каких ценах указана сумма?</label>
          <select id="money-basis" name="money_basis" aria-describedby="money-basis-hint">
            <option value="today">В сегодняшних ценах</option>
            <option value="future">В ценах на момент начала выплат</option>
          </select>
          <p id="money-basis-hint" className="hint">
            Выберите сегодняшние цены, если ориентируетесь на свои расходы сейчас.
          </p>
        </div>
        <fieldset>
          <legend>Когда получать пенсию</legend>
          <div className="form-grid">
            <label>
              Месяц начала выплат
              <input name="payout_start" type="month" min={currentMonth} required />
            </label>
            <label>
              Срок выплат, месяцев
              <input name="payout_months" type="number" min="1" max="1200" step="1" required />
            </label>
          </div>
        </fieldset>
        <fieldset aria-describedby="savings-hint">
          <legend>Накопления и риск</legend>
          <p id="savings-hint" className="hint">
            Если накоплений пока нет или вы не готовы откладывать, укажите 0 в нужном поле.
          </p>
          <div className="form-grid">
            <label>
              Уже накоплено, ₽
              <input
                name="initial_capital"
                type="number"
                inputMode="decimal"
                min="0"
                step="0.01"
                required
              />
            </label>
            <label>
              Могу откладывать в месяц, ₽
              <input
                name="monthly_contribution"
                type="number"
                inputMode="decimal"
                min="0"
                step="0.01"
                required
              />
            </label>
          </div>
          <div className="field risk-field">
            <label htmlFor="risk-notes">Ограничения риска</label>
            <textarea
              id="risk-notes"
              name="risk_notes"
              maxLength={1000}
              aria-describedby="risk-hint"
              required
            />
            <p id="risk-hint" className="hint">
              Укажите, какого риска хотите избегать, или напишите «Пока не определены».
            </p>
          </div>
        </fieldset>
        <Feedback error={error} />
        <div className="form-actions">
          <button disabled={busy}>{busy ? 'Сохраняем…' : 'Сохранить черновик'}</button>
          <p className="hint">После сохранения проверьте и подтвердите параметры.</p>
        </div>
      </form>
    </section>
  );
}
