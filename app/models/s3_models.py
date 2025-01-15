from pydantic import BaseModel
from typing import List, Optional

class FileUploadRequest(BaseModel):
    bucket_name: str
    user_id: str
    context_id: str
    name: Optional[str] = None 

class FileInfo(BaseModel):
    file_name: str
    file_key: str
    status: str

class FileUploadResponse(BaseModel):
    message: str

class DeleteResponse(BaseModel):
    message: str
