from fastapi import APIRouter, HTTPException
from .models import RemoteRequest, RemoteResponse
from ..orchestrator.orchestrator import Orchestrator
from ..config import config

router = APIRouter()
orchestrator = Orchestrator(llm_client=config.get_llm_client())


@router.post("/process", response_model=RemoteResponse)
async def process_request(request: RemoteRequest):
    try:
        response = await orchestrator.process(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
