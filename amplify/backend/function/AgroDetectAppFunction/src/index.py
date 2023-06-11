import base64
import json
import logging
import os

import boto3
import botocore
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.getLevelName("INFO"))

patch_all()

# pylint: disable=W0613
def handler(event, context):
    logger.info("Handling event: %s", json.dumps(event))

    # Env vars
    # pylint: disable=C0103
    TABLE_NAME = os.environ["DYNAMODB_TABLE_NAME"]

    # pylint: disable=C0103
    SAGEMAKER_ENDPOINT_NAME = os.environ["SAGEMAKER_INFERENCE_ENDPOINT"]

    # Gets the inference image as bytes
    image_bytes = get_image_bytes(event)

    # Sanity checks the input image
    detected_labels = detect_labels(image_bytes)

    # Checks if the input image is a plant
    if is_not_plant(detected_labels):
        return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps("Uploaded image is not a plant/leaf. Please use a different image.")
        }

    # Runs inference on the input image
    sagemaker_response = run_inference(image_bytes, SAGEMAKER_ENDPOINT_NAME)

    # Parses the response from SageMaker
    label = parse_inference_response(sagemaker_response)

    # Gets API response object from DynamoDB
    dynamodb_item = get_dynamodb_response_object(label, TABLE_NAME)

    # Parses the response from DynamoDB
    api_response = parse_dynamodb_response(dynamodb_item)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(api_response)
    }


def get_image_bytes(event):
    """ Function to get the image from the event payload.

    Args:
        event (dict): Invoking event dictionary.

    Returns:
        bytes: Image bytes.
    """

    event_body = event["body"].encode("utf-8")

    image_bytes = base64.b64decode(event_body)

    return image_bytes


def detect_labels(image_bytes):
    """ Use AWS Rekognition to sanity check the input image.

    Args:
        image_bytes (bytes): Input image as bytes.

    Returns:
        list: List of detected labels for the input image.
    """

    rekognition_client = boto3.client("rekognition")

    try:
        rekognition_response = rekognition_client.detect_labels(
        Image={
            "Bytes": image_bytes
        },
        MaxLabels = 10
        )
    except botocore.exceptions.ClientError as error:
        logger.error("Error during Rekognition call: %s", error)

    detected_labels = rekognition_response["Labels"]

    detected_labels = [label["Name"] for label in detected_labels]
    logger.info("Detected labels by Rekognition: %s", detected_labels)

    return detected_labels


def is_not_plant(detected_labels):
    """ Function to check if the input image is of a plant.

    Args:
        detected_labels (list): List of detected labels.

    Returns:
        bool: Returns if the input image is of a plant/leaf.
    """

    return "Leaf" not in detected_labels and "Plant" not in detected_labels


def return_sanity_check_response():
    """ Response in case the sanity check fails.

    Returns:
        dict: Response object in case the image fails the check.
    """

    return {
        "statusCode": 200,
        "body": json.dumps("Uploaded image is not a plant/leaf. Please use a different image.")
    }


# pylint: disable=C0103
def run_inference(image_bytes, ENDPOINT_NAME):
    """ Function to run inference on the input image.

    Args:
        image_bytes (bytes): Input image as bytes.
        ENDPOINT_NAME (str): Name of the SageMaker Endpoint on which to run the inference.

    Returns:
        dict: Response from the SageMaker Endpoint.
    """

    sagemaker_runtime_client = boto3.client("sagemaker-runtime")

    try:
        sagemaker_response = sagemaker_runtime_client.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        Body=image_bytes,
        ContentType="application/x-image"
        )
        logger.info("Sagemaker response: %s", sagemaker_response)

        return sagemaker_response

    except botocore.exceptions.ClientError as error:
        logger.error("Error during SageMaker call: %s", error)


def parse_inference_response(sagemaker_response):
    """ Function to parse the response from SageMaker.

    Args:
        sagemaker_response (dict): SageMaker response dictionary.

    Returns:
        str: Detected label.
    """

    label = sagemaker_response["Body"].read()

    label = label.decode("utf-8")
    logger.info("Detected label from SageMaker: %s", label)

    return label


# pylint: disable=C0103
def get_dynamodb_response_object(label, TABLE_NAME):
    """ Function to get the API response object from DynamoDB.

    Args:
        label (str): Detected label.
        TABLE_NAME (str): Name of the DynamoDB table.

    Returns:
        dict: Response from DynamoDB.
    """

    dynamodb_client = boto3.client("dynamodb")

    try:
        dynamodb_response = dynamodb_client.get_item(TableName=TABLE_NAME, Key={"Name": {"S": label}})
        logger.info("DynamoDB response: %s", dynamodb_response)

    except botocore.exceptions.ClientError as error:
        logger.error("Error during DynamoDB call: %s", error)

    dynamodb_item = dynamodb_response["Item"]
    logger.info("DynamoDb response item: %s", dynamodb_item)

    return dynamodb_item


def parse_dynamodb_response(response):
    """ Helper function to deserialize the DynamoDB response to standard json object.

    Args:
        response (dict): DynamoDB response dictionary.

    Returns:
        dict: API response object.
    """

    api_response = {}

    api_response["Name"] = list(response["Name"].values())[0]
    api_response["Description"] = list(response["Description"].values())[0]
    api_response["isDisease"] = list(response["isDisease"].values())[0]
    api_response["Treatments"] = beautify(response["Treatments"])
    api_response["Products"] = beautify(response["Products"])
    logger.info("Returning API response: %s", api_response)

    return api_response

def beautify(data):
    """ Helper function to deserialize part of the DynamoDB item.

    Args:
        data (dict): Dictionary to be deserialized.

    Returns:
        list: Standard object.
    """

    response = []

    for item in data["L"]:
        data_dict = {}

        key = list(item["M"].keys())[0]
        value = list(item["M"].values())[0]["S"]

        data_dict[key] = value

        response.append(data_dict)

    return response
