import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import awsconfig from '../aws-exports';
import { ImageUploadComponent } from './image-upload/image-upload.component';

Amplify.configure(awsconfig)

@NgModule({
  declarations: [
    AppComponent,
    ImageUploadComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    AmplifyAuthenticatorModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
