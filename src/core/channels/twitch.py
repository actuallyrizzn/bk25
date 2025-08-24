"""
Twitch Channel Module

Provides Twitch-specific artifact generation for chat commands and extensions.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class TwitchChannel(BaseChannel):
    """Twitch channel with chat commands and extensions support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Twitch',
            'id': 'twitch',
            'capabilities': ['chat_commands', 'extensions', 'moderation', 'alerts'],
            'artifact_types': ['chat_commands', 'extensions'],
            'metadata': {'color': '#9146FF', 'icon': '📺'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate Twitch-specific artifacts"""
        try:
            if request.type == 'chat_commands':
                return self._generate_chat_command(request.content, request.options)
            elif request.type == 'extensions':
                return self._generate_extension(request.content, request.options)
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
    
    def _generate_chat_command(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Twitch chat command"""
        try:
            command = {
                "command": content.get('command', '!bk25'),
                "description": content.get('description', 'BK25 command'),
                "usage": content.get('usage', '!bk25 [action]'),
                "cooldown": content.get('cooldown', 30),
                "permissions": content.get('permissions', ['everyone'])
            }
            
            return ArtifactResult(
                success=True,
                artifact=command,
                formatted_content=str(command),
                metadata={'platform': 'twitch', 'type': 'chat_command'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Chat command generation failed: {str(e)}"
            )
    
    def _generate_extension(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Twitch extension"""
        try:
            extension = {
                "name": content.get('name', 'BK25 Extension'),
                "description": content.get('description', 'BK25 Twitch Extension'),
                "version": content.get('version', '1.0.0'),
                "type": content.get('type', 'panel')
            }
            
            return ArtifactResult(
                success=True,
                artifact=extension,
                formatted_content=str(extension),
                metadata={'platform': 'twitch', 'type': 'extension'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Extension generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against Twitch constraints"""
        constraints = self.get_constraints()
        
        # Twitch has a 500 character limit for chat messages
        max_length = 500
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for Twitch"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'command' in response:
                return f"Twitch Command: {response['command']}"
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get Twitch-specific constraints"""
        return {
            'max_message_length': 500,
            'supports_rich_text': False,
            'supports_media': False,
            'supports_interactive': False,
            'supports_chat_commands': True,
            'supports_extensions': True
        }
