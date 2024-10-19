from flask import Flask, render_template
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure AWS credentials and S3 bucket
AWS_ACCESS_KEY = 'AKIATSBG2T23D7IOZZOC'
AWS_SECRET_KEY = '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'
S3_BUCKET_NAME = 'universal-image-bucket'

def get_s3_images():
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY,
                          config=Config(signature_version='s3v4'))
        objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
        images = [obj['Key'] for obj in objects.get('Contents', [])]
        return images
    except NoCredentialsError:
        return []

def generate_signed_url(object_key):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    url = s3.generate_presigned_url('get_object',
                                      Params={'Bucket': S3_BUCKET_NAME, 'Key': object_key},
                                      ExpiresIn=3600)  # URL expires in 1 hour
    return url

@app.route('/')
def index():
    images = get_s3_images()
    print("Images found:", images)  # Debug line
    signed_urls = [generate_signed_url(image) for image in images]
    print("Signed URLs generated:", signed_urls)  # Debug line
    return render_template('index.html', signed_urls=signed_urls)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
