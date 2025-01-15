from fastapi import APIRouter
from app.services.s3_service import read_file_from_s3, list_files_in_s3_folder
from app.services.opensearch_service import create_index, bulk_store_embeddings
from app.utils.file_parser import extract_text_from_s3
from app.utils.embedding_utils import generate_embeddings
from app.utils.response import success_response, error_response
from langchain_openai.embeddings import OpenAIEmbeddings
from app.services.secrets_manager import OS_CLIENT, OPENAI_CLIENT
from app.services.opensearch_service import OpenSearchIndices
from pydantic import BaseModel

router = APIRouter()

class ProcessRequest(BaseModel):
    bucket_name: str
    folder_path: str

@router.post("/process-files")
async def process_files(request: ProcessRequest):
    """
    Process all files from an S3 folder, generate embeddings, and store them in OpenSearch.
    """
    try:
        # List all files in the specified folder
        file_keys = await list_files_in_s3_folder(request.bucket_name, request.folder_path)

        if not file_keys:
            return error_response(message="No files found in the folder.")

        # OpenAI embedding model (using OPENAI_CLIENT)
        embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_CLIENT.api_key)

        # Create OpenSearch index if it doesn't exist
        vector_field = "docmanagerembeddings"
        dimensions = 1536  # Adjust according to your embedding model
        create_index(OpenSearchIndices.DOCUMENT_EMBEDDINGS_INDEX, vector_field, dimensions, client=OS_CLIENT)

        all_payloads = []

        # Process each file in the folder
        for s3_key in file_keys:
            # Read file from S3
            file_stream, file_extension = await read_file_from_s3(request.bucket_name, s3_key)
            text = extract_text_from_s3(file_stream, file_extension)

            if not text:
                continue  # Skip files that cannot be processed or are empty

            # Generate embeddings for the text content
            embeddings, chunks = generate_embeddings(text, embedding_model)

            # print(f"Embedding type............: {type(embeddings)}")

            # Prepare payloads for bulk indexing
            payloads = [
                {
                    "_index": OpenSearchIndices.DOCUMENT_EMBEDDINGS_INDEX,
                    "_source": {
                        "text": chunk,
                        "metadata": {"source": s3_key},
                        "vector": embedding,
                    },
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]
            all_payloads.extend(payloads)

        # Perform bulk indexing in OpenSearch
        bulk_store_embeddings(OS_CLIENT, all_payloads)

        return success_response(data=[],message="All files processed and stored successfully.")

    except Exception as e:
        return error_response(message=str(e))
