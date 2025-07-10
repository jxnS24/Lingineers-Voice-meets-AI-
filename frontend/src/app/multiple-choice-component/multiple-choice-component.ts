import {Component, EventEmitter, inject, Input, OnInit, Output} from '@angular/core';
import {MultipleChoiceOption, MultipleChoiceQuestion} from '../types/mutliple-choice';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-multiple-choice',
  standalone: false,
  templateUrl: './multiple-choice-component.html',
  styleUrl: './multiple-choice-component.sass'
})
export class MultipleChoiceComponent implements OnInit {
  private _snackBar = inject(MatSnackBar);

  @Input()
  question!: MultipleChoiceQuestion

  @Output()
  questionSubmitted = new EventEmitter<any>();

  selectedOption!: MultipleChoiceOption;

  constructor() {
  }

  ngOnInit() {

  }

  submitAnswer() {
    if (this.selectedOption.is_correct) {
      this._snackBar.open("Your answer is correct!", "Close")
    } else {
      this._snackBar.open("Your answer is incorrect!" + this.question.question.explanation, "Close")
    }

    this.questionSubmitted.emit(this.selectedOption.is_correct);
  }
}
