"""Mem0 Memory Manager for Executive Team Agents.

Provides persistent, self-improving memory for agents using Mem0.
Supports user-level, agent-level, and session-level memory scoping.
"""

from __future__ import annotations

import logging
from typing import Any

from mem0 import Memory
from pydantic import BaseModel

from agnoteamost.config import settings

logger = logging.getLogger(__name__)


class MemoryConfig(BaseModel):
    """Configuration for Mem0 memory manager."""

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    embedder_provider: str = "openai"
    embedder_model: str = "text-embedding-3-small"
    vector_store_provider: str = "qdrant"
    vector_store_url: str = "http://localhost:6333"
    collection_name: str = "agnoteam_memories"
    graph_store_enabled: bool = False


class Mem0MemoryManager:
    """Memory manager using Mem0 for persistent agent memory.

    Provides:
    - User-level memories (long-term preferences, facts)
    - Agent-level memories (agent-specific knowledge)
    - Session-level memories (conversation context)

    Example:
        ```python
        memory_manager = Mem0MemoryManager()

        # Store a memory
        memory_manager.add(
            messages=[
                {"role": "user", "content": "I prefer quarterly reports"},
                {"role": "assistant", "content": "Noted, I'll provide quarterly reports"}
            ],
            user_id="ceo",
            agent_id="cfo",
        )

        # Search memories
        relevant = memory_manager.search(
            query="report preferences",
            user_id="ceo",
        )
        ```
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        """Initialize the Mem0 memory manager.

        Args:
            config: Memory configuration (uses defaults if not provided)
        """
        self.config = config or MemoryConfig(
            llm_provider=settings.mem0_provider,
            vector_store_provider=settings.mem0_vector_store,
            vector_store_url=settings.mem0_vector_store_url,
            collection_name=settings.mem0_collection_name,
        )

        self._memory: Memory | None = None

    @property
    def memory(self) -> Memory:
        """Get or create Mem0 Memory instance."""
        if self._memory is None:
            self._memory = self._create_memory()
        return self._memory

    def _create_memory(self) -> Memory:
        """Create and configure Mem0 Memory instance."""
        config = {
            "llm": {
                "provider": self.config.llm_provider,
                "config": {
                    "model": self.config.llm_model,
                    "temperature": 0.1,
                },
            },
            "embedder": {
                "provider": self.config.embedder_provider,
                "config": {
                    "model": self.config.embedder_model,
                },
            },
            "vector_store": {
                "provider": self.config.vector_store_provider,
                "config": {
                    "url": self.config.vector_store_url,
                    "collection_name": self.config.collection_name,
                },
            },
            "version": "v1.1",
        }

        logger.info(f"Initializing Mem0 with config: {config}")
        return Memory.from_config(config)

    def add(
        self,
        messages: list[dict[str, str]],
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add memories from a conversation.

        Mem0 extracts facts from the messages and stores them.

        Args:
            messages: List of message dicts with 'role' and 'content'
            user_id: User identifier (for user-level memories)
            agent_id: Agent identifier (for agent-specific memories)
            run_id: Session/run identifier (for session-level memories)
            metadata: Additional metadata to store with memories

        Returns:
            Result dict with memory IDs created
        """
        if not any([user_id, agent_id, run_id]):
            raise ValueError("At least one of user_id, agent_id, or run_id required")

        kwargs: dict[str, Any] = {}
        if user_id:
            kwargs["user_id"] = user_id
        if agent_id:
            kwargs["agent_id"] = agent_id
        if run_id:
            kwargs["run_id"] = run_id
        if metadata:
            kwargs["metadata"] = metadata

        logger.info(f"Adding memory with scope: {kwargs}")
        result = self.memory.add(messages, **kwargs)
        return result

    def search(
        self,
        query: str,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant memories.

        Args:
            query: Search query
            user_id: Filter by user
            agent_id: Filter by agent
            run_id: Filter by session
            limit: Maximum results to return
            filters: Additional metadata filters

        Returns:
            List of relevant memories with scores
        """
        kwargs: dict[str, Any] = {"limit": limit}
        if user_id:
            kwargs["user_id"] = user_id
        if agent_id:
            kwargs["agent_id"] = agent_id
        if run_id:
            kwargs["run_id"] = run_id
        if filters:
            kwargs["filters"] = filters

        logger.debug(f"Searching memories: query='{query}', scope={kwargs}")
        results = self.memory.search(query, **kwargs)
        return results

    def get_all(
        self,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all memories for a given scope.

        Args:
            user_id: Filter by user
            agent_id: Filter by agent
            run_id: Filter by session

        Returns:
            List of all memories in scope
        """
        kwargs: dict[str, Any] = {}
        if user_id:
            kwargs["user_id"] = user_id
        if agent_id:
            kwargs["agent_id"] = agent_id
        if run_id:
            kwargs["run_id"] = run_id

        return self.memory.get_all(**kwargs)

    def update(self, memory_id: str, data: str) -> dict[str, Any]:
        """Update a specific memory.

        Args:
            memory_id: ID of memory to update
            data: New memory content

        Returns:
            Update result
        """
        return self.memory.update(memory_id, data)

    def delete(self, memory_id: str) -> dict[str, Any]:
        """Delete a specific memory.

        Args:
            memory_id: ID of memory to delete

        Returns:
            Delete result
        """
        return self.memory.delete(memory_id)

    def delete_all(
        self,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Delete all memories for a given scope.

        Args:
            user_id: Delete user's memories
            agent_id: Delete agent's memories
            run_id: Delete session's memories

        Returns:
            Delete result
        """
        kwargs: dict[str, Any] = {}
        if user_id:
            kwargs["user_id"] = user_id
        if agent_id:
            kwargs["agent_id"] = agent_id
        if run_id:
            kwargs["run_id"] = run_id

        return self.memory.delete_all(**kwargs)

    def history(self, memory_id: str) -> list[dict[str, Any]]:
        """Get change history for a memory.

        Args:
            memory_id: ID of memory

        Returns:
            List of historical changes
        """
        return self.memory.history(memory_id)

    def get_context_for_agent(
        self,
        agent_name: str,
        query: str,
        user_id: str | None = None,
    ) -> str:
        """Get relevant memory context for an agent.

        Convenience method to build context string for agent prompts.

        Args:
            agent_name: Name of the agent (used as agent_id)
            query: Current query/task
            user_id: Optional user filter

        Returns:
            Formatted context string
        """
        memories = self.search(
            query=query,
            agent_id=agent_name,
            user_id=user_id,
            limit=5,
        )

        if not memories:
            return ""

        context_parts = ["## Relevant Memories", ""]
        for mem in memories:
            memory_text = mem.get("memory", mem.get("text", ""))
            score = mem.get("score", 0)
            context_parts.append(f"- {memory_text} (relevance: {score:.2f})")

        return "\n".join(context_parts)


# Global memory manager instance
memory_manager = Mem0MemoryManager()
