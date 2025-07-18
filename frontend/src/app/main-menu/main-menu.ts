import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {LearningPath} from '../services/learning-path';
import {LearningPathStep} from '../types/learning-path';
import {MultipleChoiceOption, MultipleChoiceQuestion} from '../types/mutliple-choice';
import {QuestionService} from '../services/question';
import {LearningVocab} from '../types/learn-vocab';

@Component({
  selector: 'app-main-menu',
  templateUrl: './main-menu.html',
  styleUrl: './main-menu.sass',
  standalone: false
})
export class MainMenuComponent implements OnInit {
  inputMessage: string = '';
  messages: { sender: string, text: string, role?: string }[] = [];
  chatId: string = '';
  userId: string = localStorage.getItem('username') || 'anonymous';

  steps: LearningPathStep[] = [];
  isLearningPathGenerated: boolean = false;

  multipleChoiceQuestions: MultipleChoiceQuestion[] = []
  multipleChoiceQuestionIndex: number = 0;

  vocabQuestions: LearningVocab[] = [];
  vocabQuestionIndex: number = 0;

  correctAnswers: number = 0;
  incorrectAnswers: number = 0;

  currentQuestionType = '';
  currentQuestionIndex: number = 0;

  isComplete: boolean = false;

  constructor(
    private router: Router,
    private http: HttpClient,
    private learningPathService: LearningPath,
    private questionService: QuestionService,
  ) {
  }

  ngOnInit() {
    this.learningPathService.setLearningPathUuid("c594cd9c-e2f8-49f3-84e3-f8b097c5b5e6")
    const intervalId = setInterval(() => {
      this.learningPathService.getStatusForLearningPath(this.userId).subscribe(response => {
        console.log(response);
        if (response.status == 'finished') {
          console.log('Learning path finished');
          this.isLearningPathGenerated = true;
          clearInterval(intervalId);
          this.startLearning()
        }
      });
    }, 10_000);
  }

  logout() {
    localStorage.removeItem('username');
    this.router.navigate(['/login']);
  }

  sendMessage() {
    if (this.inputMessage.trim()) {
      const userMsg = {sender: 'You', text: this.inputMessage, role: 'user'};
      this.messages.push(userMsg);

      this.http.post<any>('http://localhost:8000/chat_conversation', {
        message: this.inputMessage,
        chat_id: this.chatId,
        user_id: this.userId
      }).subscribe({
        next: (response) => {
          this.chatId = response.chat_id; // maintain conversation context
          this.messages.push({sender: 'Chatbot', text: response.message, role: 'assistant'});
        },
        error: () => {
          this.messages.push({sender: 'Chatbot', text: 'Error contacting server.', role: 'assistant'});
        }
      });

      this.inputMessage = '';
    }
  }

  startLearning() {
    this.learningPathService.getLearningpath(this.userId).subscribe(response => {
      let steps: LearningPathStep[] = response.steps;
      if (steps && steps.length > 0) {
        this.steps = steps;
        console.log(this.steps)
        this.questionService.getMultipleChoiceQuestions(this.learningPathService.getLearningPathUuid()).subscribe(questions => {
          this.multipleChoiceQuestions = questions;

          this.questionService.getVocabQuestions(this.learningPathService.getLearningPathUuid()).subscribe(questions => {
            this.vocabQuestions = questions;

            this.currentQuestionType = this.steps[this.currentQuestionIndex].type;

            if (this.currentQuestionType == 'conversation') {
              this.nextQuestion();
            }

          });
        });

      }
    })
  }

  nextMultipleChoiceQuestion(option: MultipleChoiceOption) {
    this.multipleChoiceQuestionIndex++;
    console.log('multi', option)

    if (option) {
      this.correctAnswers++;
    } else {
      this.incorrectAnswers++;
    }
    this.nextQuestion();
  }

  nextVocabQuestion(event: any) {
    this.vocabQuestionIndex++;

    if (event) {
      this.correctAnswers++;
    } else {
      this.incorrectAnswers++;
    }

    this.nextQuestion();
  }

  nextQuestion() {
    ++this.currentQuestionIndex

    if (this.currentQuestionIndex >= this.steps.length) {
      this.isComplete = true;
      console.log('done')
      return;
    }

    this.currentQuestionType = this.steps[this.currentQuestionIndex].type;

    if (this.currentQuestionType == 'conversation') {
      this.nextQuestion();
    }
  }
}
