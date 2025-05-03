import os
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db import SessionLocal, Message, EmbeddingJob, create_tables
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_conversation(messages, chunk_size=5):
    """Chunk a conversation into manageable pieces for embedding"""
    chunks = []
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i+chunk_size]
        # Format as a conversation
        text = "\n".join([f"{msg.role}: {msg.content}" for msg in chunk])
        # Add metadata
        metadata = {
            "session_id": str(chunk[0].session_id),
            "start_time": chunk[0].timestamp.isoformat(),
            "end_time": chunk[-1].timestamp.isoformat(),
            "message_ids": [str(msg.message_id) for msg in chunk],
            "type": "conversation_history"
        }
        chunks.append((text, metadata))
    return chunks

def run_embedding_job():
    """Process pending messages and embed them into Pinecone"""
    db = SessionLocal()
    
    try:
        # Create a new job record
        job = EmbeddingJob(job_id=uuid.uuid4())
        db.add(job)
        db.commit()
        
        # Get messages that need embedding (pending and older than 1 hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        pending_messages = db.query(Message)\
            .filter(Message.embedding_status == "pending")\
            .filter(Message.timestamp < cutoff_time)\
            .order_by(Message.timestamp)\
            .all()
        
        if not pending_messages:
            logger.info("No pending messages to embed")
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # Group messages by session
        sessions = {}
        for msg in pending_messages:
            if msg.session_id not in sessions:
                sessions[msg.session_id] = []
            sessions[msg.session_id].append(msg)
        
        # Initialize Pinecone
        openai_key = os.getenv("openai_key")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not openai_key or not pinecone_api_key:
            raise ValueError("Missing API keys")
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
        pc = PineconeClient(api_key=pinecone_api_key)
        
        vectorstore = Pinecone(
            index=pc.Index("ai-agent-memory"),
            embedding=embeddings
        )
        
        # Process each session
        total_processed = 0
        for session_id, messages in sessions.items():
            logger.info(f"Processing session {session_id} with {len(messages)} messages")
            
            # Chunk the conversation
            chunks = chunk_conversation(messages)
            
            # Embed and store chunks
            texts = [chunk[0] for chunk in chunks]
            metadatas = [chunk[1] for chunk in chunks]
            
            if texts:
                vectorstore.add_texts(texts=texts, metadatas=metadatas)
                
                # Mark messages as embedded
                for msg in messages:
                    msg.embedding_status = "embedded"
                    total_processed += 1
            
            db.commit()
        
        # Update job status
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.messages_processed = total_processed
        db.commit()
        
        logger.info(f"Embedding job completed. Processed {total_processed} messages.")
        
    except Exception as e:
        logger.error(f"Error in embedding job: {str(e)}")
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    create_tables()
    # Run the embedding job
    run_embedding_job() 