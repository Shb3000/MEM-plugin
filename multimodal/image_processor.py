"""
Image processor for MEM-Plugin.
Handles image storage, embedding, and retrieval.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image
import numpy as np

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class ImageProcessor:
    """Process and store images in memory."""
    
    def __init__(self, memory_api, data_dir: str = "mem_plugin_data"):
        self.memory_api = memory_api
        self.data_dir = os.path.join(data_dir, "images")
        self.embeddings_dir = os.path.join(data_dir, "embeddings")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)
    
    def save_image(self, image_path: str, node_id: Optional[str] = None, 
                   content: Optional[str] = None) -> str:
        """Save an image to memory and create a node."""
        # Extract image extension
        _, ext = os.path.splitext(image_path)
        
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Save image file
        img_path = os.path.join(self.data_dir, f"{uuid.uuid4()}{ext}")
        img.save(img_path)
        
        # Generate embedding if available
        embedding = None
        if HAS_TORCH:
            embedding = self._generate_embedding(img)
        else:
            # Generate simple hash-based "embedding" for non-torch environment
            embedding = self._generate_simple_embedding(img)
        
        # Create node
        if content is None:
            content = f"Image file: {image_path}"
        
        relationships = []
        if node_id:
            relationships.append({
                "type": "references",
                "target_id": node_id,
                "target_type": "image"
            })
        
        node_id = self.memory_api.add(
            content, 
            node_type="image",
            metadata={"original_path": image_path, "embedded_path": img_path}
        )
        
        # Create reference edge
        if node_id and not relationships:
            relationships.append({
                "type": "references",
                "target_id": node_id
            })
        
        self.memory_api.add(
            f"Image embedding: {embedding[:100] if embedding else 'N/A'}",
            node_type="image",
            relationships=relationships
        )
        
        return node_id
    
    def _generate_embedding(self, image: Image.Image) -> List[float]:
        """Generate image embedding using PyTorch."""
        # Convert to tensor
        tensor = np.array(image).astype(np.float32)
        
        # Resize to standard size
        tensor = tensor.resize((224, 224))
        
        # Normalize
        mean = np.array([0.485, 0.456, 0.406]).reshape(1, 1, 3).astype(np.float32)
        std = np.array([0.229, 0.224, 0.225]).reshape(1, 1, 3).astype(np.float32)
        tensor = (tensor - mean) / std
        
        # Flatten
        tensor = tensor.flatten()
        
        # Use simple projection if ResNet not available
        if not hasattr(tensor, 'mean'):
            embedding = tensor.mean().tolist()
        else:
            # Use mean pooling as simple embedding
            embedding = tensor.mean().tolist()
        
        return embedding
    
    def _generate_simple_embedding(self, image: Image.Image) -> List[float]:
        """Generate simple hash-based embedding."""
        # Convert to numpy array
        arr = np.array(image).flatten()
        # Create simple hash
        hash_val = int(hashlib.md5(arr.tobytes()).hexdigest()[:8], 16)
        # Create embedding vector
        embedding = [0.1] * 512
        embedding[hash_val % 512] = 1.0
        return embedding
    
    def get_image_by_id(self, node_id: str) -> Optional[Image.Image]:
        """Retrieve image from memory by node ID."""
        node = self.memory_api.retrieve(node_id)
        if not node:
            return None
        
        metadata = node.get("metadata", {})
        img_path = metadata.get("original_path")
        if img_path and os.path.exists(img_path):
            return Image.open(img_path)
        
        return None
    
    def list_images(self) -> List[str]:
        """List all image node IDs."""
        images = self.memory_api.retrieve_all(node_type="image")
        return [n["id"] for n in images]
