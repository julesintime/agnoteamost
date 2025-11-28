"""Tests for Mattermost interface."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agnoteamost.interfaces.mattermost import Mattermost
from agnoteamost.interfaces.mattermost.mattermost import MattermostConfig


class TestMattermostConfig:
    """Tests for MattermostConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = MattermostConfig(url="test.com", token="test-token")
        assert config.url == "test.com"
        assert config.token == "test-token"
        assert config.team == "main"
        assert config.reply_to_mentions_only is True
        assert config.max_message_length == 40000

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = MattermostConfig(
            url="custom.com",
            token="custom-token",
            team="engineering",
            reply_to_mentions_only=False,
            bot_name="custom-bot",
        )
        assert config.url == "custom.com"
        assert config.team == "engineering"
        assert config.reply_to_mentions_only is False
        assert config.bot_name == "custom-bot"


class TestMattermost:
    """Tests for Mattermost interface."""

    def test_requires_one_entity(self) -> None:
        """Test that exactly one entity must be provided."""
        with pytest.raises(ValueError, match="Exactly one"):
            Mattermost()

    def test_accepts_agent(self) -> None:
        """Test that agent can be provided."""
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"

        interface = Mattermost(agent=mock_agent)
        assert interface.agent == mock_agent
        assert interface.entity == mock_agent

    def test_accepts_team(self) -> None:
        """Test that team can be provided."""
        mock_team = MagicMock()
        mock_team.name = "TestTeam"

        interface = Mattermost(team=mock_team)
        assert interface.team == mock_team
        assert interface.entity == mock_team

    def test_entity_name(self) -> None:
        """Test entity_name property."""
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"

        interface = Mattermost(agent=mock_agent)
        assert interface.entity_name == "TestAgent"

    def test_chunk_message_short(self) -> None:
        """Test that short messages are not chunked."""
        mock_agent = MagicMock()
        mock_agent.name = "Test"

        interface = Mattermost(agent=mock_agent)
        result = interface._chunk_message("Short message")
        assert result == ["Short message"]

    def test_chunk_message_long(self) -> None:
        """Test that long messages are chunked."""
        mock_agent = MagicMock()
        mock_agent.name = "Test"

        config = MattermostConfig(
            url="test.com",
            token="test",
            max_message_length=50,
        )
        interface = Mattermost(agent=mock_agent, config=config)

        long_message = "A" * 100
        result = interface._chunk_message(long_message)
        assert len(result) > 1
        assert all(len(chunk) <= 50 for chunk in result)


class TestMattermostSecurity:
    """Tests for Mattermost security utilities."""

    def test_validate_token_matching(self) -> None:
        """Test token validation with matching tokens."""
        from agnoteamost.interfaces.mattermost.security import validate_mattermost_token

        assert validate_mattermost_token("test-token", "test-token") is True

    def test_validate_token_mismatched(self) -> None:
        """Test token validation with mismatched tokens."""
        from agnoteamost.interfaces.mattermost.security import validate_mattermost_token

        assert validate_mattermost_token("wrong-token", "test-token") is False

    def test_validate_token_empty(self) -> None:
        """Test token validation with empty tokens."""
        from agnoteamost.interfaces.mattermost.security import validate_mattermost_token

        assert validate_mattermost_token("", "test-token") is False
        assert validate_mattermost_token("test-token", "") is False
        assert validate_mattermost_token(None, "test-token") is False
