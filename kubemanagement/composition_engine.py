"""
Composition engine for MEM-Plugin.
Handles dynamic cube composition and retrieval.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


class CompositionEngine:
    """Engine for composing and retrieving from multiple cubes."""
    
    def __init__(self, memory_api, data_dir: str = "mem_plugin_data"):
        self.memory_api = memory_api
        self.data_dir = os.path.join(data_dir, "cubes")
    
    def compose(self, cube_ids: List[str], 
                composition_name: str = "composed") -> str:
        """
        Compose multiple cubes into a single composition.
        
        Args:
            cube_ids: List of cube IDs to compose
            composition_name: Name for the composition
            
        Returns:
            Composition node ID
        """
        composition_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Get cube information
        cube_info = []
        for cid in cube_ids:
            cube = self.memory_api.retrieve(cid)
            if cube:
                cube_info.append({
                    "id": cid,
                    "name": cube.get("metadata", {}).get("name", "Unknown"),
                    "content_count": self._count_cube_contents(cid)
                })
        
        # Create composition node
        composition_data = f"""
Composition: {composition_name}
Created: {created_at}
Cube Information:
{json.dumps(cube_info, indent=2)}
"""
        
        node_id = self.memory_api.add(
            content=composition_data,
            node_type="text",
            metadata={
                "type": "composition",
                "name": composition_name,
                "cube_ids": cube_ids,
                "created_at": created_at
            }
        )
        
        # Create reference edges
        for cube_id in cube_ids:
            self.memory_api.add(
                content=f"Composition: {composition_name}",
                node_type="text",
                relationships=[{
                    "type": "composes",
                    "target_id": composition_id,
                    "target_type": "composition"
                }]
            )
        
        return node_id
    
    def retrieve_composition(self, composition_id: str) -> Optional[Dict]:
        """Get composition details."""
        comp = self.memory_api.retrieve(composition_id)
        if comp:
            metadata = comp.get("metadata", {})
            return {
                "id": comp["id"],
                "name": metadata.get("name"),
                "cube_ids": metadata.get("cube_ids"),
                "created_at": metadata.get("created_at"),
                "node_id": comp["id"]
            }
        return None
    
    def _count_cube_contents(self, cube_id: str) -> int:
        """Count contents in a cube."""
        contents = self.memory_api.retrieve_all()
        count = 0
        for content in contents:
            if content.get("metadata", {}).get("belongs_to", "").startswith(cube_id):
                count += 1
        return count
    
    def add_to_composition(self, composition_id: str, content: str,
                           node_type: str = "text") -> str:
        """Add content to an existing composition."""
        comp = self.retrieve_composition(composition_id)
        if not comp:
            return None
        
        node_id = self.memory_api.add(
            content=content,
            node_type=node_type
        )
        
        # Create reference to composition
        self.memory_api.add(
            content=f"Composition: {comp.get('name', 'Unknown')}",
            node_type="text",
            relationships=[{
                "type": "belongs_to",
                "target_id": composition_id,
                "target_type": "composition"
            }]
        )
        
        return node_id
