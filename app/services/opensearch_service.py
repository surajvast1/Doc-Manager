from opensearchpy import OpenSearch, helpers
from app.services.secrets_manager import SecretsManager

class OpenSearchIndices:
    DOCUMENT_EMBEDDINGS_INDEX = "document_embeddings"

def create_index(index_name: str, vector_field: str, dimensions: int,client):
    """
    Create an OpenSearch index with a vector field if it doesn't exist.
    """
    # client = SecretsManager.get_opensearch_client()

    if not client.indices.exists(index=index_name):
        index_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    vector_field: {
                        "type": "dense_vector",
                        "dims": dimensions,
                    },
                    "text": {"type": "text"},
                    "metadata": {"type": "object"},
                }
            },
        }
        client.indices.create(index=index_name, body=index_body)

def bulk_store_embeddings(client: OpenSearch, payloads: list):
    """
    Perform bulk indexing of embeddings into OpenSearch.
    """
    try:
        response = helpers.bulk(client, payloads)
        return response
    except Exception as e:
        raise RuntimeError(f"Failed to bulk index embeddings: {str(e)}")
