import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';

import { Amplify, Auth } from 'aws-amplify';
import awsconfig from './aws-exports';

Amplify.configure(awsconfig);


platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
