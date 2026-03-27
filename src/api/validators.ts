import { z } from "zod";

const actionType = z.enum(["uppercase", "pick_fields", "add_metadata"]);

export const pipelineSchema = z.object({
  name: z.string().min(1),
  action: z.object({
    type: actionType,
    config: z.record(z.unknown()).optional()
  }),
  subscribers: z.array(z.string().url()).min(1)
});
