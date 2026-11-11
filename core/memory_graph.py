"""
Memory graph module for MEM-Plugin.
Graph-based memory structure with node and edge relationships.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


class MemoryGraph:
    """Graph-based memory structure with node and edge relationships."""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: Dict[str, List[str]] = {}
        self.node_types: Dict[str, str] = {}
    
    def add_node(self, node_id: str, content: str, node_type: str, 
                 metadata: Optional[Dict] = None, relationships: Optional[List[Dict]] = None) -> str:
        """Add a new memory node to the graph."""
        if node_id and node_id not in self.nodes:
            node_data = {
                "id": node_id,
                "type": node_type,
                "content": content,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "metadata": metadata or {},
                "relationships": relationships or []
            }
            self.nodes[node_id] = node_data
            self.node_types[node_id] = node_type
            
            # Auto-create edges if relationships specified
            if relationships:
                for rel in relationships:
                    if rel.get("type") == "references":
                        target_id = rel.get("target_id")
                        if target_id and target_id not in self.nodes:
                            self.nodes[target_id] = {
                                "id": target_id,
                                "type": rel.get("target_type", "text"),
                                "content": rel.get("target_content", ""),
                                "created_at": datetime.utcnow().isoformat() + "Z",
                                "updated_at": datetime.utcnow().isoformat() + "Z",
                                "metadata": rel.get("target_metadata", {}),
                                "relationships": []
                            }
                            self.node_types[target_id] = rel.get("target_type", "text")
            
            return node_id
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, relationship_type: str = "references") -> str:
        """Add an edge between two nodes."""
        edge_id = str(uuid.uuid4())
        
        # Create source node if it doesn't exist
        if source_id and source_id not in self.nodes:
            self.nodes[source_id] = {
                "id": source_id,
                "type": "text",
                "content": "",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "metadata": {},
                "relationships": []
            }
            self.node_types[source_id] = "text"
        
        # Create target node if it doesn't exist
        if target_id and target_id not in self.nodes:
            self.nodes[target_id] = {
                "id": target_id,
                "type": "text",
                "content": "",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "metadata": {},
                "relationships": []
            }
            self.node_types[target_id] = "text"
        
        if source_id in self.edges:
            if target_id not in self.edges[source_id]:
                self.edges[source_id].append(target_id)
        else:
            self.edges[source_id] = [target_id]
        
        edge_data = {
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        if edge_id not in self.edges:
            self.edges[edge_id] = []
        self.edges[edge_id].append(target_id)
        
        return edge_id
    
    def retrieve(self, node_id: str) -> Optional[Dict]:
        """Retrieve a node by ID."""
        return self.nodes.get(node_id)
    
    def retrieve_by_type(self, node_type: str) -> List[Dict]:
        """Retrieve all nodes of a specific type."""
        return [node for node_id, node in self.nodes.items() if node["type"] == node_type]
    
    def search(self, query: str, node_type: Optional[str] = None) -> List[Dict]:
        """Search nodes by content query."""
        results = []
        for node_id, node in self.nodes.items():
            if node_type and node["type"] != node_type:
                continue
            if query.lower() in node["content"].lower():
                results.append(node)
        return results
    
    def get_neighbors(self, node_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """Get neighbor node IDs."""
        neighbors = []
        if node_id in self.edges:
            neighbors.extend(self.edges[node_id])
        return neighbors
    
    def to_graphql(self) -> Dict:
        """Convert graph to GraphQL-like structure for queries."""
        return {
            "nodes": [self.nodes[nid] for nid in self.nodes],
            "edges": [
                {
                    "id": eid,
                    "source": self.nodes.get(self.edges[eid][0], {}).get("id"),
                    "target": self.nodes.get(self.edges[eid][1], {}).get("id"),
                    "type": self.edges[eid][0] in self.edges.get(eid, [""], [""])[0] or ""
                } for eid in self.edges
            ]
        }
