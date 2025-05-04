/**
 * AI Agent API Client
 * A simple client library for interacting with the AI Agent API
 */
class AIAgentClient {
  /**
   * Create a new AI Agent client
   * @param {string} baseUrl - The base URL of the API
   */
  constructor(baseUrl = 'http://127.0.0.1:5001') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.currentPersonality = null;
  }

  /**
   * Send a stateless query to the AI agent
   * @param {string} query - The question to ask
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} - The response from the AI agent
   */
  async query(query, options = {}) {
    const { maxResults = 3, personalityId = this.currentPersonality } = options;
    
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_results: maxResults,
        personality_id: personalityId
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    return await response.json();
  }

  /**
   * Send a message in a conversation with history
   * @param {string} query - The message to send
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} - The response from the AI agent
   */
  async conversation(query, options = {}) {
    const { 
      maxResults = 3, 
      personalityId = this.currentPersonality,
      sessionId = this.sessionId
    } = options;
    
    const url = new URL(`${this.baseUrl}/conversation`);
    if (sessionId) {
      url.searchParams.append('session_id', sessionId);
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_results: maxResults,
        personality_id: personalityId
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    const data = await response.json();
    
    // Store the session ID for future requests
    if (data.session_id) {
      this.sessionId = data.session_id;
    }
    
    return data;
  }

  /**
   * Send a query that uses long-term memory
   * @param {string} query - The question to ask
   * @param {Object} options - Additional options
   * @returns {Promise<Object|string>} - The response from the AI agent
   */
  async longTermQuery(query, options = {}) {
    const { 
      maxResults = 5, 
      personalityId = this.currentPersonality,
      sessionId = this.sessionId,
      format = 'json'
    } = options;
    
    const url = new URL(`${this.baseUrl}/long_term_query`);
    url.searchParams.append('format', format);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_results: maxResults,
        personality_id: personalityId,
        session_id: sessionId
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    // Handle different response formats
    if (format === 'json') {
      return await response.json();
    } else {
      return await response.text();
    }
  }

  /**
   * Get the conversation history for a session
   * @param {string} sessionId - The session ID
   * @returns {Promise<Object>} - The conversation history
   */
  async getSessionHistory(sessionId = this.sessionId) {
    if (!sessionId) {
      throw new Error('No session ID provided');
    }
    
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/history`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    return await response.json();
  }

  /**
   * Get a list of available personalities
   * @returns {Promise<Array>} - List of personalities
   */
  async getPersonalities() {
    const response = await fetch(`${this.baseUrl}/personalities`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    return await response.json();
  }

  /**
   * Set the current personality for future requests
   * @param {string} personalityId - The personality ID to use
   */
  setPersonality(personalityId) {
    this.currentPersonality = personalityId;
  }

  /**
   * Upload a new personality file
   * @param {File} file - The personality file to upload
   * @param {string} name - Optional name for the personality
   * @returns {Promise<Object>} - The upload result
   */
  async uploadPersonality(file, name = null) {
    const formData = new FormData();
    formData.append('file', file);
    
    if (name) {
      formData.append('name', name);
    }
    
    const response = await fetch(`${this.baseUrl}/personalities/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    return await response.json();
  }

  /**
   * Get the system prompt for a personality
   * @param {string} personalityId - The personality ID
   * @returns {Promise<string>} - The system prompt
   */
  async getPersonalityPrompt(personalityId) {
    const response = await fetch(`${this.baseUrl}/personalities/${personalityId}/prompt`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Unknown error');
    }
    
    return await response.text();
  }

  /**
   * Check the health of the API
   * @returns {Promise<Object>} - Health status
   */
  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    
    return await response.json();
  }
}

// Export for use in browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AIAgentClient;
} else {
  window.AIAgentClient = AIAgentClient;
} 