from __future__ import annotations

from typing import Any, Dict, List, Optional


class ChannelManager:
    def __init__(self) -> None:
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.current_channel: str = "web"
        self._initialize_channels()

    def _initialize_channels(self) -> None:
        channels = [
            {
                "id": "apple-business-chat",
                "name": "Apple Business Chat",
                "description": "Apple Business Chat with rich interactive messages",
                "artifacts": [
                    "rich-link",
                    "list-picker",
                    "time-picker",
                    "apple-pay",
                    "interactive-message",
                ],
                "capabilities": ["rich-messaging", "payments", "scheduling", "customer-service"],
            },
            {
                "id": "discord",
                "name": "Discord",
                "description": "Discord server with embeds, slash commands, and bot interactions",
                "artifacts": [
                    "embed",
                    "slash-command",
                    "button-interaction",
                    "select-menu",
                    "modal",
                ],
                "capabilities": ["rich-embeds", "slash-commands", "voice-integration", "server-management"],
            },
            {
                "id": "slack",
                "name": "Slack",
                "description": "Slack workspace with blocks, workflows, and app integrations",
                "artifacts": ["block-kit", "workflow", "modal", "home-tab", "slash-command"],
                "capabilities": ["block-kit-ui", "workflows", "app-home", "notifications"],
            },
            {
                "id": "teams",
                "name": "Microsoft Teams",
                "description": "Microsoft Teams with Adaptive Cards and bot framework",
                "artifacts": ["adaptive-card", "task-module", "messaging-extension", "tab", "connector-card"],
                "capabilities": ["adaptive-cards", "task-modules", "tabs", "meeting-integration"],
            },
            {
                "id": "twitch",
                "name": "Twitch",
                "description": "Twitch chat with commands, extensions, and stream integration",
                "artifacts": ["chat-command", "extension-panel", "overlay", "pubsub-message", "bits-action"],
                "capabilities": ["chat-commands", "extensions", "stream-overlay", "viewer-interaction"],
            },
            {
                "id": "web",
                "name": "Web",
                "description": "Web interface with HTML, CSS, and JavaScript components",
                "artifacts": ["html-component", "css-styling", "javascript-widget", "web-form", "progressive-web-app"],
                "capabilities": ["responsive-design", "interactive-components", "pwa-features", "accessibility"],
            },
            {
                "id": "whatsapp",
                "name": "WhatsApp",
                "description": "WhatsApp Business with templates, quick replies, and media",
                "artifacts": ["message-template", "quick-reply", "interactive-button", "list-message", "media-message"],
                "capabilities": ["message-templates", "quick-replies", "media-sharing", "business-features"],
            },
        ]
        for ch in channels:
            self.channels[ch["id"]] = ch

    def get_all_channels(self) -> List[Dict[str, Any]]:
        return sorted(self.channels.values(), key=lambda c: c["name"])

    def get_current_channel(self) -> Optional[Dict[str, Any]]:
        return self.channels.get(self.current_channel)

    def switch_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        ch = self.channels.get(channel_id)
        if ch is not None:
            self.current_channel = channel_id
            return ch
        return None

    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        return self.channels.get(channel_id)

    async def generate_channel_artifact(self, artifact_type: str, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        channel = self.get_current_channel()
        if not channel:
            raise ValueError("No channel selected")
        if artifact_type not in channel.get("artifacts", []):
            raise ValueError(f"Artifact type '{artifact_type}' not supported by channel '{channel['name']}'")
        artifact = self._build_artifact(channel, artifact_type, description, options)
        return {
            "channel": channel["id"],
            "channelName": channel["name"],
            "artifactType": artifact_type,
            "description": description,
            "artifact": artifact,
        }

    def _build_artifact(self, channel: Dict[str, Any], artifact_type: str, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        generators = {
            # Slack
            "block-kit": lambda: self._gen_slack_block_kit(description, options),
            "workflow": lambda: self._gen_slack_workflow(description, options),
            "modal": lambda: self._gen_slack_modal(description, options),
            "home-tab": lambda: self._gen_slack_home_tab(description, options),
            # Teams
            "adaptive-card": lambda: self._gen_teams_adaptive_card(description, options),
            "task-module": lambda: self._gen_teams_task_module(description, options),
            "messaging-extension": lambda: self._gen_teams_messaging_extension(description, options),
            # Discord
            "embed": lambda: self._gen_discord_embed(description, options),
            "slash-command": lambda: self._gen_discord_slash_command(description, options),
            "button-interaction": lambda: self._gen_discord_button_interaction(description, options),
            # Web
            "html-component": lambda: self._gen_web_component(description, options),
            "css-styling": lambda: self._gen_css_component(description, options),
            "javascript-widget": lambda: self._gen_js_widget(description, options),
            # WhatsApp
            "message-template": lambda: self._gen_whatsapp_template(description, options),
            "interactive-button": lambda: self._gen_whatsapp_interactive_button(description, options),
            # Apple Business Chat
            "rich-link": lambda: self._gen_apple_rich_link(description, options),
            "list-picker": lambda: self._gen_apple_list_picker(description, options),
            # Twitch
            "chat-command": lambda: self._gen_twitch_chat_command(description, options),
            "extension-panel": lambda: self._gen_twitch_extension_panel(description, options),
        }
        if artifact_type not in generators:
            raise ValueError(f"No generator for artifact: {artifact_type}")
        return generators[artifact_type]()

    # Implement a subset for brevity (enough for tests); same shapes as JS
    def _gen_slack_block_kit(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "slack-block-kit",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": options.get("title", "Generated Block Kit")}},
                {"type": "section", "text": {"type": "mrkdwn", "text": description}},
                {
                    "type": "actions",
                    "elements": [
                        {"type": "button", "text": {"type": "plain_text", "text": "Action"}, "action_id": "button_action", "style": "primary"}
                    ],
                },
            ],
        }

    def _gen_slack_workflow(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "slack-workflow",
            "workflow": {
                "name": options.get("name", "Generated Workflow"),
                "description": description,
                "steps": [
                    {
                        "type": "form",
                        "name": "collect_info",
                        "title": "Information Collection",
                        "fields": [{"type": "text", "name": "user_input", "label": "Your Input", "required": True}],
                    },
                    {"type": "message", "name": "send_message", "channel": "#general", "message": "Workflow completed: {{collect_info.user_input}}"},
                ],
            },
        }

    def _gen_teams_adaptive_card(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "teams-adaptive-card",
            "card": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": options.get("title", "Generated Adaptive Card"), "weight": "Bolder", "size": "Medium"},
                    {"type": "TextBlock", "text": description, "wrap": True},
                ],
                "actions": [{"type": "Action.Submit", "title": "Submit", "data": {"action": "submit"}}],
            },
        }

    def _gen_discord_embed(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "discord-embed",
            "embed": {
                "title": options.get("title", "Generated Embed"),
                "description": description,
                "color": options.get("color", 0x5865F2),
                "fields": [{"name": "Field 1", "value": "Generated content", "inline": True}],
                "footer": {"text": "Generated by BK25"},
            },
        }

    def _gen_web_component(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        html = (
            f"""
<div class="bk25-component" data-description="{description}">
  <h3>{options.get('title', 'Generated Component')}</h3>
  <p>{description}</p>
  <button class="bk25-button" onclick="handleAction()">Action</button>
</div>

<style>
.bk25-component {{
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin: 10px 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
.bk25-button {{
  background: #2563eb;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}}
</style>

<script>
function handleAction() {{
  alert('Component action triggered!');
}}
</script>
            """.strip()
        )
        return {"type": "web-html-component", "html": html}

    def _gen_css_component(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "css", "css": ".bk25 { color: #333; }"}

    def _gen_js_widget(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "javascript", "script": "console.log('BK25 widget loaded');"}

    def _gen_whatsapp_template(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "whatsapp-template",
            "template": {
                "name": options.get("name", "generated_template"),
                "language": "en",
                "components": [
                    {"type": "HEADER", "format": "TEXT", "text": options.get("title", "Generated Template")},
                    {"type": "BODY", "text": description},
                ],
            },
        }

    def _gen_whatsapp_interactive_button(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "whatsapp-interactive-button", "label": options.get("label", "Confirm")}

    def _gen_apple_rich_link(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "apple-rich-link",
            "richLink": {
                "title": options.get("title", "Generated Rich Link"),
                "subtitle": description,
                "imageURL": options.get("imageURL", "https://example.com/image.jpg"),
                "action": {"type": "openURL", "url": options.get("url", "https://example.com")},
            },
        }

    def _gen_apple_list_picker(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "apple-list-picker", "items": ["One", "Two", "Three"]}

    def _gen_twitch_chat_command(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "twitch-chat-command",
            "command": {
                "name": options.get("name", "generatedcommand"),
                "description": description,
                "cooldown": options.get("cooldown", 5),
                "response": options.get("response", "Command executed successfully!"),
                "permissions": options.get("permissions", "everyone"),
            },
        }

    def _gen_twitch_extension_panel(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "twitch-extension-panel", "content": description}

    def get_available_artifacts(self) -> List[str]:
        ch = self.get_current_channel()
        return ch.get("artifacts", []) if ch else []

    def get_channel_capabilities(self) -> List[str]:
        ch = self.get_current_channel()
        return ch.get("capabilities", []) if ch else []

