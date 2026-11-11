"""
Unified Memory API: Single interface to add, retrieve, edit, and delete memory.
Structured as a graph, inspectable and editable by design.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from .memory_graph import MemoryGraph
from .memory_store import MemoryStore


class MemoryType(Enum):
    TEXT = "text"
    IMAGE = "image"
    TOOL_TRACE = "tool_trace"
    PERSONA = "persona"


class MemoryAPI:
    """Unified API for memory operations with graph structure."""
    
    def __init__(self, data_dir: str = "mem_plugin_data"):
        self.graph = MemoryGraph()
        self.store = MemoryStore(data_dir)
        self.version = 1
    
    def add(self, content: str, node_type: str = "text",
            metadata: Optional[Dict] = None, relationships: Optional[List[Dict]] = None,
            **kwargs) -> str:
        """
        Add new memory content to the graph.
        
        Args:
            content: The memory content to store
            node_type: Type of memory (text, image, tool_trace, persona)
            metadata: Optional metadata dict
            relationships: Optional relationships to existing nodes
            **kwargs: Additional parameters
            
        Returns:
            Node ID for the added memory
        """
        node_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Auto-create target nodes if relationships reference them
        if relationships:
            for rel in relationships:
                if rel.get("type") == "references":
                    target_id = rel.get("target_id")
                    if target_id and target_id not in self.graph.nodes:
                        self.graph.nodes[target_id] = {
                            "id": target_id,
                            "type": rel.get("target_type", "text"),
                            "content": rel.get("target_content", ""),
                            "created_at": created_at,
                            "updated_at": created_at,
                            "metadata": rel.get("target_metadata", {}),
                            "relationships": []
                        }
        
        node_data = {
            "id": node_id,
            "type": str(node_type),
            "content": content,
            "created_at": created_at,
            "updated_at": created_at,
            "metadata": metadata or {},
            "relationships": relationships or []
        }
        
        node_id = self.graph.add_node(node_id, content, str(node_type), metadata, relationships)
        self.store.save_nodes(self.graph.nodes)
        self.store.save_edges(self.graph.edges)
        
        return node_id
    
    def retrieve(self, node_id: str) -> Optional[Dict]:
        """Retrieve a memory node by ID."""
        return self.graph.retrieve(node_id)
    
    def retrieve_all(self, node_type: Optional[str] = None) -> List[Dict]:
        """Retrieve all memories, optionally filtered by type."""
        if node_type:
            return self.graph.retrieve_by_type(node_type)
        return list(self.graph.nodes.values())
    
    def search(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        """Search memories by content."""
        return self.graph.search(query, node_type)
    
    def edit(self, node_id: str, content: str, **kwargs) -> bool:
        """Edit an existing memory node."""
        if node_id in self.graph.nodes:
            node = self.graph.nodes[node_id]
            node["content"] = content
            node["updated_at"] = datetime.utcnow().isoformat() + "Z"
            self.store.save_nodes(self.graph.nodes)
            self.store.save_edges(self.graph.edges)
            return True
        return False
    
    def delete(self, node_id: str) -> bool:
        """Delete a memory node and its edges."""
        if node_id in self.graph.nodes:
            del self.graph.nodes[node_id]
            # Remove edges pointing to this node
            self.graph.edges = {
                eid: targets 
                for eid, targets in self.graph.edges.items() 
                if node_id not in targets
            }
            self.store.save_nodes(self.graph.nodes)
            self.store.save_edges(self.graph.edges)
            return True
        return False
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """Get connected nodes."""
        return self.graph.get_neighbors(node_id, relationship_type)
    
    def to_graphql(self) -> Dict:
        """Export graph in GraphQL-like format."""
        return self.graph.to_graphql()
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        node_types = {}
        for node in self.graph.nodes.values():
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        return {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "node_types": node_types,
            "data_path": self.store.get_memory_path()
        }
    
    def export(self, format: str = "json") -> str:
        """Export entire memory system."""
        if format == "json":
            return json.dumps(self.graph.to_graphql(), indent=2, ensure_ascii=False)
        return "Not implemented"
