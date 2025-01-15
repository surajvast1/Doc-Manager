from fastapi.responses import JSONResponse
from typing import Any

def success_response(data: Any, message: str = "Success", status_code: int = 200) -> JSONResponse:
    """
    Generates a success response with custom message and data.
    """
    return JSONResponse(
        content={"status": "success", "message": message, "data": data},
        status_code=status_code
    )

def error_response(message: str = "An error occurred", status_code: int = 400) -> JSONResponse:
    """
    Generates an error response with custom message.
    """
    return JSONResponse(
        content={"status": "error", "message": message},
        status_code=status_code
    )
