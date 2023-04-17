import base64
import json
import logging
import os

import boto3
import botocore


def handler(event, context):
  print('received event:')
  print(event)

  TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]
  SAGEMAKER_ENDPOINT_NAME = os.environ["SAGEMAKER_INFERENCE_ENDPOINT"]

  event_body = event["body"].encode('utf-8')
  print("Event body: ", event_body)

  image_bytes = base64.b64decode(event_body)
  print("Image Bytes: ", image_bytes)

  rekognition_client = boto3.client("rekognition")

  rekognition_response = rekognition_client.detect_labels(
    Image={
      "Bytes": image_bytes
    },
    MaxLabels = 10
  )
  print("Rekognition response: ", rekognition_response)

  detected_labels = rekognition_response["Labels"]

  detected_labels = [label["Name"] for label in detected_labels]
  print("Detected labels: ", detected_labels)

  if "Leaf" not in detected_labels and "Plant" not in detected_labels:
    return {
      "statusCode": 200,
      "body": json.dumps("Uploaded image is not a plant/leaf. Please use a different image.")
    }

  sagemaker_runtime_client = boto3.client("sagemaker-runtime")

  try:
    sagemaker_response = sagemaker_runtime_client.invoke_endpoint(
      EndpointName=SAGEMAKER_ENDPOINT_NAME,
      Body=image_bytes,
      ContentType="application/x-image"
    )
    print("Sagemaker response: ", sagemaker_response)
  except botocore.exceptions.ClientError as error:
      print("Error: ", error)

  label = sagemaker_response['Body'].read()
  label = label.decode('utf-8')

  dynamodb_client = boto3.client("dynamodb")

  try:
    dynamodb_response = dynamodb_client.get_item(TableName=TABLE_NAME, Key={"Name": {"S": label}})
    print("Dynamodb response: ", dynamodb_response)
  except botocore.exceptions.ClientError as error:
    print("Error2: ", error)

  dynamodb_item = dynamodb_response['Item']

  api_response = parse_response(dynamodb_item)

  return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps(api_response)
  }

def parse_response(response):
    api_response = {}

    api_response['Name'] = list(response['Name'].values())[0]
    api_response['Description'] = list(response['Description'].values())[0]
    api_response['isDisease'] = list(response['isDisease'].values())[0]
    api_response['Treatments'] = beautify(response['Treatments'])
    api_response['Products'] = beautify(response['Products'])

    return api_response

def beautify(data):
    response = []
    for item in data['L']:
        data_dict = {}
        key = list(item['M'].keys())[0]
        value = list(item['M'].values())[0]['S']
        data_dict[key] = value
        response.append(data_dict)
    return response
