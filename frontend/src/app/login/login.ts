import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {LoginResponse} from '../types/Login';
import { Router } from '@angular/router';
import {LearningPath} from '../services/learning-path';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.html',
  styleUrl: './login.sass'
})
export class LoginComponent {
  username = '';
  password = '';
  message = '';

  constructor(
    private http: HttpClient,
    private router: Router,
    private learningPathService: LearningPath
  ) {}

  onSubmit() {
    this.http.post<LoginResponse>('http://localhost:8000/login', {username: this.username, password: this.password})
      .subscribe({
        next: (response) => {
          if (response.status == 'success') {
            localStorage.setItem('username', response.message);
            this.message = 'Login successful! Username stored';
            // Trigger learning path generation
            this.learningPathService.triggerLearningPathGeneration(this.username).subscribe(response => {
              this.learningPathService.setLearningPathUuid(response.learning_path_id);
              this.router.navigate(['/main-menu']); // Redirect to main menu
            });
          } else {
            this.message = response.message || 'Login failed';
          }
        },
        error: (err) => this.message = err.message || 'Login failed'
      });
  }

  register() {
    this.http.post('http://localhost:8000/register', {username: this.username, password: this.password})
      .subscribe({
        next: () => this.message = 'Registered successfully!',
        error: err => this.message = err.error.detail || 'Registration failed'
      });
  }
}
