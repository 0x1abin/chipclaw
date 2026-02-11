"""
ChipClaw Context Builder
Assembles system prompt from bootstrap + memory + skills
"""
import os
from ..utils import format_runtime_info


class ContextBuilder:
    """Builds context for LLM from various sources"""
    
    def __init__(self, workspace, memory, skills):
        self.workspace = workspace
        self.memory = memory
        self.skills = skills
    
    def _load_bootstrap_file(self, filename):
        """Load a bootstrap markdown file from workspace"""
        path = f"{self.workspace}/{filename}"
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        return None
    
    def build_system_prompt(self, channel=None, chat_id=None):
        """
        Assemble system prompt from:
        1. Identity (ESP32-S3 runtime info)
        2. Bootstrap files (AGENTS.md, IDENTITY.md, etc.)
        3. Memory context
        4. Active skills
        5. Skills summary
        
        Args:
            channel: Current channel name (optional)
            chat_id: Current chat ID (optional)
        
        Returns:
            Formatted system prompt string
        """
        sections = []
        
        # 1. Runtime Identity
        runtime_info = format_runtime_info()
        identity_section = f"""# ChipClaw Agent

You are ChipClaw, an autonomous AI agent running on ESP32-S3 hardware.

## Runtime Environment
{runtime_info}

## Current Context
- Channel: {channel or 'unknown'}
- Chat ID: {chat_id or 'unknown'}
"""
        sections.append(identity_section)
        
        # 2. Bootstrap Files
        bootstrap_files = ['IDENTITY.md', 'AGENTS.md', 'SOUL.md', 'USER.md', 'TOOLS.md']
        for filename in bootstrap_files:
            content = self._load_bootstrap_file(filename)
            if content:
                sections.append(f"## {filename}\n{content}")
        
        # 3. Memory Context
        memory_context = self.memory.get_memory_context()
        if memory_context:
            sections.append(f"# Memory\n{memory_context}")
        
        # 4. Always-loaded Skills
        always_skills = self.skills.get_always_skills()
        if always_skills:
            sections.append("# Active Skills")
            for skill in always_skills:
                skill_name = skill['frontmatter'].get('name', skill['name'])
                sections.append(f"## Skill: {skill_name}\n{skill['content']}")
        
        # 5. Skills Summary
        skills_summary = self.skills.build_skills_summary()
        if skills_summary:
            sections.append(skills_summary)
        
        return '\n\n'.join(sections)
    
    def build_messages(self, history, current_message, channel=None, chat_id=None):
        """
        Build messages list for LLM API
        
        Args:
            history: List of previous message dicts from session
            current_message: Current user message string
            channel: Channel name
            chat_id: Chat ID
        
        Returns:
            List of message dicts in OpenAI format
        """
        messages = []
        
        # System prompt
        system_prompt = self.build_system_prompt(channel, chat_id)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add history
        for msg in history:
            messages.append(msg)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def add_assistant_message(self, messages, content, tool_calls=None):
        """
        Helper: Add assistant message to messages list
        
        Args:
            messages: Messages list to modify
            content: Assistant response content
            tool_calls: Optional tool calls data
        """
        msg = {
            "role": "assistant",
            "content": content
        }
        if tool_calls:
            msg["tool_calls"] = tool_calls
        messages.append(msg)
    
    def add_tool_result(self, messages, tool_call_id, result):
        """
        Helper: Add tool result message
        
        Args:
            messages: Messages list to modify
            tool_call_id: Tool call ID from LLM
            result: Tool execution result string
        """
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": str(result)
        })
