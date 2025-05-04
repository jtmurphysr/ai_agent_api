# AI Agent Webhook Integration Guide

This document explains how to integrate the AI Agent API with external systems using webhooks.

## Overview

While the AI Agent API doesn't directly provide webhook endpoints, you can implement webhook integration patterns to connect the agent with external systems like Slack, Discord, or custom applications.

## Implementation Patterns

### 1. Polling Pattern

For systems that don't support webhooks, implement a polling mechanism:

```javascript
// Set up a polling interval
const POLL_INTERVAL = 60000; // 1 minute

// Function to check for new messages
async function pollForNewMessages(lastMessageId) {
  const response = await fetch(`http://127.0.0.1:5001/sessions/${sessionId}/history`);
  const data = await response.json();
  
  // Filter for messages newer than lastMessageId
  const newMessages = data.messages.filter(msg => {
    return new Date(msg.timestamp) > new Date(lastMessageId);
  });
  
  if (newMessages.length > 0) {
    // Process new messages
    processNewMessages(newMessages);
    
    // Update lastMessageId
    lastMessageId = newMessages[newMessages.length - 1].timestamp;
  }
  
  // Continue polling
  setTimeout(() => pollForNewMessages(lastMessageId), POLL_INTERVAL);
}

// Start polling
let lastMessageId = new Date().toISOString();
pollForNewMessages(lastMessageId);
```

### 2. Proxy Server Pattern

Create a proxy server that handles both the AI Agent API and webhook delivery:

```javascript
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

// Store webhook subscribers
const subscribers = [];

// Register webhook endpoint
app.post('/register-webhook', (req, res) => {
  const { url, events } = req.body;
  subscribers.push({ url, events });
  res.json({ success: true, message: 'Webhook registered' });
});

