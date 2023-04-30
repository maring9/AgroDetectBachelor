import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import awsconfig from '../aws-exports';
import { FooterComponent } from './components/footer/footer.component';
import { HeaderComponent } from './components/header/header.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { InferencePageComponent } from './pages/inference-page/inference-page.component';

Amplify.configure(awsconfig)

@NgModule({
  declarations: [
    AppComponent,
    FooterComponent,
    InferencePageComponent,
    HeaderComponent,
    HomePageComponent,
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
