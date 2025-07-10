import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {LearningPathStatusResponse, LearningPathTriggerResponse} from '../types/learning-path';

@Injectable({
  providedIn: 'root'
})
export class LearningPath {

  private learningPathUuid = ""

  constructor(
    private http: HttpClient,
  ) { }

  triggerLearningPathGeneration(userId: string) {
    return this.http.get<LearningPathTriggerResponse>('http://localhost:8000/learning_path/' + userId)
  }

  getStatusForLearningPath(userId: string) {
    return this.http.get<LearningPathStatusResponse>('http://localhost:8000/learning_path/' + userId + '/' + this.learningPathUuid);
  }

  setLearningPathUuid(uuid: string) {
    this.learningPathUuid = uuid;
  }

  getLearningPathUuid(): string {
    return this.learningPathUuid;
  }
}
