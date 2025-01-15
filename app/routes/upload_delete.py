from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
from typing import List,Optional
from app.services.s3_service import upload_files_to_s3, delete_files_from_s3
from app.utils.response import success_response, error_response

router = APIRouter()

class FileData(BaseModel):
    file_name: str
    file_content: str  # Base64 encoded content of the file

class UploadRequest(BaseModel):
    bucket_name: str    
    user_id: str
    context_id: str
    name: Optional[str] = None
    files: Optional[List[FileData]] = None  # Make this optional
    action: str   # Can be 'upload' or 'delete'

@router.post("/files")
async def handle_files(request: UploadRequest):
    """
    API endpoint to either upload or delete files to/from S3.
    """
    try:
        if request.action == "upload":
            # Process upload
            uploaded_files = await upload_files_to_s3(request)
            return success_response(
                message="Files uploaded successfully",
                data={"files": uploaded_files}
            )
        elif request.action == "delete":
            # Process delete
            return await delete_files_from_s3(request.bucket_name, request.user_id, request.context_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action specified.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return error_response(str(e), status_code=500)
