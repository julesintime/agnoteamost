"""Mattermost interface for AgentOS.

This module provides Mattermost integration for AgentOS, allowing agents
to receive messages from and send responses to Mattermost channels and DMs.

Based on the Agno Slack interface pattern, adapted for Mattermost API.
"""

from agnoteamost.interfaces.mattermost.mattermost import Mattermost

__all__ = ["Mattermost"]
