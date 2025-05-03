# long_term_memory.py

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from pinecone import Pinecone as PineconeClient
import os

def create_long_term_chain(index_name: str = "ai-agent-memory"):
    # Fetch environment variables
    openai_key = os.getenv("openai_key")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not openai_key or not pinecone_api_key:
        raise ValueError("Required environment variables missing.")

    # Initialize Pinecone client
    pc = PineconeClient(api_key=pinecone_api_key)

    # Set up embeddings and LLM
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    # Initialize vector store
    vectorstore = Pinecone(
        index=pc.Index(index_name),
        embedding=embeddings,
        text_key="content"
    )

    # Create conversational retrieval chain
    memory_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True
    )

    return memory_chain

def create_hybrid_memory_chain(index_name: str = "ai-agent-memory"):
    """
    Creates a chain that combines recent conversation history from Postgres
    with semantic retrieval from Pinecone
    """
    # Fetch environment variables
    openai_key = os.getenv("openai_key")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not openai_key or not pinecone_api_key:
        raise ValueError("Required environment variables missing.")

    # Set up embeddings and LLM
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    # Initialize Pinecone client
    pc = PineconeClient(api_key=pinecone_api_key)

    # Initialize vector store
    vectorstore = Pinecone(
        index=pc.Index(index_name),
        embedding=embeddings,
        text_key="content"
    )

    # Create conversational retrieval chain without memory
    # (we'll provide the memory from Postgres)
    memory_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True,
        verbose=True
    )

    return memory_chain