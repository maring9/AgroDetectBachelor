import { Component } from '@angular/core';
import { Auth, API } from 'aws-amplify';

@Component({
  selector: 'app-image-upload',
  templateUrl: './image-upload.component.html',
  styleUrls: ['./image-upload.component.css']
})
export class ImageUploadComponent {

  b64EncodedImage?: string = "";
  response?: object;

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    // if (!file) {
    //   return false;
    // }
    const reader = new FileReader();
    console.log('Encoding image...');
    reader.readAsDataURL(file);

    reader.onload = () => {
      this.b64EncodedImage= reader.result?.toString().split(',')[1];
      console.log(this.b64EncodedImage);

    };
  }

  async runInference() {
    console.log('Running inference');
    const user = await Auth.currentAuthenticatedUser();

    const jwtToken = user.signInUserSession.idToken.jwtToken;
    console.log(jwtToken);

    const requestData = {
      body: this.b64EncodedImage,
      headers : {
        Authorization: jwtToken
      }
    }
    console.log('Sending request, waiting for response...');

    try {
      this.response = await API.post('AgroDetectAppApi', '/inference', requestData);
      console.log('Response: ', this.response);
    } catch (error) {
      console.log("Error running inference: ", error)
    }

  }
}
