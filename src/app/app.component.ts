import { Component } from '@angular/core';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../aws-exports';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(public authenticator: AuthenticatorService) {
    Amplify.configure(awsmobile);
  }
  title = 'AgroDetectBachelor';
}
