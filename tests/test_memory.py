import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.memory import ConversationMemory, Conversation, ConversationMessage

class TestConversationMessage:
    """Test ConversationMessage dataclass"""
    
    def test_conversation_message_creation(self):
        """Test creating a ConversationMessage instance"""
        message = ConversationMessage(
            role="user",
            content="Hello, how can you help me?",
            timestamp=datetime.now(),
            metadata={"channel": "web", "persona": "vanilla"}
        )
        
        assert message.role == "user"
        assert message.content == "Hello, how can you help me?"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata["channel"] == "web"
        assert message.metadata["persona"] == "vanilla"
    
    def test_conversation_message_defaults(self):
        """Test ConversationMessage with default values"""
        message = ConversationMessage(
            role="assistant",
            content="I can help you with automation!"
        )
        
        assert message.role == "assistant"
        assert message.content == "I can help you with automation!"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}
    
    def test_conversation_message_to_dict(self):
        """Test ConversationMessage.to_dict() method"""
        timestamp = datetime.now()
        message = ConversationMessage(
            role="user",
            content="Test message",
            timestamp=timestamp,
            metadata={"test": "value"}
        )
        
        result = message.to_dict()
        
        assert result["role"] == "user"
        assert result["content"] == "Test message"
        assert result["timestamp"] == timestamp
        assert result["metadata"]["test"] == "value"

class TestConversation:
    """Test Conversation dataclass"""
    
    def test_conversation_creation(self):
        """Test creating a Conversation instance"""
        conversation = Conversation(
            id="test_conversation",
            persona_id="vanilla",
            channel_id="web",
            created_at=datetime.now()
        )
        
        assert conversation.id == "test_conversation"
        assert conversation.persona_id == "vanilla"
        assert conversation.channel_id == "web"
        assert isinstance(conversation.created_at, datetime)
        assert conversation.updated_at == conversation.created_at
        assert conversation.messages == []
        assert conversation.metadata == {}
    
    def test_conversation_defaults(self):
        """Test Conversation with default values"""
        conversation = Conversation(id="minimal")
        
        assert conversation.id == "minimal"
        assert conversation.persona_id == ""
        assert conversation.channel_id == ""
        assert isinstance(conversation.created_at, datetime)
        assert conversation.updated_at == conversation.created_at
        assert conversation.messages == []
        assert conversation.metadata == {}
    
    def test_conversation_add_message(self):
        """Test adding messages to conversation"""
        conversation = Conversation(id="test")
        message1 = ConversationMessage(role="user", content="Hello")
        message2 = ConversationMessage(role="assistant", content="Hi there!")
        
        conversation.add_message(message1)
        conversation.add_message(message2)
        
        assert len(conversation.messages) == 2
        assert conversation.messages[0].role == "user"
        assert conversation.messages[1].role == "assistant"
        assert conversation.updated_at > conversation.created_at
    
    def test_conversation_get_context(self):
        """Test getting conversation context"""
        conversation = Conversation(id="test")
        messages = [
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi there!"),
            ConversationMessage(role="user", content="How are you?"),
            ConversationMessage(role="assistant", content="I'm doing well!")
        ]
        
        for message in messages:
            conversation.add_message(message)
        
        context = conversation.get_context(limit=2)
        assert len(context) == 2
        assert context[0].content == "How are you?"
        assert context[1].content == "I'm doing well!"
    
    def test_conversation_get_context_no_limit(self):
        """Test getting conversation context without limit"""
        conversation = Conversation(id="test")
        messages = [
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi there!")
        ]
        
        for message in messages:
            conversation.add_message(message)
        
        context = conversation.get_context()
        assert len(context) == 2
    
    def test_conversation_to_dict(self):
        """Test Conversation.to_dict() method"""
        conversation = Conversation(
            id="test",
            persona_id="vanilla",
            channel_id="web"
        )
        
        result = conversation.to_dict()
        
        assert result["id"] == "test"
        assert result["persona_id"] == "vanilla"
        assert result["channel_id"] == "web"
        assert "created_at" in result
        assert "updated_at" in result
        assert "messages" in result
        assert "metadata" in result

