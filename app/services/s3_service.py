from fastapi import UploadFile, File, Form
import boto3
import uuid
import os
import mimetypes
from app.utils.response import error_response, success_response

s3 = boto3.client('s3')
MAX_TOTAL_SIZE_MB = 15  
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024  

async def upload_files_to_s3(
    files: list[UploadFile] = File(...),
    bucket_name: str = Form(...),
    user_id: str = Form(...),
    context_id: str = Form(...),
    name: str = Form(None)
):
    try:
        # Assign a default name if not provided
        name = name or f"default-{uuid.uuid4()}"
        collection_prefix = os.path.join(user_id, context_id, name, "")

        # Check total size of uploaded files
        total_size = sum(file.size for file in files)
        if total_size > MAX_TOTAL_SIZE_BYTES:
            raise ValueError(f"Total file size exceeds {MAX_TOTAL_SIZE_MB} MB limit.")

        uploaded_files = []

        # Process and upload each file
        for file in files:
            file_name = file.filename
            file_bytes = await file.read()
            file_type = file.content_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            file_key = os.path.join(collection_prefix, file_name)

            # Upload to S3
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=file_bytes,
                ContentType=file_type
            )

            uploaded_files.append({
                "file_name": file_name,
                "file_key": file_key,
                "status": "uploaded"
            })

        return success_response(data=uploaded_files)
    except Exception as e:
        return error_response(f"Error uploading files: {e}", status_code=500)


async def delete_files_from_s3(bucket_name, user_id, context_id):
    try:
        collection_prefix = os.path.join(user_id, context_id, "")
        objects_to_delete = s3.list_objects_v2(Bucket=bucket_name, Prefix=collection_prefix)

        if 'Contents' in objects_to_delete:
            delete_keys = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]
            s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_keys})
            
            success_response(data={"message": "File successfully deleted"})
        else:
            raise ValueError("No files found to delete.")
    except Exception as e:
        return error_response(f"Error during file deletion: {e}", status_code=500)

async def read_file_from_s3(bucket_name, s3_key):
    """
    Reads a file from S3 and returns a file stream and file extension.
    """
    obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    file_stream = io.BytesIO(obj['Body'].read())
    file_extension = os.path.splitext(s3_key)[-1].lower()
    return file_stream, file_extension

# Function to list all files in a specific folder in an S3 bucket
async def list_files_in_s3_folder(bucket_name: str, folder_path: str):
    s3 = boto3.client("s3")
    print(f"Listing files in bucket: {bucket_name}, folder: {folder_path}")
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
        print(f"S3 response: {response}")

        if 'Contents' not in response:
            print("No files found in the folder.")
            return []

        file_keys = [file['Key'] for file in response['Contents']]
        print(f"Files found: {file_keys}")
        return file_keys
    except NoCredentialsError:
        print("Error: No credentials found for accessing S3.")
        raise ValueError("Credentials not found for accessing S3")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise ValueError(f"Error listing files in S3: {e}")
    