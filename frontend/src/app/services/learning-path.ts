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
    if (!this.learningPathUuid) {
      throw new Error('Learning path UUID is not set. Please set it before calling this method.');
    }

    return this.http.get<LearningPathStatusResponse>('http://localhost:8000/learning_path/' + userId + '/' + this.learningPathUuid + '/status');
  }

  getLearningpath(userId: string) {
    return this.http.get<any>('http://localhost:8000/learning_path/' + userId + '/' + this.learningPathUuid);
  }

  setLearningPathUuid(uuid: string) {
    this.learningPathUuid = uuid;
  }

  getLearningPathUuid(): string {
    return this.learningPathUuid;
  }
}
