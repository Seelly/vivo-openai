import uuid
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.v1 import validator
from starlette.responses import StreamingResponse

from vivo import VivoGPT


class ChatMessage(BaseModel):
    role: str
    content: str

    @validator('role')
    def validate_role(self, v):
        if v not in ["user", "assistant"]:
            raise ValueError('role must be either "user" or "assistant"')
        return v


class ChatCompletionRequest(BaseModel):
    model: str = 'vivo-BlueLM-TB-Pro'
    messages: Optional[List[ChatMessage]] = None
    prompt: Optional[str] = None
    max_tokens: Optional[int] = 4096  # 最大 token 数量限制
    temperature: Optional[float] = 0.7  # 温度参数
    stream: Optional[bool] = False  # 是否开启流式输出
    top_p: Optional[float] = 0.7
    top_k: Optional[int] = 50
    max_new_tokens: Optional[int] = 2048
    repetition_penalty: Optional[float] = 1.02


app = FastAPI()

gpt = VivoGPT(app_id="", app_key="")


@app.post("/v1/chat/completions")
@app.post("/v1/completions")
async def chat_completions(request: ChatCompletionRequest):
    request_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    params = {
        'requestId': request_id
    }
    if request.messages is not None and request.prompt is not None:
        return {"error": "messages and prompt cannot be used at the same time"}
    data = {
        'sessionId': session_id,
        'model': request.model,
        'extra': {
            'temperature': request.temperature,
            'top_p': request.top_p,
            'top_k': request.top_k,
            'max_new_tokens': request.max_new_tokens,
            'repetition_penalty': request.repetition_penalty
        }
    }
    if request.messages is not None:
        data['messages'] = [msg.dict() for msg in request.messages]
    elif request.prompt is not None:
        data['prompt'] = request.prompt
    if request.stream:
        return StreamingResponse(gpt.stream_vivogpt(params, data), media_type="text/event-stream")

    return gpt.vivogpt(params, data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
