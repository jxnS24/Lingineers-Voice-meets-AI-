export interface MultipleChoiceOption {
  text: string;
  is_correct: boolean;
}

export interface MultipleChoiceQuestion {
  chosen_option: string;
  learning_path_id: string;
  question: {
    question: string;
    explanation: string;
    options: MultipleChoiceOption[]
  }
}
