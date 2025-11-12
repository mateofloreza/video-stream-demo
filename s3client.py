# s3client.py
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from uuid import uuid4

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# ✅ Explicit regional endpoint and signature version
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(signature_version="s3v4"),
)

def generate_s3_key(original_filename: str) -> str:
    return f"uploads/{uuid4().hex}_{original_filename.replace(' ', '_')}"

def upload_fileobj(fileobj, key: str, content_type: str) -> None:
    s3.upload_fileobj(
        Fileobj=fileobj,
        Bucket=S3_BUCKET,
        Key=key,
        ExtraArgs={"ContentType": content_type},
    )

def get_presigned_url(key: str, expires_in: int = 3600) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )

def stream_s3_object(key: str, chunk_size: int = 8 * 1024 * 1024):
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    body = obj["Body"]
    while True:
        chunk = body.read(chunk_size)
        if not chunk:
            break
        yield chunk

