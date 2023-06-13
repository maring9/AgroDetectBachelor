import base64
import json
import os
import unittest
from io import BytesIO
from unittest import mock

import boto3
import pytest
from botocore.stub import Stubber

# pylint: disable=E0402
from ..index import (beautify, get_image_bytes, handler, is_not_plant,
                     parse_dynamodb_response, parse_inference_response,
                     return_sanity_check_response)
from .payload import ENV_VARS, EVENT, SAGEMAKER, DYNAMODB, REKOGNITION


class TestFunctions:
    def test_get_image_bytes_valid_event(self):
        # Test case 1: Valid event payload
        event = {
            "body": "VGhpcyBpcyBhIHN0cmluZyBtZXNzYWdl"
        }
        expected_output = b"This is a string message"
        assert get_image_bytes(event) == expected_output

    def test_get_image_bytes_empty_even(self):
        # Test case 2: Empty event payload
        event = {
            "body": ""
        }
        expected_output = b""
        assert get_image_bytes(event) == expected_output

    def test_get_image_bytes_invalid_event(self):
        # Test case 3: Invalid event payload (non-base64 encoded string)
        event = {
            "body": "This is not a base64 encoded string"
        }

        with pytest.raises(base64.binascii.Error):
            get_image_bytes(event)

    def test_get_image_bytes_missing_body(self):
        # Test case 4: Invalid event (missing 'body' key)
        event = {}

        with pytest.raises(KeyError):
            get_image_bytes(event)

    def test_is_not_plant(self):
        # Test case 1: No plant-related labels detected
        detected_labels = ["Cat", "Dog", "Car"]
        assert is_not_plant(detected_labels) is True

    def test_is_not_plant_only_leaf(self):
        # Test case 2: Only "Leaf" detected
        detected_labels = ["Leaf"]
        assert is_not_plant(detected_labels) is False

    def test_is_not_plant_only_plant(self):
        # Test case 3: Only "Plant" detected
        detected_labels = ["Plant"]
        assert is_not_plant(detected_labels) is False

    def test_is_not_plant_both(self):
        # Test case 4: Both "Leaf" and "Plant" detected
        detected_labels = ["Leaf", "Plant"]
        assert is_not_plant(detected_labels) is False

    def test_is_not_plant_empty(self):
        # Test case 5: Empty detected_labels list
        detected_labels = []
        assert is_not_plant(detected_labels) is True

    def test_is_not_plant_multiple(self):
        # Test case 6: Multiple labels including "Leaf" and "Plant"
        detected_labels = ["Cat", "Leaf", "Dog", "Plant", "Car"]
        assert is_not_plant(detected_labels) is False

    def test_return_sanity_check_response(self):
        expected_response = {
            "statusCode": 200,
            "body": json.dumps("Uploaded image is not a plant/leaf. Please use a different image.")
        }

        response = return_sanity_check_response()

        assert response == expected_response

    def test_parse_inference_response_single_label(self):
        # Test case 1: Valid response with a single label
        sagemaker_response = {
            "Body": BytesIO(b"Tomato Healthy")
        }
        expected_label = "Tomato Healthy"

        assert parse_inference_response(sagemaker_response) == expected_label

    def test_parse_dynamodb_response_disease(self):
        # Test case 1: Valid response with all fields
        response = {
            "Name": {"S": "Test Disease"},
            "Description": {"S": "Test Description"},
            "isDisease": {"BOOL": True},
            "Treatments": {"L":
                        [
                            {
                            "M": {
                                "Test Treatment Key": {"S": "Test Treatment Value"}
                                }
                            }
                            ]
                        },
            "Products": {"L":
                        [
                        {
                            "M": {
                            "Test Product Key": {"S": "Test Product Value"}
                            }
                            }
                        ]
                        }
                    }
        expected_response = {
            "Name": "Test Disease",
            "Description": "Test Description",
            "isDisease": True,
            "Treatments": [{"Test Treatment Key": "Test Treatment Value"}],
            "Products": [{"Test Product Key": "Test Product Value"}]
        }

        assert parse_dynamodb_response(response) == expected_response


    def test_parse_dynamodb_response_healthy(self):
        # Test case 1: Valid response with all fields
        response = {
            "Name": {"S": "Test Healthy"},
            "Description": {"S": ""},
            "isDisease": {"BOOL": False},
            "Treatments": {"L": []
                        },
            "Products": {"L": []
                        }
                    }
        expected_response = {
            "Name": "Test Healthy",
            "Description": "",
            "isDisease": False,
            "Treatments": [],
            "Products": []
        }

        assert parse_dynamodb_response(response) == expected_response

    def test_beautify_valid_single(self):
        # Test case 1: Valid input dictionary with a single item
        data = {
            "L": [{"M": {"Item1": {"S": "Value1"}}}]
        }
        expected_output = [{"Item1": "Value1"}]
        assert beautify(data) == expected_output

    def test_beautify_valid_multiple(self):
        # Test case 2: Valid input dictionary with multiple items
        data = {
            "L": [
                {"M": {"Item1": {"S": "Value1"}}},
                {"M": {"Item2": {"S": "Value2"}}},
                {"M": {"Item3": {"S": "Value3"}}}
            ]
        }
        expected_output = [{"Item1": "Value1"}, {"Item2": "Value2"}, {"Item3": "Value3"}]
        assert beautify(data) == expected_output

    def test_beautify_valid_empty(self):
        # Test case 3: Empty input dictionary
        data = {
            "L": []
        }
        expected_output = []
        assert beautify(data) == expected_output

        # Test case 4: Invalid input dictionary (missing 'L' key)
        data = {}
        with pytest.raises(KeyError):
            beautify(data)


