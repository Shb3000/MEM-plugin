"""
Test suite for MEM-Plugin.
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly
from core.memory_api import MemoryAPI, MemoryType
from integration.sidebar_plugin import SidebarPlugin


def test_memory_api():
    """Test memory API functionality."""
    print("Testing Memory API...")
    
    # Initialize API
    memory_api = MemoryAPI()
    
    # Test add memory
    node_id = memory_api.add("Hello, World!", MemoryType.TEXT)
    assert node_id is not None, "Failed to add memory"
    print(f"  ✓ Added memory: {node_id}")
    
    # Test retrieve
    retrieved = memory_api.retrieve(node_id)
    assert retrieved is not None, "Failed to retrieve memory"
    assert retrieved["content"] == "Hello, World!", "Content mismatch"
    print(f"  ✓ Retrieved memory: {node_id}")
    
    # Test search
    results = memory_api.search("Hello")
    assert len(results) == 1, "Search returned unexpected results"
    print(f"  ✓ Searched for 'Hello'")
    
    # Test edit
    memory_api.edit(node_id, "Updated content!")
    retrieved = memory_api.retrieve(node_id)
    assert retrieved["content"] == "Updated content!", "Edit failed"
    print(f"  ✓ Edited memory")
    
    # Test delete
    memory_api.delete(node_id)
    retrieved = memory_api.retrieve(node_id)
    assert retrieved is None, "Delete failed"
    print(f"  ✓ Deleted memory")
    
    # Test stats
    stats = memory_api.get_stats()
    assert "total_nodes" in stats, "Stats missing total_nodes"
    print(f"  ✓ Got stats: {stats['total_nodes']} nodes")
    
    print("Memory API tests passed!\n")


def test_sidebar_plugin():
    """Test sidebar plugin functionality."""
    print("Testing Sidebar Plugin...")
    
    # Initialize plugin
    memory_api = MemoryAPI()
    sidebar = SidebarPlugin(memory_api)
    
    # Create sidebar entry
    entry_id = sidebar.create_sidebar_entry()
    assert entry_id is not None, "Failed to create sidebar entry"
    print(f"  ✓ Created sidebar entry: {entry_id}")
    
    # Get sidebar entry
    entry = sidebar.get_sidebar_entry(entry_id)
    assert entry is not None, "Failed to get sidebar entry"
    assert "name" in entry, "Missing name in entry"
    print(f"  ✓ Got sidebar entry")
    
    # Get memory panel content
    content = sidebar.get_memory_panel_content()
    assert "stats" in content, "Missing stats in panel content"
    print(f"  ✓ Got memory panel content")
    
    print("Sidebar Plugin tests passed!\n")


def test_integration():
    """Test DSHIntegration."""
    print("Testing DSH Integration...")
    
    memory_api = MemoryAPI()
    from integration.dsh_integration import DSHIntegration
    dsh = DSHIntegration(memory_api)
    
    # Get memory summary
    summary = dsh.get_memory_summary()
    assert "integration_id" in summary, "Missing integration_id"
    assert "total_memories" in summary, "Missing total_memories"
    print(f"  ✓ Got memory summary")
    
    # Add memory through integration
    node_id = dsh.add_memory("Test memory from DSH integration", "text")
    assert node_id is not None, "Failed to add memory through integration"
    print(f"  ✓ Added memory through DSH integration: {node_id}")
    
    # Search through integration
    results = dsh.search_memories("test")
    print(f"  ✓ Searched memories through DSH integration")
    
    print("DSH Integration tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("MEM-Plugin Test Suite")
    print("=" * 50)
    print()
    
    test_memory_api()
    test_sidebar_plugin()
    test_integration()
    
    print("=" * 50)
    print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
