import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

declare var webkitSpeechRecognition: any;

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
}

@Component({
  selector: 'app-conversation',
  standalone: false,
  templateUrl: './conversation.html',
  styleUrl: './conversation.sass'
})
export class Conversation {
  inputMessage: string = '';
  recognition: any;
  audioUrl: string | null = null;
  messages: ChatMessage[] = [];

  constructor(private http: HttpClient) {}

  startSpeechToText() {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser.');
      return;
    }
    this.recognition = new webkitSpeechRecognition();
    this.recognition.lang = 'en-US';
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      this.inputMessage = transcript;
      this.sendMessage();
    };

    this.recognition.onerror = (event: any) => {
      alert('Speech recognition error: ' + event.error);
    };

    this.recognition.start();
  }

  sendMessage() {
    if (!this.inputMessage.trim()) return;
    // Add user message to history
    this.messages.push({ sender: 'user', text: this.inputMessage });
    this.audioUrl = null;
    const userInput = this.inputMessage;
    this.inputMessage = '';
    this.http.post('http://localhost:8000/conversation', {
      message: userInput,
      chat_id: '',
      user_id: localStorage.getItem('username') || 'anonymous'
    }, { responseType: 'arraybuffer' }).subscribe({
      next: (audioData) => {
        const blob = new Blob([audioData], { type: 'audio/wav' });
        this.audioUrl = URL.createObjectURL(blob);
        // Show a placeholder or a static message for AI response
        this.messages.push({ sender: 'ai', text: 'AI response (audio below):' });
      },
      error: () => {
        this.messages.push({ sender: 'ai', text: 'Error contacting server.' });
      }
    });
  }
}
