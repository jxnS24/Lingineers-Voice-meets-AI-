import {Component, EventEmitter, inject, Input, OnInit, Output} from '@angular/core';
import {LearningVocab} from '../types/learn-vocab';
import {MatSnackBar} from '@angular/material/snack-bar';


@Component({
  selector: 'app-learn-vocab',
  standalone: false,
  templateUrl: './learn-vocab.html',
  styleUrl: './learn-vocab.sass'
})
export class LearnVocab implements OnInit {
  @Input()
  question!: LearningVocab

  @Output()
  questionSubmitted = new EventEmitter<any>();

  userAnswer: string = '';
  isCorrect: boolean = false;

  private _snackBar = inject(MatSnackBar);

  constructor() {}

  ngOnInit() {
  }


  submitAnswer() {
    if (!this.question) return;
    this.isCorrect = this.userAnswer.trim().toLowerCase() === this.question.expected_english.trim().toLowerCase();

    if(this.isCorrect){
      this._snackBar.open('You got it right!', 'Close');
    } else {
      this._snackBar.open(`Incorrect! The correct answer is: ${this.question.expected_english}`, 'Close');
    }

    this.userAnswer = ""
    this.questionSubmitted.emit(this.isCorrect);
  }
}
