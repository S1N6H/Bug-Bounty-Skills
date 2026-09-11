---
name: gateway-adapter-development
description: Develop, debug, and maintain Hermes gateway platform adapters (Telegram, Discord, Slack, Raft, etc.)
version: 1.0.0
author: Hermes Agent
license: MIT
---
# Hermes Gateway Adapter Development

This skill covers the development, debugging, and maintenance of Hermes gateway platform adapters. These adapters enable Hermes to connect to various messaging platforms like Telegram, Discord, Slack, WhatsApp, and specialized adapters like Raft.

## Overview

Gateway adapters live in `plugins/platforms/<platform>/adapter.py` and inherit from `BasePlatformAdapter`. They handle:
- Connecting to the platform
- Sending and receiving messages
- Handling platform-specific features (threads, reactions, etc.)
- Integrating with Hermes' session and messaging system

## Common Adapter Structure

```python
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from aiohttp import web  # Most adapters use aiohttp for webhooks
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)

logger = logging.getLogger(__name__)

class YourPlatformAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform("your_platform"))
        # Initialize adapter-specific attributes
        self._runner = None
        # ... other initialization

    async def connect(self, *, is_reconnect: bool = False) -> bool:
        """Set up the connection to the platform."""
        # Implementation specific to your platform
        pass

    async def disconnect(self) -> None:
        """Clean up the connection."""
        # Cleanup resources
        pass

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """Send a message to the platform."""
        # Implementation for sending messages
        return SendResult(success=True)

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Get information about a chat/channel."""
        # Return chat metadata
        return {"name": f"your_platform/{chat_id}", "type": "your_platform"}

    # Optional: Handle incoming webhooks/updates from the platform
    async def _handle_update(self, request: "web.Request") -> "web.Response":
        """Process incoming updates from the platform."""
        # Verify authenticity, parse update, convert to MessageEvent
        pass
```

## Development Best Practices

### 1. Platform-Specific Considerations
- **Authentication**: Handle API keys, OAuth tokens, or bot tokens securely
- **Rate Limits**: Implement rate limiting or backoff strategies as needed by the platform
- **Message Formatting**: Adapt to the platform's message formatting capabilities (Markdown, HTML, plain text)
- **Special Features**: Support for threads, reactions, attachments, etc. if applicable

### 2. Error Handling and Logging
- Use structured logging with meaningful context
- Catch and handle platform-specific exceptions
- Log connection/disconnection events for debugging
- Include relevant IDs (chat_id, user_id, message_id) in logs when appropriate

### 3. Declaring Long-Message Capability (`splits_long_messages`)

When your platform's transport has generous or no per-message size limit (SMTP, local filesystem, or an API with a high limit), and your `send()` method passes the full body through without its own chunking, the delivery router in `gateway/delivery.py` will truncate cron output at 4000 chars before it reaches your adapter — unless you declare capability.

Set `splits_long_messages: bool = True` as a class-level attribute on your adapter:

```python
class YourPlatformAdapter(BasePlatformAdapter):
    # Your platform's transport can handle long messages natively
    # (no practical per-message limit at the 4K truncation threshold).
    splits_long_messages = True
```

This tells `gateway/delivery.py` (via `getattr(adapter, "splits_long_messages", False)`) to skip the 4K truncation gate and pass the full payload through. The flag is checked as a class attribute — no `__init__` override needed.

**When to set it:**
- Your adapter's `send()` already has its own truncation/chunking logic (e.g. Telegram, Discord, Slack, Teams) → set `True` (the adapter splits natively).
- Your adapter uses SMTP (email), a local file write, or an API with no meaningful message cap → set `True` (the adapter can handle the full payload; no splitting needed).
- Your adapter uses a transport with a strict per-message limit and does NOT implement its own chunking → leave as `False` (default) — the delivery router truncates safely.

**Current adapters with `True`**: YuanBao, WhatsApp Cloud, BlueBubbles, Weixin, Teams, Discord, Slack, Matrix, WhatsApp native, Feishu, Mattermost, Telegram, Email. Default in `BasePlatformAdapter` is `False` (conservative).

See the `hermes-bugfixes` skill (`references/bug55-email-splits-long-messages.md`) for the original bug that motivated this pattern.

### 4. Testing Adapters
- Unit test adapter logic in isolation
- Use mock objects for platform API clients
- Test connection/disconnection sequences
- Verify message sending/receiving workflows
- Consider integration tests with test instances of the platform (if available)

## Troubleshooting Common Issues

### Raft Adapter: BRIDGE_ALREADY_RUNNING Error

**Problem**: When running Hermes in Raft bridge mode, after an unclean shutdown (crash, kill, restart), attempting to start the gateway fails with:
```
Error: raft agent bridge is already running for this profile/agent/adapter state.
Code: BRIDGE_ALREADY_RUNNING
```

