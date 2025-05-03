import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import Pinecone
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from pinecone import Pinecone as PineconeClient
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain

# Database models and session management
from db import Session as DbSession, Message, get_db
from formatter import format_conversation_summary
from personality_manager import PersonalityManager

# FastAPI initialization
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize chains
    success = initialize_chains()
    if not success:
        print("WARNING: Failed to initialize chains. API may not function correctly.")
    yield
    # Shutdown: clean up resources if needed
    # (No cleanup needed for now)

app = FastAPI(
    title="AI Agent API",
    description="API for querying an AI agent with vectorstore-backed knowledge",
    version="0.2.0",
    lifespan=lifespan
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3
    personality_id: Optional[str] = None

class LongTermQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    max_results: Optional[int] = 5
    personality_id: Optional[str] = None

class ConversationResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

class PersonalityResponse(BaseModel):
    id: str
    name: str
    type: str
    role: str

# Global variables for chains
retrieval_qa_chain = None
conversational_chain = None
personality_manager = None

# Initialize global resources
def initialize_chains():
    global retrieval_qa_chain, conversational_chain, personality_manager
    
    try:
        openai_key = os.getenv("openai_key")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")

        if not openai_key or not pinecone_api_key:
            raise ValueError("Missing required environment variables.")

        # Initialize personality manager
        personality_manager = PersonalityManager()

        pc_client = PineconeClient(api_key=pinecone_api_key)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
        
        # Create default LLM with default personality
        default_system_prompt = personality_manager.create_system_prompt()
        llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_key
        )

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

def get_llm_with_personality(personality_id: Optional[str] = None):
    """Get an LLM instance with the specified personality."""
    openai_key = os.getenv("openai_key")
    
    if personality_id:
        system_prompt = personality_manager.create_system_prompt(personality_id)
    else:
        system_prompt = personality_manager.create_system_prompt()
        
    # Create the LLM with system prompt
    llm = ChatOpenAI(
        model="gpt-4o", 
        openai_api_key=openai_key
    )
    
    # Create a chain with the system prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain

# Basic Query endpoint
@app.post("/query", response_model=ConversationResponse)
async def query(request: QueryRequest):
    if retrieval_qa_chain is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Use custom personality if specified
        if request.personality_id:
            # Get the personality chain
            personality_chain = get_llm_with_personality(request.personality_id)
            
            # Get documents from retriever
            retrieval_qa_chain.retriever.search_kwargs["k"] = request.max_results
            docs = retrieval_qa_chain.retriever.get_relevant_documents(request.query)
            
            # Format the context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Run the personality chain with the query and context
            result_text = personality_chain.run(input=f"{request.query}\n\nContext: {context}")
            
            return ConversationResponse(response=result_text)
        else:
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
        
        # Store personality ID in session metadata if provided
        if request.personality_id:
            if not db_session.session_metadata:
                db_session.session_metadata = {}
            db_session.session_metadata['personality_id'] = request.personality_id
            
        db.commit()

        # Get recent messages
        recent_messages = db.query(Message)\
            .filter(Message.session_id == uuid.UUID(session_id))\
            .order_by(Message.timestamp.desc())\
            .limit(10)\
            .all()
        
        chat_history = [(msg.role, msg.content) for msg in reversed(recent_messages)]

        # Get personality ID from session metadata or request
        personality_id = None
        if db_session.session_metadata and 'personality_id' in db_session.session_metadata:
            personality_id = db_session.session_metadata['personality_id']
        elif request.personality_id:
            personality_id = request.personality_id
            
        # Use custom personality if specified
        if personality_id:
            # Get the personality chain
            personality_chain = get_llm_with_personality(personality_id)
            
            # Get documents from retriever
            conversational_chain.retriever.search_kwargs["k"] = request.max_results
            docs = conversational_chain.retriever.get_relevant_documents(request.query)
            
            # Format the context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Format chat history for context
            history_text = ""
            if chat_history:
                history_text = "Previous conversation:\n"
                for role, content in chat_history:
                    history_text += f"{role.capitalize()}: {content}\n"
            
            # Run the personality chain with the query, context, and history
            full_query = f"{request.query}\n\nContext: {context}\n\n{history_text}"
            result_text = personality_chain.run(input=full_query)
            
            result = {"answer": result_text, "source_documents": docs}
        else:
            # Process the query with default chain
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
        personality_id = request.personality_id
        if request.session_id:
            try:
                uuid_obj = uuid.UUID(request.session_id)
                db_session = db.query(DbSession).filter(DbSession.session_id == uuid_obj).first()
                
                if db_session:
                    # Get personality ID from session metadata if not provided in request
                    if not personality_id and db_session.session_metadata and 'personality_id' in db_session.session_metadata:
                        personality_id = db_session.session_metadata['personality_id']
                        
                    recent_messages = db.query(Message)\
                        .filter(Message.session_id == uuid_obj)\
                        .order_by(Message.timestamp.desc())\
                        .limit(20)\
                        .all()
                    
                    chat_history = [(msg.role, msg.content) for msg in reversed(recent_messages)]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Use custom personality if specified
        if personality_id:
            # Get the personality chain
            personality_chain = get_llm_with_personality(personality_id)
            
            # Get documents from retriever
            conversational_chain.retriever.search_kwargs["k"] = request.max_results
            docs = conversational_chain.retriever.get_relevant_documents(request.query)
            
            # Format the context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Format chat history for context
            history_text = ""
            if chat_history:
                history_text = "Previous conversation:\n"
                for role, content in chat_history:
                    history_text += f"{role.capitalize()}: {content}\n"
            
            # Run the personality chain with the query, context, and history
            full_query = f"{request.query}\n\nContext: {context}\n\n{history_text}"
            result_text = personality_chain.run(input=full_query)
            
            result = {"answer": result_text, "source_documents": docs}
        else:
            # Process the query with default chain
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

# Personality management endpoints
@app.get("/personalities", response_model=List[PersonalityResponse])
async def list_personalities():
    """List all available personalities."""
    if personality_manager is None:
        raise HTTPException(status_code=500, detail="Personality manager not initialized")
    
    personalities = personality_manager.list_personalities()
    return [
        PersonalityResponse(
            id=personality_id,
            name=data['name'],
            type=data['type'],
            role=data['role']
        )
        for personality_id, data in personalities.items()
    ]

@app.post("/personalities/upload")
async def upload_personality(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None)
):
    """Upload a new personality file."""
    if personality_manager is None:
        raise HTTPException(status_code=500, detail="Personality manager not initialized")
    
    try:
        # Create a temporary file
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Add the personality
        personality_id = personality_manager.add_personality(temp_file_path)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return {"message": f"Personality uploaded successfully", "personality_id": personality_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading personality: {str(e)}")

@app.get("/personalities/{personality_id}/prompt")
async def get_personality_prompt(personality_id: str):
    """Get the system prompt for a personality."""
    if personality_manager is None:
        raise HTTPException(status_code=500, detail="Personality manager not initialized")
    
    try:
        prompt = personality_manager.create_system_prompt(personality_id)
        return PlainTextResponse(content=prompt)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Health endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "chains_initialized": retrieval_qa_chain is not None and conversational_chain is not None,
        "personalities_loaded": len(personality_manager.personalities) if personality_manager else 0
    }

if __name__ == "__main__":
    import uvicorn
    # For development with auto-reload, run this command instead:
    # uvicorn api:app --host 127.0.0.1 --port 5001 --reload
    uvicorn.run(app, host="127.0.0.1", port=5001)
