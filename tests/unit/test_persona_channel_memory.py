import os
import tempfile
from bk25.persona_manager import PersonaManager
from bk25.channel_manager import ChannelManager
from bk25.memory import ConversationMemory


def test_persona_manager_loads_and_builds_prompt(tmp_path):
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    (personas_dir / "vanilla.json").write_text(
        '{"id":"vanilla","name":"Vanilla","description":"d","greeting":"hi","systemPrompt":"You are V.","channels":["web"]}'
    )
    pm = PersonaManager(personas_path=str(personas_dir))
    import asyncio

    asyncio.get_event_loop().run_until_complete(pm.initialize())
    prompt = pm.build_persona_prompt("Hello", [])
    assert "You are V." in prompt
    assert "User: Hello" in prompt


def test_channel_manager_switch_and_artifacts():
    cm = ChannelManager()
    channels = cm.get_all_channels()
    assert any(c["id"] == "web" for c in channels)
    assert cm.get_current_channel()["id"] == "web"
    assert cm.switch_channel("slack")["id"] == "slack"
    assert "block-kit" in cm.get_available_artifacts()


def test_memory_roundtrip(tmp_path):
    db = tmp_path / "bk25.db"
    mem = ConversationMemory(db_path=str(db))
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(mem.add_message("user", "hello", {}))
    msgs = loop.run_until_complete(mem.get_recent_messages(5))
    assert msgs[-1]["content"] == "hello"
