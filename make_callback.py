import boto3
import os
import json
import requests

dynamodb = boto3.resource('dynamodb')

FILES_TABLE = os.environ['FILES_TABLE']


def make_callback(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            if new_image['status']['S'] == 'PROCESSED':
                callback_url = new_image['callback_url']['S']
                textract_results = json.loads(new_image['textract_results']['S'])

                requests.post(callback_url, json={'textract_results': textract_results})
