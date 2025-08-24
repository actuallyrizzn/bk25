"""
Slack Channel Module

Provides Slack-specific artifact generation using Block Kit.
Handles Slack UI components, workflows, and app integrations.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class SlackChannel(BaseChannel):
    """Slack channel with Block Kit support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Slack',
            'id': 'slack',
            'capabilities': ['blocks', 'threads', 'reactions', 'slash_commands'],
            'artifact_types': ['blocks', 'attachments', 'modals'],
            'metadata': {'color': '#4A154B', 'icon': '[SLACK]'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate Slack-specific artifacts"""
        try:
            if request.type == 'blocks':
                return self._generate_block_kit(request.content, request.options)
            elif request.type == 'attachments':
                return self._generate_attachment(request.content, request.options)
            elif request.type == 'modals':
                return self._generate_modal(request.content, request.options)
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
    
    def _generate_block_kit(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Slack Block Kit UI components"""
        try:
            blocks = []
            
            # Add header section
            if options and options.get('show_header', True):
                blocks.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": content.get('title', 'BK25 Response'),
                        "emoji": True
                    }
                })
            
            # Add main content
            if content.get('text'):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": content['text']
                    }
                })
            
            # Add code blocks if present
            if content.get('code'):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{content.get('language', 'text')}\n{content['code']}\n```"
                    }
                })
            
            # Add action buttons if present
            if content.get('actions'):
                actions = []
                for action in content['actions']:
                    actions.append({
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": action.get('label', 'Action'),
                            "emoji": True
                        },
                        "value": action.get('value', ''),
                        "action_id": action.get('id', 'action')
                    })
                
                if actions:
                    blocks.append({
                        "type": "actions",
                        "elements": actions
                    })
            
            return ArtifactResult(
                success=True,
                artifact={
                    "blocks": blocks,
                    "channel": options.get('channel', 'general'),
                    "thread_ts": options.get('thread_ts')
                },
                formatted_content=str(blocks),
                metadata={
                    'platform': 'slack',
                    'block_count': len(blocks),
                    'supports_threading': True
                }
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Block Kit generation failed: {str(e)}"
            )
    
    def _generate_attachment(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Slack attachment"""
        try:
            attachment = {
                "color": options.get('color', '#36a64f') if options else '#36a64f',
                "title": content.get('title', 'BK25 Attachment'),
                "text": content.get('text', ''),
                "fields": []
            }
            
            # Add fields if present
            if content.get('fields'):
                for field in content['fields']:
                    attachment['fields'].append({
                        "title": field.get('title', ''),
                        "value": field.get('value', ''),
                        "short": field.get('short', True)
                    })
            
            return ArtifactResult(
                success=True,
                artifact=attachment,
                formatted_content=str(attachment),
                metadata={'platform': 'slack', 'type': 'attachment'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Attachment generation failed: {str(e)}"
            )
    
    def _generate_modal(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Slack modal"""
        try:
            modal = {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": content.get('title', 'BK25 Modal'),
                    "emoji": True
                },
                "submit": {
                    "type": "plain_text",
                    "text": content.get('submit_text', 'Submit'),
                    "emoji": True
                },
                "close": {
                    "type": "plain_text",
                    "text": content.get('close_text', 'Cancel'),
                    "emoji": True
                },
                "blocks": []
            }
            
            # Add input blocks
            if content.get('inputs'):
                for input_field in content['inputs']:
                    modal['blocks'].append({
                        "type": "input",
                        "block_id": input_field.get('id', 'input'),
                        "label": {
                            "type": "plain_text",
                            "text": input_field.get('label', 'Input'),
                            "emoji": True
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": input_field.get('action_id', 'input'),
                            "placeholder": {
                                "type": "plain_text",
                                "text": input_field.get('placeholder', 'Enter text...')
                            }
                        }
                    })
            
            return ArtifactResult(
                success=True,
                artifact=modal,
                formatted_content=str(modal),
                metadata={'platform': 'slack', 'type': 'modal'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Modal generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against Slack constraints"""
        constraints = self.get_constraints()
        
        # Slack has a 3000 character limit for messages
        max_length = 3000
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for Slack"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'blocks' in response:
                return f"Slack Block Kit: {len(response['blocks'])} blocks"
            elif 'text' in response:
                return response['text']
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get Slack-specific constraints"""
        return {
            'max_message_length': 3000,
            'supports_rich_text': True,
            'supports_media': True,
            'supports_interactive': True,
            'supports_threading': True,
            'supports_reactions': True,
            'supports_blocks': True,
            'supports_modals': True
        }
