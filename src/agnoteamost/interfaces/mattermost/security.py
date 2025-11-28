"""Security utilities for Mattermost interface.

Provides token validation for Mattermost webhooks and slash commands.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def validate_mattermost_token(
    request_token: str | None,
    expected_token: str,
) -> bool:
    """Validate Mattermost webhook/slash command token.

    Mattermost uses a simple token-based authentication for webhooks.

    Args:
        request_token: Token from the incoming request
        expected_token: Expected token configured in Mattermost

    Returns:
        True if tokens match, False otherwise
    """
    if not request_token or not expected_token:
        return False

    return hmac.compare_digest(request_token, expected_token)


def validate_request_timestamp(
    timestamp: int | str | None,
    max_age_seconds: int = 300,
) -> bool:
    """Validate that request timestamp is within acceptable range.

    Helps prevent replay attacks by rejecting old requests.

    Args:
        timestamp: Unix timestamp from request (seconds)
        max_age_seconds: Maximum acceptable age in seconds (default: 5 minutes)

    Returns:
        True if timestamp is valid, False otherwise
    """
    if timestamp is None:
        return False

    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False

    current_time = int(time.time())
    age = abs(current_time - ts)

    return age <= max_age_seconds


def generate_response_signature(
    response_body: str,
    secret: str,
    timestamp: int | None = None,
) -> str:
    """Generate HMAC signature for response.

    Can be used if Mattermost is configured to verify response signatures.

    Args:
        response_body: Response body content
        secret: Signing secret
        timestamp: Unix timestamp (uses current time if not provided)

    Returns:
        HMAC-SHA256 signature
    """
    if timestamp is None:
        timestamp = int(time.time())

    sig_basestring = f"v0:{timestamp}:{response_body}"
    signature = hmac.new(
        secret.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"v0={signature}"


async def verify_webhook_request(
    request: Request,
    webhook_token: str | None,
    expected_token: str,
) -> None:
    """Verify an incoming webhook request.

    Raises HTTPException if verification fails.

    Args:
        request: FastAPI request object
        webhook_token: Token from webhook payload
        expected_token: Expected token

    Raises:
        HTTPException: If verification fails
    """
    if not expected_token:
        # No token configured, skip validation
        logger.warning("No webhook token configured, skipping validation")
        return

    if not validate_mattermost_token(webhook_token, expected_token):
        logger.warning("Invalid webhook token")
        raise HTTPException(status_code=401, detail="Invalid token")


class MattermostSecurityMiddleware:
    """Middleware for Mattermost request security.

    Validates tokens and timestamps for all Mattermost endpoints.
    """

    def __init__(self, expected_token: str | None = None) -> None:
        """Initialize security middleware.

        Args:
            expected_token: Expected webhook token
        """
        self.expected_token = expected_token

    async def verify_request(
        self,
        request: Request,
        token: str | None = None,
        timestamp: int | None = None,
    ) -> None:
        """Verify an incoming request.

        Args:
            request: FastAPI request
            token: Token from request
            timestamp: Timestamp from request

        Raises:
            HTTPException: If verification fails
        """
        # Validate token if configured
        if self.expected_token:
            if not validate_mattermost_token(token, self.expected_token):
                raise HTTPException(status_code=401, detail="Invalid token")

        # Validate timestamp if provided
        if timestamp is not None:
            if not validate_request_timestamp(timestamp):
                raise HTTPException(status_code=401, detail="Request too old")
