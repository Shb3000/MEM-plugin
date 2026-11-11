"""
Run MEM-Plugin tests directly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules directly
from core.memory_api import MemoryAPI


def test_memory_api():
    """Test memory API functionality."""
    print("Testing Memory API...")
    
    # Initialize API
    memory_api = MemoryAPI()
    
    # Test add memory - use string type directly
    node_id = memory_api.add("Hello, World!", "text")
    assert node_id is not None, "Failed to add memory"
    print("  [OK] Added memory: " + node_id)
    
    # Test retrieve
    retrieved = memory_api.retrieve(node_id)
    assert retrieved is not None, "Failed to retrieve memory"
    assert retrieved["content"] == "Hello, World!", "Content mismatch"
    print("  [OK] Retrieved memory: " + node_id)
    
    # Test search
    results = memory_api.search("Hello")
    assert len(results) == 1, "Search returned unexpected results"
    print("  [OK] Searched for 'Hello'")
    
    # Test edit
    memory_api.edit(node_id, "Updated content!")
    retrieved = memory_api.retrieve(node_id)
    assert retrieved["content"] == "Updated content!", "Edit failed"
    print("  [OK] Edited memory")
    
    # Test delete
    memory_api.delete(node_id)
    retrieved = memory_api.retrieve(node_id)
    assert retrieved is None, "Delete failed"
    print("  [OK] Deleted memory")
    
    # Test stats
    stats = memory_api.get_stats()
    assert "total_nodes" in stats, "Stats missing total_nodes"
    print("  [OK] Got stats: " + str(stats['total_nodes']) + " nodes")
    
    print("Memory API tests passed!\n")


if __name__ == "__main__":
    test_memory_api()
    print("All tests passed!")
