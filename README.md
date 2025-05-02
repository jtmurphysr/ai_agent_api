# AI Agent API

A FastAPI-based service that provides access to an AI agent with vectorstore-backed knowledge.

## Overview

This API allows applications to query an AI agent that uses:
- OpenAI's GPT-4o model for generating responses
- Pinecone vector database for knowledge retrieval
- LangChain for orchestrating the retrieval-augmented generation process

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key
- A configured Pinecone index named "ai-agent-memory"

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install fastapi uvicorn langchain-openai langchain-pinecone pinecone-client pydantic
   ```
3. Set environment variables:
   ```
   export openai_key=your_openai_api_key
   export PINECONE_API_KEY=your_pinecone_api_key
   ```

### Running the API
