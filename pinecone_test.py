import os
from pinecone import Pinecone

# Initialize Pinecone explicitly using your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# List your current Pinecone indexes
indexes = pc.list_indexes().names()
print("✅ Current Pinecone indexes:", indexes)
