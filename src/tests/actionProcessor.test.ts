import { describe, expect, it } from "vitest";
import { applyAction } from "../utils/actionProcessor";

describe("applyAction", () => {
  it("uppercases nested strings", () => {
    const output = applyAction(
      { type: "uppercase" },
      { msg: "hello", nested: { value: "world" } },
      "event-1"
    ) as Record<string, unknown>;

    expect(output.msg).toBe("HELLO");
    expect((output.nested as Record<string, unknown>).value).toBe("WORLD");
  });

  it("picks selected fields", () => {
    const output = applyAction(
      { type: "pick_fields", config: { fields: ["a", "c"] } },
      { a: 1, b: 2, c: 3 },
      "event-2"
    );

    expect(output).toEqual({ a: 1, c: 3 });
  });

  it("adds metadata", () => {
    const output = applyAction(
      { type: "add_metadata" },
      { a: 1 },
      "event-3"
    ) as Record<string, unknown>;

    expect(output.a).toBe(1);
    expect(output._metadata).toBeTruthy();
  });
});
