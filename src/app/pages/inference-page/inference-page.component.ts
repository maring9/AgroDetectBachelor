import { Component } from '@angular/core';
import { Auth, API, Storage } from 'aws-amplify';
import { InferenceResponse } from 'src/app/model/inference_response';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../../../aws-exports';
import { DeviceDetectorService } from 'ngx-device-detector';

@Component({
  selector: 'app-inference-page',
  templateUrl: './inference-page.component.html',
  styleUrls: ['./inference-page.component.css']
})

export class InferencePageComponent {
  isMobileOrTablet: boolean = false;

  constructor(public authenticator: AuthenticatorService, private deviceService: DeviceDetectorService) {
    Amplify.configure(awsmobile);
    this.isMobileOrTablet = deviceService.isMobile() || deviceService.isTablet();
    console.log("Is device mobile: ", this.isMobileOrTablet);
  }
  b64EncodedImage?: string = "";
  inferenceResponse?: InferenceResponse;

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    this.saveImage(file);

    const reader = new FileReader();
    console.log('Encoding image...');
    reader.readAsDataURL(file);

    reader.onload = () => {
      this.b64EncodedImage= reader.result?.toString().split(',')[1];
      console.log(this.b64EncodedImage);

    };
  }

  async saveImage(file: File) {
    try {
      const response = await Storage.put(file.name, file, {
        level: "private"
      });
    } catch (error) {
        console.log("Error uploading file: ", error);
    }
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
      const response = await API.post('AgroDetectAppApi', '/inference', requestData);
      console.log('Response: ', response);

      this.inferenceResponse = new InferenceResponse(response.Name, response.Description, response.isDisease, response.Products, response.Treatments);
      console.log("Inference response: ", this.inferenceResponse)
    } catch (error) {
      console.log("Error running inference: ", error)
    }

  }
}
