import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import Pinecone
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from pinecone import Pinecone as PineconeClient

# Database models and session management
from db import Session as DbSession, Message, get_db
from formatter import format_conversation_summary

# FastAPI initialization
app = FastAPI(
    title="AI Agent API",
    description="API for querying an AI agent with vectorstore-backed knowledge",
    version="0.2.0"
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3

class LongTermQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    max_results: Optional[int] = 5

class ConversationResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

# Global variables for chains
retrieval_qa_chain = None
conversational_chain = None

# Initialize global resources
def initialize_chains():
    global retrieval_qa_chain, conversational_chain
    
    try:
        openai_key = os.getenv("openai_key")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")

        if not openai_key or not pinecone_api_key:
            raise ValueError("Missing required environment variables.")

        pc_client = PineconeClient(api_key=pinecone_api_key)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

        vectorstore = Pinecone(
            index=pc_client.Index("ai-agent-memory"),
            embedding=embeddings,
            text_key="content"
        )

        retrieval_qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )

        conversational_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever()
        )
        
        return True
    except Exception as e:
        print(f"Error initializing chains: {str(e)}")
        return False

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    success = initialize_chains()
    if not success:
        print("WARNING: Failed to initialize chains. API may not function correctly.")

# Basic Query endpoint
@app.post("/query", response_model=ConversationResponse)
async def query(request: QueryRequest):
    if retrieval_qa_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        retrieval_qa_chain.retriever.search_kwargs["k"] = request.max_results
        result = retrieval_qa_chain.invoke({"query": request.query})
        return ConversationResponse(response=result['result'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying agent: {str(e)}")

# Conversation endpoint
@app.post("/conversation", response_model=ConversationResponse)
async def conversation(request: QueryRequest, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    if conversational_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Create or retrieve session
        if not session_id:
            db_session = DbSession(session_id=uuid.uuid4())
            db.add(db_session)
            db.commit()
            session_id = str(db_session.session_id)
        else:
            try:
                uuid_obj = uuid.UUID(session_id)
                db_session = db.query(DbSession).filter(DbSession.session_id == uuid_obj).first()
                if not db_session:
                    db_session = DbSession(session_id=uuid_obj)
                    db.add(db_session)
                    db.commit()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Update last active timestamp
        db_session.last_active = datetime.utcnow()
        db.commit()

        # Get recent messages
        recent_messages = db.query(Message)\
            .filter(Message.session_id == uuid.UUID(session_id))\
            .order_by(Message.timestamp.desc())\
            .limit(10)\
            .all()
        
        chat_history = [(msg.role, msg.content) for msg in reversed(recent_messages)]

        # Process the query
        conversational_chain.retriever.search_kwargs["k"] = request.max_results
        result = conversational_chain.invoke({
            "question": request.query,
            "chat_history": chat_history
        })

        # Store messages in database
        new_message = Message(session_id=uuid.UUID(session_id), role="user", content=request.query)
        db.add(new_message)
        assistant_response = Message(session_id=uuid.UUID(session_id), role="assistant", content=result['answer'])
        db.add(assistant_response)
        db.commit()

        # Extract sources if available
        sources = None
        if "source_documents" in result:
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]

        return ConversationResponse(
            response=result['answer'], 
            session_id=session_id,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in conversation: {str(e)}")

# Long-term query endpoint
@app.post("/long_term_query")
async def long_term_query(
    request: LongTermQueryRequest, 
    db: Session = Depends(get_db),
    format: Optional[str] = "json"
):
    if conversational_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Get recent messages if session_id is provided
        chat_history = []
        if request.session_id:
            try:
                uuid_obj = uuid.UUID(request.session_id)
                recent_messages = db.query(Message)\
                    .filter(Message.session_id == uuid_obj)\
                    .order_by(Message.timestamp.desc())\
                    .limit(20)\
                    .all()
                
                chat_history = [(msg.role, msg.content) for msg in reversed(recent_messages)]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Process the query
        conversational_chain.retriever.search_kwargs["k"] = request.max_results
        result = conversational_chain.invoke({
            "question": request.query,
            "chat_history": chat_history
        })

        # Extract sources if available
        sources = None
        if "source_documents" in result:
            sources = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]

        # Format response based on format parameter
        response_dict = {
            "response": result["answer"],
            "session_id": request.session_id,
            "sources": sources
        }
        
        if format.lower() == "markdown":
            formatted_response = format_conversation_summary(response_dict, request.session_id)
            return PlainTextResponse(content=formatted_response, media_type="text/markdown")
        elif format.lower() == "html":
            import markdown
            formatted_response = format_conversation_summary(response_dict, request.session_id)
            html_content = markdown.markdown(formatted_response)
            return HTMLResponse(content=html_content)
        else:
            # Default JSON response
            return ConversationResponse(
                response=result["answer"],
                session_id=request.session_id,
                sources=sources
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in long-term memory: {str(e)}")

# Health endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "chains_initialized": retrieval_qa_chain is not None and conversational_chain is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)
