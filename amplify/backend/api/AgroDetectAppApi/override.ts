// This file is used to override the REST API resources configuration
import { AmplifyApiRestResourceStackTemplate } from '@aws-amplify/cli-extensibility-helper';

export function override(resources: AmplifyApiRestResourceStackTemplate) {

  // Add a parameter to your Cloud Formation Template for the User Pool's ID. The name of resource is the name of the folder in amplify/backend/auth
  resources.addCfnParameter({
      type: "String",
      description: "The id of an existing User Pool to connect. If this is changed, a user pool will not be created for you.",
      default: "agrodetectapp47ba0d9a",
    },
    "AuthCognitoUserPoolId",
    { "Fn::GetAtt": ["authagrodetectapp47ba0d9a", "Outputs.UserPoolId"], }
  ); // YourAuthSetting can be found `ls amplify/backend/auth`

  // Create the authorizer using the AuthCognitoUserPoolId parameter defined above
  resources.restApi.addPropertyOverride("Body.securityDefinitions", {
    Cognito: {
      type: "apiKey",
      name: "Authorization",
      in: "header",
      "x-amazon-apigateway-authtype": "cognito_user_pools",
      "x-amazon-apigateway-authorizer": {
        type: "cognito_user_pools",
        providerARNs: [
          { 'Fn::Sub': 'arn:aws:cognito-idp:${AWS::Region}:${AWS::AccountId}:userpool/${AuthCognitoUserPoolId}' },
        ],
      },
    },
  });

  // For every path in your REST API
  for (const path in resources.restApi.body.paths) {
    if (path.startsWith('/somepath')) {
       console.log('Skip the path not to use Authorization header', path);
       continue;
    }
     console.log('Make the path for restapi to have Authorization', path);
    // Add the Authorization header as a parameter to requests
    resources.restApi.addPropertyOverride(
      `Body.paths.${path}.x-amazon-apigateway-any-method.parameters`,
      [
        ...resources.restApi.body.paths[path]["x-amazon-apigateway-any-method"]
          .parameters,
        {
          name: "Authorization",
          in: "header",
          required: false,
          type: "string",
        },
      ]
    );
    // Use your new Cognito User Pool authorizer for security
    resources.restApi.addPropertyOverride(
      `Body.paths.${path}.x-amazon-apigateway-any-method.security`,
      [ { Cognito: [], }, ]
    );
  }
}
