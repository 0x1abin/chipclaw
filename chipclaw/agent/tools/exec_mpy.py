"""
ChipClaw Self-Programming Tool
Execute MicroPython code via exec()
"""
import sys
import io
from .base import Tool


class ExecMicroPythonTool(Tool):
    """Execute MicroPython code with stdout capture"""
    
    name = "exec_micropython"
    description = "Execute MicroPython code and return output. Use for hardware control, automation, and self-programming. For complex logic, create a .py file with write_file and import it here."
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "MicroPython code to execute"
            }
        },
        "required": ["code"]
    }
    
    def __init__(self, workspace="/workspace"):
        self.workspace = workspace
    
    def execute(self, code):
        """Execute code and capture output"""
        import gc
        
        # Collect garbage before execution
        gc.collect()
        
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            # Provide workspace path in scope
            scope = {
                '__workspace__': self.workspace,
                '__name__': '__exec__'
            }
            
            # Execute code
            exec(code, scope)
            
            # Get output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Collect garbage after execution
            gc.collect()
            
            if output:
                return output
            else:
                return "Code executed successfully (no output)"
        
        except Exception as e:
            sys.stdout = old_stdout
            import sys
            exc_type, exc_value, exc_tb = sys.exc_info()
            
            # Format traceback
            import traceback
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
            error_msg = ''.join(tb_lines)
            
            gc.collect()
            return f"Error executing code:\n{error_msg}"
