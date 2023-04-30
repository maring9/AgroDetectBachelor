from io import BytesIO
import json
import numpy as np
from collections import namedtuple
from PIL import Image
import logging
import base64
from consts import IMAGE_SIZE, CLASSES

Context = namedtuple('Context',
                     'model_name, model_version, method, rest_uri, grpc_uri, '
                     'custom_attributes, request_content_type, accept_header')

def get_prediction_label(prediction):
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
    
    logging.info("Using Context: {}".format(context))
    logging.info("Got data object: {}".format(data))
    if context.request_content_type == 'application/x-image':
        json_data = json.loads(data.read())
        logging.info("JSON Data: {}".format(json_data))
        
        b64_image = json_data['body-json']
        logging.info("Base64 encoded image: {}".format(b64_image))
        
        image = Image.open(BytesIO(base64.b64decode(b64_image)))
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
        
        logging.info("Payload for TFS: {}".format(instance))

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