from app.services.secrets_manager import OS_CLIENT  # Import the pre-initialized OpenSearch client


def fetch_context_from_opensearch(index_name, query):
    """Fetch relevant context from OpenSearch."""
    try:
        search_body = {
            "query": {
                "match": {
                    "text": query
                }
            }
        }
        response = OS_CLIENT.search(index=index_name, body=search_body)
        hits = response['hits']['hits']

        # Combine the most relevant results into a single context
        context = " ".join(hit['_source']['text'] for hit in hits if '_source' in hit and 'text' in hit['_source'])
        return context
    except Exception as e:
        raise RuntimeError(f"Error fetching data from OpenSearch: {str(e)}")
