import boto3
import os
import uuid
from utils import jsonify

S3_BUCKET = os.environ['S3_BUCKET']
s3_client = boto3.client('s3', region_name='us-east-1')


def lambda_handler(event, context):
    file_uuid = str(uuid.uuid1())

    url = s3_client.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': f'input/{file_uuid}.jpg',
            'ContentType': 'image/jpeg'
        }
    )

    return jsonify({'url': url})

