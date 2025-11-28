"""FastAPI routes for Mattermost interface.

Provides HTTP endpoints for Mattermost webhook integration as an alternative
to WebSocket-based real-time events.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import BaseModel

if TYPE_CHECKING:
    from agnoteamost.interfaces.mattermost.mattermost import Mattermost

logger = logging.getLogger(__name__)


class MattermostOutgoingWebhook(BaseModel):
    """Mattermost outgoing webhook payload."""

    token: str | None = None
    team_id: str | None = None
    team_domain: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    timestamp: int | None = None
    user_id: str | None = None
    user_name: str | None = None
    post_id: str | None = None
    text: str | None = None
    trigger_word: str | None = None
    file_ids: str | None = None


class MattermostSlashCommand(BaseModel):
    """Mattermost slash command payload."""

    token: str | None = None
    team_id: str | None = None
    team_domain: str | None = None
    channel_id: str | None = None
    channel_name: str | None = None
    user_id: str | None = None
    user_name: str | None = None
    command: str | None = None
    text: str | None = None
    response_url: str | None = None
    trigger_id: str | None = None


class MattermostWebhookResponse(BaseModel):
    """Response format for Mattermost webhooks."""

    text: str | None = None
    response_type: str = "in_channel"  # or "ephemeral"
    username: str | None = None
    icon_url: str | None = None
    goto_location: str | None = None
    attachments: list[dict[str, Any]] | None = None


def attach_routes(app: FastAPI, interface: Mattermost) -> None:
    """Attach Mattermost HTTP routes to FastAPI app.

    Provides endpoints for:
    - Outgoing webhooks (for message-based triggers)
    - Slash commands (for /command triggers)
    - Health check

    Args:
        app: FastAPI application
        interface: Mattermost interface instance
    """

    @app.post("/mattermost/webhook", response_model=MattermostWebhookResponse)
    async def handle_outgoing_webhook(
        request: Request,
        webhook: MattermostOutgoingWebhook,
        background_tasks: BackgroundTasks,
    ) -> MattermostWebhookResponse:
        """Handle Mattermost outgoing webhook.

        This endpoint receives messages that match trigger words and
        returns a response to be posted in the channel.
        """
        logger.info(f"Received webhook from {webhook.user_name}: {webhook.text}")

        if not webhook.text:
            return MattermostWebhookResponse(text="No message provided")

        # Clean the message (remove trigger word if present)
        message = webhook.text
        if webhook.trigger_word:
            message = message.replace(webhook.trigger_word, "", 1).strip()

        if not message:
            return MattermostWebhookResponse(
                text="Hello! How can I help you?",
                response_type="in_channel",
            )

        try:
            # Process with agent/team/workflow
            session_id = f"mattermost_{webhook.channel_id}_{webhook.post_id}"

            if interface.agent:
                response = await interface.agent.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            elif interface.team:
                response = await interface.team.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            elif interface.workflow:
                response = await interface.workflow.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            else:
                response_text = "No agent configured."

            return MattermostWebhookResponse(
                text=response_text,
                response_type="in_channel",
                username=interface.entity_name,
            )

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return MattermostWebhookResponse(
                text=f"Sorry, I encountered an error: {str(e)}",
                response_type="ephemeral",
            )

    @app.post("/mattermost/command", response_model=MattermostWebhookResponse)
    async def handle_slash_command(
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> MattermostWebhookResponse:
        """Handle Mattermost slash command.

        Slash commands are invoked with /command syntax.
        Form data is sent as application/x-www-form-urlencoded.
        """
        form_data = await request.form()
        command = MattermostSlashCommand(
            token=form_data.get("token"),
            team_id=form_data.get("team_id"),
            channel_id=form_data.get("channel_id"),
            user_id=form_data.get("user_id"),
            user_name=form_data.get("user_name"),
            command=form_data.get("command"),
            text=form_data.get("text"),
            response_url=form_data.get("response_url"),
            trigger_id=form_data.get("trigger_id"),
        )

        logger.info(f"Received command {command.command} from {command.user_name}: {command.text}")

        message = command.text or ""
        if not message:
            return MattermostWebhookResponse(
                text=f"Usage: {command.command} <your question>",
                response_type="ephemeral",
            )

        try:
            session_id = f"mattermost_{command.channel_id}_{command.user_id}"

            if interface.agent:
                response = await interface.agent.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            elif interface.team:
                response = await interface.team.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            elif interface.workflow:
                response = await interface.workflow.arun(
                    message=message,
                    session_id=session_id,
                )
                response_text = response.content if response else "I couldn't generate a response."

            else:
                response_text = "No agent configured."

            return MattermostWebhookResponse(
                text=response_text,
                response_type="in_channel",
                username=interface.entity_name,
            )

        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return MattermostWebhookResponse(
                text=f"Sorry, I encountered an error: {str(e)}",
                response_type="ephemeral",
            )

    @app.get("/mattermost/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint for Mattermost integration."""
        return {
            "status": "healthy",
            "interface": "mattermost",
            "entity": interface.entity_name,
        }
