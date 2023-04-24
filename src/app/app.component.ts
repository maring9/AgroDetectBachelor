import { Component } from '@angular/core';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../aws-exports';
import { HeaderComponent } from './header/header.component';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(public authenticator: AuthenticatorService) {
    Amplify.configure(awsmobile);
  }
  title = 'AgroDetectBachelorFrontend';
}

// <h2>{{console.log(user.signInUserSession.idToken)}}</h2>
// console = console;