// Proxy endpoint for AI Agent
app.post('/agent-query', async (req, res) => {
  try {
    // Forward request to AI Agent API
    const agentResponse = await axios.post('http://127.0.0.1:5001/query', req.body);
    
    // Send response back to client
    res.json(agentResponse.data);
    
    // Notify webhooks
    notifyWebhooks('query', {
      query: req.body.query,
      response: agentResponse.data.response,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Function to notify webhooks
function notifyWebhooks(event, data) {
  subscribers.forEach(sub => {
    if (sub.events.includes(event) || sub.events.includes('*')) {
      axios.post(sub.url, {
        event,
        data,
        timestamp: new Date().toISOString()
      }).catch(err => console.error(`Webhook delivery failed: ${err.message}`));
    }
  });
}

app.listen(3000, () => {
  console.log('Proxy server running on port 3000');
});
```

## Integration Examples

### Slack Integration

```javascript
const { WebClient } = require('@slack/web-api');
const express = require('express');
const app = express();
app.use(express.json());

// Initialize Slack client
const slack = new WebClient(process.env.SLACK_TOKEN);

// AI Agent client
const AIAgentClient = require('./ai_agent_client');
const agent = new AIAgentClient('http://127.0.0.1:5001');

// Map Slack channels to agent sessions
const channelSessions = {};

// Handle Slack events
app.post('/slack/events', async (req, res) => {
  // Verify Slack request (implementation omitted)
  
  const event = req.body.event;
  
  // Only process messages from users (not bots)
  if (event.type === 'message' && !event.bot_id) {
    const { channel, text, user } = event;
    
    try {
      let response;
      
      // Get or create session for this channel
      if (!channelSessions[channel]) {
        // Start a new conversation
        response = await agent.conversation(text);
        channelSessions[channel] = response.session_id;
      } else {
        // Continue existing conversation
        response = await agent.conversation(text, { 
          sessionId: channelSessions[channel] 
        });
      }
      
      // Send response back to Slack
      await slack.chat.postMessage({
        channel,
        text: response.response,
        thread_ts: event.thread_ts
      });
    } catch (error) {
      console.error('Error processing message:', error);
      
      // Send error message to Slack
      await slack.chat.postMessage({
        channel,
        text: "Sorry, I encountered an error processing your request.",
        thread_ts: event.thread_ts
      });
    }
  }
  
  res.sendStatus(200);
});

app.listen(3000, () => {
  console.log('Slack integration server running on port 3000');
});
```

### Discord Integration

```javascript
const { Client, GatewayIntentBits } = require('discord.js');
const AIAgentClient = require('./ai_agent_client');

// Initialize Discord client
const discord = new Client({ 
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// AI Agent client
const agent = new AIAgentClient('http://127.0.0.1:5001');

// Map Discord channels to agent sessions
const channelSessions = {};

discord.on('messageCreate', async message => {
  // Ignore messages from bots
  if (message.author.bot) return;
  
  // Check if message mentions the bot or is in a DM
  const isMentioned = message.mentions.has(discord.user.id);
  const isDM = message.channel.type === 'DM';
  
  if (isMentioned || isDM) {
    // Remove mention from message
    let content = message.content;
    if (isMentioned) {
      content = content.replace(`<@${discord.user.id}>`, '').trim();
    }
    
    // Show typing indicator
    message.channel.sendTyping();
    
    try {
      let response;
      
      // Get or create session for this channel
      if (!channelSessions[message.channel.id]) {
        response = await agent.conversation(content);
        channelSessions[message.channel.id] = response.session_id;
      } else {
        response = await agent.conversation(content, {
          sessionId: channelSessions[message.channel.id]
        });
      }
      
      // Send response back to Discord
      await message.reply(response.response);
    } catch (error) {
      console.error('Error processing message:', error);
      await message.reply("Sorry, I encountered an error processing your request.");
    }
  }
});

// Login to Discord
discord.login(process.env.DISCORD_TOKEN);
```

### Custom Web Application

```javascript
// Example using the AIAgentClient in a web application with webhook support

const AIAgentClient = require('./ai_agent_client');
const agent = new AIAgentClient('http://127.0.0.1:5001');

// Register a webhook for notifications
async function registerWebhook(webhookUrl) {
  // Using the proxy server pattern from above
  const response = await fetch('http://localhost:3000/register-webhook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: webhookUrl,
      events: ['query', 'conversation', 'personality_change']
    }),
  });
  
  return await response.json();
}

// Example webhook handler (server-side)
app.post('/webhook-receiver', (req, res) => {
  const { event, data } = req.body;
  
  console.log(`Received webhook event: ${event}`);
  
  switch (event) {
    case 'query':
      // Process query event
      notifyUser(data.response);
      break;
    case 'conversation':
      // Update conversation UI
      updateConversationHistory(data);
      break;
    case 'personality_change':
      // Update UI to reflect personality change
      updatePersonalityDisplay(data.personality_id);
      break;
  }
  
  res.sendStatus(200);
});
```

## Best Practices

### Security Considerations

1. **Authentication**: Always implement authentication for webhook endpoints
   ```javascript
   // Example webhook authentication middleware
   function validateWebhook(req, res, next) {
     const token = req.headers['x-webhook-token'];
     if (!token || token !== process.env.WEBHOOK_SECRET) {
       return res.status(401).json({ error: 'Unauthorized' });
     }
     next();
   }
   
   app.post('/webhook-receiver', validateWebhook, (req, res) => {
     // Process webhook
   });
   ```

2. **HTTPS**: Always use HTTPS for webhook communications
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Payload Validation**: Validate incoming webhook payloads

### Reliability

1. **Retry Logic**: Implement retry logic for failed webhook deliveries
   ```javascript
   async function sendWebhookWithRetry(url, data, maxRetries = 3) {
     let retries = 0;
     
     while (retries < maxRetries) {
       try {
         await axios.post(url, data);
         return true;
       } catch (error) {
         retries++;
         console.log(`Webhook delivery failed, retry ${retries}/${maxRetries}`);
         
         if (retries >= maxRetries) {
           console.error(`Max retries reached for webhook: ${url}`);
           return false;
         }
         
         // Exponential backoff
         await new Promise(r => setTimeout(r, 1000 * Math.pow(2, retries)));
       }
     }
   }
   ```

2. **Acknowledgements**: Implement acknowledgement mechanisms
3. **Logging**: Log all webhook activities for debugging

### Scalability

1. **Asynchronous Processing**: Process webhooks asynchronously
   ```javascript
   app.post('/agent-query', async (req, res) => {
     // Respond to client immediately
     res.json({ status: 'processing' });
     
     // Process in background
     processQueryAndNotifyWebhooks(req.body).catch(err => {
       console.error('Background processing error:', err);
     });
   });
   ```

2. **Queue System**: Use a message queue for high-volume webhook processing
3. **Batching**: Batch webhook notifications when appropriate

## Extending the API

To make webhook integration more native, consider extending the AI Agent API with these endpoints:

1. **Webhook Registration**
   ```
   POST /webhooks/register
   ```

2. **Webhook Management**
   ```
   GET /webhooks
   DELETE /webhooks/{webhook_id}
   ```

3. **Event Subscription**
   ```
   POST /webhooks/{webhook_id}/events
   ```

These extensions would make it easier to integrate the AI Agent with external systems without requiring a proxy server. 