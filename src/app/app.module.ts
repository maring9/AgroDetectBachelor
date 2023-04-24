import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import awsconfig from '../aws-exports';
import { ImageUploadComponent } from './image-upload/image-upload.component';
import { FooterComponent } from './footer/footer.component';
import { InferencePageComponent } from './inference-page/inference-page.component';
import { HeaderComponent } from './header/header.component';

Amplify.configure(awsconfig)

@NgModule({
  declarations: [
    AppComponent,
    ImageUploadComponent,
    FooterComponent,
    InferencePageComponent,
    HeaderComponent,
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
