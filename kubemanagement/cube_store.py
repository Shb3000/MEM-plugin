"""
Cube storage and metadata for MEM-Plugin.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class CubeStore:
    """Store cube metadata and configurations."""
    
    def __init__(self, data_dir: str = "mem_plugin_data"):
        self.data_dir = os.path.join(data_dir, "cubes")
        self.cubes_file = os.path.join(self.data_dir, "cubes.json")
        self.cube_metadata_dir = os.path.join(self.data_dir, "metadata")
        os.makedirs(self.cube_metadata_dir, exist_ok=True)
    
    def save_cube(self, cube_id: str, cube_data: Dict) -> bool:
        """Save cube metadata."""
        try:
            with open(self.cubes_file, 'w', encoding='utf-8') as f:
                json.dump(cubes_file, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving cube: {e}")
            return False
    
    def load_all(self) -> Dict:
        """Load all cube metadata."""
        cubes = {}
        if os.path.exists(self.cubes_file):
            with open(self.cubes_file, 'r', encoding='utf-8') as f:
                cubes = json.load(f)
        return cubes
    
    def get_cube(self, cube_id: str) -> Optional[Dict]:
        """Get cube metadata."""
        cubes = self.load_all()
        return cubes.get(cube_id)
    
    def list_cubes(self) -> List[Dict]:
        """List all cubes."""
        cubes = self.load_all()
        return list(cubes.values())
    
    def delete_cube(self, cube_id: str) -> bool:
        """Delete cube metadata."""
        cubes = self.load_all()
        if cube_id in cubes:
            del cubes[cube_id]
            try:
                with open(self.cubes_file, 'w', encoding='utf-8') as f:
                    json.dump(cubes, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"Error deleting cube: {e}")
                return False
        return False
