# CORS Configuration for AI Agent API

This document explains how to configure Cross-Origin Resource Sharing (CORS) for the AI Agent API to allow web applications from different domains to interact with it.

## What is CORS?

CORS is a security feature implemented by browsers that restricts web applications from making requests to a domain different from the one that served the web application. Without proper CORS configuration, your frontend application hosted on one domain (e.g., `https://yourapplication.com`) won't be able to make API requests to your AI Agent API hosted on another domain (e.g., `https://api.yourapplication.com`).

## Implementing CORS in FastAPI

FastAPI provides built-in support for CORS through the `CORSMiddleware`. Here's how to add it to your API:

### Basic CORS Configuration

Add the following code to your `api.py` file, just after creating the FastAPI app instance:

```python
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="API for querying an AI agent with vectorstore-backed knowledge",
    version="0.2.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
```

### Production-Ready CORS Configuration

For production environments, it's better to restrict the allowed origins to specific domains:

```python
from fastapi.middleware.cors import CORSMiddleware

# Get allowed origins from environment variable or use default
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://yourapplication.com")
origins = [origin.strip() for origin in allowed_origins.split(",")]

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)
```

## CORS Options Explained

- **allow_origins**: List of origins that are allowed to make cross-origin requests
- **allow_credentials**: Whether to support cookies in cross-origin requests
- **allow_methods**: HTTP methods that are allowed for cross-origin requests
- **allow_headers**: HTTP headers that can be used in cross-origin requests

## Testing CORS Configuration

You can test your CORS configuration using a simple web page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CORS Test</title>
    <script>
        async function testAPI() {
            try {
                const response = await fetch('http://127.0.0.1:5001/health', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                console.log('Success:', data);
            } catch (error) {
                document.getElementById('result').textContent = 'Error: ' + error.message;
                console.error('Error:', error);
            }
        }
    </script>
</head>
<body>
    <h1>CORS Test</h1>
    <button onclick="testAPI()">Test API</button>
    <pre id="result"></pre>
</body>
</html>
```

Save this file and open it in a browser. Click the "Test API" button to see if your API responds correctly.

## Common CORS Issues and Solutions

### Issue: Credentials Not Included

If you're using cookies or authentication headers, you need to include credentials in the fetch request:

```javascript
fetch('http://127.0.0.1:5001/query', {
    method: 'POST',
    credentials: 'include',  // Include credentials
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query: 'Hello' })
});
```

### Issue: Preflight Requests Failing

For complex requests (like those with custom headers or using methods other than GET/POST), browsers send a preflight OPTIONS request. Ensure your server handles OPTIONS requests correctly:

```python
@app.options("/{path:path}")
async def options_route(path: str):
    return {"detail": "OK"}
```

### Issue: Specific Headers Not Allowed

If you need to use specific headers in your requests, make sure they're included in the `allow_headers` list:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Custom-Header"],
)
```

## CORS in Development vs. Production

### Development

During development, you might want to allow all origins for convenience:

```python
if os.getenv("ENVIRONMENT") == "development":
    # Allow all origins in development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Restrict origins in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    )
```

### Production

In production, always restrict allowed origins to your specific domains:

```python
# For production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourapplication.com",
        "https://app.yourapplication.com",
        "https://admin.yourapplication.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

## Security Considerations

1. **Avoid using `allow_origins=["*"]` in production** - This allows any website to make requests to your API
2. **Be careful with `allow_credentials=True`** - Only use this if you need to support cookies or authentication headers
3. **Restrict allowed methods and headers** to only what your application needs
4. **Consider using a CORS proxy** for more complex scenarios

By properly configuring CORS, you'll ensure that your frontend applications can securely communicate with your AI Agent API while maintaining appropriate security boundaries. 