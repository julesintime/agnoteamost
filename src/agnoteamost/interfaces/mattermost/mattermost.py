"""Mattermost interface for AgentOS.

Adapts the Agno Slack interface pattern for Mattermost:
- Connects to Mattermost via WebSocket for real-time events
- Processes message events and routes to agents/teams/workflows
- Sends responses back to Mattermost channels/threads
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from mattermostdriver import Driver
from pydantic import BaseModel

if TYPE_CHECKING:
    from agno.agent import Agent
    from agno.team import Team
    from agno.workflow import Workflow

logger = logging.getLogger(__name__)


class MattermostConfig(BaseModel):
    """Configuration for Mattermost interface."""

    url: str
    token: str
    team: str = "main"
    scheme: str = "https"
    port: int = 443
    reply_to_mentions_only: bool = True
    bot_name: str = "executive-bot"
    bot_id: str = ""  # Bot user ID for self-message detection (optional, fetched if not provided)
    max_message_length: int = 40000


class Mattermost:
    """Mattermost interface for AgentOS.

    Mounts Mattermost event handlers and sends agent responses back to
    Mattermost channels and threads.

    Similar to Agno's Slack interface, but adapted for Mattermost API.

    Args:
        agent: Optional Agent to handle messages
        team: Optional Team to handle messages
        workflow: Optional Workflow to handle messages
        config: Mattermost configuration
        reply_to_mentions_only: Only respond to @mentions and DMs (default: True)

    Example:
        ```python
        from agno.agent import Agent
        from agno.os import AgentOS
        from agnoteamost.interfaces.mattermost import Mattermost

        agent = Agent(name="Bot", model=OpenAIChat(id="gpt-4o"))
        mattermost = Mattermost(
            agent=agent,
            config=MattermostConfig(
                url="mattermost.example.com",
                token="your-bot-token",
                team="main",
            ),
        )
        agent_os = AgentOS(agents=[agent], interfaces=[mattermost])
        app = agent_os.get_app()
        ```
    """

    def __init__(
        self,
        agent: Agent | None = None,
        team: Team | None = None,
        workflow: Workflow | None = None,
        config: MattermostConfig | None = None,
        reply_to_mentions_only: bool = True,
    ) -> None:
        if sum(x is not None for x in [agent, team, workflow]) != 1:
            raise ValueError("Exactly one of agent, team, or workflow must be provided")

        self.agent = agent
        self.team = team
        self.workflow = workflow
        self.config = config or MattermostConfig(
            url="localhost",
            token="",
            team="main",
        )
        self.reply_to_mentions_only = reply_to_mentions_only

        self._driver: Driver | None = None
        self._bot_user_id: str | None = None
        self._bot_username: str = config.bot_name if config else "executive-bot"
        self._running = False

    @property
    def entity(self) -> Agent | Team | Workflow:
        """Return the AI entity (agent, team, or workflow)."""
        if self.agent:
            return self.agent
        if self.team:
            return self.team
        if self.workflow:
            return self.workflow
        raise ValueError("No entity configured")

    @property
    def entity_name(self) -> str:
        """Return the name of the AI entity."""
        return self.entity.name or "AgentOS"

    def _init_driver(self) -> Driver:
        """Initialize the Mattermost driver."""
        # Parse URL to extract hostname (driver expects hostname only, not full URL)
        url = self.config.url
        if url.startswith("https://"):
            hostname = url.replace("https://", "")
            scheme = "https"
            port = 443
        elif url.startswith("http://"):
            hostname = url.replace("http://", "")
            scheme = "http"
            port = 80
        else:
            hostname = url
            scheme = self.config.scheme
            port = self.config.port

        # Remove trailing slash if present
        hostname = hostname.rstrip("/")

        driver = Driver({
            "url": hostname,
            "token": self.config.token,
            "scheme": scheme,
            "port": port,
            "basepath": "/api/v4",
            "verify": True,
            "timeout": 30,
        })
        return driver

    async def connect(self) -> None:
        """Connect to Mattermost and start listening for events."""
        self._driver = self._init_driver()
        self._driver.login()

        # Use configured bot_id if provided, otherwise fetch from API
        if self.config.bot_id:
            self._bot_user_id = self.config.bot_id
            logger.info(f"Using configured bot ID: {self._bot_user_id}")
        else:
            # Fetch bot user ID from API for self-message detection
            me = self._driver.users.get_user("me")
            self._bot_user_id = me.get("id")
            self._bot_username = me.get("username", self.config.bot_name)
            logger.info(f"Connected to Mattermost as {me.get('username')} (ID: {self._bot_user_id})")

        # Start WebSocket listener
        self._running = True
        self._driver.init_websocket(self._handle_websocket_event)

    async def disconnect(self) -> None:
        """Disconnect from Mattermost."""
        self._running = False
        if self._driver:
            self._driver.logout()

    async def _handle_websocket_event(self, event_json: str) -> None:
        """Handle incoming WebSocket events from Mattermost."""
        try:
            event = json.loads(event_json)
            event_type = event.get("event")

            if event_type == "posted":
                await self._handle_posted_event(event)
            elif event_type == "hello":
                logger.info("Mattermost WebSocket connection established")

        except Exception as e:
            logger.error(f"Error handling WebSocket event: {e}")

    async def _handle_posted_event(self, event: dict[str, Any]) -> None:
        """Handle a 'posted' event (new message)."""
        try:
            data = event.get("data", {})
            post_json = data.get("post", "{}")
            post = json.loads(post_json) if isinstance(post_json, str) else post_json

            # Extract message details
            message = post.get("message", "")
            channel_id = post.get("channel_id", "")
            user_id = post.get("user_id", "")
            post_id = post.get("id", "")
            root_id = post.get("root_id", "")  # Thread parent ID

            # Ignore messages from the bot itself
            if user_id == self._bot_user_id:
                return

            # Check if we should respond
            is_dm = data.get("channel_type") == "D"

            # Check for mentions - Mattermost uses @username format
            # Also check post props for explicit mentions
            props = post.get("props", {})
            mentioned_ids = props.get("mentioned_ids", []) or []
            is_explicit_mention = self._bot_user_id and self._bot_user_id in mentioned_ids
            is_text_mention = f"@{self._bot_username}" in message or f"@{self.config.bot_name}" in message
            is_mention = is_explicit_mention or is_text_mention

            if self.reply_to_mentions_only and not is_dm and not is_mention:
                return

            # Clean message (remove bot mention)
            clean_message = message.replace(f"@{self._bot_username}", "").replace(f"@{self.config.bot_name}", "").strip()

            if not clean_message:
                return

            logger.info(f"Processing message from user {user_id}: {clean_message[:50]}...")

            # Process message with agent/team/workflow
            response = await self._process_message(
                message=clean_message,
                user_id=user_id,
                channel_id=channel_id,
                thread_id=root_id or post_id,  # Use thread ID for session
            )

            # Send response back to Mattermost
            if response:
                await self._send_response(
                    channel_id=channel_id,
                    message=response,
                    root_id=root_id or post_id,  # Reply in thread
                )

        except Exception as e:
            logger.error(f"Error handling posted event: {e}")

    async def _process_message(
        self,
        message: str,
        user_id: str,
        channel_id: str,
        thread_id: str,
    ) -> str | None:
        """Process a message with the configured AI entity.

        Args:
            message: The user's message
            user_id: Mattermost user ID
            channel_id: Mattermost channel ID
            thread_id: Thread ID for session continuity

        Returns:
            The agent's response, or None if no response
        """
        try:
            # Use thread_id as session_id for conversation continuity
            session_id = f"mattermost_{channel_id}_{thread_id}"

            if self.agent:
                response = await self.agent.arun(
                    message=message,
                    session_id=session_id,
                )
                return response.content if response else None

            if self.team:
                response = await self.team.arun(
                    message=message,
                    session_id=session_id,
                )
                return response.content if response else None

            if self.workflow:
                response = await self.workflow.arun(
                    message=message,
                    session_id=session_id,
                )
                return response.content if response else None

            return None

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _send_response(
        self,
        channel_id: str,
        message: str,
        root_id: str | None = None,
    ) -> None:
        """Send a response back to Mattermost.

        Args:
            channel_id: Channel to send to
            message: Message content
            root_id: Parent post ID for threading
        """
        if not self._driver:
            logger.error("Driver not initialized")
            return

        try:
            # Split long messages
            messages = self._chunk_message(message)

            for msg in messages:
                post_data = {
                    "channel_id": channel_id,
                    "message": msg,
                }
                if root_id:
                    post_data["root_id"] = root_id

                self._driver.posts.create_post(post_data)
                await asyncio.sleep(0.1)  # Rate limiting

        except Exception as e:
            logger.error(f"Error sending response: {e}")

    def _chunk_message(self, message: str) -> list[str]:
        """Split a message into chunks if it exceeds max length."""
        if len(message) <= self.config.max_message_length:
            return [message]

        chunks = []
        while message:
            if len(message) <= self.config.max_message_length:
                chunks.append(message)
                break

            # Find a good split point (newline or space)
            split_point = self.config.max_message_length
            for char in ["\n\n", "\n", " "]:
                last_break = message[:split_point].rfind(char)
                if last_break > 0:
                    split_point = last_break
                    break

            chunks.append(message[:split_point])
            message = message[split_point:].lstrip()

        return chunks

    def attach_routes(self, app: Any) -> None:
        """Attach Mattermost routes to FastAPI app.

        This method is called by AgentOS to integrate the interface.

        Args:
            app: FastAPI application instance
        """
        from agnoteamost.interfaces.mattermost.router import attach_routes

        attach_routes(app, self)

    async def start_websocket_listener(self) -> None:
        """Start the WebSocket listener in background."""
        await self.connect()
        logger.info("Mattermost WebSocket listener started")

        # Keep running until stopped
        while self._running:
            await asyncio.sleep(1)
