"""
ChipClaw Tool Registry
"""


class ToolRegistry:
    """Manages tool registration and execution"""
    
    def __init__(self):
        self.tools = {}  # {name: Tool instance}
    
    def register(self, tool):
        """
        Register a tool instance
        
        Args:
            tool: Tool instance
        """
        if not tool.name:
            raise ValueError("Tool must have a name")
        self.tools[tool.name] = tool
    
    def get(self, name):
        """
        Get tool by name
        
        Args:
            name: Tool name
        
        Returns:
            Tool instance or None
        """
        return self.tools.get(name)
    
    def get_definitions(self):
        """
        Return list of tool schemas for LLM
        
        Returns:
            List of tool definition dicts
        """
        return [tool.to_schema() for tool in self.tools.values()]
    
    def execute(self, name, params):
        """
        Execute tool by name with params
        
        Args:
            name: Tool name
            params: Dict of parameters
        
        Returns:
            Tool result (string or object)
        """
        tool = self.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        
        try:
            return tool.execute(**params)
        except Exception as e:
            import sys
            # Get traceback info
            exc_type, exc_value, exc_tb = sys.exc_info()
            return f"Error executing tool '{name}': {exc_type.__name__}: {exc_value}"
