import os
from openai import OpenAI
from pinecone import Pinecone

openai_client = OpenAI(api_key=os.getenv("openai_key"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("ai-agent-memory")

query_text = "How did we set up dnsmasq on Raspberry Pi?"
query_embedding = openai_client.embeddings.create(
    input=query_text,
    model="text-embedding-3-small"
).data[0].embedding

results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
for match in results['matches']:
    print(f"Score: {match['score']}\nContent: {match['metadata']['content'][:300]}...\n---")
