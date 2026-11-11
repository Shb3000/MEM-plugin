"""
Tool tracer for MEM-Plugin.
Captures and stores tool execution traces.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable


class ToolTracer:
    """Capture and store tool execution traces."""
    
    def __init__(self, memory_api):
        self.memory_api = memory_api
    
    def trace(self, tool_name: str, tool_type: str, 
              inputs: Dict, outputs: Optional[Dict] = None,
              errors: Optional[List] = None) -> str:
        """
        Trace a tool execution and store it in memory.
        
        Args:
            tool_name: Name of the tool
            tool_type: Type of tool (command, api, file, etc.)
            inputs: Input parameters
            outputs: Output results
            errors: Any error messages
            
        Returns:
            Node ID for the trace
        """
        trace_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        trace_content = f"""
Tool: {tool_name}
Type: {tool_type}
Timestamp: {created_at}

Inputs:
{json.dumps(inputs, indent=2)}
"""
        
        if outputs:
            trace_content += f"""

Outputs:
{json.dumps(outputs, indent=2)}
"""
        
        if errors:
            trace_content += f"""

Errors:
{json.dumps(errors, indent=2)}
"""
        
        # Create tool trace node
        node_id = self.memory_api.add(
            content=trace_content,
            node_type="tool_trace",
            metadata={
                "tool_name": tool_name,
                "tool_type": tool_type,
                "inputs": inputs,
                "outputs": outputs,
                "errors": errors,
                "trace_id": trace_id
            }
        )
        
        # Create reference to inputs if they exist
        for input_key, input_value in inputs.items():
            if isinstance(input_value, str):
                self.memory_api.add(
                    content=f"Tool input: {input_key}",
                    node_type="text",
                    metadata={"input_key": input_key}
                )
        
        return node_id
    
    def list_traces(self, tool_name: Optional[str] = None) -> List[str]:
        """List all tool trace node IDs."""
        traces = self.memory_api.retrieve_all(node_type="tool_trace")
        if tool_name:
            traces = [t for t in traces if t.get("metadata", {}).get("tool_name") == tool_name]
        return [t["id"] for t in traces]
    
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        """Get a tool trace by ID."""
        trace_node = self.memory_api.retrieve(trace_id)
        if trace_node:
            return {
                "id": trace_node["id"],
                "tool_name": trace_node.get("metadata", {}).get("tool_name"),
                "tool_type": trace_node.get("metadata", {}).get("tool_type"),
                "inputs": trace_node.get("metadata", {}).get("inputs"),
                "outputs": trace_node.get("metadata", {}).get("outputs"),
                "errors": trace_node.get("metadata", {}).get("errors")
            }
