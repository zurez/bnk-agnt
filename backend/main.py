
import json
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from model import ChatRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Chatbot for Sarj Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
async def health_check():
    return {"status":"healthy"}

@app.get("api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    async def generate():
        yield json.dumps({
            "hello":"world"
        })
        
    return StreamingResponse(generate(),media_type="application/x-ndjson")
    pass
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000)
