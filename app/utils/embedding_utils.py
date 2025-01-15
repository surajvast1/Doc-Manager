from langchain.text_splitter import CharacterTextSplitter

def chunk_text(text, chunk_size=1000, overlap=100):
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def generate_embeddings(text, embedding_model):
    chunks = chunk_text(text)
    embeddings = [embedding_model.embed_documents([chunk])[0] for chunk in chunks]
    return embeddings, chunks
