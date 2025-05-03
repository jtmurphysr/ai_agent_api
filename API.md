# AI Agent API Documentation

## Base URL

When running locally: `http://127.0.0.1:5001`

## Endpoints

### Query the AI Agent (Stateless)

```
POST /query
```

Submit a query to the AI agent and receive a response based on the agent's knowledge. This endpoint is stateless and doesn't maintain conversation history.

#### Request Body

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| query | string | The question or query for the AI agent | Yes | - |
| max_results | integer | Maximum number of documents to retrieve from the vector store | No | 3 |

#### Example Request

```json
{
  "query": "What is the capital of France?",
  "max_results": 5
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| response | string | The AI agent's response to the query |
| session_id | string | Session ID (only for session-based endpoints) |
| sources | array | Source documents used for the response (if available) |

#### Example Response

```json
{
  "response": "The capital of France is Paris."
}
```

### Conversation with In-Memory History

```
POST /conversation
```

Submit a query to the AI agent with in-memory conversation history. This endpoint maintains conversation context between requests but the history is lost if the server restarts.

#### Request Body

Same as `/query` endpoint.

#### Response

Same as `/query` endpoint.

### Long-Term Memory Query

```
POST /long_term_query
```

Submit a query that leverages the user's conversation history and semantically similar content from the vector database.

#### Request Body

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| query | string | The question or query for the AI agent | Yes | - |
| session_id | string | Optional session ID to retrieve specific conversation history | No | null |
| max_results | integer | Maximum number of documents to retrieve from the vector store | No | 5 |

#### Query Parameters

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| format | string | Response format: "json", "markdown", or "html" | No | "json" |

#### Example Request

```json
{
  "query": "Based on all our past conversations, what topics do I frequently discuss?",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Example Usage with Format

```
POST /long_term_query?format=markdown
```

This will return a beautifully formatted markdown response instead of JSON.

#### Response

The response format depends on the `format` parameter:

- **JSON** (default): Standard JSON response with fields below
- **Markdown**: A formatted markdown text with categorized topics and sources
- **HTML**: The markdown content converted to HTML for direct display

##### JSON Response Fields:

| Field | Type | Description |
|-------|------|-------------|
| response | string | The AI agent's response to the query |
| session_id | string | Session ID (if provided in the request) |
| sources | array | Source documents used for the response (if available) |

#### Example Response

##### JSON Response:
```json
{
  "response": "Based on our past conversations, you frequently discuss artificial intelligence, machine learning frameworks, and software architecture patterns. You've shown particular interest in vector databases and retrieval-augmented generation techniques.",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "sources": [
    {
      "content": "Conversation from 2023-05-15 about machine learning frameworks and their applications in production environments.",
      "metadata": {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "start_time": "2023-05-15T14:23:15Z",
        "end_time": "2023-05-15T14:45:22Z",
        "type": "conversation_history"
      }
    }
  ]
}
```

##### Markdown Response:

```markdown
# 📚 **Summary of Your Frequent Conversation Topics**

Based on our past conversations, here's a categorized overview of topics you frequently discuss:

## 1. 🚀 Strategic Writing and Communication
- Professional bios, LinkedIn profiles, and leadership posts.
- Examples: *"Can you write a powerful blurb for Potable Press?"*

## 2. 🔧 Technical Troubleshooting & Systems Design
- Linux server administration, Docker, Flask applications, and HomeKit setups.

...

## 🗃️ **Sources Referenced:**
- INTJ Personality Analysis (`conversation_id`: 2)
- Interaction Summary and Tone (`conversation_id`: 156)

---
```

#### Usage Notes

1. **Session-Based Retrieval**: If you provide a session_id, the endpoint will retrieve and use that specific conversation history.

2. **Global Retrieval**: If no session_id is provided, the endpoint will rely on semantic search across all conversations in the vector database.

3. **Semantic Search**: This endpoint uses vector embeddings to find relevant past conversations, even if they don't contain the exact keywords in your query.

4. **Meta-Analysis**: This endpoint is particularly useful for questions about patterns, preferences, or summaries of past interactions.

5. **Formatted Responses**: Use the `format` parameter to get responses in markdown or HTML for better presentation in user interfaces.

### Hybrid Memory Query

```
POST /hybrid_memory
```

Submit a query that uses both database (PostgreSQL/SQLite) for recent conversation history and Pinecone for semantic retrieval. This endpoint maintains conversation history in the database.

#### Request Body

Same as `/query` endpoint.

#### Query Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| session_id | string | Session ID for continuing a conversation | No |

#### Response

| Field | Type | Description |
|-------|------|-------------|
| response | string | The AI agent's response to the query |
| session_id | string | Session ID for the conversation |
| sources | array | Source documents used for the response (if available) |

#### Example Response

```json
{
  "response": "Paris has a population of approximately 2.2 million people in the city proper, while the greater Paris metropolitan area has a population of about 12 million.",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "sources": [
    {
      "content": "Paris is the capital and most populous city of France. The city proper has a population of 2.2 million, while the Paris metropolitan area has a population of over 12 million people.",
      "metadata": {
        "source": "geography_database",
        "last_updated": "2023-01-15"
      }
    }
  ]
}
```

### Get Session History

```
GET /sessions/{session_id}/history
```

Retrieve the conversation history for a specific session.

#### Path Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| session_id | string | Session ID | Yes |

#### Query Parameters

| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| limit | integer | Maximum number of messages to return | No | 50 |

#### Response

```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?",
      "timestamp": "2023-06-01T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "The capital of France is Paris.",
      "timestamp": "2023-06-01T12:00:01Z"
    }
  ]
}
```

### Health Check

```
GET /health
```

Check if the API service is running properly.

#### Response

```json
{
  "status": "healthy"
}
```

## Error Handling

Errors are returned as JSON objects with a `detail` field containing the error message:

```json
{
  "detail": "Error message here"
}
```

Common error scenarios:
- Agent not initialized (missing environment variables)
- Error during query processing
- Invalid session ID format
- Session not found
- Database connection issues

## Database Configuration

The API automatically detects and uses:
- PostgreSQL if available (using the DATABASE_URL environment variable or system username)
- SQLite as a fallback for development environments

This allows for easy development setup while supporting production-grade database capabilities when needed. 