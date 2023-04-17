import json
import os

import boto3
import botocore

# TODO
# WORKING BUT NEEDS REFACTOR

TABLE_NAME = "DataTable"

DATA_DIRECTORY = r'C:\Users\marin\Desktop\AgroDetectBachelorFrontend\data'


def to_list(dict_):
    list_item = []
    for (key, value) in dict_.items():
        list_item.append({
            key: value
        })
    return list_item


def to_bool(string):
    if string.lower() == "false":
        return False
    else:
        return bool(string)


def transform(base_path):
    items_paths = [os.path.join(base_path, item) for item in os.listdir(base_path)]
    for path in items_paths:
        print("Transforming: ", path)
        with open(path, 'r') as f:
            object_ = json.load(f)
        item = {}
        item['Name'] = object_['Name']
        item['isDisease'] = object_['isDisease']
        item['Description'] = object_['Description']
        item['Treatments'] = to_list(object_['Treatment'])
        item['Products'] = to_list(object_['Products'])

        with open(path, 'w') as f:
            json.dump(item, f,indent=4)


def upload_files(base_dir):
    items_paths = [os.path.join(base_dir, item) for item in os.listdir(base_dir)]
    dynamodb_client = boto3.client("dynamodb")

    try:
        for path in items_paths:
            print("Uploading: ", path)
            with open(path, 'r') as f:
                data_item = json.load(f)
            dynamodb_item = transform_dynamodb_format(data_item)
            resp = dynamodb_client.put_item(TableName=TABLE_NAME, Item=dynamodb_item)
    except botocore.exceptions.ClientError as error:
        print(error)


def edit(object_):
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


def transform_dynamodb_format(object_):
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

if __name__ == '__main__':
  upload_files(DATA_DIRECTORY)
