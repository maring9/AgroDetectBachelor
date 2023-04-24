import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { InferencePageComponent } from './inference-page/inference-page.component';
const routes: Routes = [
  { path: '', redirectTo:'/home', pathMatch: 'full'},
  { path: 'home', component: AppComponent},
  { path: 'inference', component: InferencePageComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
