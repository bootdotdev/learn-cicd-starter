export function nextDelayMs(baseMs: number, attempt: number): number {
  return baseMs * Math.pow(2, Math.max(0, attempt - 1));
}
