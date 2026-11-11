"""
Feedback processor for MEM-Plugin.
Handles memory correction and refinement via natural language feedback.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class FeedbackProcessor:
    """Process and store memory feedback."""
    
    def __init__(self, memory_api):
        self.memory_api = memory_api
    
    def submit_feedback(self, node_id: str, feedback: str,
                       feedback_type: str = "correction",
                       metadata: Optional[Dict] = None) -> str:
        """
        Submit feedback for memory correction.
        
        Args:
            node_id: Target memory node ID
            feedback: Natural language feedback
            feedback_type: Type (correction, supplement, replace)
            metadata: Optional metadata
            
        Returns:
            Feedback node ID
        """
        feedback_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        feedback_content = f"""
Feedback for memory: {node_id}
Type: {feedback_type}
Submitted: {created_at}

Feedback:
{feedback}
"""
        
        if metadata:
            feedback_content += f"""

Metadata:
{json.dumps(metadata, indent=2)}
"""
        
        node_id = self.memory_api.add(
            content=feedback_content,
            node_type="text",
            metadata={
                "type": "feedback",
                "target_id": node_id,
                "feedback_type": feedback_type,
                "feedback_id": feedback_id,
                "created_at": created_at
            }
        )
        
        # Create reference edge
        self.memory_api.add(
            content=f"Feedback: {feedback_type}",
            node_type="text",
            relationships=[{
                "type": "is_feedback_for",
                "target_id": node_id,
                "target_type": "memory"
            }]
        )
        
        return node_id
    
    def list_feedback(self, node_id: str) -> List[Dict]:
        """List all feedback for a memory node."""
        feedbacks = self.memory_api.retrieve_all()
        results = []
        
        for fb in feedbacks:
            if fb.get("metadata", {}).get("is_feedback_for", "").startswith(node_id):
                metadata = fb.get("metadata", {})
                results.append({
                    "id": fb["id"],
                    "type": metadata.get("feedback_type"),
                    "target_id": metadata.get("target_id"),
                    "created_at": metadata.get("created_at"),
                    "content": fb.get("content")
                })
        
        return results
    
    def apply_correction(self, feedback_id: str, node_id: str,
                        correction_content: str) -> bool:
        """
        Apply correction from feedback.
        
        Args:
            feedback_id: Feedback node ID
            node_id: Target memory node ID
            correction_content: Content to replace/supplement
            
        Returns:
            True if successful
        """
        fb = self.memory_api.retrieve(feedback_id)
        if not fb:
            return False
        
        if node_id not in self.memory_api.graph.nodes:
            return False
        
        # Apply the correction
        return self.memory_api.edit(node_id, correction_content)
