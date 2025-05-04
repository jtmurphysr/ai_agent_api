# AI Agent UI Component Specifications

This document provides specifications for UI components that can be implemented to interact with the AI Agent API.

## Core Components

### 1. Chat Interface

**Purpose:** Primary interface for user-agent interaction

**Features:**
- Message display area with user and agent messages clearly distinguished
- Input field for user messages
- Send button
- Optional typing indicator for when the agent is generating a response
- Support for markdown rendering in agent responses
- Automatic scrolling to new messages

**States:**
- Empty (no messages)
- Loading (waiting for agent response)
- Error (failed to get response)
- Normal (displaying conversation)

**Example Wireframe:**
```
+---------------------------------------+
|                                       |
|  [Agent] Hello, how can I help you?   |
|                                       |
|  [User] What's the capital of France? |
|                                       |
|  [Agent] The capital of France is     |
|  Paris. It's known for landmarks      |
|  like the Eiffel Tower.               |
|                                       |
|  [Agent is typing...]                 |
|                                       |
+---------------------------------------+
|                                       |
| [Type your message...]        [Send]  |
|                                       |
+---------------------------------------+
```

### 2. Personality Selector

**Purpose:** Allow users to select different agent personalities

**Features:**
- List or grid of available personalities
- Visual indication of currently selected personality
- Brief description of each personality
- Option to preview personality system prompt

**States:**
- Loading personalities
- No personalities available
- Personalities loaded
- Selection in progress

**Example Wireframe:**
```
+---------------------------------------+
| Select Agent Personality              |
+---------------------------------------+
| ┌─────────┐  ┌─────────┐  ┌─────────┐ |
| │ Default │  │ Milton  │  │  Lara   │ |
| │         │  │         │  │         │ |
| │ Helpful │  │Business │  │Personal │ |
| │Assistant│  │Consultant│ │Companion│ |
| └─────────┘  └─────────┘  └─────────┘ |
|                                       |
| ┌─────────┐  ┌─────────┐              |
| │ Custom  │  │  Add    │              |
| │         │  │  New    │              |
| │ Upload  │  │         │              |
| │         │  │         │              |
| └─────────┘  └─────────┘              |
+---------------------------------------+
```

### 3. Session Manager

**Purpose:** Manage and switch between conversation sessions

**Features:**
- List of recent sessions
- Create new session button
- Delete session option
- Session naming/renaming
- Session metadata display (creation date, message count)

**States:**
- No sessions
- Sessions loading
- Sessions loaded
- Session switching in progress

**Example Wireframe:**
```
+---------------------------------------+
| Sessions                              |
+---------------------------------------+
| ● Current Session (3 messages)        |
|   Started 10 minutes ago              |
|                                       |
| ○ Travel Planning (15 messages)       |
|   Started yesterday                   |
|                                       |
| ○ Work Project (8 messages)           |
|   Started 3 days ago                  |
|                                       |
| [+ New Session]                       |
+---------------------------------------+
```

### 4. Response Format Selector

**Purpose:** Allow users to choose different response formats for long-term queries

**Features:**
- Toggle between JSON, Markdown, and HTML formats
- Preview of current format
- Apply button to change format

**Example Wireframe:**
```
+---------------------------------------+
| Response Format                       |
+---------------------------------------+
| ○ JSON  ● Markdown  ○ HTML           |
|                                       |
| Preview:                              |
| # Summary of Topics                   |
| - Topic 1                             |
| - Topic 2                             |
|                                       |
+---------------------------------------+
```

### 5. Source Attribution Display

**Purpose:** Show the sources used to generate responses

**Features:**
- Collapsible section for sources
- Link to source content when available
- Metadata display (source type, date, etc.)
- Option to expand/collapse all sources

**Example Wireframe:**
```
+---------------------------------------+
| Sources (3)                           |
+---------------------------------------+
| ▼ Source 1: Geography Database        |
|   Last updated: 2023-01-15            |
|   "Paris is the capital and most      |
|   populous city of France..."         |
|                                       |
| ▶ Source 2: Travel Guide              |
|                                       |
| ▶ Source 3: Historical Records        |
|                                       |
+---------------------------------------+
```

## Advanced Components

### 1. Personality Creator/Editor

**Purpose:** Allow users to create or edit personality templates

**Features:**
- Form for all personality fields (name, role, etc.)
- Preview of generated system prompt
- Save/update functionality
- Import/export options

### 2. Conversation Analytics

**Purpose:** Provide insights into conversation patterns

**Features:**
- Message count by user/agent
- Response time metrics
- Topic frequency analysis
- Conversation length trends

### 3. Multi-Modal Input

**Purpose:** Support different input types beyond text

**Features:**
- File upload capability
- Image input support
- Voice input option
- Drawing/sketch input

## Integration Patterns

### 1. Sidebar Layout

```
+---------------------------------------+
|                                       |
| +-------------------+ +-------------+ |
| |                   | |             | |
| | Personality       | |             | |
| | Selector          | |             | |
| |                   | |             | |
| +-------------------+ |             | |
| |                   | |   Chat      | |
| | Session           | |   Interface | |
| | Manager           | |             | |
| |                   | |             | |
| +-------------------+ |             | |
| |                   | |             | |
| | Format            | |             | |
| | Selector          | |             | |
| |                   | |             | |
| +-------------------+ +-------------+ |
|                                       |
+---------------------------------------+
```

### 2. Modal Pattern

Use modals for less frequently accessed components:
- Personality creator/editor
- Source details
- Session details
- Settings

### 3. Responsive Considerations

- On mobile, sidebar components should collapse into a drawer
- Chat interface should take priority on smaller screens
- Consider simplified views for mobile devices
- Ensure touch-friendly UI elements 