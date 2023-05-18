import json
import logging
from collections import namedtuple
from io import BytesIO

import numpy as np
from consts import CLASSES, IMAGE_SIZE
from PIL import Image

Context = namedtuple('Context',
                     'model_name, model_version, method, rest_uri, grpc_uri, '
                     'custom_attributes, request_content_type, accept_header')

def get_prediction_label(prediction):
    """ Function to parse the model prediction.

    Args:
        prediction (dict): Dictionary containing the prediction array.

    Returns:
        str: Prediction label.
    """

    json_predictions = json.loads(prediction)

    probabilites = json_predictions['predictions'][0]

    prediction_index = np.argmax(probabilites)

    return CLASSES[prediction_index]


def input_handler(data, context):
    """ Pre-process request input before it is sent to TensorFlow Serving REST API
    Args:
        data (obj): the request data, in format of dict or string
        context (Context): an object containing request and configuration details
    Returns:
        (dict): a JSON-serializable dict that contains request body and headers
    """

    if context.request_content_type == 'application/x-image':
        image_bytes = data.read()

        image = Image.open(BytesIO(image_bytes))
        logging.info("Opened image for inference")

        rgb_image = image.convert('RGB')
        logging.info("Image mode set to: {}".format(rgb_image.mode))

        resized_image = rgb_image.resize(IMAGE_SIZE)
        logging.info("Resized image to: {}".format(resized_image.mode))

        np_image = np.array(resized_image, dtype='f')
        logging.info("Converted image to type {}".format(np_image.dtype))

        scaled_image = np_image / 255
        logging.info("Scaled np array")

        instance = np.expand_dims(scaled_image, axis=0)
        logging.info("Expanded to: {}".format(instance.shape))

        payload = json.dumps({"instances": instance.tolist()})
        logging.info("Sending payload: {}".format(payload))

        return payload

    else:
        _return_error(415, 'Unsupported content type "{}"'.format(context.request_content_type or 'Unknown'))


def output_handler(data, context):
    """Post-process TensorFlow Serving output before it is returned to the client.
    Args:
        data (obj): the TensorFlow serving response
        context (Context): an object containing request and configuration details
    Returns:
        (bytes, string): data to return to client, response content type
    """

    logging.info("Got output data: {} with status: ".format(data.content, data))

    if data.status_code != 200:
        raise Exception(data.content.decode('utf-8'))

    response_content_type = context.accept_header
    prediction = data.content

    prediction_label = get_prediction_label(prediction)
    logging.info("Prediction: {}".format(prediction_label))

    return prediction_label, response_content_type


def _return_error(code, message):
    raise ValueError('Error: {}, {}'.format(str(code), message))
