"""
Microsoft Teams Channel Module

Provides Teams-specific artifact generation using Adaptive Cards.
Handles Teams UI components, task modules, and bot framework integration.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class TeamsChannel(BaseChannel):
    """Microsoft Teams channel with Adaptive Cards support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Microsoft Teams',
            'id': 'teams',
            'capabilities': ['adaptive_cards', 'task_modules', 'bot_framework', 'tabs'],
            'artifact_types': ['adaptive_cards', 'task_modules', 'bot_activities'],
            'metadata': {'color': '#6264A7', 'icon': '🏢'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate Teams-specific artifacts"""
        try:
            if request.type == 'adaptive_cards':
                return self._generate_adaptive_card(request.content, request.options)
            elif request.type == 'task_modules':
                return self._generate_task_module(request.content, request.options)
            elif request.type == 'bot_activities':
                return self._generate_bot_activity(request.content, request.options)
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
    
    def _generate_adaptive_card(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Microsoft Teams Adaptive Card"""
        try:
            card = {
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [],
                "actions": []
            }
            
            # Add title
            if content.get('title'):
                card['body'].append({
                    "type": "TextBlock",
                    "text": content['title'],
                    "size": "Large",
                    "weight": "Bolder",
                    "wrap": True
                })
            
            # Add subtitle
            if content.get('subtitle'):
                card['body'].append({
                    "type": "TextBlock",
                    "text": content['subtitle'],
                    "size": "Medium",
                    "weight": "Bolder",
                    "wrap": True,
                    "color": "Accent"
                })
            
            # Add main text
            if content.get('text'):
                card['body'].append({
                    "type": "TextBlock",
                    "text": content['text'],
                    "wrap": True
                })
            
            # Add code block if present
            if content.get('code'):
                card['body'].append({
                    "type": "TextBlock",
                    "text": content['code'],
                    "wrap": True,
                    "fontFamily": "Monospace",
                    "backgroundColor": "Default"
                })
            
            # Add facts if present
            if content.get('facts'):
                fact_set = {
                    "type": "FactSet",
                    "facts": []
                }
                for fact in content['facts']:
                    fact_set['facts'].append({
                        "title": fact.get('title', ''),
                        "value": fact.get('value', '')
                    })
                card['body'].append(fact_set)
            
            # Add action buttons
            if content.get('actions'):
                for action in content['actions']:
                    card['actions'].append({
                        "type": "Action.Submit",
                        "title": action.get('label', 'Action'),
                        "data": {
                            "action": action.get('id', 'action'),
                            "value": action.get('value', '')
                        }
                    })
            
            return ArtifactResult(
                success=True,
                artifact=card,
                formatted_content=str(card),
                metadata={
                    'platform': 'teams',
                    'card_version': '1.4',
                    'body_elements': len(card['body']),
                    'actions': len(card['actions'])
                }
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Adaptive Card generation failed: {str(e)}"
            )
    
    def _generate_task_module(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Teams task module"""
        try:
            task_module = {
                "taskInfo": {
                    "title": content.get('title', 'BK25 Task'),
                    "height": options.get('height', 'medium') if options else 'medium',
                    "width": options.get('width', 'medium') if options else 'medium',
                    "url": options.get('url', ''),
                    "card": None
                }
            }
            
            # Add card if present
            if content.get('card'):
                task_module['taskInfo']['card'] = content['card']
            
            return ArtifactResult(
                success=True,
                artifact=task_module,
                formatted_content=str(task_module),
                metadata={'platform': 'teams', 'type': 'task_module'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Task module generation failed: {str(e)}"
            )
    
    def _generate_bot_activity(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Teams bot activity"""
        try:
            activity = {
                "type": "message",
                "text": content.get('text', ''),
                "attachments": []
            }
            
            # Add adaptive card attachment if present
            if content.get('card'):
                activity['attachments'].append({
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": content['card']
                })
            
            # Add suggested actions if present
            if content.get('suggested_actions'):
                activity['suggestedActions'] = {
                    "actions": []
                }
                for action in content['suggested_actions']:
                    activity['suggestedActions']['actions'].append({
                        "type": "imBack",
                        "title": action.get('label', 'Action'),
                        "value": action.get('value', '')
                    })
            
            return ArtifactResult(
                success=True,
                artifact=activity,
                formatted_content=str(activity),
                metadata={'platform': 'teams', 'type': 'bot_activity'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Bot activity generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against Teams constraints"""
        constraints = self.get_constraints()
        
        # Teams has a 25,000 character limit for messages
        max_length = 25000
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for Teams"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'type' in response and response['type'] == 'AdaptiveCard':
                return f"Teams Adaptive Card: {len(response.get('body', []))} elements"
            elif 'text' in response:
                return response['text']
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get Teams-specific constraints"""
        return {
            'max_message_length': 25000,
            'supports_rich_text': True,
            'supports_media': True,
            'supports_interactive': True,
            'supports_adaptive_cards': True,
            'supports_task_modules': True,
            'supports_bot_framework': True,
            'supports_tabs': True
        }
