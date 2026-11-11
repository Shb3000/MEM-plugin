"""
Persona manager for MEM-Plugin.
Handles agent persona definitions and management.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class PersonaManager:
    """Manage agent personas in memory."""
    
    def __init__(self, memory_api):
        self.memory_api = memory_api
    
    def create_persona(self, name: str, description: str, 
                      traits: Dict, instructions: str,
                      context: Optional[str] = None) -> str:
        """
        Create a new persona.
        
        Args:
            name: Persona name
            description: Persona description
            traits: Character traits
            instructions: Persona instructions
            context: Initial context
            
        Returns:
            Node ID for the persona
        """
        persona_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        persona_data = f"""
Persona: {name}
Description: {description}
Traits: {json.dumps(traits, indent=2)}
Instructions:
{instructions}
"""
        
        if context:
            persona_data += f"""

Context:
{context}
"""
        
        node_id = self.memory_api.add(
            content=persona_data,
            node_type="persona",
            metadata={
                "name": name,
                "description": description,
                "traits": traits,
                "instructions": instructions,
                "created_at": created_at
            }
        )
        
        return node_id
    
    def list_personas(self) -> List[str]:
        """List all persona node IDs."""
        personas = self.memory_api.retrieve_all(node_type="persona")
        return [p["id"] for p in personas]
    
    def get_persona(self, persona_id: str) -> Optional[Dict]:
        """Get a persona by ID."""
        persona = self.memory_api.retrieve(persona_id)
        if persona:
            metadata = persona.get("metadata", {})
            return {
                "id": persona["id"],
                "name": metadata.get("name"),
                "description": metadata.get("description"),
                "traits": metadata.get("traits"),
                "instructions": metadata.get("instructions"),
                "created_at": metadata.get("created_at")
            }
        return None
    
    def update_persona(self, persona_id: str, **kwargs) -> bool:
        """Update a persona."""
        content = f"""
Persona: {kwargs.get('name', '')}
Description: {kwargs.get('description', '')}
Traits: {json.dumps(kwargs.get('traits', {}), indent=2)}
Instructions:
{kwargs.get('instructions', '')}
"""
        return self.memory_api.edit(persona_id, content)
