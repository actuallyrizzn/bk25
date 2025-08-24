"""
Discord Channel Module

Provides Discord-specific artifact generation using embeds and slash commands.
Handles Discord bot interactions, rich embeds, and reactions.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class DiscordChannel(BaseChannel):
    """Discord channel with embeds and slash commands support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Discord',
            'id': 'discord',
            'capabilities': ['embeds', 'slash_commands', 'reactions', 'voice'],
            'artifact_types': ['embeds', 'slash_commands', 'components'],
            'metadata': {'color': '#5865F2', 'icon': '[DISCORD]'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate Discord-specific artifacts"""
        try:
            if request.type == 'embeds':
                return self._generate_embed(request.content, request.options)
            elif request.type == 'slash_commands':
                return self._generate_slash_command(request.content, request.options)
            elif request.type == 'components':
                return self._generate_component(request.content, request.options)
            else:
                return ArtifactResult(
                    success=False,
                    error=f"Unsupported artifact type: {request.type}"
                )
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Artifact generation failed: {str(e)}"
            )
    
    def _generate_embed(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Discord embed"""
        try:
            embed = {
                "title": content.get('title', 'BK25 Response'),
                "description": content.get('description', ''),
                "color": options.get('color', 0x5865F2) if options else 0x5865F2,
                "fields": [],
                "footer": {
                    "text": "BK25 - Multi-Persona Channel Simulator"
                }
            }
            
            # Add author if present
            if content.get('author'):
                embed['author'] = {
                    "name": content['author'].get('name', 'BK25'),
                    "icon_url": content['author'].get('icon_url', '')
                }
            
            # Add thumbnail if present
            if content.get('thumbnail'):
                embed['thumbnail'] = {
                    "url": content['thumbnail']
                }
            
            # Add fields if present
            if content.get('fields'):
                for field in content['fields']:
                    embed['fields'].append({
                        "name": field.get('name', ''),
                        "value": field.get('value', ''),
                        "inline": field.get('inline', False)
                    })
            
            # Add timestamp if present
            if content.get('timestamp'):
                embed['timestamp'] = content['timestamp']
            
            return ArtifactResult(
                success=True,
                artifact=embed,
                formatted_content=str(embed),
                metadata={
                    'platform': 'discord',
                    'type': 'embed',
                    'field_count': len(embed['fields'])
                }
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Embed generation failed: {str(e)}"
            )
    
    def _generate_slash_command(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Discord slash command"""
        try:
            command = {
                "name": content.get('name', 'bk25'),
                "description": content.get('description', 'BK25 command'),
                "options": []
            }
            
            # Add command options if present
            if content.get('options'):
                for option in content['options']:
                    command['options'].append({
                        "name": option.get('name', ''),
                        "description": option.get('description', ''),
                        "type": option.get('type', 3),  # String type
                        "required": option.get('required', False)
                    })
            
            return ArtifactResult(
                success=True,
                artifact=command,
                formatted_content=str(command),
                metadata={'platform': 'discord', 'type': 'slash_command'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Slash command generation failed: {str(e)}"
            )
    
    def _generate_component(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Discord component (buttons, select menus)"""
        try:
            component = {
                "type": content.get('type', 1),  # Action Row
                "components": []
            }
            
            # Add buttons if present
            if content.get('buttons'):
                for button in content['buttons']:
                    component['components'].append({
                        "type": 2,  # Button
                        "style": button.get('style', 1),  # Primary
                        "label": button.get('label', 'Button'),
                        "custom_id": button.get('id', 'button')
                    })
            
            return ArtifactResult(
                success=True,
                artifact=component,
                formatted_content=str(component),
                metadata={'platform': 'discord', 'type': 'component'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Component generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against Discord constraints"""
        constraints = self.get_constraints()
        
        # Discord has a 2000 character limit for messages
        max_length = 2000
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for Discord"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'title' in response and 'description' in response:
                return f"Discord Embed: {response['title']}"
            elif 'name' in response:
                return f"Discord Command: {response['name']}"
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get Discord-specific constraints"""
        return {
            'max_message_length': 2000,
            'supports_rich_text': True,
            'supports_media': True,
            'supports_interactive': True,
            'supports_embeds': True,
            'supports_slash_commands': True,
            'supports_components': True,
            'supports_reactions': True
        }
