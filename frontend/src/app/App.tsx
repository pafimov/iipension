import { useEffect, useState } from 'react';
import { api } from '../shared/api/client';
import type { Goal, Session } from '../shared/api/client';
import { Feedback } from '../shared/ui/Feedback';
import { Login } from '../features/auth/Login';
import { GoalForm } from '../features/goals/GoalForm';
import { GoalList } from '../features/goals/GoalList';
export function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    const isActive = () => active;
    void api
      .session()
      .then(async (value) => {
        if (!isActive()) return;
        setSession(value);
        if (value.user) {
          const page = await api.goals();
          if (isActive()) {
            setGoals(page.items);
            setHasMore(page.has_more);
          }
        }
      })
      .catch(() => {
        if (isActive()) setError('Не удалось подключиться. Проверьте сервис и обновите страницу.');
      })
      .finally(() => {
        if (isActive()) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  async function loggedIn(value: Session) {
    setError('');
    try {
      const page = await api.goals();
      setGoals(page.items);
      setHasMore(page.has_more);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось загрузить пенсионные планы');
    } finally {
      setSession(value);
    }
  }
  async function logout() {
    setBusy(true);
    setError('');
    try {
      setSession(await api.logout());
      setGoals([]);
      setReviewId(null);
      setHasMore(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось выйти');
    } finally {
      setBusy(false);
    }
  }
  async function loadMore() {
    setBusy(true);
    setError('');
    try {
      const page = await api.goals(goals.length);
      setGoals((old) => [...old, ...page.items]);
      setHasMore(page.has_more);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось загрузить пенсионные планы');
    } finally {
      setBusy(false);
    }
  }
  const user = session?.user;
  return (
    <>
      <a className="skip" href="#main">
        К содержимому
      </a>
      <header className="site-header">
        <div className="shell header-inner">
          <a className="brand" href="/">
            <span className="brand-mark" aria-hidden="true">
              ₽
            </span>
            Личная пенсия
          </a>
          {user && (
            <div className="account">
              <span>{user.username}</span>
              <button
                className="secondary"
                disabled={busy}
                onClick={() => {
                  void logout();
                }}
              >
                Выйти
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="shell" id="main">
        <div className={user ? 'overview' : 'overview welcome'}>
          <div className="intro">
            <h1>
              {user ? 'Ваша' : 'Спланируйте'}{' '}
              <mark>{user ? 'личная пенсия' : 'личную пенсию'}</mark>
            </h1>
            <p>
              Укажите, сколько хотите получать в месяц, когда начать и сколько готовы откладывать.
            </p>
          </div>
          {!user && !loading && session && <Login onLogin={loggedIn} />}
        </div>
        <Feedback error={error} />
        {loading ? (
          <p role="status">Загружаем данные…</p>
        ) : user ? (
          <div className="workspace">
            <GoalForm
              onSaved={(goal) => {
                setGoals((old) => [goal, ...old]);
                setReviewId(goal.id);
              }}
            />
            <GoalList
              goals={goals}
              reviewId={reviewId}
              onConfirmed={(goal) => {
                setGoals((old) => old.map((item) => (item.id === goal.id ? goal : item)));
                setReviewId(goal.id);
              }}
              onLoadMore={hasMore ? () => void loadMore() : undefined}
              pageBusy={busy}
            />
          </div>
        ) : null}
      </main>
      <footer className="shell availability">Расчёт пенсионных выплат пока недоступен.</footer>
    </>
  );
}
