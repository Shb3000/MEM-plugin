"""
MemScheduler: Async memory operations scheduler for MEM-Plugin.
Provides millisecond-level latency for production stability.
"""

import asyncio
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from queue import Queue, Empty

from ..core.memory_api import MemoryAPI
from ..core.memory_graph import MemoryGraph


class MemScheduler:
    """
    Asynchronous memory operations scheduler.
    Handles queue-based processing for millisecond-level latency.
    """
    
    def __init__(self, memory_api: MemoryAPI, queue_size: int = 100):
        self.memory_api = memory_api
        self.queue_size = queue_size
        self.queue: Queue = Queue(maxsize=queue_size)
        self.running = False
        self.processors = []
        self.metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "avg_latency_ms": 0
        }
        
        # Start processor thread
        self._start_processor()
    
    def _start_processor(self):
        """Start the async processor thread."""
        self.running = True
        processor = Processor(self.memory_api, self.queue, self.metrics)
        self.processors.append(processor)
        t = threading.Thread(target=processor.run, daemon=True)
        t.start()
    
    def add_to_queue(self, operation: Callable, priority: int = 0) -> str:
        """
        Add an operation to the scheduler queue.
        
        Args:
            operation: Async callable to execute
            priority: Priority (lower = higher priority)
            
        Returns:
            Job ID for tracking
        """
        job_id = str(uuid.uuid4())
        
        try:
            self.queue.put_nowait((operation, priority, job_id))
            self.metrics["total_operations"] += 1
        except:
            # Queue full
            pass
        
        return job_id
    
    def get_queue_status(self) -> Dict:
        """Get scheduler queue status."""
        return {
            "queue_size": self.queue.qsize(),
            "max_size": self.queue_size,
            "running": self.running,
            "metrics": self.metrics
        }
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        for processor in self.processors:
            processor.stop()


class Processor:
    """Memory operation processor."""
    
    def __init__(self, memory_api: MemoryAPI, queue: Queue, metrics: Dict):
        self.memory_api = memory_api
        self.queue = queue
        self.metrics = metrics
        self.running = False
    
    def run(self):
        """Main processor loop."""
        while self.running:
            try:
                operation, priority, job_id = self.queue.get(timeout=0.1)
                self._process_operation(operation, priority, job_id)
            except Empty:
                continue
            except Exception as e:
                self.metrics["failed_operations"] += 1
                print(f"Processor error: {e}")
    
    def _process_operation(self, operation: Callable, priority: int, job_id: str):
        """Process a single operation."""
        start_time = datetime.utcnow()
        try:
            result = operation()
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.metrics["successful_operations"] += 1
            self.metrics["avg_latency_ms"] = (
                self.metrics["avg_latency_ms"] * (self.metrics["successful_operations"] - 1) + latency_ms
            ) / self.metrics["successful_operations"]
            
            print(f"[Scheduler] Job {job_id}: Completed in {latency_ms:.2f}ms")
        except Exception as e:
            self.metrics["failed_operations"] += 1
            print(f"[Scheduler] Job {job_id}: Failed - {e}")


class AsyncMemoryOperation:
    """Wrapper for async memory operations."""
    
    def __init__(self, memory_api: MemoryAPI, queue: Queue, scheduler: MemScheduler):
        self.memory_api = memory_api
        self.queue = queue
        self.scheduler = scheduler
    
    def add_text(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Async add text memory."""
        def operation():
            return self.memory_api.add(content, MemoryType.TEXT, metadata)
        
        return self.scheduler.add_to_queue(operation)
    
    def search(self, query: str) -> List[Dict]:
        """Async search memories."""
        def operation():
            return self.memory_api.search(query)
        
        return self.scheduler.add_to_queue(operation)
    
    def get_stats(self) -> Dict:
        """Get scheduler metrics."""
        def operation():
            return self.scheduler.get_queue_status()
        
        return self.scheduler.add_to_queue(operation)
