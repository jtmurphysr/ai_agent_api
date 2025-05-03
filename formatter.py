# response_formatter.py
from typing import List, Dict, Optional

def format_conversation_summary(response: Dict, session_id: Optional[str] = None) -> str:
    """
    Formats the response dictionary into a markdown-formatted string.

    Parameters:
        response (Dict): Raw response from the vectorstore and LLM.
        session_id (str, optional): Unique identifier for the conversation session.

    Returns:
        str: Markdown-formatted summary.
    """
    markdown = "# 📚 **Summary of Your Frequent Conversation Topics**\n\n"
    markdown += "Based on our past conversations, here's a categorized overview of topics you frequently discuss:\n\n"

    markdown += response['response'] + "\n\n"

    if response.get('sources'):
        markdown += "---\n\n## 🗃️ **Sources Referenced:**\n"
        for source in response['sources']:
            metadata = source.get('metadata', {})
            title = metadata.get('conversation_title', 'Unknown')
            cid = metadata.get('conversation_id', 'Unknown')
            markdown += f"- **{title}** (`conversation_id`: {int(cid)})\n"

    if session_id:
        markdown += f"\n---\n_Session ID: `{session_id}`_\n"

    markdown += "\n---\n"
    markdown += "_This summary aligns with your typical strategic, pragmatic, and analytical communication style._"

    return markdown