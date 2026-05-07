from app.services.memory_service import SessionMemoryService


def test_memory_service_trims_to_limit() -> None:
    memory = SessionMemoryService(limit=2)

    memory.append_turn("default", "hello", "hi")
    memory.append_turn("default", "how are you", "good")
    memory.append_turn("default", "third", "reply")

    turns = memory.recent_turns("default")

    assert len(turns) == 2
    assert turns[0].user == "how are you"
    assert turns[1].user == "third"