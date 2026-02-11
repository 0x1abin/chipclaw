"""
ChipClaw Memory System
Manages long-term memory (MEMORY.md) and daily notes (YYYY-MM-DD.md)
"""
import os
from ..utils import ensure_dir, today_date, file_exists


class MemoryStore:
    """Memory management system mirroring nanobot's workspace/memory/ structure"""
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.memory_dir = workspace + "/memory"
        ensure_dir(self.memory_dir)
    
    def read_long_term(self):
        """
        Read long-term memory from MEMORY.md
        
        Returns:
            String content or empty string if file doesn't exist
        """
        path = self.memory_dir + "/MEMORY.md"
        if file_exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading long-term memory: {e}")
                return ""
        return ""
    
    def write_long_term(self, content):
        """
        Write long-term memory to MEMORY.md
        
        Args:
            content: String content to write
        """
        path = self.memory_dir + "/MEMORY.md"
        try:
            with open(path, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing long-term memory: {e}")
    
    def read_today(self):
        """
        Read today's daily note (YYYY-MM-DD.md)
        
        Returns:
            String content or empty string if file doesn't exist
        """
        date = today_date()
        path = f"{self.memory_dir}/{date}.md"
        if file_exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading daily note: {e}")
                return ""
        return ""
    
    def append_today(self, content):
        """
        Append to today's daily note (YYYY-MM-DD.md)
        
        Args:
            content: String content to append
        """
        date = today_date()
        path = f"{self.memory_dir}/{date}.md"
        try:
            with open(path, 'a') as f:
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
        except Exception as e:
            print(f"Error appending to daily note: {e}")
    
    def get_recent_memories(self, days=3):
        """
        Get recent daily notes (last N days)
        Reduced from 7 days in nanobot to save RAM on ESP32
        
        Args:
            days: Number of recent days to retrieve
        
        Returns:
            List of (date, content) tuples
        """
        import time
        
        memories = []
        current_time = time.time()
        
        # Check each of the last N days
        for i in range(days):
            # Calculate date for (today - i days)
            target_time = current_time - (i * 86400)  # 86400 seconds = 1 day
            t = time.localtime(target_time)
            date = f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
            
            path = f"{self.memory_dir}/{date}.md"
            if file_exists(path):
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    if content.strip():
                        memories.append((date, content))
                except Exception as e:
                    print(f"Error reading {date}.md: {e}")
        
        return memories
    
    def get_memory_context(self):
        """
        Format memory for inclusion in system prompt
        
        Returns:
            Formatted string with long-term and recent memories
        """
        sections = []
        
        # Long-term memory
        long_term = self.read_long_term()
        if long_term.strip():
            sections.append("## Long-Term Memory\n" + long_term)
        
        # Recent daily notes
        recent = self.get_recent_memories()
        if recent:
            sections.append("## Recent Daily Notes")
            for date, content in recent:
                sections.append(f"### {date}\n{content}")
        
        if sections:
            return "\n\n".join(sections)
        else:
            return "No memory records yet."
