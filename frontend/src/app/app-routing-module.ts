import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login';
import {MainMenuComponent} from './main-menu/main-menu';
import { Conversation } from './conversation/conversation'; // Add this import

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'main-menu', component: MainMenuComponent },
  { path: 'ai-conversation', component: Conversation },
  { path: '', redirectTo: '/login', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
