# MEM-Plugin: Persistent Memory OS for DeepSeek Harness

A unified memory operating system for LLMs and AI agents that unifies store/retrieve/manage operations for long-term memory, enabling context-aware and personalized interactions.

## Core Features

- **Unified Memory API**: Single API to add, retrieve, edit, and delete memory - structured as a graph, inspectable and editable by design
- **Multi-Modal Memory**: Native support for text, images, tool traces, and personas
- **Multi-Cube Knowledge Base Management**: Composable memory cubes with isolation, controlled sharing, and dynamic composition
- **Async Ingestion via MemScheduler**: Millisecond-level latency for production stability
- **Memory Feedback & Correction**: Natural-language refinement of existing memories

## Architecture

```
MEM-Plugin/
├── core/
│   ├── memory_api.py          # Unified API: add, retrieve, edit, delete
│   ├── memory_graph.py        # Graph-based memory structure
│   └── memory_store.py        # Local storage backend
├── multimodal/
│   ├── image_processor.py     # Image handling and embedding
│   ├── tool_tracer.py         # Tool execution traces
│   └── persona_manager.py     # Agent persona management
├── kubemanagement/
│   ├── cube_manager.py        # Multi-cube knowledge base
│   ├── cube_store.py          # Cube storage and metadata
│   └── composition_engine.py  # Dynamic cube composition
├── schedulers/
│   └── mem_scheduler.py       # Async memory operations
├── feedback/
│   ├── feedback_processor.py  # Memory correction system
│   └── memory_review.py       # Natural language feedback
├── integration/
│   ├── dsh_integration.py     # DeepSeek Harness integration
│   └── sidebar_plugin.py      # Sidebar icon and panel
├── installer/
│   └── setup.py               # Installation script
└── __init__.py
```

## Installation

Run the installer to deploy the plugin to DeepSeek Desktop app.
