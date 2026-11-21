import type { components } from './schema';
export type Goal = components['schemas']['GoalOutput'];
export type GoalInput = components['schemas']['GoalInput'];
export type GoalPage = components['schemas']['GoalPage'];
export interface Session {
  user: { username: string } | null;
}
function csrfToken(): string {
  return (
    document.cookie
      .split('; ')
      .find((part) => part.startsWith('csrftoken='))
      ?.slice(10) ?? ''
  );
}
export async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method: body === undefined ? 'GET' : 'POST',
    credentials: 'same-origin',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!response.ok) {
    const messages: Record<number, string> = {
      401: 'Не удалось войти или сессия завершилась. Обновите страницу и войдите снова.',
      403: 'Действие отклонено. Обновите страницу и проверьте вход.',
      409: 'Дата цели устарела. Создайте новый черновик.',
      422: 'Проверьте поля: суммы с точностью до копейки, сроки и ограничения риска.',
      429: 'Слишком много попыток входа. Повторите позже.',
    };
    throw new Error(messages[response.status] ?? 'Сервис временно недоступен. Повторите действие.');
  }
  return (await response.json()) as T;
}
export const api = {
  session: () => request<Session>('/api/auth/session'),
  login: (username: string, password: string) =>
    request<Session>('/api/auth/login', { username, password }),
  logout: () => request<Session>('/api/auth/logout', {}),
  goals: (offset = 0) => request<GoalPage>(`/api/v1/goals?offset=${String(offset)}`),
  saveGoal: (goal: GoalInput) => request<Goal>('/api/v1/goals', goal),
  confirm: (id: string) => request<Goal>(`/api/v1/goals/${id}/confirm`, { confirmed: true }),
};
