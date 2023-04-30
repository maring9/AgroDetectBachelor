import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { InferencePageComponent } from './pages/inference-page/inference-page.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
const routes: Routes = [
  { path: '', redirectTo:'/home', pathMatch: 'full'},
  { path: 'home', component: HomePageComponent},
  { path: 'inference', component: InferencePageComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
