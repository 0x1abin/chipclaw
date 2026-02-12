"""
ChipClaw Agent Loop
Main agent processing loop
"""
import gc

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from .memory import MemoryStore
from .skills import SkillsManager
from .context import ContextBuilder
from .tools.registry import ToolRegistry
from .tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from .tools.hardware import GPIOTool, I2CScanTool
from .tools.exec_mpy import ExecMicroPythonTool
from .tools.http_fetch import HTTPFetchTool
from .tools.curl import CurlTool
from .tools.message import MessageTool


class AgentLoop:
    """Main agent loop: process inbound messages"""
    
    def __init__(self, bus, provider, sessions, config):
        self.bus = bus
        self.provider = provider
        self.sessions = sessions
        self.config = config
        
        # Initialize components
        workspace = config.workspace
        self.memory = MemoryStore(workspace)
        self.skills = SkillsManager(workspace)
        self.context = ContextBuilder(workspace, self.memory, self.skills)
        
        # Initialize tools
        self.tools = ToolRegistry()
        self._register_tools()
        
        # Agent configuration
        self.max_tool_iterations = config.get("agent", "max_tool_iterations", default=15)
        self.model = config.get("agent", "model", default="gpt-4")
        self.max_tokens = config.get("agent", "max_tokens", default=4096)
        self.temperature = config.get("agent", "temperature", default=0.7)
    
    def _register_tools(self):
        """Register all available tools"""
        workspace = self.config.workspace
        
        # Filesystem tools
        restrict = self.config.get("hardware", "restrict_to_workspace", default=True)
        allowed_dir = workspace if restrict else "/"
        
        self.tools.register(ReadFileTool(allowed_dir=allowed_dir))
        self.tools.register(WriteFileTool(allowed_dir=allowed_dir))
        self.tools.register(ListDirTool(allowed_dir=allowed_dir))
        
        # Hardware tools
        self.tools.register(GPIOTool())
        self.tools.register(I2CScanTool())
        
        # Self-programming
        self.tools.register(ExecMicroPythonTool(workspace=workspace))
        
        # HTTP
        self.tools.register(HTTPFetchTool())
        self.tools.register(CurlTool())
        
        # Message tool
        self.tools.register(MessageTool(self.bus))
    
    async def run(self):
        """Main loop: process inbound messages"""
        print("Agent loop started")
        
        while True:
            try:
                # Consume inbound message (blocking)
                msg = await self.bus.consume_inbound()
                print(f"Processing: {msg}")
                
                # Handle message
                await self._handle_message(msg)
                
                # Collect garbage between messages
                gc.collect()
            
            except Exception as e:
                print(f"Error in agent loop: {e}")
                import sys
                sys.print_exception(e)
    
    async def _handle_message(self, msg):
        """Process one message and generate response"""
        try:
            # Get or create session
            session = self.sessions.get_or_create(msg.session_key)
            
            # Build messages for LLM
            max_history = self.config.get("agent", "max_session_messages", default=20)
            history = session.get_history(max=max_history)
            messages = self.context.build_messages(
                history,
                msg.content,
                channel=msg.channel,
                chat_id=msg.chat_id
            )
            
            # Set context for message tool
            message_tool = self.tools.get("send_message")
            if message_tool:
                message_tool.set_context(msg.channel, msg.chat_id)
            
            # Tool execution loop
            tool_iterations = 0
            while tool_iterations < self.max_tool_iterations:
                # Call LLM
                print(f"Calling LLM (iteration {tool_iterations + 1})...")
                response = await self.provider.chat(
                    messages=messages,
                    tools=self.tools.get_definitions(),
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                # Check if we have tool calls
                if response.has_tool_calls:
                    print(f"Got {len(response.tool_calls)} tool calls")
                    
                    # Add assistant message with tool calls
                    assistant_msg = {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": []
                    }
                    for tc in response.tool_calls:
                        assistant_msg["tool_calls"].append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": str(tc.arguments)
                            }
                        })
                    messages.append(assistant_msg)
                    
                    # Execute tools
                    for tc in response.tool_calls:
                        print(f"Executing tool: {tc.name}({tc.arguments})")
                        result = self.tools.execute(tc.name, tc.arguments)
                        print(f"Tool result: {result}")
                        
                        # Add tool result to messages
                        self.context.add_tool_result(messages, tc.id, result)
                    
                    tool_iterations += 1
                    gc.collect()
                else:
                    # No more tool calls, we have final response
                    break
            
            # Get final response content
            final_content = response.content or "I completed the requested actions."
            
            # Save to session
            session.add_message("user", msg.content)
            session.add_message("assistant", final_content)
            self.sessions.save(session)
            
            # Send response via bus
            from ..bus.events import OutboundMessage
            reply = OutboundMessage(
                channel=msg.channel,
                chat_id=msg.chat_id,
                content=final_content,
                reply_to=msg
            )
            await self.bus.publish_outbound(reply)
            
            print(f"Response sent: {final_content[:100]}...")
        
        except Exception as e:
            print(f"Error handling message: {e}")
            import sys
            sys.print_exception(e)
            
            # Send error message
            from ..bus.events import OutboundMessage
            error_reply = OutboundMessage(
                channel=msg.channel,
                chat_id=msg.chat_id,
                content=f"Error processing message: {e}"
            )
            await self.bus.publish_outbound(error_reply)
