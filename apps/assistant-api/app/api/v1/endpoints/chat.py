from fastapi import APIRouter, Depends

from app.core.dependencies import get_conversation_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ConversationService = Depends(get_conversation_service),
) -> ChatResponse:
    return await service.respond(request)