# AI Agent API: Key Features

## Core Capabilities

### 🧠 Intelligent Querying
- **Natural Language Understanding:** Process and respond to complex questions in natural language
- **Knowledge Retrieval:** Access information from a vector database of documents and conversations
- **Contextual Awareness:** Understand the context of questions within ongoing conversations
- **Multi-turn Dialogues:** Maintain coherent conversations across multiple interactions

### 🔄 Memory Systems
- **Short-term Memory:** Track conversation context within a single session
- **Long-term Memory:** Store and retrieve information from past conversations
- **Semantic Search:** Find relevant information based on meaning, not just keywords
- **Hybrid Storage:** Combine SQL database and vector store for optimal information retrieval

### 👤 Personality Customization
- **Flexible Agent Identities:** Switch between different agent personalities
- **Tone Control:** Adjust communication style from professional to conversational
- **Domain Specialization:** Create personalities optimized for specific knowledge domains
- **Consistent Character:** Maintain consistent personality traits across conversations

## API Endpoints

### Query (Stateless)
- **`/query`**
  - Single-turn question answering without conversation history
  - **Ideal for:** Quick information retrieval, standalone questions
  - **Features:**
    - Adjustable document retrieval (`max_results` parameter)
    - Personality selection
    - Source attribution

### Conversation
- **`/conversation`**
  - Multi-turn conversations with persistent history
  - **Ideal for:** Ongoing dialogues, follow-up questions
  - **Features:**
    - Session-based memory
    - Personality persistence across the conversation
    - Automatic context management

### Long-Term Memory Query
- **`/long_term_query`**
  - Comprehensive queries that leverage both conversation history and semantic search
  - **Ideal for:** Questions about past interactions, pattern recognition
  - **Features:**
    - Multiple response formats (JSON, Markdown, HTML)
    - Cross-session memory retrieval
    - Rich, formatted responses for complex questions

### Personality Management
- **`/personalities`**
  - Create, list, and use custom agent personalities
  - **Ideal for:** Tailoring the agent for different use cases
  - **Features:**
    - JSON template-based personalities
    - Raw prompt personalities
    - Runtime personality switching

## Personality System

### Template-Based Personalities
Define structured personalities with:
- **Core Identity:** Name, role, and primary characteristics
- **Communication Style:** Language complexity, interaction level, humor, empathy
- **Behavioral Guidelines:** Response length, speed, proactivity
- **Example Responses:** Sample outputs that demonstrate the personality's style

### Raw Prompt Personalities
Create personalities using direct system prompts for maximum control over:
- **Voice and Tone:** How the agent expresses itself
- **Domain Knowledge:** Specialized expertise areas
- **Interaction Patterns:** How the agent engages with users

### Example Personalities
- **Milton:** A senior business consultant with professional tone and business expertise
- **Lara:** A personalized companion with a more personal, poetic style
- **Default:** A helpful, neutral assistant for general-purpose use

## Technical Features

### Database Flexibility
- PostgreSQL support for production environments
- SQLite fallback for development and testing
- Automatic database detection and configuration

### Response Formatting
- JSON for programmatic use
- Markdown for readable, structured text
- HTML for direct display in web applications

### Health Monitoring
- System status checks
- Chain initialization verification
- Personality loading confirmation

## Integration Options

### REST API
- Standard HTTP endpoints
- JSON request/response format
- Stateless and stateful operation modes

### Session Management
- UUID-based session tracking
- Persistent conversation history
- Cross-session information retrieval

### Deployment Flexibility
- Local development server
- Cloud deployment ready
- Environment variable configuration