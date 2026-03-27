// src/tests/auth.test.ts
import { describe, it, expect } from "vitest";
import { getAPIKey } from "../api/auth";

describe("getAPIKey", () => {
  it("should return a key", () => {
    const key = getAPIKey();
    expect(key).toBe("my-secret-key");
  });
});
