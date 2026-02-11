"""
ChipClaw Session Manager
Manages conversation sessions with JSONL storage
"""
import os
import json
from ..utils import ensure_dir, safe_filename


class Session:
    """Conversation session with message history"""
    
    def __init__(self, key):
        self.key = key          # "channel:chat_id"
        self.messages = []      # List of message dicts
    
    def add_message(self, role, content, **kwargs):
        """
        Add message to history
        
        Args:
            role: "user" | "assistant" | "system" | "tool"
            content: Message content
            **kwargs: Additional fields (e.g., tool_calls, tool_call_id)
        """
        msg = {
            "role": role,
            "content": content
        }
        msg.update(kwargs)
        self.messages.append(msg)
    
    def get_history(self, max=20):
        """
        Get last N messages
        
        Args:
            max: Maximum messages to return
        
        Returns:
            List of message dicts
        """
        return self.messages[-max:] if len(self.messages) > max else self.messages
    
    def clear(self):
        """Clear all messages"""
        self.messages = []


class SessionManager:
    """Manages sessions with JSONL file storage"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.sessions_dir = f"{data_dir}/sessions"
        ensure_dir(self.sessions_dir)
        self.sessions = {}  # {key: Session}
    
    def get_or_create(self, key):
        """
        Get existing session or create new one
        
        Args:
            key: Session key (e.g., "mqtt:chat123")
        
        Returns:
            Session instance
        """
        if key not in self.sessions:
            self.sessions[key] = self._load(key)
        return self.sessions[key]
    
    def save(self, session):
        """
        Save session to JSONL file
        
        Args:
            session: Session instance
        """
        path = f"{self.sessions_dir}/{safe_filename(session.key)}.jsonl"
        try:
            with open(path, 'w') as f:
                for msg in session.messages:
                    f.write(json.dumps(msg) + '\n')
        except Exception as e:
            print(f"Error saving session {session.key}: {e}")
    
    def _load(self, key):
        """
        Load session from JSONL file
        
        Args:
            key: Session key
        
        Returns:
            Session instance (new or loaded)
        """
        session = Session(key)
        path = f"{self.sessions_dir}/{safe_filename(key)}.jsonl"
        
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            msg = json.loads(line)
                            session.messages.append(msg)
                print(f"Loaded session {key} with {len(session.messages)} messages")
            except Exception as e:
                print(f"Error loading session {key}: {e}")
        
        return session
    
    def delete(self, key):
        """
        Delete session
        
        Args:
            key: Session key
        """
        if key in self.sessions:
            del self.sessions[key]
        
        path = f"{self.sessions_dir}/{safe_filename(key)}.jsonl"
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting session file {key}: {e}")
