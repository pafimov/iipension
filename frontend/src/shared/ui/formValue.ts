export function formValue(data: FormData, field: string): string {
  const value = data.get(field);
  if (typeof value !== 'string') throw new Error(`Missing text field: ${field}`);
  return value;
}
