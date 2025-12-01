import warnings
try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.simplefilter("ignore", UnsupportedFieldAttributeWarning)
except ImportError:
    pass

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from openinference.instrumentation.langchain import LangChainInstrumentor
from config import settings

if settings.is_arize_phoenix_enabled():
    from arize.otel import register
    logger.info(f"Configuring Arize Phoenix: {settings.phoenix_space_id[:4]}... / {settings.phoenix_project_name}")
    
    try:
        tracer_provider = register(
            space_id=settings.phoenix_space_id,
            api_key=settings.phoenix_api_key,
            project_name=settings.phoenix_project_name,
            set_global_tracer_provider=True,
            batch=True,
        )
    except Exception as e:
        logger.error(f"Failed to register Arize Phoenix: {e}")
        raise
else:
    from phoenix.otel import register
    tracer_provider = register(
        project_name=settings.phoenix_project_name,
        endpoint=settings.phoenix_collector_endpoint,
        set_global_tracer_provider=True,
        batch=True,
    )

LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from bankbot.graph import graph
from mcp.mcp_impl import engine


app = FastAPI(title="Chatbot for Learning")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="bankbot",
        description="Banking related stuff",
        graph=graph,
    ),
    path="/bankbot",
)

# manual rate limiting for /bankbot since the endpoint is created internaly
bankbot_requests = defaultdict(list)

@app.middleware("http")
async def rate_limit_bankbot(request: Request, call_next):
    if request.url.path.startswith("/bankbot"):
        client_ip = get_remote_address(request)
        now = datetime.now()
        
        # prune old entries
        bankbot_requests[client_ip] = [
            t for t in bankbot_requests[client_ip] if now - t < timedelta(minutes=1)
        ]
        
        if len(bankbot_requests[client_ip]) >= 10:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceded. Please try again later."},
                headers={"Retry-After": "60"}
            )
        
        bankbot_requests[client_ip].append(now)
    
    return await call_next(request)


@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "components": {"api": "healthy", "database": "connected"}
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy", 
                "error": str(e),
                "components": {"api": "healthy", "database": "disconnected"}
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)