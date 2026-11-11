"""
MEM-Plugin: Persistent Memory OS for DeepSeek Harness

A unified memory operating system for LLMs and AI agents.
"""

from .core.memory_api import MemoryAPI
from .core.memory_graph import MemoryGraph
from .core.memory_store import MemoryStore
from .multimodal.image_processor import ImageProcessor
from .multimodal.tool_tracer import ToolTracer
from .multimodal.persona_manager import PersonaManager
from .kubemanagement.cube_manager import CubeManager
from .kubemanagement.cube_store import CubeStore
from .kubemanagement.composition_engine import CompositionEngine
from .schedulers.mem_scheduler import MemScheduler
from .feedback.feedback_processor import FeedbackProcessor
from .feedback.memory_review import MemoryReview
from .integration.dsh_integration import DSHIntegration
from .integration.sidebar_plugin import SidebarPlugin
from .installer.setup import create_installer

__version__ = "1.0.0"
__author__ = "MEM-Plugin Team"
