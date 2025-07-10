import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {MultipleChoiceQuestion} from '../types/mutliple-choice';
import {LearningVocab} from '../types/learn-vocab';

@Injectable({
  providedIn: 'root'
})
export class QuestionService {

  constructor(
    private http: HttpClient
  ) { }

  getMultipleChoiceQuestions(learningPathId: string) {
    return this.http.get<MultipleChoiceQuestion[]>(`http://localhost:8000/multiple-choice/${learningPathId}`);
  }

  getMultipleChoiceQuestion(learningPathId: string, index: string) {
    return this.http.get<MultipleChoiceQuestion>(`http://localhost:8000/multiple-choice/${learningPathId}/${index}`);
  }

  getVocabQuestions(learningPathId: string) {
    return this.http.get<LearningVocab[]>(`http://localhost:8000/vocab/${learningPathId}`);
  }

  getVocabQuestion(learningPathId: string, index: string) {
    return this.http.get<LearningVocab>(`http://localhost:8000/vocab/${learningPathId}/${index}`);
  }
}
