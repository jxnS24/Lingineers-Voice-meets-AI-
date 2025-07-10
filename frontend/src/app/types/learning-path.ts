export interface LearningPathTriggerResponse {
  learning_path_id: string
}

export interface LearningPathStatusResponse {
  status: "finished" | "error" | "in_progress" | "in_preparation";
}

export interface LearningPathStep {
  step: string
  type: "vocab" | "multiple_choice" | "conversation"
}
