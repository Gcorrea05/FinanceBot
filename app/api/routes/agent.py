from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.api.schemas.agent import FinanceAgentRequest, FinanceAgentResponse
from app.container import Container

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query", response_model=FinanceAgentResponse)
def query_agent(
    payload: FinanceAgentRequest,
    container: Container = Depends(get_container),
) -> FinanceAgentResponse:
    result = container.finance_agent.answer(payload.question)
    return FinanceAgentResponse(
        intent=result.intent,
        answer=result.answer,
        data=result.data,
    )
