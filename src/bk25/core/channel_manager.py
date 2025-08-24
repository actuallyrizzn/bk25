"""
BK25 Channel Manager

Handles channel simulation and generation of channel-specific artifacts
like Teams Adaptive Cards, Slack workflows, Discord embeds, etc.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from ..models.channel import Channel, ChannelCapability, ChannelMessage, ChannelArtifact


class ChannelManager:
    """Manages channel simulation and artifact generation"""
    
    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.current_channel = "web"
        self.initialize_channels()
    
    def initialize_channels(self) -> None:
        """Initialize supported channels with their capabilities"""
        channels_data = [
            {
                "id": "apple-business-chat",
                "name": "Apple Business Chat",
                "description": "Apple Business Chat with rich interactive messages",
                "artifact_types": ["rich-link", "list-picker", "time-picker", "apple-pay", "interactive-message"],
                "native_features": ["rich-messaging", "payments", "scheduling", "customer-service"]
            },
            {
                "id": "discord",
                "name": "Discord",
                "description": "Discord server with embeds, slash commands, and bot interactions",
                "artifact_types": ["embed", "slash-command", "button-interaction", "select-menu", "modal"],
                "native_features": ["rich-embeds", "slash-commands", "voice-integration", "server-management"]
            },
            {
                "id": "slack",
                "name": "Slack",
                "description": "Slack workspace with blocks, workflows, and app integrations",
                "artifact_types": ["block-kit", "workflow", "modal", "home-tab", "slash-command"],
                "native_features": ["block-kit-ui", "workflows", "app-home", "notifications"]
            },
            {
                "id": "teams",
                "name": "Microsoft Teams",
                "description": "Microsoft Teams with Adaptive Cards and bot framework",
                "artifact_types": ["adaptive-card", "task-module", "messaging-extension", "tab", "connector-card"],
                "native_features": ["adaptive-cards", "task-modules", "tabs", "meeting-integration"]
            },
            {
                "id": "twitch",
                "name": "Twitch",
                "description": "Twitch chat with commands, extensions, and stream integration",
                "artifact_types": ["chat-command", "extension-panel", "overlay", "pubsub-message", "bits-action"],
                "native_features": ["chat-commands", "extensions", "stream-overlay", "viewer-interaction"]
            },
            {
                "id": "web",
                "name": "Web",
                "description": "Web interface with HTML, CSS, and JavaScript components",
                "artifact_types": ["html-component", "css-styling", "javascript-widget", "web-form", "progressive-web-app"],
                "native_features": ["responsive-design", "interactive-components", "pwa-features", "accessibility"]
            },
            {
                "id": "whatsapp",
                "name": "WhatsApp",
                "description": "WhatsApp Business with templates, quick replies, and media",
                "artifact_types": ["message-template", "quick-reply", "interactive-button", "list-message", "media-message"],
                "native_features": ["message-templates", "quick-replies", "media-sharing", "business-features"]
            }
        ]
        
        for channel_data in channels_data:
            # Create capabilities from artifact types
            capabilities = [
                ChannelCapability(
                    name=artifact_type.replace("-", " ").title(),
                    description=f"Generate {artifact_type} artifacts",
                    artifacts=[artifact_type]
                )
                for artifact_type in channel_data["artifact_types"]
            ]
            
            channel = Channel(
                id=channel_data["id"],
                name=channel_data["name"],
                description=channel_data["description"],
                capabilities=capabilities,
                native_features=channel_data["native_features"],
                artifact_types=channel_data["artifact_types"]
            )
            self.channels[channel.id] = channel
        
        print(f"📺 Channel Manager initialized with {len(self.channels)} channels")
    
    def get_all_channels(self) -> List[Channel]:
        """Get all available channels"""
        return sorted(self.channels.values(), key=lambda c: c.name)
    
    def get_current_channel(self) -> Optional[Channel]:
        """Get current channel"""
        return self.channels.get(self.current_channel)
    
    def switch_channel(self, channel_id: str) -> Optional[Channel]:
        """Switch to a different channel"""
        channel = self.channels.get(channel_id)
        if channel:
            self.current_channel = channel_id
            print(f"📺 Switched to channel: {channel.name} ({channel.id})")
            return channel
        else:
            print(f"⚠️ Channel not found: {channel_id}")
            return None
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        return self.channels.get(channel_id)
    
    async def generate_channel_artifact(
        self, 
        artifact_type: str, 
        description: str, 
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate channel-specific artifact"""
        channel = self.get_current_channel()
        if not channel:
            raise ValueError("No channel selected")
        
        if artifact_type not in channel.artifact_types:
            raise ValueError(f"Artifact type '{artifact_type}' not supported by channel '{channel.name}'")
        
        options = options or {}
        
        # Generate the artifact based on channel and type
        artifact = await self.build_artifact(channel, artifact_type, description, options)
        
        return {
            "channel": channel.id,
            "channel_name": channel.name,
            "artifact_type": artifact_type,
            "description": description,
            "artifact": artifact,
            "generated_at": datetime.now().isoformat()
        }
    
    async def build_artifact(
        self, 
        channel: Channel, 
        artifact_type: str, 
        description: str, 
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build specific artifact for channel"""
        generators = {
            # Slack artifacts
            "block-kit": lambda: self.generate_slack_block_kit(description, options),
            "workflow": lambda: self.generate_slack_workflow(description, options),
            "modal": lambda: self.generate_slack_modal(description, options),
            "home-tab": lambda: self.generate_slack_home_tab(description, options),
            
            # Teams artifacts
            "adaptive-card": lambda: self.generate_teams_adaptive_card(description, options),
            "task-module": lambda: self.generate_teams_task_module(description, options),
            "messaging-extension": lambda: self.generate_teams_messaging_extension(description, options),
            
            # Discord artifacts
            "embed": lambda: self.generate_discord_embed(description, options),
            "slash-command": lambda: self.generate_discord_slash_command(description, options),
            "button-interaction": lambda: self.generate_discord_button_interaction(description, options),
            
            # Web artifacts
            "html-component": lambda: self.generate_web_component(description, options),
            "css-styling": lambda: self.generate_css_component(description, options),
            "javascript-widget": lambda: self.generate_javascript_widget(description, options),
            
            # WhatsApp artifacts
            "message-template": lambda: self.generate_whatsapp_template(description, options),
            "interactive-button": lambda: self.generate_whatsapp_interactive_button(description, options),
            
            # Apple Business Chat artifacts
            "rich-link": lambda: self.generate_apple_rich_link(description, options),
            "list-picker": lambda: self.generate_apple_list_picker(description, options),
            
            # Twitch artifacts
            "chat-command": lambda: self.generate_twitch_chat_command(description, options),
            "extension-panel": lambda: self.generate_twitch_extension_panel(description, options)
        }
        
        generator = generators.get(artifact_type)
        if not generator:
            raise ValueError(f"No generator found for artifact type: {artifact_type}")
        
        return generator()
    
    # Slack artifact generators
    def generate_slack_block_kit(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Slack Block Kit UI"""
        return {
            "type": "slack-block-kit",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": options.get("title", "Generated Block Kit")
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": description
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Action"
                            },
                            "action_id": "button_action",
                            "style": "primary"
                        }
                    ]
                }
            ]
        }
    
    def generate_slack_workflow(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Slack Workflow"""
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
                        "fields": [
                            {
                                "type": "text",
                                "name": "user_input",
                                "label": "Your Input",
                                "required": True
                            }
                        ]
                    },
                    {
                        "type": "message",
                        "name": "send_message",
                        "channel": "#general",
                        "message": "Workflow completed: {{collect_info.user_input}}"
                    }
                ]
            }
        }
    
    def generate_slack_modal(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Slack Modal"""
        return {
            "type": "slack-modal",
            "modal": {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": options.get("title", "Generated Modal")
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": description
                        }
                    }
                ]
            }
        }
    
    def generate_slack_home_tab(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Slack Home Tab"""
        return {
            "type": "slack-home-tab",
            "home": {
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{options.get('title', 'Generated Home Tab')}*\n\n{description}"
                        }
                    }
                ]
            }
        }
    
    # Teams artifact generators
    def generate_teams_adaptive_card(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Teams Adaptive Card"""
        return {
            "type": "teams-adaptive-card",
            "card": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": options.get("title", "Generated Adaptive Card"),
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": description,
                        "wrap": True
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Submit",
                        "data": {
                            "action": "submit"
                        }
                    }
                ]
            }
        }
    
    def generate_teams_task_module(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Teams Task Module"""
        return {
            "type": "teams-task-module",
            "task": {
                "type": "continue",
                "value": {
                    "title": options.get("title", "Generated Task Module"),
                    "height": options.get("height", 500),
                    "width": options.get("width", 600),
                    "url": options.get("url", "https://example.com/task")
                }
            }
        }
    
    def generate_teams_messaging_extension(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Teams Messaging Extension"""
        return {
            "type": "teams-messaging-extension",
            "extension": {
                "composeExtensionType": "result",
                "composeExtensionQueryOptions": {
                    "queryParameterName": "search"
                },
                "composeExtensionResponse": {
                    "type": "result",
                    "attachmentLayout": "list",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.card.adaptive",
                            "content": description
                        }
                    ]
                }
            }
        }
    
    # Discord artifact generators
    def generate_discord_embed(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Discord Embed"""
        return {
            "type": "discord-embed",
            "embed": {
                "title": options.get("title", "Generated Embed"),
                "description": description,
                "color": options.get("color", 0x5865F2),
                "fields": [
                    {
                        "name": "Field 1",
                        "value": "Generated content",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Generated by BK25"
                },
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def generate_discord_slash_command(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Discord Slash Command"""
        return {
            "type": "discord-slash-command",
            "command": {
                "name": options.get("name", "generated_command"),
                "description": description,
                "options": [
                    {
                        "name": "parameter",
                        "description": "Command parameter",
                        "type": 3,  # STRING type
                        "required": False
                    }
                ]
            }
        }
    
    def generate_discord_button_interaction(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Discord Button Interaction"""
        return {
            "type": "discord-button-interaction",
            "components": [
                {
                    "type": 1,  # ACTION_ROW
                    "components": [
                        {
                            "type": 2,  # BUTTON
                            "style": 1,  # PRIMARY
                            "label": options.get("label", "Generated Button"),
                            "custom_id": "generated_button_action"
                        }
                    ]
                }
            ]
        }
    
    # Web artifact generators
    def generate_web_component(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Web HTML Component"""
        title = options.get("title", "Generated Component")
        return {
            "type": "web-html-component",
            "html": f"""
<div class="bk25-component" data-description="{description}">
  <h3>{title}</h3>
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
        }
    
    def generate_css_component(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSS Styling Component"""
        return {
            "type": "web-css-component",
            "css": f"""
/* Generated CSS for: {description} */
.generated-component {{
  /* Component styles */
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}}

.generated-component h3 {{
  margin: 0;
  color: #1f2937;
  font-weight: 600;
}}

.generated-component p {{
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}}
            """.strip()
        }
    
    def generate_javascript_widget(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JavaScript Widget"""
        widget_name = options.get("name", "GeneratedWidget")
        return {
            "type": "web-javascript-widget",
            "javascript": f"""
// Generated JavaScript Widget: {description}
class {widget_name} {{
  constructor(element) {{
    this.element = element;
    this.init();
  }}
  
  init() {{
    this.render();
    this.bindEvents();
  }}
  
  render() {{
    this.element.innerHTML = `
      <div class="widget-container">
        <h3>{options.get("title", "Generated Widget")}</h3>
        <p>{description}</p>
        <button class="widget-action">Click Me</button>
      </div>
    `;
  }}
  
  bindEvents() {{
    const button = this.element.querySelector('.widget-action');
    button.addEventListener('click', () => {{
      this.handleAction();
    }});
  }}
  
  handleAction() {{
    console.log('Widget action triggered!');
    // Add your custom logic here
  }}
}}

// Initialize widget
document.addEventListener('DOMContentLoaded', () => {{
  const widgets = document.querySelectorAll('.{widget_name.lower()}-container');
  widgets.forEach(widget => new {widget_name}(widget));
}});
            """.strip()
        }
    
    # WhatsApp artifact generators
    def generate_whatsapp_template(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WhatsApp Message Template"""
        return {
            "type": "whatsapp-template",
            "template": {
                "name": options.get("name", "generated_template"),
                "language": "en",
                "components": [
                    {
                        "type": "HEADER",
                        "format": "TEXT",
                        "text": options.get("title", "Generated Template")
                    },
                    {
                        "type": "BODY",
                        "text": description
                    },
                    {
                        "type": "BUTTONS",
                        "buttons": [
                            {
                                "type": "QUICK_REPLY",
                                "text": "Yes"
                            },
                            {
                                "type": "QUICK_REPLY",
                                "text": "No"
                            }
                        ]
                    }
                ]
            }
        }
    
    def generate_whatsapp_interactive_button(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WhatsApp Interactive Button"""
        return {
            "type": "whatsapp-interactive-button",
            "interactive": {
                "type": "button",
                "body": {
                    "text": description
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "button_1",
                                "title": options.get("button_text", "Action")
                            }
                        }
                    ]
                }
            }
        }
    
    # Apple Business Chat artifact generators
    def generate_apple_rich_link(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Apple Business Chat Rich Link"""
        return {
            "type": "apple-rich-link",
            "richLink": {
                "title": options.get("title", "Generated Rich Link"),
                "subtitle": description,
                "imageURL": options.get("imageURL", "https://example.com/image.jpg"),
                "action": {
                    "type": "openURL",
                    "url": options.get("url", "https://example.com")
                }
            }
        }
    
    def generate_apple_list_picker(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Apple Business Chat List Picker"""
        return {
            "type": "apple-list-picker",
            "listPicker": {
                "receivedMessage": {
                    "title": options.get("title", "Generated List Picker"),
                    "subtitle": description
                },
                "sections": [
                    {
                        "title": "Options",
                        "items": [
                            {
                                "title": "Option 1",
                                "subtitle": "First option",
                                "identifier": "option_1"
                            },
                            {
                                "title": "Option 2", 
                                "subtitle": "Second option",
                                "identifier": "option_2"
                            }
                        ]
                    }
                ]
            }
        }
    
    # Twitch artifact generators
    def generate_twitch_chat_command(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Twitch Chat Command"""
        return {
            "type": "twitch-chat-command",
            "command": {
                "name": options.get("name", "generatedcommand"),
                "description": description,
                "cooldown": options.get("cooldown", 5),
                "response": options.get("response", "Command executed successfully!"),
                "permissions": options.get("permissions", "everyone")
            }
        }
    
    def generate_twitch_extension_panel(self, description: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Twitch Extension Panel"""
        return {
            "type": "twitch-extension-panel",
            "panel": {
                "title": options.get("title", "Generated Extension Panel"),
                "description": description,
                "html": f"""
                <div class="twitch-panel">
                    <h3>{options.get("title", "Generated Panel")}</h3>
                    <p>{description}</p>
                    <button onclick="handlePanelAction()">Panel Action</button>
                </div>
                <script>
                function handlePanelAction() {{
                    Twitch.ext.rig.log('Panel action triggered!');
                }}
                </script>
                """.strip()
            }
        }
    
    def get_available_artifacts(self) -> List[str]:
        """Get available artifacts for current channel"""
        channel = self.get_current_channel()
        return channel.artifact_types if channel else []
    
    def get_channel_capabilities(self) -> List[str]:
        """Get channel capabilities"""
        channel = self.get_current_channel()
        return channel.native_features if channel else []