import { PipelineAction } from "../types";

function deepUppercase(value: unknown): unknown {
  if (typeof value === "string") return value.toUpperCase();
  if (Array.isArray(value)) return value.map(deepUppercase);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value)) out[k] = deepUppercase(v);
    return out;
  }
  return value;
}

export function applyAction(
  action: PipelineAction,
  payload: unknown,
  eventId: string
): unknown {
  if (action.type === "uppercase") {
    return deepUppercase(payload);
  }

  if (action.type === "pick_fields") {
    const fields = action.config?.fields;
    if (!Array.isArray(fields) || typeof payload !== "object" || payload === null) {
      return {};
    }

    const input = payload as Record<string, unknown>;
    const output: Record<string, unknown> = {};
    for (const field of fields) {
      if (typeof field === "string" && field in input) output[field] = input[field];
    }
    return output;
  }

  if (action.type === "add_metadata") {
    const original = payload && typeof payload === "object" ? payload : { payload };
    return {
      ...original,
      _metadata: {
        eventId,
        processedAt: new Date().toISOString()
      }
    };
  }

  return payload;
}
