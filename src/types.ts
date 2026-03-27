export type ActionType = "uppercase" | "pick_fields" | "add_metadata";

export interface PipelineAction {
  type: ActionType;
  config?: Record<string, unknown>;
}

export interface PipelineInput {
  name: string;
  action: PipelineAction;
  subscribers: string[];
}
