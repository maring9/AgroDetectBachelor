import { Component } from '@angular/core';
import { Auth, API, Storage } from 'aws-amplify';
import { InferenceResponse } from 'src/app/model/inference_response';
import { AuthenticatorService } from '@aws-amplify/ui-angular';
import { Amplify } from 'aws-amplify';
import awsmobile from '../../../aws-exports';
import { DeviceDetectorService } from 'ngx-device-detector';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-inference-page',
  templateUrl: './inference-page.component.html',
  styleUrls: ['./inference-page.component.css']
})

export class InferencePageComponent {
  isMobileOrTablet: boolean = false;
  url: any;
	msg = "";
  isNotPlant: boolean = false;
  isFinished: boolean = false;

  constructor(public authenticator: AuthenticatorService, private deviceService: DeviceDetectorService) {
    Amplify.configure(awsmobile);
    this.isMobileOrTablet = deviceService.isMobile() || deviceService.isTablet();
  }
  b64EncodedImage?: string = "";
  inferenceResponse?: InferenceResponse;

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    this.saveImage(file);

    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = () => {
      this.b64EncodedImage= reader.result?.toString().split(',')[1];
      console.log(this.b64EncodedImage);
    };

    if(!event.target.files[0] || event.target.files[0].length == 0) {
			this.msg = 'You must select an image';
			return;
		}

		var mimeType = event.target.files[0].type;

		if (mimeType.match(/image\/*/) == null) {
			this.msg = "Only images are supported";
			return;
		}

    var fileReader = new FileReader();
		fileReader.readAsDataURL(event.target.files[0]);

		fileReader.onload = (_event) => {
			this.msg = "";
			this.url = fileReader.result;
		}

    this.isNotPlant = false;
    this.isFinished = false;
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
    const user = await Auth.currentAuthenticatedUser();
    const jwtToken = user.signInUserSession.idToken.jwtToken;

    const requestData = {
      body: this.b64EncodedImage,
      headers : {
        Authorization: jwtToken
      }
    }

    try {
      const response = await API.post('AgroDetectAppApi', '/inference', requestData);
      this.isFinished = true;
      if (typeof response === 'string') {
        this.isNotPlant = true;
      } else {
        this.inferenceResponse = new InferenceResponse(response.Name, response.Description, response.isDisease, response.Products, response.Treatments);
      }
    } catch (error) {
      console.log("Error running inference: ", error)
    }

  }

	selectFile(event: any) {
	}
}
