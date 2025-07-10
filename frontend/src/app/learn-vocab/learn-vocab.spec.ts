import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LearnVocab } from './learn-vocab';

describe('LearnVocab', () => {
  let component: LearnVocab;
  let fixture: ComponentFixture<LearnVocab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LearnVocab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LearnVocab);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
