"""
Personality Manager for AI Agent API

Handles loading, validating, and applying personality templates to the AI agent.
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

class PersonalityManager:
    """Manages agent personalities and prompts."""
    
    def __init__(self, personalities_dir: str = "personalities"):
        """Initialize the personality manager.
        
        Args:
            personalities_dir: Directory where personality files are stored
        """
        self.personalities_dir = personalities_dir
        self.personalities = {}
        self.default_personality = None
        self._ensure_dir_exists()
        self._load_personalities()
    
    def _ensure_dir_exists(self):
        """Ensure the personalities directory exists."""
        os.makedirs(self.personalities_dir, exist_ok=True)
    
    def _load_personalities(self):
        """Load all personality files from the personalities directory."""
        for file_path in Path(self.personalities_dir).glob("*.*"):
            if file_path.suffix in ['.json', '.fil', '.txt', '.md']:
                try:
                    personality_id = file_path.stem
                    self.personalities[personality_id] = self._load_personality_file(file_path)
                    
                    # Set the first personality as default
                    if self.default_personality is None:
                        self.default_personality = personality_id
                except Exception as e:
                    print(f"Error loading personality {file_path}: {str(e)}")
    
    def _load_personality_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a personality from a file.
        
        Args:
            file_path: Path to the personality file
            
        Returns:
            Dictionary containing the personality data
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
            # If it's a JSON file, parse it
            if file_path.suffix == '.json':
                try:
                    return {
                        'type': 'template',
                        'data': json.loads(content),
                        'path': str(file_path)
                    }
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON in personality file: {file_path}")
            
            # Otherwise, treat it as a raw prompt
            return {
                'type': 'prompt',
                'data': content,
                'path': str(file_path)
            }
    
    def get_personality(self, personality_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a personality by ID.
        
        Args:
            personality_id: ID of the personality to get, or None for default
            
        Returns:
            Dictionary containing the personality data
            
        Raises:
            ValueError: If the personality ID doesn't exist
        """
        if personality_id is None:
            personality_id = self.default_personality
            
        if personality_id not in self.personalities:
            raise ValueError(f"Personality not found: {personality_id}")
            
        return self.personalities[personality_id]
    
    def list_personalities(self) -> Dict[str, Dict[str, Any]]:
        """List all available personalities.
        
        Returns:
            Dictionary of personality IDs to metadata
        """
        result = {}
        for personality_id, personality in self.personalities.items():
            if personality['type'] == 'template':
                # For JSON templates, extract name and role
                data = personality['data']
                result[personality_id] = {
                    'type': 'template',
                    'name': data.get('name', personality_id),
                    'role': data.get('role', 'Assistant'),
                    'path': personality['path']
                }
            else:
                # For raw prompts, just use the ID as name
                result[personality_id] = {
                    'type': 'prompt',
                    'name': personality_id,
                    'role': 'Custom Agent',
                    'path': personality['path']
                }
        
        return result
    
    def create_system_prompt(self, personality_id: Optional[str] = None) -> str:
        """Create a system prompt from a personality.
        
        Args:
            personality_id: ID of the personality to use, or None for default
            
        Returns:
            System prompt string for the LLM
        """
        personality = self.get_personality(personality_id)
        
        if personality['type'] == 'prompt':
            # For raw prompts, just return the content
            return personality['data']
        
        # For JSON templates, format it into a system prompt
        data = personality['data']
        prompt = f"You are {data['name']}, {data['role']}.\n\n"
        prompt += f"{data['core_identity']}\n\n"
        
        # Add communication style
        comm_style = data.get('communication_style', {})
        prompt += "Communication style:\n"
        for key, value in comm_style.items():
            prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        prompt += "\n"
        
        # Add anchor phrases if present
        if 'anchor_phrases' in data and data['anchor_phrases']:
            prompt += "Use these anchor phrases in your responses:\n"
            for phrase in data['anchor_phrases']:
                prompt += f"- \"{phrase}\"\n"
            prompt += "\n"
        
        # Add behavioral guidelines
        if 'behavioral_guidelines' in data:
            prompt += "Guidelines for your responses:\n"
            for key, value in data['behavioral_guidelines'].items():
                prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
            prompt += "\n"
        
        # Add example responses if present
        if 'example_responses' in data and data['example_responses']:
            prompt += "Examples of your typical responses:\n"
            for example in data['example_responses']:
                prompt += f"- \"{example}\"\n"
            prompt += "\n"
        
        return prompt
    
    def add_personality(self, file_path: str) -> str:
        """Add a new personality from a file.
        
        Args:
            file_path: Path to the personality file
            
        Returns:
            ID of the added personality
            
        Raises:
            ValueError: If the file doesn't exist or is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")
            
        # Copy the file to the personalities directory
        personality_id = path.stem
        target_path = Path(self.personalities_dir) / path.name
        
        # Read the source file
        with open(path, 'r') as src:
            content = src.read()
            
        # Write to the target location
        with open(target_path, 'w') as dst:
            dst.write(content)
            
        # Load the personality
        self.personalities[personality_id] = self._load_personality_file(target_path)
        
        return personality_id 