import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import Pinecone
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from pinecone import Pinecone as PineconeClient

app = FastAPI(
    title="AI Agent API",
    description="API for querying an AI agent with vectorstore-backed knowledge",
    version="0.1.0"
)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3

class QueryResponse(BaseModel):
    response: str

# Global resource initialization
qa_chain: Optional[RetrievalQA] = None
conv_chain: Optional[ConversationalRetrievalChain] = None

@app.on_event("startup")
async def startup_event():
    global qa_chain, conv_chain

    openai_key = os.getenv("openai_key")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not openai_key or not pinecone_api_key:
        raise ValueError("Missing required environment variables: openai_key or PINECONE_API_KEY")

    pc = PineconeClient(api_key=pinecone_api_key)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    vectorstore = Pinecone(
        index=pc.Index("ai-agent-memory"),
        embedding=embeddings,
        text_key="content"
    )

    # Stateless retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )

    # Conversational retrieval chain with memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        qa_chain.retriever.search_kwargs["k"] = request.max_results
        result = qa_chain.invoke({"query": request.query})
        return QueryResponse(response=result['result'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying agent: {str(e)}")

@app.post("/conversation", response_model=QueryResponse)
async def conversation(request: QueryRequest):
    if conv_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        conv_chain.retriever.search_kwargs["k"] = request.max_results
        result = conv_chain.invoke({"question": request.query})
        return QueryResponse(response=result['answer'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in conversation: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)
