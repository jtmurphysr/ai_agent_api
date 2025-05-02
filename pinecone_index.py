from pinecone import Pinecone, ServerlessSpec
import os

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "ai-agent-memory"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI text-embedding-3-small embeddings
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # your Pinecone region
    )
    print(f"✅ Index '{index_name}' created successfully.")
else:
    print(f"Index '{index_name}' already exists.")
