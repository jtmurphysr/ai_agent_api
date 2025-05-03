# AI Agent API

A FastAPI-based service that provides access to an AI agent with vectorstore-backed knowledge retrieval.

## Overview

This API allows applications to query an AI agent that uses:
- OpenAI's GPT-4o model for generating responses
- Pinecone vector database for semantic knowledge retrieval
- PostgreSQL database for conversation history storage (with SQLite fallback for development)
- LangChain for orchestrating the retrieval-augmented generation process

The API is designed to be the backend component for a multi-platform AI assistant as described in the [agent specification](agent_spec.md).

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key
- A configured Pinecone index named "ai-agent-memory"
- PostgreSQL database (optional - will fall back to SQLite for development)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```
   export openai_key=your_openai_api_key
   export PINECONE_API_KEY=your_pinecone_api_key
   export DATABASE_URL=postgresql://username:password@localhost/ai_agent  # Optional
   ```
4. Create the PostgreSQL database (if using PostgreSQL):
   ```
   createdb ai_agent
   ```
5. Initialize the database:
   ```
   python setup_db.py
   ```

### Running the API

```
python api.py
```

The API will be available at http://127.0.0.1:5001

### Running the Embedding Job

To periodically embed conversations into Pinecone:

```
python embedding_job.py
```

This can be scheduled to run daily using cron or another scheduler:

```
# Example cron entry (runs daily at 2 AM)
0 2 * * * /path/to/python /path/to/embedding_job.py >> /path/to/logs/embedding.log 2>&1
```

## API Documentation

See [API.md](API.md) for detailed API documentation.

## Features

- Query the AI agent with natural language questions
- Multiple conversation modes:
  - Stateless queries
  - In-memory conversation history
  - Long-term memory with client-managed history
  - Hybrid memory using PostgreSQL/SQLite and Pinecone
- Adjust the number of retrieved documents used for context
- Retrieve conversation history by session
- Periodic embedding of conversations into the vector database
- Health check endpoint for monitoring
- Database flexibility (PostgreSQL with SQLite fallback)

## Architecture

The system uses a hybrid memory architecture:
1. **Database** (PostgreSQL or SQLite) stores raw conversation data with session management
2. **Pinecone** stores semantic embeddings for efficient retrieval
3. **Embedding Job** periodically processes conversations from the database and adds them to Pinecone
4. **Hybrid Query** combines recent history from the database with semantic search from Pinecone

## Planned Enhancements

See [functional_discussion.md](functional_discussion.md) for planned enhancements, including:
- Custom prompt configuration
- Model flexibility
- Authentication and security

## Development

This project is under active development. The current implementation provides a working foundation that will be enhanced according to the specifications in [agent_spec.md](agent_spec.md).

## License

[Your license information here]
