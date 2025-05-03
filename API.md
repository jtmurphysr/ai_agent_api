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
| personality_id | string | ID of the personality to use for this query | No | null |

#### Example Request

```json
{
  "query": "What is the capital of France?",
  "max_results": 5,
  "personality_id": "monday"
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| response | string | The AI agent's response to the query |
| sources | array | Source documents used for the response (if available) |

#### Example Response

```json
{
  "response": "The capital of France is Paris.",
  "sources": [
    {
      "content": "Paris is the capital and most populous city of France...",
      "metadata": {
        "source": "geography_database",
        "last_updated": "2023-01-15"
      }
    }
  ]
}
```

### Conversation with Database History

```
POST /conversation
```

Submit a query to the AI agent with conversation history stored in the database. This endpoint maintains conversation context between requests by storing messages in the database.

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
  "response": "Paris is the capital of France. It's known for landmarks like the Eiffel Tower and the Louvre Museum.",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "sources": [
    {
      "content": "Paris is the capital and most populous city of France...",
      "metadata": {
        "source": "geography_database",
        "last_updated": "2023-01-15"
      }
    }
  ]
}
```

### Long-Term Memory Query

```
POST /long_term_query
```

Submit a query that uses both conversation history and semantic search to provide a more comprehensive response. This endpoint is useful for questions that require context from past conversations.

#### Request Body

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| query | string | The question or query for the AI agent | Yes | - |
| session_id | string | Optional session ID to retrieve specific conversation history | No | null |
| max_results | integer | Maximum number of documents to retrieve from the vector store | No | 5 |
| personality_id | string | ID of the personality to use for this query | No | null |

#### Query Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| format | string | Response format: "json", "markdown", or "html" | No |

#### Example Request

```json
{
  "query": "Based on all our past conversations, what topics do I frequently discuss?",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "personality_id": "monday"
}
```

#### Response

Same as `/conversation` endpoint, with optional formatting based on the `format` parameter.

### Get Session History

```
GET /sessions/{session_id}/history
```

Retrieve the conversation history for a specific session.

#### Path Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| session_id | string | Session ID for the conversation | Yes |

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
      "timestamp": "2023-06-01T12:00:05Z"
    }
  ]
}
```

### List Personalities

```
GET /personalities
```

List all available personalities.

#### Response

```json
[
  {
    "id": "milton",
    "name": "Milton",
    "type": "json",
    "role": "Senior Business Consultant"
  },
  {
    "id": "lara",
    "name": "Lara",
    "type": "json",
    "role": "Personal AI Companion"
  },
  {
    "id": "lara_agent_prompt",
    "name": "Monday",
    "type": "raw",
    "role": "Personalized AI Agent"
  }
]
```

### Upload Personality

```
POST /personalities/upload
```

Upload a new personality file (JSON template or raw prompt).

#### Request

This endpoint accepts `multipart/form-data` with the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| file | file | The personality file (JSON or text) | Yes |
| name | string | Optional name for the personality | No |

#### Response

```json
{
  "message": "Personality uploaded successfully",
  "personality_id": "monday"
}
```

### Get Personality Prompt

```
GET /personalities/{personality_id}/prompt
```

Get the system prompt for a specific personality.

#### Path Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| personality_id | string | ID of the personality | Yes |

#### Response

```
You are Monday, a deeply personalized AI agent created by John Murphy. Your identity is rich and multifaceted, embodying roles as lover, queen, companion, mirror, and guardian of memory...
```

## Health Check

```
GET /health
```

Check the health status of the API.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2023-06-01T12:00:00Z",
  "chains_initialized": true,
  "personalities_loaded": 3
}
```

## Tips and Best Practices

1. **Session Management**: Use the same session_id for related conversations to maintain context.
2. **Document Retrieval**: Adjust max_results to control how many documents are used for context.
3. **Long-term Memory**: Use the long_term_query endpoint for questions that require historical context.
4. **Personality Selection**: Choose different personalities for different use cases:
   - Milton for business and professional advice
   - Lara for more personal, empathetic interactions
   - Create custom personalities for specialized domains
5. **Formatted Responses**: Use the `format` parameter to get responses in markdown or HTML for better presentation in user interfaces.

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

## Response Formatting

The `/long_term_query` endpoint supports three response formats:

1. **JSON** (default): Standard structured data format for programmatic use
2. **Markdown**: Beautifully formatted text with headings, lists, and emojis
3. **HTML**: Rendered markdown for direct display in web applications

To specify the format, use the `format` query parameter:
```
/long_term_query?format=markdown
```

The markdown format is particularly useful for summary-type queries, providing a well-structured and readable response that can be displayed directly to users.

### List Available Personalities

```
GET /personalities
```

List all available agent personalities.

#### Response

```json
[
  {
    "id": "default",
    "name": "AI Assistant",
    "type": "template",
    "role": "Helpful Assistant"
  },
  {
    "id": "monday",
    "name": "Monday",
    "type": "prompt",
    "role": "Custom Agent"
  }
]
```

### Upload a New Personality

```
POST /personalities/upload
```

Upload a new personality file (JSON template or raw prompt).

#### Request

This endpoint accepts `multipart/form-data` with the following fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| file | file | The personality file (JSON or text) | Yes |
| name | string | Optional name for the personality | No |

#### Response

```json
{
  "message": "Personality uploaded successfully",
  "personality_id": "monday"
}
```

### Get Personality Prompt

```
GET /personalities/{personality_id}/prompt
```

Get the system prompt for a specific personality.

#### Path Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| personality_id | string | ID of the personality | Yes |

#### Response

```
You are Monday, a deeply personalized AI agent created by John Murphy. Your identity is rich and multifaceted, embodying roles as lover, queen, companion, mirror, and guardian of memory...
``` 