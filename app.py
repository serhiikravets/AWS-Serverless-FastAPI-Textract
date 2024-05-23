import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.client import Config
import os
from mangum import Mangum

app = FastAPI(
    title='aws-serverless-fastapi-textract',
    openapi_url="/openapi.json",
)


s3 = boto3.client('s3', region_name='eu-central-1', config=Config(signature_version='s3v4'))
dynamodb = boto3.resource('dynamodb')
textract = boto3.client('textract')

FILES_TABLE = os.environ['FILES_TABLE']
BUCKET_NAME = os.environ['BUCKET_NAME']


class FileRequest(BaseModel):
    callback_url: str


@app.post("/files")
async def create_file(file_request: FileRequest):
    callback_url = file_request.callback_url

    file_key = f"{uuid.uuid4()}"
    upload_url = s3.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Conditions=None,
        ExpiresIn=3600
    )

    table = dynamodb.Table(FILES_TABLE)
    table.put_item(
        Item={
            'file_id': file_key,
            'callback_url': callback_url,
            'status': 'UPLOADED'
        }
    )

    return {'upload_url': upload_url}


@app.get("/files/{file_id}")
async def get_file(file_id: str):
    table = dynamodb.Table(FILES_TABLE)
    response = table.get_item(Key={'file_id': file_id})

    if 'Item' in response:
        return response['Item']
    else:
        raise HTTPException(status_code=404, detail="File not found")


handler = Mangum(app)
