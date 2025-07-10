import { TestBed } from '@angular/core/testing';

import { LearningPath } from './learning-path';

describe('LearningPath', () => {
  let service: LearningPath;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LearningPath);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
