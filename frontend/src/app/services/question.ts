import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {MultipleChoiceQuestion} from '../types/mutliple-choice';

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
}
