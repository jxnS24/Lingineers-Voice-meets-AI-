import {NgModule, provideBrowserGlobalErrorListeners} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {AppRoutingModule} from './app-routing-module';
import {App} from './app';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatFormFieldModule} from '@angular/material/form-field'; // add this
import {MatInputModule} from '@angular/material/input'; // add this
import {FormsModule} from '@angular/forms';
import {LoginComponent} from './login/login';
import {MainMenuComponent} from './main-menu/main-menu';
import {provideHttpClient} from '@angular/common/http';
import {Conversation} from './conversation/conversation';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MultipleChoiceComponent} from './multiple-choice-component/multiple-choice-component';
import {MatRadioModule} from '@angular/material/radio';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import { LearnVocab } from './learn-vocab/learn-vocab';

@NgModule({
  declarations: [
    App,
    LoginComponent,
    MainMenuComponent,
    Conversation,
    MultipleChoiceComponent,
    MultipleChoiceComponent,
    LearnVocab
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatSidenavModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatSnackBarModule
  ],
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient()
  ],
  bootstrap: [App]
})
export class AppModule {
}
