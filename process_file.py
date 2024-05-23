import boto3
import os
import json

s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

FILES_TABLE = os.environ['FILES_TABLE']
BUCKET_NAME = os.environ['BUCKET_NAME']


def process_file(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']

        response = textract.analyze_document(
            Document={'S3Object': {'Bucket': bucket_name, 'Name': file_key}},
            FeatureTypes=['TABLES', 'FORMS']
        )

        table = dynamodb.Table(FILES_TABLE)
        table.update_item(
            Key={'file_id': file_key},
            UpdateExpression="set textract_results=:r, #status=:s",
            ExpressionAttributeValues={
                ':r': json.dumps(response),
                ':s': 'PROCESSED'
            },
            ExpressionAttributeNames={'#status': 'status'}
        )
