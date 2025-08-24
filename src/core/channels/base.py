"""
Base Channel Module

Abstract base class for all channel modules.
Defines the interface for artifact generation and channel simulation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

@dataclass
class ArtifactRequest:
    """Request for artifact generation"""
    type: str
    content: Any
    options: Optional[Dict[str, Any]] = None
    persona_id: Optional[str] = None
    channel_id: Optional[str] = None

@dataclass
class ArtifactResult:
    """Result of artifact generation"""
    success: bool
    artifact: Optional[Any] = None
    formatted_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseChannel(ABC):
    """Abstract base class for all channel modules"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get('name', 'unknown')
        self.id = config.get('id', 'unknown')
        self.capabilities = config.get('capabilities', [])
        self.artifact_types = config.get('artifact_types', [])
        self.metadata = config.get('metadata', {})
        
    @abstractmethod
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate a platform-specific artifact"""
        pass
    
    @abstractmethod
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against channel constraints"""
        pass
    
    @abstractmethod
    def format_response(self, response: Any) -> str:
        """Format response for this channel"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of supported capabilities"""
        return self.capabilities
    
    def supports_artifact_type(self, artifact_type: str) -> bool:
        """Check if artifact type is supported"""
        return artifact_type in self.artifact_types
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get channel metadata"""
        return self.metadata
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get channel constraints and limitations"""
        return {
            'max_message_length': 1000,
            'supports_rich_text': True,
            'supports_media': False,
            'supports_interactive': False
        }
