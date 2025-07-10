export interface LearningPathTriggerResponse {
  learning_path_id: string
}

export interface LearningPathStatusResponse {
  status: "finished" | "error" | "in_progress" | "in_preparation";
}
