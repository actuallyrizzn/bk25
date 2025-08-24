"""
BK25 Persona Data Models

Data models for the persona system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Persona(BaseModel):
    """Persona data model"""
    id: str = Field(..., description="Unique persona identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Persona description")
    greeting: str = Field(..., description="Persona greeting message")
    system_prompt: str = Field(..., alias="systemPrompt", description="System prompt for LLM")
    capabilities: List[str] = Field(default_factory=list, description="Persona capabilities")
    examples: List[str] = Field(default_factory=list, description="Example interactions")
    channels: Optional[List[str]] = Field(None, description="Supported channels")
    personality: Optional[Dict[str, Any]] = Field(None, description="Personality traits")

    class Config:
        populate_by_name = True


class PersonaMetadata(BaseModel):
    """Persona metadata for UI display"""
    id: str
    name: str
    description: str
    greeting: str
    capabilities: List[str]
    examples: List[str]
    personality: Optional[Dict[str, Any]] = None


class CreatePersonaRequest(BaseModel):
    """Request model for creating custom personas"""
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    greeting: str = Field(..., description="Greeting message")
    system_prompt: str = Field(..., description="System prompt")
    capabilities: List[str] = Field(default_factory=list, description="Capabilities")
    examples: List[str] = Field(default_factory=list, description="Examples")
    channels: Optional[List[str]] = Field(None, description="Supported channels")
    personality: Optional[Dict[str, Any]] = Field(None, description="Personality traits")