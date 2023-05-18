import json
import os

import boto3
import botocore

TABLE_NAME = "DataTable"
DATA_DIRECTORY = r'C:\Users\marin\Desktop\AgroDetectBachelorFrontend\data'


def upload_files(base_dir):
  """ Helper function to upload API response objects to the DynamoDb Table.

  Args:
      base_dir (str): Path of the json objects.
  """

  items_paths = [os.path.join(base_dir, item) for item in os.listdir(base_dir)]
  # Creates the path for each json object in the base directory

  dynamodb_client = boto3.client("dynamodb")

  try:
      for path in items_paths:
          print("Uploading: ", path)

          with open(path, 'r') as f:
              data_item = json.load(f)
          # Loads the json data to be uploaded

          dynamodb_item = transform_to_dynamodb_format(data_item)
          # Transforms the json object into DynamoDB expected format

          resp = dynamodb_client.put_item(TableName=TABLE_NAME, Item=dynamodb_item)

  except botocore.exceptions.ClientError as error:
      print(error)


def transform_to_dynamodb_format(object_):
  """ Function to transform the json data into DynamoDB format.

  Args:
      object_ (dict): Json object representing an API response data object.

  Returns:
      dict: DynamoDB compatible data object.
  """

  dynamodb_item = {
      "Name": {
          "S": object_["Name"]
      },
      "Description": {
          "S": object_["Description"]
      },
      "isDisease": {
          "BOOL": to_bool(object_["isDisease"])
      },
      "Products": {
          "L": edit(object_["Products"])
      },
      "Treatments": {
          "L": edit(object_["Treatments"])
      }
  }

  return dynamodb_item


def to_bool(string):
  """ Function to transform_raw_data the ras response data.

  Args:
      string (str): String representing boolean value.

  Returns:
      bool: String as boolean.
  """

  if string.lower() == "false":
      return False
  else:
      return bool(string)


def edit(object_):
  """ Helper function to transform_raw_data the raw data into suitable json format.

  Args:
      object_ (list): Part of the object to be transformed to DynamoDb format.

  Returns:
      list: Transformed list of objects in DynamoDB format.
  """

  transformed_list = []

  for obj in object_:
      transformed_item = {
          "M": {
              list(obj.keys())[0]: {
                  "S": list(obj.values())[0]
              }
          }
      }

      transformed_list.append(transformed_item)

  return transformed_list


def to_list(dict_):
  """ Function to transform_raw_data the raw response data.

  Args:
      dict_ (dict): Dictionary to be transformed.

  Returns:
      list: Transformed list of data.
  """

  list_item = []

  for (key, value) in dict_.items():
      list_item.append({
          key: value
      })

  return list_item


def transform_raw_data(base_path):
  """ Function to transform the API response data objects into a better json format.

  Args:
      base_path (str): Base path of the response objects to be transformed
  """

  # Creates the path for each json object in the base directory
  items_paths = [os.path.join(base_path, item) for item in os.listdir(base_path)]

  for path in items_paths:
      print("Transforming: ", path)

      # Reads the json object
      with open(path, 'r') as f:
          object_ = json.load(f)

      # Transforms the json object into a better format
      item = {}
      item['Name'] = object_['Name']
      item['isDisease'] = object_['isDisease']
      item['Description'] = object_['Description']
      item['Treatments'] = to_list(object_['Treatment'])
      item['Products'] = to_list(object_['Products'])

      # Saves the transformed object
      with open(path, 'w') as f:
          json.dump(item, f,indent=4)


if __name__ == '__main__':
  upload_files(DATA_DIRECTORY)
