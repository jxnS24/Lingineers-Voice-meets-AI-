import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {LearningPath} from '../services/learning-path';

@Component({
  selector: 'app-main-menu',
  templateUrl: './main-menu.html',
  styleUrl: './main-menu.sass',
  standalone: false
})
export class MainMenuComponent implements OnInit {
  inputMessage: string = '';
  showFiller = false;
  messages: { sender: string, text: string, role?: string }[] = [];
  chatId: string = '';
  userId: string = localStorage.getItem('username') || 'anonymous';

  isLearningPathGenerated: boolean = false;

  constructor(
    private router: Router,
    private http: HttpClient,
    private learningPathService: LearningPath
  ) {
  }

  ngOnInit() {
    setInterval(() => {
      this.learningPathService.getStatusForLearningPath(this.userId).subscribe(response => {
        console.log(response);
        if (response.status == 'finished') {
          console.log('Learning path finished');
          this.isLearningPathGenerated = true;
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
}
