# AI Agent API Documentation

## Base URL

When running locally: `http://127.0.0.1:5001`

## Endpoints

### Query the AI Agent

```
POST /query
```

Submit a query to the AI agent and receive a response based on the agent's knowledge.

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

#### Example Response

```json
{
  "response": "The capital of France is Paris."
}
```

#### Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 500 | Server error (agent not initialized or query processing error) |

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

#### Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Service is healthy |

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