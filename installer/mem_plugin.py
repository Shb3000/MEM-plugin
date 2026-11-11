
# MEM-Plugin: Persistent Memory OS for DeepSeek Harness

# Main entry point for the plugin
"""
MEM-Plugin: Persistent Memory OS for DeepSeek Harness

Main module for the plugin.
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

# Import main plugin modules
from core.memory_api import MemoryAPI, MemoryType
from core.memory_graph import MemoryGraph
from core.memory_store import MemoryStore
from multimodal.image_processor import ImageProcessor
from multimodal.tool_tracer import ToolTracer
from multimodal.persona_manager import PersonaManager
from kubemanagement.cube_manager import CubeManager
from kubemanagement.composition_engine import CompositionEngine
from schedulers.mem_scheduler import MemScheduler
from feedback.feedback_processor import FeedbackProcessor
from feedback.memory_review import MemoryReview
from integration.dsh_integration import DSHIntegration
from integration.sidebar_plugin import SidebarPlugin


def initialize_plugin(data_dir: str = "mem_plugin_data"):
    """Initialize MEM-Plugin instance."""
    # Core API
    memory_api = MemoryAPI(data_dir)
    
    # Sidebar integration
    sidebar = SidebarPlugin(memory_api)
    
    # Multilmodal components
    image_processor = ImageProcessor(memory_api)
    tool_tracer = ToolTracer(memory_api)
    persona_manager = PersonaManager(memory_api)
    
    # Knowledge base management
    cube_manager = CubeManager(memory_api)
    composition_engine = CompositionEngine(memory_api)
    
    # Scheduler
    scheduler = MemScheduler(memory_api)
    
    # Feedback
    feedback_processor = FeedbackProcessor(memory_api)
    memory_review = MemoryReview(memory_api)
    
    # DeepSeek Harness integration
    dsh_integration = DSHIntegration(memory_api)
    
    return {
        "memory_api": memory_api,
        "sidebar": sidebar,
        "image_processor": image_processor,
        "tool_tracer": tool_tracer,
        "persona_manager": persona_manager,
        "cube_manager": cube_manager,
        "composition_engine": composition_engine,
        "scheduler": scheduler,
        "feedback_processor": feedback_processor,
        "memory_review": memory_review,
        "dsh_integration": dsh_integration,
    }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MEM-Plugin: Persistent Memory OS")
    parser.add_argument("--init", action="store_true", help="Initialize plugin")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    parser.add_argument("--search", help="Search memories")
    parser.add_argument("--add", help="Add memory content")
    parser.add_argument("--get-memories", nargs="+", help="Get memories")
    parser.add_argument("--delete-memories", nargs="+", help="Delete memories")
    
    args = parser.parse_args()
    
    if args.init:
        initialize_plugin()
        print("Plugin initialized successfully.")
    
    elif args.stats:
        plugin = initialize_plugin()
        stats = plugin["memory_api"].get_stats()
        print("Total Memories: " + str(stats['total_nodes']))
        print("Total Edges: " + str(stats['total_edges']))
        print("Data Path: " + stats['data_path'])
    
    elif args.search:
        plugin = initialize_plugin()
        results = plugin["memory_api"].search(args.search)
        print("Found " + str(len(results)) + " memories:")
        for result in results:
            print("ID: " + result['id'])
            print("Content: " + result['content'][:100] + "...")
            print()
    
    elif args.add:
        plugin = initialize_plugin()
        if args.add:
            content = args.add
        else:
            content = "New memory content"
        
        node_id = plugin["memory_api"].add(content)
        print("Memory added. Node ID: " + node_id)
    
    elif args.get_memories:
        plugin = initialize_plugin()
        for mem_type in args.get_memories:
            memories = plugin["memory_api"].retrieve_all(node_type=mem_type)
            print(mem_type.capitalize() + " memories (" + str(len(memories)) + "):")
            for mem in memories:
                print("ID: " + mem['id'])
                print("Content: " + mem['content'][:100] + "...")
                print()
    
    elif args.delete_memories:
        plugin = initialize_plugin()
        for mem_id in args.delete_memories:
            if plugin["memory_api"].delete(mem_id):
                print("Memory " + mem_id + " deleted.")
            else:
                print("Memory " + mem_id + " not found.")


if __name__ == "__main__":
    main()
