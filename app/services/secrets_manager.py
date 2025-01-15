from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from openai import OpenAI
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

# Load environment variables
load_dotenv()

# API URLs - Keep only OpenSearch
class APIUrls:
    OPEN_SEARCH_URL = "https://search-cellstrat-477fgqwwllgxyc3yez6gk2if6q.aos.us-east-1.on.aws"

# OpenSearch Indices
class OpenSearchIndices:
    DOCUMENT_EMBEDDINGS_INDEX = "document_embeddings"  # Your index name here

# AWS Configuration
class AWSConfig:
    REGION = 'us-east-1'
class SecretsManager:
    @staticmethod
    def get_secrets(secret_id: str):
        """Fetch secrets from AWS Secrets Manager."""
        print(f"AWS Profile: {os.getenv('AWS_PROFILE')}")
        session = boto3.Session(profile_name=os.getenv('AWS_PROFILE'))
        sm = session.client('secretsmanager', region_name=AWSConfig.REGION)
        return sm.get_secret_value(SecretId=secret_id)['SecretString']

    @staticmethod
    def get_opensearch_client():
        """Initialize and return OpenSearch client."""
        try:
            session = boto3.Session(profile_name=os.getenv('AWS_PROFILE'))
            
            # Get AWS credentials for authentication
            aws_credentials = session.get_credentials()
            auth = AWSV4SignerAuth(aws_credentials, AWSConfig.REGION, "es")
            
            return OpenSearch(
                hosts=[APIUrls.OPEN_SEARCH_URL],
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found. Please configure your environment or provide valid credentials.")


# Initialize OpenAI API Key
os.environ['OPENAI_API_KEY'] = SecretsManager.get_secrets('openai_api_key')

# Initialize clients
OS_CLIENT = SecretsManager.get_opensearch_client()

# OpenAI client initialization (assuming OpenAI is a wrapper for OpenAI API)
OPENAI_CLIENT = OpenAI()
