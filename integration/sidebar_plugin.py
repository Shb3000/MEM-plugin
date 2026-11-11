"""
Sidebar plugin for MEM-Plugin.
Creates sidebar icon and displays memory information panel.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.memory_api import MemoryAPI


class SidebarPlugin:
    """Plugin for DeepSeek Harness sidebar integration."""
    
    ICON_PATH = "mem_icon.svg"
    
    def __init__(self, memory_api: MemoryAPI):
        self.memory_api = memory_api
        self.data_dir = os.path.join(memory_api.store.data_dir, "sidebar")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create icon if not exists
        self._ensure_icon()
    
    def _ensure_icon(self):
        """Ensure sidebar icon exists."""
        icon_path = os.path.join(self.data_dir, self.ICON_PATH)
        if not os.path.exists(icon_path):
            # Create a simple SVG icon
            icon_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="15" fill="#4A90D9"/>
  <circle cx="50" cy="50" r="25" fill="#FFFFFF"/>
  <path d="M30 70 Q50 50 70 70" stroke="#4A90D9" stroke-width="5" fill="none"/>
  <circle cx="50" cy="30" r="8" fill="#4A90D9"/>
</svg>"""
            with open(icon_path, 'w') as f:
                f.write(icon_svg)
    
    def create_sidebar_entry(self, entry_id: Optional[str] = None) -> str:
        """Create sidebar entry for MEM-Plugin."""
        entry_id = entry_id or str(uuid.uuid4())
        entry_path = os.path.join(self.data_dir, f"{entry_id}.json")
        
        # Get memory summary
        summary = self.memory_api.get_stats()
        
        entry_data = {
            "entry_id": entry_id,
            "name": "MEM-Plugin",
            "description": "Persistent Memory OS",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "memory_stats": {
                "total_memories": summary["total_nodes"],
                "total_edges": summary["total_edges"],
                "node_types": summary["node_types"]
            },
            "recent_memories": self.get_recent_memories(5),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "icon_path": self.ICON_PATH
        }
        
        with open(entry_path, 'w') as f:
            json.dump(entry_data, f, indent=2)
        
        return entry_id
    
    def get_sidebar_entry(self, entry_id: str) -> Optional[Dict]:
        """Get sidebar entry data."""
        entry_path = os.path.join(self.data_dir, f"{entry_id}.json")
        if os.path.exists(entry_path):
            with open(entry_path, 'r') as f:
                return json.load(f)
        return None
    
    def update_sidebar_entry(self, entry_id: str, updates: Dict) -> bool:
        """Update sidebar entry."""
        entry_path = os.path.join(self.data_dir, f"{entry_id}.json")
        entry = self.get_sidebar_entry(entry_id)
        if entry:
            entry.update(updates)
            with open(entry_path, 'w') as f:
                json.dump(entry, f, indent=2)
            return True
        return False
    
    def get_memory_panel_content(self) -> Dict:
        """Get content for memory info panel."""
        stats = self.memory_api.get_stats()
        
        # Get memories by type
        text_memories = self.memory_api.retrieve_all(node_type="text")
        image_memories = self.memory_api.retrieve_all(node_type="image")
        tool_memories = self.memory_api.retrieve_all(node_type="tool_trace")
        persona_memories = self.memory_api.retrieve_all(node_type="persona")
        
        return {
            "stats": stats,
            "by_type": {
                "text": len(text_memories),
                "image": len(image_memories),
                "tool_trace": len(tool_memories),
                "persona": len(persona_memories)
            },
            "text_memories": text_memories[:10],
            "image_memories": image_memories[:5],
            "tool_memories": tool_memories[:5],
            "persona_memories": persona_memories[:5],
            "data_path": stats["data_path"]
        }
    
    def get_entry_path(self, entry_id: str) -> str:
        """Get absolute path to entry file."""
        return os.path.join(self.data_dir, f"{entry_id}.json")
