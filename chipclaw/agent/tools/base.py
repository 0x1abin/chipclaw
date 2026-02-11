"""
ChipClaw Tool Base Class
"""


class Tool:
    """
    Base class for tools
    Not using ABC for MicroPython compatibility
    """
    
    # Override these in subclass
    name = None
    description = None
    parameters = {}  # JSON Schema dict
    
    def execute(self, **params):
        """
        Execute the tool with given parameters
        Override in subclass
        
        Args:
            **params: Tool parameters
        
        Returns:
            Result string or object
        """
        raise NotImplementedError("Subclass must implement execute()")
    
    def to_schema(self):
        """
        Return OpenAI function calling schema
        
        Returns:
            Dict in OpenAI tools format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
