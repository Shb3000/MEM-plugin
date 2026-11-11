"""
DeepSeek Harness integration for MEM-Plugin.
Handles sidebar integration and icon display.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.memory_api import MemoryAPI
from ..feedback.feedback_processor import FeedbackProcessor
from ..feedback.memory_review import MemoryReview
from ..multimodal.image_processor import ImageProcessor
from ..multimodal.tool_tracer import ToolTracer
from ..multimodal.persona_manager import PersonaManager
from ..kubemanagement.cube_manager import CubeManager
from ..kubemanagement.composition_engine import CompositionEngine
from ..schedulers.mem_scheduler import MemScheduler


class DSHIntegration:
    """Integration with DeepSeek Harness platform."""
    
    def __init__(self, memory_api: MemoryAPI):
        self.memory_api = memory_api
        self.feedback_processor = FeedbackProcessor(memory_api)
        self.memory_review = MemoryReview(memory_api)
        self.image_processor = ImageProcessor(memory_api)
        self.tool_tracer = ToolTracer(memory_api)
        self.persona_manager = PersonaManager(memory_api)
        self.cube_manager = CubeManager(memory_api)
        self.composition_engine = CompositionEngine(memory_api)
        self.scheduler = MemScheduler(memory_api)
        
        # Integration metadata
        self.integration_id = str(uuid.uuid4())
        self.version = "1.0.0"
    
    def get_memory_summary(self) -> Dict:
        """Get summary of all memories."""
        stats = self.memory_api.get_stats()
        
        # Count by type
        type_counts = {
            "text": len([n for n in self.memory_api.retrieve_all() 
                        if n.get("type") == "text"]),
            "image": len([n for n in self.memory_api.retrieve_all() 
                         if n.get("type") == "image"]),
            "tool_trace": len([n for n in self.memory_api.retrieve_all() 
                              if n.get("type") == "tool_trace"]),
            "persona": len([n for n in self.memory_api.retrieve_all() 
                           if n.get("type") == "persona"]),
        }
        
        # Get recent memories (last 10)
        all_memories = self.memory_api.retrieve_all()
        recent = all_memories[-10:]
        
        return {
            "integration_id": self.integration_id,
            "version": self.version,
            "total_memories": stats["total_nodes"],
            "total_edges": stats["total_edges"],
            "data_path": stats["data_path"],
            "type_counts": type_counts,
            "recent_memories": [
                {
                    "id": m["id"],
                    "type": m.get("type"),
                    "created_at": m.get("created_at"),
                    "content_preview": m.get("content", "")[:100] + "..." if len(m.get("content", "")) > 100 else m.get("content", "")
                }
                for m in recent
            ],
            "scheduler_status": self.scheduler.get_queue_status()
        }
    
    def get_memory_stats(self) -> Dict:
        """Get quick memory statistics."""
        return self.memory_api.get_stats()
    
    def search_memories(self, query: str) -> List[Dict]:
        """Search memories."""
        results = self.memory_api.search(query)
        return results
    
    def add_memory(self, content: str, node_type: str = "text",
                  metadata: Optional[Dict] = None) -> str:
        """Add new memory."""
        node_id = self.memory_api.add(content, 
                                      node_type=MemoryType(node_type).value if node_type else MemoryType.TEXT.value,
                                      metadata=metadata)
        return node_id
    
    def get_recent_memories(self, count: int = 10) -> List[Dict]:
        """Get recent memories."""
        memories = self.memory_api.retrieve_all()
        return memories[-count:]
    
    def get_memory_graph(self) -> Dict:
        """Get memory graph in GraphQL format."""
        return self.memory_api.to_graphql()
    
    def get_feedback(self, node_id: str) -> List[Dict]:
        """Get feedback for a memory node."""
        return self.feedback_processor.list_feedback(node_id)
