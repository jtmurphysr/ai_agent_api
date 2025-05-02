import os
import json
import uuid
from pinecone import Pinecone
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Pinecone and OpenAI clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("openai_key"))

# Connect to Pinecone index
index = pc.Index("ai-agent-memory")

# Load your chunk data explicitly
with open("conversation_chunks.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)

# Function to generate OpenAI embeddings explicitly
def get_embedding(text: str) -> list:
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Embed and insert chunks explicitly into Pinecone
batch_size = 100  # Adjust batch size as needed

for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding chunks"):
    batch = chunks[i:i + batch_size]

    vectors = []
    for chunk in batch:
        chunk_text = chunk["text"]
        embedding = get_embedding(chunk_text)
        unique_id = str(uuid.uuid4())
        metadata = {
            "conversation_title": chunk.get("conversation_title", ""),
            "conversation_id": chunk.get("conversation_id", ""),
            "start_message_idx": chunk.get("start_message_idx", 0),
            "end_message_idx": chunk.get("end_message_idx", 0),
            "word_count": chunk.get("word_count", 0),
            "content": chunk_text
        }

        vectors.append({"id": unique_id, "values": embedding, "metadata": metadata})

    # Upsert batch explicitly into Pinecone
    index.upsert(vectors=vectors)

print("✅ All chunks embedded and stored in Pinecone.")

