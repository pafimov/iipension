import { afterEach, expect, it, vi } from 'vitest';
import { request } from './client';
afterEach(() => vi.unstubAllGlobals());
it('uses same-origin cookies and CSRF without browser token storage', async () => {
  document.cookie = 'csrftoken=example-token';
  const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }));
  vi.stubGlobal('fetch', fetchMock);
  await request('/api/test', { value: '1.00' });
  expect(fetchMock).toHaveBeenCalledWith(
    '/api/test',
    expect.objectContaining({
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': 'example-token' },
    }),
  );
});
it('does not expose raw server error or retry writes', async () => {
  const fetchMock = vi.fn().mockResolvedValue(new Response('private debug trace', { status: 500 }));
  vi.stubGlobal('fetch', fetchMock);
  await expect(request('/api/test', {})).rejects.toThrow('Сервис временно недоступен');
  expect(fetchMock).toHaveBeenCalledTimes(1);
});
