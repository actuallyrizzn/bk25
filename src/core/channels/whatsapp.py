"""
WhatsApp Channel Module

Provides WhatsApp-specific artifact generation for business messaging.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class WhatsAppChannel(BaseChannel):
    """WhatsApp channel with business messaging support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'WhatsApp',
            'id': 'whatsapp',
            'capabilities': ['media', 'templates', 'quick_replies', 'location'],
            'artifact_types': ['templates', 'media', 'interactive'],
            'metadata': {'color': '#25D366', 'icon': '[WHATSAPP]'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate WhatsApp-specific artifacts"""
        try:
            if request.type == 'templates':
                return self._generate_template(request.content, request.options)
            elif request.type == 'media':
                return self._generate_media(request.content, request.options)
            elif request.type == 'interactive':
                return self._generate_interactive(request.content, request.options)
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
    
    def _generate_template(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate WhatsApp message template"""
        try:
            template = {
                "name": content.get('name', 'bk25_template'),
                "language": content.get('language', 'en'),
                "components": []
            }
            
            # Add header if present
            if content.get('header'):
                template['components'].append({
                    "type": "header",
                    "text": content['header']
                })
            
            # Add body
            if content.get('body'):
                template['components'].append({
                    "type": "body",
                    "text": content['body']
                })
            
            # Add buttons if present
            if content.get('buttons'):
                template['components'].append({
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": 0,
                    "parameters": [{"type": "text", "text": content['buttons'][0]}]
                })
            
            return ArtifactResult(
                success=True,
                artifact=template,
                formatted_content=str(template),
                metadata={'platform': 'whatsapp', 'type': 'template'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Template generation failed: {str(e)}"
            )
    
    def _generate_media(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate WhatsApp media message"""
        try:
            media = {
                "type": content.get('media_type', 'image'),
                "url": content.get('url', ''),
                "caption": content.get('caption', '')
            }
            
            return ArtifactResult(
                success=True,
                artifact=media,
                formatted_content=str(media),
                metadata={'platform': 'whatsapp', 'type': 'media'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Media generation failed: {str(e)}"
            )
    
    def _generate_interactive(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate WhatsApp interactive message"""
        try:
            interactive = {
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": content.get('text', '')},
                    "action": {
                        "buttons": []
                    }
                }
            }
            
            # Add buttons
            if content.get('buttons'):
                for button in content['buttons']:
                    interactive['interactive']['action']['buttons'].append({
                        "type": "reply",
                        "reply": {"id": button.get('id', ''), "title": button.get('title', '')}
                    })
            
            return ArtifactResult(
                success=True,
                artifact=interactive,
                formatted_content=str(interactive),
                metadata={'platform': 'whatsapp', 'type': 'interactive'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Interactive generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against WhatsApp constraints"""
        constraints = self.get_constraints()
        
        # WhatsApp has a 4096 character limit for messages
        max_length = 4096
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for WhatsApp"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'name' in response:
                return f"WhatsApp Template: {response['name']}"
            elif 'type' in response:
                return f"WhatsApp {response['type']} message"
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get WhatsApp-specific constraints"""
        return {
            'max_message_length': 4096,
            'supports_rich_text': False,
            'supports_media': True,
            'supports_interactive': True,
            'supports_templates': True,
            'supports_quick_replies': True
        }
