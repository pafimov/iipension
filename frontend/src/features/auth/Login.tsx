import { formValue } from '../../shared/ui/formValue';
import { useState } from 'react';
import { api } from '../../shared/api/client';
import type { Session } from '../../shared/api/client';
import { Feedback } from '../../shared/ui/Feedback';
export function Login({ onLogin }: { onLogin: (session: Session) => Promise<void> }) {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError('');
    try {
      await onLogin(await api.login(formValue(data, 'username'), formValue(data, 'password')));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось войти');
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="card login" aria-labelledby="login-title">
      <h2 id="login-title">Вход в личный кабинет</h2>
      <form
        onSubmit={(event) => {
          void submit(event);
        }}
      >
        <label>
          Имя пользователя
          <input name="username" autoComplete="username" required maxLength={150} />
        </label>
        <label>
          Пароль
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
            maxLength={1024}
          />
        </label>
        <Feedback error={error} />
        <button disabled={busy}>{busy ? 'Входим…' : 'Войти'}</button>
      </form>
    </section>
  );
}
