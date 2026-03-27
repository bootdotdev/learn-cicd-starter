import { describe, expect, it } from "vitest";
import { nextDelayMs } from "../worker/retry";

describe("nextDelayMs", () => {
  it("creates exponential backoff", () => {
    expect(nextDelayMs(1000, 1)).toBe(1000);
    expect(nextDelayMs(1000, 2)).toBe(2000);
    expect(nextDelayMs(1000, 3)).toBe(4000);
  });
});
