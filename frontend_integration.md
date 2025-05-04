# AI Agent Frontend Integration Guide

This guide provides practical examples and best practices for integrating the AI Agent API into frontend applications.

## Getting Started

### Basic Query Implementation

```javascript
// Example using fetch API
async function queryAgent(question) {
  const response = await fetch('http://127.0.0.1:5001/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question,
      max_results: 3
    }),
  });
  
  return await response.json();
}

// Usage
queryAgent("What is the capital of France?")
  .then(data => {
    console.log(data.response);
  })
  .catch(error => console.error('Error:', error));
```

### Managing Conversations

```javascript
// Store session ID between requests
let currentSessionId = null;

async function conversationWithAgent(question) {
  const response = await fetch('http://127.0.0.1:5001/conversation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question,
      max_results: 3
    }),
    // Add session ID if we have one
    ...(currentSessionId && { 
      params: { session_id: currentSessionId } 
    })
  });
  
  const data = await response.json();
  
  // Save the session ID for future requests
  currentSessionId = data.session_id;
  
  return data;
}
```

### Using Different Personalities

```javascript
// Function to get available personalities
async function getPersonalities() {
  const response = await fetch('http://127.0.0.1:5001/personalities');
  return await response.json();
}

// Query with a specific personality
async function queryWithPersonality(question, personalityId) {
  const response = await fetch('http://127.0.0.1:5001/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question,
      personality_id: personalityId
    }),
  });
  
  return await response.json();
}
```

### Displaying Formatted Responses

```javascript
// Get a markdown-formatted response
async function getLongTermSummary(question) {
  const response = await fetch('http://127.0.0.1:5001/long_term_query?format=markdown', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question
    }),
  });
  
  // Get the response as text since it's markdown
  return await response.text();
}

// Display using a markdown renderer
import ReactMarkdown from 'react-markdown';

function MarkdownResponse({ markdownText }) {
  return <ReactMarkdown>{markdownText}</ReactMarkdown>;
}
```

## UI Component Examples

### Chat Interface

```jsx
function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    
    // Clear input
    setInput('');
    
    try {
      // Send to API
      const response = await fetch('http://127.0.0.1:5001/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          max_results: 3
        }),
        ...(sessionId && { params: { session_id: sessionId } })
      });
      
      const data = await response.json();
      
      // Save session ID
      if (!sessionId) {
        setSessionId(data.session_id);
      }
      
      // Add assistant response to UI
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'Sorry, there was an error processing your request.' 
      }]);
    }
  };
  
  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
```

### Personality Selector

```jsx
function PersonalitySelector({ onSelect }) {
  const [personalities, setPersonalities] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadPersonalities() {
      try {
        const response = await fetch('http://127.0.0.1:5001/personalities');
        const data = await response.json();
        setPersonalities(data);
      } catch (error) {
        console.error('Error loading personalities:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadPersonalities();
  }, []);
  
  if (loading) return <div>Loading personalities...</div>;
  
  return (
    <div className="personality-selector">
      <h3>Choose a personality</h3>
      <div className="personality-list">
        {personalities.map(personality => (
          <div 
            key={personality.id}
            className="personality-card"
            onClick={() => onSelect(personality.id)}
          >
            <h4>{personality.name}</h4>
            <p>{personality.role}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Best Practices

### Error Handling

Always implement proper error handling in your frontend:

```javascript
try {
  const response = await fetch('http://127.0.0.1:5001/query', {
    // request details
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Unknown error');
  }
  
  const data = await response.json();
  // Process successful response
} catch (error) {
  // Handle error appropriately
  console.error('API Error:', error.message);
  // Show user-friendly error message
}
```

### Session Management

- Store the session ID in localStorage or sessionStorage for persistence across page reloads
- Consider implementing an automatic session recovery mechanism
- Implement session timeout handling

### Optimistic UI Updates

For better user experience, update the UI optimistically before receiving API responses:

```javascript
// Add user message immediately
setMessages(prev => [...prev, { role: 'user', content: input }]);
// Show typing indicator
setIsTyping(true);

try {
  // API call
  const data = await sendToApi(input);
  // Replace typing indicator with actual response
  setIsTyping(false);
  setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
} catch (error) {
  // Handle error
}
```

### Handling Long Responses

For long responses, consider implementing:
- Progressive rendering
- Scrolling to new messages
- Collapsible sections for very long responses

## Advanced Integration

### Uploading Custom Personalities

```javascript
async function uploadPersonality(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://127.0.0.1:5001/personalities/upload', {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
}

// Usage with file input
function PersonalityUploader() {
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const result = await uploadPersonality(file);
        alert(`Personality uploaded successfully! ID: ${result.personality_id}`);
      } catch (error) {
        alert('Error uploading personality: ' + error.message);
      }
    }
  };
  
  return (
    <div>
      <h3>Upload Custom Personality</h3>
      <input type="file" accept=".json,.fil,.txt,.md" onChange={handleFileChange} />
    </div>
  );
}
```

### Health Check Integration

```javascript
// Periodic health check
function useHealthCheck(interval = 60000) {
  const [status, setStatus] = useState({
    healthy: false,
    chainsInitialized: false,
    personalitiesLoaded: 0,
    lastChecked: null
  });
  
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5001/health');
        const data = await response.json();
        
        setStatus({
          healthy: data.status === 'healthy',
          chainsInitialized: data.chains_initialized,
          personalitiesLoaded: data.personalities_loaded,
          lastChecked: new Date()
        });
      } catch (error) {
        setStatus(prev => ({
          ...prev,
          healthy: false,
          lastChecked: new Date()
        }));
      }
    };
    
    // Initial check
    checkHealth();
    
    // Set up interval
    const intervalId = setInterval(checkHealth, interval);
    
    // Clean up
    return () => clearInterval(intervalId);
  }, [interval]);
  
  return status;
}
``` 