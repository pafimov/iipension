import { useEffect, useRef, useState } from 'react';
import { api } from '../../shared/api/client';
import type { Goal } from '../../shared/api/client';
import { Feedback } from '../../shared/ui/Feedback';

const rubles = new Intl.NumberFormat('ru-RU');
const month = new Intl.DateTimeFormat('ru-RU', { month: 'long', year: 'numeric', timeZone: 'UTC' });

function displayAmount(amount: string): string {
  const [whole = '0', fraction = '00'] = amount.split('.');
  const formatted = rubles.format(BigInt(whole)).replace(/\s/g, ' ');
  return fraction === '00' ? formatted : `${formatted},${fraction}`;
}

export function GoalList({
  goals,
  reviewId,
  onConfirmed,
  onLoadMore,
  pageBusy,
}: {
  goals: Goal[];
  reviewId: string | null;
  onConfirmed: (goal: Goal) => void;
  onLoadMore: (() => void) | undefined;
  pageBusy: boolean;
}) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState('');
  const reviewHeading = useRef<HTMLHeadingElement>(null);
  const reviewedGoal = goals.find((goal) => goal.id === reviewId);
  useEffect(() => {
    if (reviewedGoal) reviewHeading.current?.focus();
  }, [reviewedGoal]);

  async function confirm(id: string) {
    setBusy(id);
    setError('');
    try {
      onConfirmed(await api.confirm(id));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось подтвердить');
    } finally {
      setBusy(null);
    }
  }
  return (
    <section className="card saved" aria-labelledby="saved-title">
      <h2 id="saved-title">Сохранённые планы</h2>
      <Feedback error={error} />
      {goals.length === 0 ? (
        <p className="hint">Здесь появится черновик, когда вы сохраните параметры пенсии.</p>
      ) : (
        <ul className="plans" role="list">
          {goals.map((goal) => (
            <li key={goal.id}>
              <div className="plan-heading">
                <p id={`status-${goal.id}`} className="plan-status">
                  {goal.confirmed_at ? 'Параметры подтверждены' : 'Черновик'}
                </p>
                <h3
                  ref={goal.id === reviewId ? reviewHeading : undefined}
                  tabIndex={-1}
                  aria-describedby={`status-${goal.id}`}
                >
                  {displayAmount(goal.monthly_income)}&nbsp;₽ <small>в месяц</small>
                </h3>
              </div>
              <dl>
                <div>
                  <dt>Сумма</dt>
                  <dd>
                    {goal.money_basis === 'today'
                      ? 'В сегодняшних ценах'
                      : 'В ценах на момент начала выплат'}
                  </dd>
                </div>
                <div>
                  <dt>Начало выплат</dt>
                  <dd>{month.format(new Date(goal.payout_start))}</dd>
                </div>
                <div>
                  <dt>Срок выплат</dt>
                  <dd>{goal.payout_months} мес.</dd>
                </div>
                <div>
                  <dt>Уже накоплено</dt>
                  <dd>{displayAmount(goal.initial_capital)}&nbsp;₽</dd>
                </div>
                <div>
                  <dt>Могу откладывать</dt>
                  <dd>{displayAmount(goal.monthly_contribution)}&nbsp;₽ / мес.</dd>
                </div>
                <div className="plan-risk">
                  <dt>Ограничения риска</dt>
                  <dd>{goal.risk_notes}</dd>
                </div>
              </dl>
              {!goal.confirmed_at && (
                <button
                  className="secondary"
                  disabled={busy !== null}
                  onClick={() => {
                    void confirm(goal.id);
                  }}
                >
                  {busy === goal.id ? 'Подтверждаем…' : 'Подтвердить параметры'}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      {onLoadMore && (
        <button className="secondary more-plans" disabled={pageBusy} onClick={onLoadMore}>
          Показать ещё планы
        </button>
      )}
    </section>
  );
}
