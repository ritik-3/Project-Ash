from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str
    voice_model_ready: bool
    wake_word_model: str
