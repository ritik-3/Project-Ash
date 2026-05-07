from fastapi.testclient import TestClient

from app.core.dependencies import get_conversation_service
from app.main import app
from app.schemas.chat import ChatRequest, ChatResponse


class FakeConversationService:
    async def respond(self, request: ChatRequest) -> ChatResponse:  # type: ignore[override]
        return ChatResponse(
            status="ok",
            session_id=request.session_id,
            reply=f"Echo: {request.message}",
            history_size=1,
            model="test-model",
        )


def test_chat_endpoint() -> None:
    app.dependency_overrides[get_conversation_service] = lambda: FakeConversationService()
    client = TestClient(app)

    response = client.post("/api/v1/chat", json={"session_id": "default", "message": "hello ash"})

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Echo: hello ash"
    assert body["history_size"] == 1