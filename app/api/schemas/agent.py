from typing import Any

from pydantic import BaseModel, Field


class FinanceAgentRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class FinanceAgentResponse(BaseModel):
    intent: str
    answer: str
    data: dict[str, Any]
