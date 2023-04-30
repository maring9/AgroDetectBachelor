import { Component } from '@angular/core';
import { HeaderComponent } from 'src/app/components/header/header.component';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../../../aws-exports';
import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';
@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.css']
})
export class HomePageComponent {
  constructor(public authenticator: AuthenticatorService) {
    Amplify.configure(awsmobile);
  }
}