**Root Cause**: The Raft adapter creates a lock file at `$HERMES_HOME/agent-comms-core/<agent-id>/default/bridge.lock` containing the PID of the bridge process. On unclean shutdown, this lock file is not cleaned up, causing subsequent starts to believe a bridge is still running.

**Solution**: Implement stale lock file detection and cleanup in the adapter's `_spawn_bridge` method:

```python
def _spawn_bridge(self, port: int) -> None:
    raft_bin = shutil.which("raft")
    if not raft_bin:
        logger.warning("[raft] raft CLI not found in PATH; bridge not spawned")
        return

    profile = os.environ.get("RAFT_PROFILE", "")
    if not profile:
        logger.warning("[raft] RAFT_PROFILE not set; bridge not spawned")
        return

    # Check for and remove stale lock file
    try:
        from hermes_agent.hermes_state import state_manager
        agent_id = state_manager.agent_id
    except Exception:
        agent_id = None
    
    if agent_id:
        hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
        lock_dir = os.path.join(hermes_home, "agent-comms-core", agent_id, "default")
        lock_file = os.path.join(lock_dir, "bridge.lock")
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    try:
                        # Check if process is still alive (signal 0 doesn't kill)
                        os.kill(pid, 0)
                        # Process exists, we will not remove the lock file
                        logger.warning(f"[raft] Lock file {lock_file} exists with PID {pid}, which is still alive. Not removing.")
                    except OSError:
                        # Process does not exist, remove the lock file
                        os.remove(lock_file)
                        logger.warning(f"[raft] Removed stale lock file {lock_file} (PID {pid})")
                else:
                    # Invalid PID in lock file, remove it
                    os.remove(lock_file)
                    logger.warning(f"[raft] Removed lock file {lock_file} with invalid PID {pid_str}")
            except Exception as e:
                logger.warning(f"[raft] Failed to check lock file {lock_file}: {e}")
    
    # Continue with normal bridge spawning...
    endpoint = f"http://{self._host}:{port}{self._path}"
    # ... rest of the method
```

### General Adapter Troubleshooting

1. **Connection Issues**:
   - Verify network connectivity to the platform's API
   - Check authentication credentials/tokens
   - Confirm required permissions/scopes are granted
   - Look for rate limit errors (HTTP 429)

2. **Message Delivery Problems**:
   - Check message formatting requirements for the platform
   - Verify chat/channel IDs are correct
   - Ensure the bot/user has permission to send in the target location
   - Inspect platform-specific message delivery requirements (thread IDs, etc.)

3. **Update/Webhook Handling**:
   - Verify webhook URL is correctly configured and accessible
   - Check signature/token validation for incoming requests
   - Ensure proper error responses (HTTP codes) for invalid requests
   - Validate payload structure before processing

## Debugging Techniques

### Enabling Adapter-Specific Logging
Most adapters use Python's logging module. To increase verbosity:
```bash
# Set environment variable for debug logging
export HERMES_LOG_LEVEL=DEBUG
# Or specifically for the adapter
export LOGGING_LEVEL_platforms.your_platform=DEBUG
```

### Inspecting Adapter State
- Check the adapter's connection status via `/platforms` slash command in gateway
- Review gateway logs for connection/disconnection events
- Monitor network traffic to/from the platform's API
- Verify adapter configuration is loaded correctly

## Testing Your Adapter

### Unit Testing Approach
1. Mock platform-specific API clients
2. Test connection/disconnection logic
3. Verify message formatting matches platform requirements
4. Test error handling paths (network errors, auth failures, etc.)
5. Validate state management (connected/disconnected flags)

### Integration Testing
1. Deploy to a test/staging environment
2. Use test accounts/bots on the target platform
3. Verify end-to-end message flow: send → receive → process
4. Test edge cases: network interruptions, rate limits, malformed inputs
5. Check resource cleanup on shutdown

## Publishing and Distribution

If you've developed an adapter for a platform not officially supported by Hermes:

1. Ensure your adapter follows the same structure as existing adapters
2. Add proper error handling and logging
3. Include documentation in the adapter's docstring and comments
4. Consider contributing upstream to the Hermes repository
5. Alternatively, users can install it as a custom plugin in `~/.hermes/plugins/`

## Resources

- Existing adapters: `plugins/platforms/` directory in the Hermes repository
- Base adapter documentation: `gateway/platforms/base.py`
- Platform-specific API documentation (refer to each platform's developer docs)
- Hermes gateway architecture: `gateway/run.py` and related files
- **[Inbound message pipeline & debounce pitfalls](references/inbound-message-pipeline-and-debounce-pitfalls.md)** — full message flow diagram, `rich_sent_store` reply resolution, debounce/merge field-carriage gaps, interrupt-vs-pending drain loop race condition, and debugging checklist
- **[Subprocess bridge pattern](references/subprocess-bridge-pattern.md)** — Python adapter spawning a Node.js subprocess with HTTP polling (WhatsApp, Minecraft via mineflayer, etc.)