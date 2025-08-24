"""
BK25 Channel Data Models

Data models for the channel simulation system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChannelCapability(BaseModel):
    """Channel capability definition"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    artifacts: List[str] = Field(default_factory=list, description="Supported artifacts")


class Channel(BaseModel):
    """Channel data model"""
    id: str = Field(..., description="Unique channel identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Channel description")
    capabilities: List[ChannelCapability] = Field(default_factory=list, description="Channel capabilities")
    native_features: List[str] = Field(default_factory=list, description="Native platform features")
    artifact_types: List[str] = Field(default_factory=list, description="Supported artifact types")
    message_format: Optional[str] = Field(None, description="Message format template")


class ChannelMessage(BaseModel):
    """Channel-formatted message"""
    channel: str = Field(..., description="Channel identifier")
    content: str = Field(..., description="Formatted message content")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="Channel artifacts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Channel-specific metadata")


class ChannelArtifact(BaseModel):
    """Channel artifact (rich content)"""
    type: str = Field(..., description="Artifact type")
    title: str = Field(..., description="Artifact title")
    content: str = Field(..., description="Artifact content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Artifact metadata")