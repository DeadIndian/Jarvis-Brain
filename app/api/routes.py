from fastapi import APIRouter, HTTPException, Header, Security
from .models import RemoteRequest, RemoteResponse
from ..orchestrator.orchestrator import Orchestrator
from ..config import config

router = APIRouter()
orchestrator = Orchestrator(llm_client=config.get_llm_client())


async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != config.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


@router.post("/process", response_model=RemoteResponse)
async def process_request(request: RemoteRequest, api_key: str = Security(verify_api_key)):
    try:
        response = await orchestrator.process(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
