import { Component } from '@angular/core';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../../../aws-exports';
@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  constructor(public authenticator: AuthenticatorService) {
    Amplify.configure(awsmobile);
  }
}
