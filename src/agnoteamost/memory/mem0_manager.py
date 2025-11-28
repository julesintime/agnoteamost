"""Mem0 Memory Manager for Executive Team Agents.

Provides persistent, self-improving memory for agents using Mem0.
Supports both cloud (MemoryClient) and self-hosted (Memory) deployments.
Supports user-level, agent-level, and session-level memory scoping.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from pydantic import BaseModel

from agnoteamost.config import settings

logger = logging.getLogger(__name__)


class MemoryConfig(BaseModel):
    """Configuration for Mem0 memory manager."""

    # Cloud settings
    api_key: str | None = None
    project_id: str | None = None

    # Self-hosted settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    embedder_provider: str = "openai"
    embedder_model: str = "text-embedding-3-small"
    vector_store_provider: str = "qdrant"
    vector_store_url: str = "http://localhost:6333"
    collection_name: str = "agnoteam_memories"


class Mem0MemoryManager:
    """Memory manager using Mem0 for persistent agent memory.

    Automatically uses Mem0 Cloud if API key is configured,
    otherwise falls back to self-hosted Memory instance.

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
            config: Memory configuration (uses settings if not provided)
        """
        self.config = config or MemoryConfig(
            api_key=settings.mem0_api_key,
            project_id=settings.mem0_project_id,
            llm_provider=settings.mem0_provider,
            vector_store_provider=settings.mem0_vector_store,
            vector_store_url=settings.mem0_vector_store_url,
            collection_name=settings.mem0_collection_name,
        )

        self._client: Any = None
        self._use_cloud = bool(self.config.api_key)

    @property
    def client(self) -> Any:
        """Get or create Mem0 client instance."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> Any:
        """Create and configure Mem0 client instance."""
        if self._use_cloud:
            return self._create_cloud_client()
        else:
            return self._create_oss_client()

    def _create_cloud_client(self) -> Any:
        """Create Mem0 cloud client (MemoryClient)."""
        from mem0 import MemoryClient

        logger.info(f"Initializing Mem0 Cloud client (project: {self.config.project_id})")

        # Set API key in environment if not already set
        if self.config.api_key and not os.getenv("MEM0_API_KEY"):
            os.environ["MEM0_API_KEY"] = self.config.api_key

        client = MemoryClient(api_key=self.config.api_key)
        return client

    def _create_oss_client(self) -> Any:
        """Create self-hosted Mem0 Memory instance."""
        from mem0 import Memory

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

        logger.info(f"Initializing Mem0 self-hosted with config: {config}")
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

        # Add project_id for cloud client
        if self._use_cloud and self.config.project_id:
            kwargs["project_id"] = self.config.project_id

        logger.info(f"Adding memory with scope: {kwargs}")
        result = self.client.add(messages, **kwargs)
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

        # Add project_id for cloud client
        if self._use_cloud and self.config.project_id:
            kwargs["project_id"] = self.config.project_id

        logger.debug(f"Searching memories: query='{query}', scope={kwargs}")
        results = self.client.search(query, **kwargs)

        # Normalize response format (cloud vs OSS may differ)
        if isinstance(results, dict) and "results" in results:
            return results["results"]
        return results if isinstance(results, list) else []

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

        # Add project_id for cloud client
        if self._use_cloud and self.config.project_id:
            kwargs["project_id"] = self.config.project_id

        results = self.client.get_all(**kwargs)

        # Normalize response format
        if isinstance(results, dict) and "results" in results:
            return results["results"]
        return results if isinstance(results, list) else []

    def update(self, memory_id: str, data: str) -> dict[str, Any]:
        """Update a specific memory.

        Args:
            memory_id: ID of memory to update
            data: New memory content

        Returns:
            Update result
        """
        return self.client.update(memory_id, data)

    def delete(self, memory_id: str) -> dict[str, Any]:
        """Delete a specific memory.

        Args:
            memory_id: ID of memory to delete

        Returns:
            Delete result
        """
        return self.client.delete(memory_id)

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

        # Add project_id for cloud client
        if self._use_cloud and self.config.project_id:
            kwargs["project_id"] = self.config.project_id

        return self.client.delete_all(**kwargs)

    def history(self, memory_id: str) -> list[dict[str, Any]]:
        """Get change history for a memory.

        Args:
            memory_id: ID of memory

        Returns:
            List of historical changes
        """
        return self.client.history(memory_id)

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
        try:
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
                score = mem.get("score", mem.get("relevance_score", 0))
                context_parts.append(f"- {memory_text} (relevance: {score:.2f})")

            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Error fetching memory context: {e}")
            return ""


# Global memory manager instance
memory_manager = Mem0MemoryManager()
