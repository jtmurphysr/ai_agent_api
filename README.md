# AI Agent API

A FastAPI-based service that provides access to an AI agent with vectorstore-backed knowledge retrieval.

## Overview

This API allows applications to query an AI agent that uses:
- OpenAI's GPT-4o model for generating responses
- Pinecone vector database for knowledge retrieval
- LangChain for orchestrating the retrieval-augmented generation process

The API is designed to be the backend component for a multi-platform AI assistant as described in the [agent specification](agent_spec.md).

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

```
python api.py
```

The API will be available at http://127.0.0.1:5001

## API Documentation

See [API.md](API.md) for detailed API documentation.

## Features

- Query the AI agent with natural language questions
- Adjust the number of retrieved documents used for context
- Health check endpoint for monitoring

## Planned Enhancements

See [functional_discussion.md](functional_discussion.md) for planned enhancements, including:
- Conversation memory and history
- Custom prompt configuration
- Continuous embedding pipeline
- Source attribution
- Model flexibility
- Authentication and security

## Development

This project is under active development. The current implementation provides a working foundation that will be enhanced according to the specifications in [agent_spec.md](agent_spec.md).

## License

[Your license information here]
