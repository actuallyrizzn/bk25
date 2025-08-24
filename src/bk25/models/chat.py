"""
BK25 Chat Data Models

Pydantic models for request/response handling in the chat API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    persona: Optional[str] = Field("vanilla", description="Persona ID to use")
    channel: Optional[str] = Field("web", description="Channel to simulate")
    platform: Optional[str] = Field("powershell", description="Target platform for automation")
    session_id: Optional[str] = Field(None, description="Session identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class AutomationResult(BaseModel):
    """Generated automation script result"""
    platform: str = Field(..., description="Target platform")
    description: str = Field(..., description="Script description")
    script: str = Field(..., description="Generated script code")
    documentation: Optional[str] = Field(None, description="Script documentation")
    filename: Optional[str] = Field(None, description="Suggested filename")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    type: str = Field(..., description="Response type: 'conversation' or 'automation'")
    message: str = Field(..., description="AI response message")
    automation: Optional[AutomationResult] = Field(None, description="Generated automation if applicable")
    conversational: bool = Field(True, description="Whether response is conversational")
    persona_info: Optional[Dict[str, Any]] = Field(None, description="Current persona information")
    channel_info: Optional[Dict[str, Any]] = Field(None, description="Current channel information")


class ConversationMessage(BaseModel):
    """Individual conversation message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    context: Dict[str, Any] = Field(default_factory=dict, description="Message context")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    tagline: str = Field(..., description="BK25 tagline")
    ollama: str = Field(..., description="Ollama connection status")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")