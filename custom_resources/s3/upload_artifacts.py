import os
import json
import boto3
import botocore

ARTIFACTS_PATH = r'C:\Users\marin\Desktop\AgroDetectBachelor\model\model.tar.gz'

BUCKET_NAME = 'agro-detect-model-artifacts-bucket'

OBJECT_KEY = 'model.tar.gz'

def upload_object(object_path, bucket_name, object_key):
    s3_client = boto3.client("s3")
    try:
        with open(object_path, 'rb') as f:
            response = s3_client.upload_fileobj(f, bucket_name, object_key)
    except botocore.exceptions.ClientError as error:
        print("Error ocured: ", error)

if __name__ == '__main__':
    upload_object(ARTIFACTS_PATH, BUCKET_NAME, OBJECT_KEY)