rekognition_client = boto3.client("rekognition", region_name="eu-central-1")
rekognition_client_stubber = Stubber(rekognition_client)

sagemaker_client = boto3.client("sagemaker-runtime", region_name="eu-central-1")
sagemaker_client_stubber = Stubber(sagemaker_client)

dynamodb_client = boto3.client("dynamodb", region_name="eu-central-1")
dynamodb_client_stubber = Stubber(dynamodb_client)

CLIENT_STUB_DICT = {
    "rekognition": rekognition_client_stubber.client,
    "sagemaker-runtime": sagemaker_client_stubber.client,
    "dynamodb": dynamodb_client_stubber.client
}

# pylint: disable=W0613
def client_stub(service_name, **kwargs):
    return CLIENT_STUB_DICT[service_name]

class TestBotoFunctions(unittest.TestCase):
    def setup_class(self):
        rekognition_client_stubber.activate()
        sagemaker_client_stubber.activate()
        dynamodb_client_stubber.activate()

    def teardown_class(self):
        rekognition_client_stubber.deactivate()
        sagemaker_client_stubber.deactivate()
        dynamodb_client_stubber.deactivate()

    @mock.patch("boto3.client", client_stub)
    @mock.patch.dict(os.environ, ENV_VARS)
    def test_handler_successful_healthy(self):
        rekognition_client_stubber.add_response(
        method="detect_labels",
        service_response=REKOGNITION["RESPONSE"],
        expected_params=REKOGNITION["EXPECTED_PARAMS"])

        sagemaker_client_stubber.add_response(
        method="invoke_endpoint",
        service_response=SAGEMAKER["RESPONSE"],
        expected_params=SAGEMAKER["EXPECTED_PARAMS"])

        dynamodb_client_stubber.add_response(
        method="get_item",
        service_response=DYNAMODB["RESPONSE"],
        expected_params=DYNAMODB["EXPECTED_PARAMS"])

        handler(EVENT, None)

    @mock.patch("boto3.client", client_stub)
    @mock.patch.dict(os.environ, ENV_VARS)
    def test_handler_successful_not_plant(self):
        self.setup_class()
        rekognition_client_stubber.add_response(
        method="detect_labels",
        service_response=REKOGNITION["NOT_PLANT_RESPONSE"],
        expected_params=REKOGNITION["EXPECTED_PARAMS"])

        handler(EVENT, None)

    @mock.patch("boto3.client", client_stub)
    @mock.patch.dict(os.environ, ENV_VARS)
    def test_handler_rekognition_error(self):
        self.setup_class()

        rekognition_client_stubber.add_client_error(
        method="detect_labels",
        service_error_code="TestError",
        )

        handler(EVENT, None)

    @mock.patch("boto3.client", client_stub)
    @mock.patch.dict(os.environ, ENV_VARS)
    def test_handler_sagemaker_error(self):
        self.setup_class()

        rekognition_client_stubber.add_response(
        method="detect_labels",
        service_response=REKOGNITION["RESPONSE"],
        expected_params=REKOGNITION["EXPECTED_PARAMS"])

        sagemaker_client_stubber.add_client_error(
        method="invoke_endpoint",
        service_error_code="TestError")

        handler(EVENT, None)


rekognition_client2 = boto3.client("rekognition", region_name="eu-central-1")
rekognition_client_stubber2 = Stubber(rekognition_client)

sagemaker_client2 = boto3.client("sagemaker-runtime", region_name="eu-central-1")
sagemaker_client_stubber2 = Stubber(sagemaker_client)

dynamodb_client2 = boto3.client("dynamodb", region_name="eu-central-1")
dynamodb_client_stubber2 = Stubber(dynamodb_client)

CLIENT_STUB_DICT2 = {
    "rekognition": rekognition_client_stubber2.client,
    "sagemaker-runtime": sagemaker_client_stubber2.client,
    "dynamodb": dynamodb_client_stubber2.client
}

# pylint: disable=W0613
def client_stubs2(service_name, **kwargs):
    return CLIENT_STUB_DICT2[service_name]
class DynamoDBError:
    def setup_class(self):
        rekognition_client_stubber2.activate()
        sagemaker_client_stubber2.activate()
        dynamodb_client_stubber2.activate()

    def teardown_class(self):
        rekognition_client_stubber2.deactivate()
        sagemaker_client_stubber2.deactivate()
        dynamodb_client_stubber2.deactivate()

    @mock.patch("boto3.client", client_stubs2)
    @mock.patch.dict(os.environ, ENV_VARS)
    def test_handler_dynamodb_error(self):
        rekognition_client_stubber2.add_response(
        method="detect_labels",
        service_response=REKOGNITION["RESPONSE"],
        expected_params=REKOGNITION["EXPECTED_PARAMS"])

        sagemaker_client_stubber2.add_response(
        method="invoke_endpoint",
        service_response=SAGEMAKER["RESPONSE"],
        expected_params=SAGEMAKER["EXPECTED_PARAMS"])

        dynamodb_client_stubber2.add_client_error(
        method="get_item",
        service_error_code="TestError")

        handler(EVENT, None)
