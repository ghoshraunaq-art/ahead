from pydantic import BaseModel, ConfigDict


class ContextIntelligenceResponse(BaseModel):
    entity_type: str
    entity_id: int
    context: list[dict]

    model_config = ConfigDict(from_attributes=True)