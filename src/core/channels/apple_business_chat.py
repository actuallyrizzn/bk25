"""
Apple Business Chat Channel Module

Provides Apple Business Chat-specific artifact generation for iOS users.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class AppleBusinessChatChannel(BaseChannel):
    """Apple Business Chat channel with rich links and payments support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Apple Business Chat',
            'id': 'apple-business-chat',
            'capabilities': ['rich_links', 'payments', 'scheduling', 'file_sharing'],
            'artifact_types': ['rich_links', 'interactive_messages', 'payments'],
            'metadata': {'color': '#000000', 'icon': '[APPLE]'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate Apple Business Chat-specific artifacts"""
        try:
            if request.type == 'rich_links':
                return self._generate_rich_link(request.content, request.options)
            elif request.type == 'interactive_messages':
                return self._generate_interactive_message(request.content, request.options)
            elif request.type == 'payments':
                return self._generate_payment(request.content, request.options)
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
    
    def _generate_rich_link(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Apple Business Chat rich link"""
        try:
            rich_link = {
                "type": "rich_link",
                "url": content.get('url', ''),
                "title": content.get('title', ''),
                "description": content.get('description', ''),
                "image": content.get('image', ''),
                "metadata": {
                    "domain": content.get('domain', ''),
                    "app_id": content.get('app_id', '')
                }
            }
            
            return ArtifactResult(
                success=True,
                artifact=rich_link,
                formatted_content=str(rich_link),
                metadata={'platform': 'apple-business-chat', 'type': 'rich_link'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Rich link generation failed: {str(e)}"
            )
    
    def _generate_interactive_message(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Apple Business Chat interactive message"""
        try:
            interactive = {
                "type": "interactive",
                "title": content.get('title', ''),
                "subtitle": content.get('subtitle', ''),
                "buttons": []
            }
            
            # Add buttons
            if content.get('buttons'):
                for button in content['buttons']:
                    interactive['buttons'].append({
                        "type": button.get('type', 'text'),
                        "title": button.get('title', ''),
                        "value": button.get('value', '')
                    })
            
            return ArtifactResult(
                success=True,
                artifact=interactive,
                formatted_content=str(interactive),
                metadata={'platform': 'apple-business-chat', 'type': 'interactive_message'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Interactive message generation failed: {str(e)}"
            )
    
    def _generate_payment(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate Apple Business Chat payment request"""
        try:
            payment = {
                "type": "payment",
                "amount": content.get('amount', '0.00'),
                "currency": content.get('currency', 'USD'),
                "description": content.get('description', ''),
                "merchant_id": content.get('merchant_id', ''),
                "payment_type": content.get('payment_type', 'apple_pay')
            }
            
            return ArtifactResult(
                success=True,
                artifact=payment,
                formatted_content=str(payment),
                metadata={'platform': 'apple-business-chat', 'type': 'payment'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Payment generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against Apple Business Chat constraints"""
        constraints = self.get_constraints()
        
        # Apple Business Chat has a 2000 character limit for messages
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
        """Format response for Apple Business Chat"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'type' in response:
                return f"Apple Business Chat {response['type']} message"
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get Apple Business Chat-specific constraints"""
        return {
            'max_message_length': 2000,
            'supports_rich_text': True,
            'supports_media': True,
            'supports_interactive': True,
            'supports_rich_links': True,
            'supports_payments': True,
            'supports_scheduling': True,
            'supports_file_sharing': True
        }
