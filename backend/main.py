
import warnings
try:
    from pydantic.warnings import UnsupportedFieldAttributeWarning
    warnings.simplefilter("ignore", UnsupportedFieldAttributeWarning)
except ImportError:
    pass

from copilotkit.sdk import CopilotKitRemoteEndpoint
import json
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from bankbot.graph import graph
from copilotkit import LangGraphAGUIAgent, LangGraphAgent
from dotenv import load_dotenv
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from copilotkit.integrations.fastapi import add_fastapi_endpoint
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

register(
  project_name="bank-agent",
)
LangChainInstrumentor(
  
).instrument()


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
    name="",
    description="Banking related stuff",
    graph=graph,
  ),
  path="/bankbot",
)

@app.get("/health")
async def health_check():
    return {"status":"healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000)
