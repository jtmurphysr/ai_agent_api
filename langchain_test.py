import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from pinecone import Pinecone

openai_key = os.getenv("openai_key")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

# Explicitly specify metadata key 'content'
vectorstore = PineconeVectorStore(
    index=pc.Index("ai-agent-memory"),
    embedding=embeddings,
    text_key="content"  # important fix here
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

def query_agent(query_text):
    result = qa_chain.invoke({"query": query_text})
    return result['result']

# Test run
if __name__ == "__main__":
    response = query_agent("How did we configure dnsmasq on the Raspberry Pi?")
    print("Agent response:", response)
    