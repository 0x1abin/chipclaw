"""
ChipClaw Filesystem Tools
"""
import os
from .base import Tool
from ...utils import ensure_dir, truncate_string


class ReadFileTool(Tool):
    """Read file contents"""
    
    name = "read_file"
    description = "Read contents of a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path to read"
            }
        },
        "required": ["path"]
    }
    
    def __init__(self, allowed_dir="/workspace"):
        self.allowed_dir = allowed_dir
    
    def execute(self, path):
        """Read file contents"""
        # Security check
        if not path.startswith(self.allowed_dir):
            return f"Error: Access denied. Files must be within {self.allowed_dir}"
        
        if not os.path.exists(path):
            return f"Error: File not found: {path}"
        
        try:
            with open(path, 'r') as f:
                content = f.read()
            # Truncate large files to save RAM
            return truncate_string(content, max_len=10240)  # 10KB limit
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFileTool(Tool):
    """Write file contents"""
    
    name = "write_file"
    description = "Write contents to a file (creates parent directories if needed)"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path to write"
            },
            "content": {
                "type": "string",
                "description": "Content to write"
            }
        },
        "required": ["path", "content"]
    }
    
    def __init__(self, allowed_dir="/workspace"):
        self.allowed_dir = allowed_dir
    
    def execute(self, path, content):
        """Write file contents"""
        # Security check
        if not path.startswith(self.allowed_dir):
            return f"Error: Access denied. Files must be within {self.allowed_dir}"
        
        try:
            # Create parent directory if needed
            parent = '/'.join(path.split('/')[:-1])
            if parent:
                ensure_dir(parent)
            
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {e}"


class ListDirTool(Tool):
    """List directory contents"""
    
    name = "list_dir"
    description = "List contents of a directory"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list (default: current directory)"
            }
        }
    }
    
    def __init__(self, allowed_dir="/workspace"):
        self.allowed_dir = allowed_dir
    
    def execute(self, path="."):
        """List directory contents"""
        # Convert relative path
        if path == ".":
            path = self.allowed_dir
        
        # Security check
        if not path.startswith(self.allowed_dir):
            return f"Error: Access denied. Path must be within {self.allowed_dir}"
        
        if not os.path.exists(path):
            return f"Error: Directory not found: {path}"
        
        try:
            entries = []
            for item in os.listdir(path):
                item_path = f"{path}/{item}"
                try:
                    stat = os.stat(item_path)
                    is_dir = stat[0] & 0x4000  # S_IFDIR
                    size = stat[6]
                    entries.append({
                        "name": item,
                        "type": "dir" if is_dir else "file",
                        "size": size
                    })
                except:
                    entries.append({"name": item, "type": "unknown", "size": 0})
            
            # Format output
            lines = [f"Contents of {path}:"]
            for entry in entries:
                type_marker = "/" if entry["type"] == "dir" else ""
                size_str = f" ({entry['size']} bytes)" if entry["type"] == "file" else ""
                lines.append(f"  {entry['name']}{type_marker}{size_str}")
            
            return '\n'.join(lines)
        except Exception as e:
            return f"Error listing directory: {e}"
