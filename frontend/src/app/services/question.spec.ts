import { TestBed } from '@angular/core/testing';

import { Question } from './question';

describe('Question', () => {
  let service: Question;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Question);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
