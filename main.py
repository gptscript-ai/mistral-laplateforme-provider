import json
import os
from typing import AsyncIterable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from openai import AsyncOpenAI, AsyncStream
from openai._types import NOT_GIVEN
from openai.types.chat import ChatCompletionChunk

debug = os.environ.get('DEBUG', False) == "true"


def log(*args):
    if debug:
        print(*args)


base_url = "https://api.mistral.ai/v1"

if "MISTRAL_API_KEY" not in os.environ:
    raise KeyError("MISTRAL_API_KEY is not set in environment variables")
api_key = os.environ["MISTRAL_API_KEY"]
client = AsyncOpenAI(api_key=api_key, base_url=base_url)
app = FastAPI()

system: str = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
Call the provided tools as needed to complete the task.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


@app.middleware("http")
async def log_body(request: Request, call_next):
    body = await request.body()
    log("REQUEST BODY: ", body)
    return await call_next(request)


@app.get("/")
async def get_root():
    return "ok"


@app.get("/v1/models")
async def list_models() -> JSONResponse:
    data: list[dict] = []
    async for model in client.models.list():
        data.append({
            "id": model.id,
            "object": model.object,
            "created": model.created,
            "owned_by": model.owned_by
        })
    return JSONResponse(content={"object": "list", "data": data})


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.body()
    data = json.loads(data)

    messages = data["messages"]
    messages.insert(0, {"role": "system", "content": system})

    stream = await client.chat.completions.create(
        model=data["model"],
        messages=messages,
        max_tokens=data.get("max_tokens", NOT_GIVEN),
        tools=data.get("tools", NOT_GIVEN),
        tool_choice=data.get("tool_choice", NOT_GIVEN),
        stream=data.get("stream", NOT_GIVEN),
        top_p=data.get("top_p", NOT_GIVEN),
        temperature=data.get("temperature", NOT_GIVEN),
    )

    async def convert_stream(stream: AsyncStream[ChatCompletionChunk]) -> AsyncIterable[str]:
        async for chunk in stream:
            log("CHUNK: ", chunk.model_dump_json())
            yield "data: " + str(chunk.model_dump_json()) + "\n\n"

    return StreamingResponse(convert_stream(stream), media_type="application/x-ndjson")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)