class TestConversationMemory:
    """Test ConversationMemory class"""
    
    @pytest.fixture
    def memory(self):
        """Create ConversationMemory instance"""
        return ConversationMemory(max_conversations=5, max_messages_per_conversation=10)
    
    def test_initialization(self, memory):
        """Test ConversationMemory initialization"""
        assert memory.max_conversations == 5
        assert memory.max_messages_per_conversation == 10
        assert memory.conversations == {}
    
    def test_create_conversation_success(self, memory):
        """Test successful conversation creation"""
        conversation = memory.create_conversation(
            "test_conv",
            "vanilla",
            "web"
        )
        
        assert conversation is not None
        assert conversation.id == "test_conv"
        assert conversation.persona_id == "vanilla"
        assert conversation.channel_id == "web"
        assert "test_conv" in memory.conversations
    
    def test_create_conversation_duplicate_id(self, memory):
        """Test creating conversation with duplicate ID"""
        # Create first conversation
        conv1 = memory.create_conversation("duplicate", "vanilla", "web")
        assert conv1 is not None
        
        # Try to create second with same ID
        conv2 = memory.create_conversation("duplicate", "expert", "discord")
        
        # Should return existing conversation
        assert conv2 is not None
        assert conv2.id == "duplicate"
        assert conv2.persona_id == "vanilla"  # Original values preserved
        assert conv2.channel_id == "web"
    
    def test_get_conversation_existing(self, memory):
        """Test getting existing conversation"""
        created = memory.create_conversation("test", "vanilla", "web")
        retrieved = memory.get_conversation("test")
        
        assert retrieved is not None
        assert retrieved.id == "test"
        assert retrieved == created
    
    def test_get_conversation_nonexistent(self, memory):
        """Test getting non-existent conversation"""
        conversation = memory.get_conversation("nonexistent")
        assert conversation is None
    
    def test_add_message_success(self, memory):
        """Test successfully adding message to conversation"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        message = ConversationMessage(role="user", content="Hello")
        
        memory.add_message("test", "user", "Hello")
        
        assert len(conversation.messages) == 1
        assert conversation.messages[0].role == "user"
        assert conversation.messages[0].content == "Hello"
    
    def test_add_message_nonexistent_conversation(self, memory):
        """Test adding message to non-existent conversation"""
        # Should not crash, just return
        memory.add_message("nonexistent", "user", "Hello")
        assert "nonexistent" not in memory.conversations
    
    def test_add_message_exceeds_limit(self, memory):
        """Test adding message when conversation is at limit"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Add messages up to limit
        for i in range(10):
            memory.add_message("test", "user", f"Message {i}")
        
        assert len(conversation.messages) == 10
        
        # Add one more message
        memory.add_message("test", "user", "Extra message")
        
        # Should still have 10 messages (oldest removed)
        assert len(conversation.messages) == 10
        assert conversation.messages[0].content == "Message 1"  # First message removed
        assert conversation.messages[-1].content == "Extra message"  # Newest added
    
    def test_get_conversation_history_existing(self, memory):
        """Test getting conversation history for existing conversation"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        memory.add_message("test", "user", "Hello")
        memory.add_message("test", "assistant", "Hi there!")
        
        history = memory.get_conversation_history("test")
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"
    
    def test_get_conversation_history_nonexistent(self, memory):
        """Test getting conversation history for non-existent conversation"""
        history = memory.get_conversation_history("nonexistent")
        assert history == []
    
    def test_get_conversation_history_with_limit(self, memory):
        """Test getting conversation history with limit"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Add 5 messages
        for i in range(5):
            memory.add_message("test", "user", f"Message {i}")
        
        # Get history with limit 3
        history = memory.get_conversation_history("test", limit=3)
        assert len(history) == 3
        assert history[0].content == "Message 2"  # Most recent messages
        assert history[1].content == "Message 3"
        assert history[2].content == "Message 4"
    
    def test_get_conversation_context_existing(self, memory):
        """Test getting conversation context for existing conversation"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        memory.add_message("test", "user", "Hello")
        memory.add_message("test", "assistant", "Hi there!")
        
        context = memory.get_conversation_context("test")
        assert context is not None
        assert "Hello" in context
        assert "Hi there!" in context
    
    def test_get_conversation_context_nonexistent(self, memory):
        """Test getting conversation context for non-existent conversation"""
        context = memory.get_conversation_context("nonexistent")
        assert context is None
    
    def test_get_all_conversation_summaries(self, memory):
        """Test getting all conversation summaries"""
        # Create multiple conversations
        memory.create_conversation("conv1", "vanilla", "web")
        memory.create_conversation("conv2", "expert", "discord")
        memory.create_conversation("conv3", "friendly", "slack")
        
        summaries = memory.get_all_conversation_summaries()
        assert len(summaries) == 3
        
        # Check that all conversations are represented
        conv_ids = [summary["id"] for summary in summaries]
        assert "conv1" in conv_ids
        assert "conv2" in conv_ids
        assert "conv3" in conv_ids
    
    def test_get_memory_stats(self, memory):
        """Test getting memory statistics"""
        # Create conversations and add messages
        memory.create_conversation("conv1", "vanilla", "web")
        memory.create_conversation("conv2", "expert", "discord")
        
        memory.add_message("conv1", "user", "Hello")
        memory.add_message("conv1", "assistant", "Hi!")
        memory.add_message("conv2", "user", "How are you?")
        
        stats = memory.get_memory_stats()
        
        assert stats["total_conversations"] == 2
        assert stats["total_messages"] == 3
        assert stats["max_conversations"] == 5
        assert stats["max_messages_per_conversation"] == 10
        assert "oldest_conversation" in stats
        assert "newest_conversation" in stats
    
    def test_conversation_limit_enforcement(self, memory):
        """Test that conversation limit is enforced"""
        # Create conversations up to limit
        for i in range(5):
            memory.create_conversation(f"conv{i}", "vanilla", "web")
        
        assert len(memory.conversations) == 5
        
        # Try to create one more
        memory.create_conversation("extra", "expert", "discord")
        
        # Should still have 5 conversations
        assert len(memory.conversations) == 5
        
        # Oldest conversation should be removed
        assert "conv0" not in memory.conversations
        assert "extra" in memory.conversations
    
    def test_message_limit_enforcement(self, memory):
        """Test that message limit is enforced"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Add messages up to limit
        for i in range(10):
            memory.add_message("test", "user", f"Message {i}")
        
        assert len(conversation.messages) == 10
        
        # Add more messages
        for i in range(5):
            memory.add_message("test", "user", f"Extra {i}")
        
        # Should still have 10 messages
        assert len(conversation.messages) == 10
        
        # Oldest messages should be removed
        assert conversation.messages[0].content == "Extra 0"
        assert conversation.messages[-1].content == "Extra 4"
    
    def test_conversation_metadata(self, memory):
        """Test conversation metadata handling"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Add metadata
        conversation.metadata["user_id"] = "user123"
        conversation.metadata["session_id"] = "session456"
        
        # Retrieve conversation
        retrieved = memory.get_conversation("test")
        assert retrieved.metadata["user_id"] == "user123"
        assert retrieved.metadata["session_id"] == "session456"
    
    def test_message_metadata(self, memory):
        """Test message metadata handling"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Add message with metadata
        memory.add_message("test", "user", "Hello", {"channel": "web", "timestamp": "2024-01-01"})
        
        # Check message metadata
        message = conversation.messages[0]
        assert message.metadata["channel"] == "web"
        assert message.metadata["timestamp"] == "2024-01-01"
    
    def test_conversation_timestamps(self, memory):
        """Test conversation timestamp handling"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        initial_created = conversation.created_at
        initial_updated = conversation.updated_at
        
        # Wait a bit
        import time
        time.sleep(0.001)
        
        # Add message
        memory.add_message("test", "user", "Hello")
        
        # Created time should not change
        assert conversation.created_at == initial_created
        
        # Updated time should change
        assert conversation.updated_at > initial_updated
    
    def test_conversation_cleanup(self, memory):
        """Test conversation cleanup when limit exceeded"""
        # Create conversations up to limit
        for i in range(5):
            memory.create_conversation(f"conv{i}", "vanilla", "web")
        
        # Create one more to trigger cleanup
        memory.create_conversation("new", "expert", "discord")
        
        # Oldest should be removed
        assert "conv0" not in memory.conversations
        assert "new" in memory.conversations
        
        # Should still have max_conversations
        assert len(memory.conversations) == 5
    
    def test_error_handling_invalid_conversation_id(self, memory):
        """Test error handling with invalid conversation ID"""
        # Should not crash with invalid IDs
        memory.add_message("", "user", "Hello")
        memory.add_message(None, "user", "Hello")
        memory.add_message(123, "user", "Hello")
        
        # No conversations should be created
        assert len(memory.conversations) == 0
    
    def test_error_handling_invalid_message_data(self, memory):
        """Test error handling with invalid message data"""
        conversation = memory.create_conversation("test", "vanilla", "web")
        
        # Should handle invalid message data gracefully
        memory.add_message("test", "", "Hello")  # Empty role
        memory.add_message("test", "user", "")   # Empty content
        memory.add_message("test", None, "Hello") # None role
        memory.add_message("test", "user", None)  # None content
        
        # Should still have the conversation
        assert "test" in memory.conversations
        # But no valid messages should be added
        assert len(conversation.messages) == 0

if __name__ == "__main__":
    pytest.main([__file__])
