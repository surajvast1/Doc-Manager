from fastapi import FastAPI, HTTPException, Request,APIRouter
from app.services.context_service import fetch_context_from_opensearch
from app.services.response_service import get_openai_response
from app.services.opensearch_service import OpenSearchIndices
from pydantic import BaseModel
router = APIRouter()

class ResponseRequest(BaseModel):
    question: str


@router.post("/search-and-respond")
async def search_and_respond(request: ResponseRequest):
    try:

        collection_name = OpenSearchIndices.DOCUMENT_EMBEDDINGS_INDEX

        if not collection_name or not request.question:
            raise HTTPException(status_code=400, detail="Missing 'collection_name' or 'question' in request.")

        # Fetch relevant context from OpenSearch
        relevant_context = fetch_context_from_opensearch(collection_name, request.question)

        if not relevant_context:
            return {"message": "No relevant context found for the question."}

        # Generate a response using OpenAI
        response = get_openai_response(relevant_context, request.question)

        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
