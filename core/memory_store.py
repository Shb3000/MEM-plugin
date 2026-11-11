"""
Local memory storage backend for MEM-Plugin.
Uses JSON files with SQLite for graph indexing.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

class MemoryStore:
    """Local storage backend with file-based persistence."""
    
    def __init__(self, data_dir: str = "mem_plugin_data"):
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File paths
        self.nodes_file = os.path.join(self.data_dir, "nodes.json")
        self.edges_file = os.path.join(self.data_dir, "edges.json")
        self.index_file = os.path.join(self.data_dir, "index.db")
        
        # Initialize database if not exists
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for indexing."""
        conn = sqlite3.connect(self.index_file)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            content TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            target_id TEXT,
            relationship_type TEXT,
            created_at TEXT,
            FOREIGN KEY (source_id) REFERENCES nodes(id),
            FOREIGN KEY (target_id) REFERENCES nodes(id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def save_nodes(self, nodes: Dict[str, Dict]):
        """Save nodes to JSON file."""
        with open(self.nodes_file, 'w', encoding='utf-8') as f:
            json.dump(nodes, f, ensure_ascii=False, indent=2)
    
    def save_edges(self, edges: Dict[str, List[str]]):
        """Save edges to JSON file."""
        with open(self.edges_file, 'w', encoding='utf-8') as f:
            json.dump(edges, f, ensure_ascii=False, indent=2)
    
    def save_to_db(self, node_id: str, node_data: Dict, edge_id: str = None):
        """Save node and edge to SQLite database."""
        conn = sqlite3.connect(self.index_file)
        cursor = conn.cursor()
        
        node_data_json = json.dumps(node_data, ensure_ascii=False)
        
        cursor.execute("""
        INSERT OR REPLACE INTO nodes (id, type, content, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, node_data.get('type', ''), node_data.get('content', ''),
           node_data.get('created_at', ''), node_data.get('updated_at', ''),
           node_data.get('metadata', '')))
        
        if edge_id:
            edge_data = {
                "id": edge_id,
                "source_id": node_id,
                "target_id": node_data.get('relationships', [{}])[0].get('target_id') if node_data.get('relationships') else None,
                "relationship_type": "references"
            }
            edge_data_json = json.dumps(edge_data, ensure_ascii=False)
            cursor.execute("""
            INSERT OR REPLACE INTO edges (id, source_id, target_id, relationship_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (edge_id, node_id, edge_data.get('target_id'), "references",
           edge_data.get('created_at', datetime.utcnow().isoformat() + "Z")))
        
        conn.commit()
        conn.close()
    
    def load_all(self) -> Dict:
        """Load all data from files and database."""
        nodes = {}
        edges = {}
        
        # Load from files
        if os.path.exists(self.nodes_file):
            with open(self.nodes_file, 'r', encoding='utf-8') as f:
                nodes = json.load(f)
        
        if os.path.exists(self.edges_file):
            with open(self.edges_file, 'r', encoding='utf-8') as f:
                edges = json.load(f)
        
        # Load from database
        if os.path.exists(self.index_file):
            conn = sqlite3.connect(self.index_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM nodes")
            for row in cursor.fetchall():
                nodes[row[0]] = {
                    "id": row[0],
                    "type": row[1],
                    "content": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "metadata": row[5]
                }
            
            cursor.execute("SELECT * FROM edges")
            for row in cursor.fetchall():
                edges[row[0]] = [row[1], row[2], row[3], row[4]]
            
            conn.close()
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_memory_path(self) -> str:
        """Get absolute path to memory data directory."""
        return self.data_dir
