import warnings
import os
try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.simplefilter("ignore", UnsupportedFieldAttributeWarning)
except ImportError:
    pass

import logging
from dotenv import load_dotenv

load_dotenv()

from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor


tracer_provider = register(
    project_name=os.getenv("PHOENIX_PROJECT_NAME", "bank-agent"),
    endpoint=os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006/v1/traces"),
)

LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

from copilotkit.sdk import CopilotKitRemoteEndpoint
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from bankbot.graph import graph
from copilotkit import LangGraphAGUIAgent, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot for Learning")

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)