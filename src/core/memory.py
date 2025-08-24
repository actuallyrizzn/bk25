"""
BK25 Conversation Memory

Manages conversation context and history for maintaining coherent conversations
across different personas and channels.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from ..logging_config import get_logger

logger = get_logger("memory")

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Conversation:
    """Conversation thread with messages"""
    id: str
    persona_id: str
    channel: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConversationMemory:
    """Manages conversation memory and context"""
    
    def __init__(self, max_conversations: int = 100, max_messages_per_conversation: int = 50):
        self.conversations: Dict[str, Conversation] = {}
        self.max_conversations = max_conversations
        self.max_messages_per_conversation = max_messages_per_conversation
        self.logger = get_logger("memory")
    
    def create_conversation(self, conversation_id: str, persona_id: str, channel: str = "web") -> Conversation:
        """Create a new conversation thread"""
        if conversation_id in self.conversations:
            self.logger.warning(f"Conversation {conversation_id} already exists, returning existing")
            return self.conversations[conversation_id]
        
        conversation = Conversation(
            id=conversation_id,
            persona_id=persona_id,
            channel=channel
        )
        
        self.conversations[conversation_id] = conversation
        
        # Clean up old conversations if we exceed the limit
        if len(self.conversations) > self.max_conversations:
            self._cleanup_old_conversations()
        
        self.logger.info(f"Created conversation {conversation_id} for persona {persona_id}")
        return conversation
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation {conversation_id} not found")
            return False
        
        conversation = self.conversations[conversation_id]
        
        # Check message limit
        if len(conversation.messages) >= self.max_messages_per_conversation:
            # Remove oldest message
            conversation.messages.pop(0)
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        conversation.messages.append(message)
        conversation.updated_at = time.time()
        
        self.logger.debug(f"Added {role} message to conversation {conversation_id}")
        return True
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get conversation history, optionally limited to recent messages"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_conversation_context(self, conversation_id: str, max_tokens: int = 1000) -> str:
        """Get conversation context as formatted string for LLM prompts"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return ""
        
        context = f"Conversation ID: {conversation_id}\n"
        context += f"Persona: {conversation.persona_id}\n"
        context += f"Channel: {conversation.channel}\n\n"
        
        # Add recent messages
        for message in conversation.messages[-10:]:  # Last 10 messages
            context += f"{message.role.capitalize()}: {message.content}\n"
        
        return context
    
    def switch_persona(self, conversation_id: str, new_persona_id: str) -> bool:
        """Switch persona for a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        old_persona = conversation.persona_id
        conversation.persona_id = new_persona_id
        conversation.updated_at = time.time()
        
        # Add system message about persona switch
        self.add_message(
            conversation_id,
            "system",
            f"Persona switched from {old_persona} to {new_persona_id}"
        )
        
        self.logger.info(f"Switched persona in conversation {conversation_id}: {old_persona} -> {new_persona_id}")
        return True
    
    def get_conversations_for_persona(self, persona_id: str) -> List[Conversation]:
        """Get all conversations for a specific persona"""
        return [
            conv for conv in self.conversations.values()
            if conv.persona_id == persona_id
        ]
    
    def get_conversations_for_channel(self, channel: str) -> List[Conversation]:
        """Get all conversations for a specific channel"""
        return [
            conv for conv in self.conversations.values()
            if conv.channel == channel
        ]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self.logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False
    
    def clear_conversations(self) -> None:
        """Clear all conversations"""
        self.conversations.clear()
        self.logger.info("Cleared all conversations")
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get a summary of a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        return {
            'id': conversation.id,
            'persona_id': conversation.persona_id,
            'channel': conversation.channel,
            'message_count': len(conversation.messages),
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'last_message': conversation.messages[-1].content if conversation.messages else None
        }
    
    def get_all_conversation_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all conversations"""
        return [
            self.get_conversation_summary(conv_id)
            for conv_id in self.conversations.keys()
        ]
    
    def _cleanup_old_conversations(self) -> None:
        """Remove old conversations to stay within limits"""
        if len(self.conversations) <= self.max_conversations:
            return
        
        # Sort by last update time and remove oldest
        sorted_conversations = sorted(
            self.conversations.items(),
            key=lambda x: x[1].updated_at
        )
        
        conversations_to_remove = len(self.conversations) - self.max_conversations
        for i in range(conversations_to_remove):
            conv_id, _ = sorted_conversations[i]
            del self.conversations[conv_id]
        
        self.logger.info(f"Cleaned up {conversations_to_remove} old conversations")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        
        return {
            'total_conversations': len(self.conversations),
            'total_messages': total_messages,
            'max_conversations': self.max_conversations,
            'max_messages_per_conversation': self.max_messages_per_conversation,
            'memory_usage_percent': (len(self.conversations) / self.max_conversations) * 100
        }
