import uvicorn
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from agent import sky_companion_app, get_system_prompt
from models import llm, analyze_sentiment, analyze_image
from tools import sky_tools

app = FastAPI(title="SKY Companion API Server")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "user"
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    sentiment: str
    escalate_to_human: bool

class ImageAnalysisRequest(BaseModel):
    user_id: Optional[str] = "user"
    image: str # Base64 string, file path, or data URL
    prompt: Optional[str] = "Analyze this image in detail."
    image_identifier: Optional[str] = "uploaded_image"

@app.post("/api/analyze-image")
async def analyze_image_endpoint(request: ImageAnalysisRequest):
    print(f"\n--- Image Analysis Request ---")
    print(f"User ID: {request.user_id} | Identifier: {request.image_identifier}")
    
    result = analyze_image(
        image_input=request.image,
        prompt=request.prompt,
        user_id=request.user_id,
        image_identifier=request.image_identifier
    )
    
    return {
        "status": "success",
        "analysis_id": result["analysis_id"],
        "image_identifier": result["image_identifier"],
        "analysis": result["analysis_result"],
        "output_json": result.get("json_output")
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.thread_id or "default"
    print(f"\n--- API Request (Blocking) [Thread: {thread_id}] ---")
    print(f"User: {request.message}")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run the compiled LangGraph workflow with thread checkpointer memory
    state = sky_companion_app.invoke({
        "messages": [HumanMessage(content=request.message)],
        "user_id": request.user_id,
        "sentiment": "Neutral",
        "escalate_to_human": False
    }, config=config)
    
    # Extract results
    reply = state["messages"][-1].content
    sentiment = state.get("sentiment", "Neutral")
    escalate_to_human = state.get("escalate_to_human", False)
    
    print(f"Agent reply: {reply}")
    print(f"Sentiment: {sentiment} | Escalate: {escalate_to_human}")
    
    return ChatResponse(
        reply=reply,
        sentiment=sentiment,
        escalate_to_human=escalate_to_human
    )

STREAM_TOKEN_DELAY = 0.18  # Decreased streaming response speed for comfortable, measured reading

async def chat_stream_generator(message: str, user_id: str = "user", thread_id: str = "default"):
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Fetch previous thread history from checkpointer
    try:
        snapshot = sky_companion_app.get_state(config)
        existing_messages = list(snapshot.values.get("messages", [])) if snapshot and snapshot.values else []
    except Exception as e:
        print(f"Error fetching state snapshot: {e}")
        existing_messages = []

    # 2. Sentiment analysis
    sentiment = analyze_sentiment(message)
    escalate_to_human = True if sentiment == "Angry/Frustrated" else False
    
    # Send initial metadata
    initial_metadata = {
        "type": "metadata",
        "sentiment": sentiment,
        "escalate_to_human": escalate_to_human
    }
    yield f"data: {json.dumps(initial_metadata)}\n\n"
    
    user_msg = HumanMessage(content=message)
    
    if escalate_to_human:
        reply = "SYSTEM: Routing to Support Agent..."
        words = reply.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
            await asyncio.sleep(STREAM_TOKEN_DELAY)
        
        # Persist to thread checkpointer
        sky_companion_app.update_state(config, {
            "messages": [user_msg, SystemMessage(content=reply)],
            "sentiment": sentiment,
            "escalate_to_human": True
        })
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    # Build context: system prompt + previous chat turns + new user message
    history_with_current = existing_messages + [user_msg]
    prompt_content = get_system_prompt(user_id, sentiment)
    system_prompt = SystemMessage(content=prompt_content)
    full_messages = [system_prompt] + history_with_current

    llm_with_tools = llm.bind_tools(sky_tools) if sky_tools else llm
    
    try:
        first_response = llm_with_tools.invoke(full_messages)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        from models import generate_fallback_response
        first_response = generate_fallback_response(full_messages, sky_tools)

    if hasattr(first_response, "tool_calls") and first_response.tool_calls:
        # Execute tools
        tool_outputs = []
        for tool_call in first_response.tool_calls:
            for t in sky_tools:
                if t.name == tool_call["name"]:
                    args = dict(tool_call["args"])
                    result = t.invoke(args)
                    tool_outputs.append(HumanMessage(content=f"Tool output: {result}"))
        
        # Combine messages for synthesis
        synthesis_messages = full_messages + [first_response] + tool_outputs
        accumulated_reply = ""
        
        # Stream synthesis response with pacing delay
        try:
            async for chunk in llm.astream(synthesis_messages):
                token = chunk.content
                accumulated_reply += token
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
                await asyncio.sleep(STREAM_TOKEN_DELAY)
        except Exception as e:
            print(f"Streaming synthesis error: {e}")
            from models import generate_fallback_response
            fallback = generate_fallback_response(synthesis_messages, sky_tools)
            accumulated_reply = fallback.content
            yield f"data: {json.dumps({'type': 'token', 'token': accumulated_reply})}\n\n"
            
        final_ai_msg = AIMessage(content=accumulated_reply)
        sky_companion_app.update_state(config, {
            "messages": [user_msg, first_response] + tool_outputs + [final_ai_msg],
            "sentiment": sentiment,
            "escalate_to_human": False
        })
    else:
        # No tool calls, stream response content token/word by word with pacing delay
        reply = first_response.content
        words = reply.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
            await asyncio.sleep(STREAM_TOKEN_DELAY)
        
        sky_companion_app.update_state(config, {
            "messages": [user_msg, first_response],
            "sentiment": sentiment,
            "escalate_to_human": False
        })
            
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id or "default"
    print(f"\n--- API Request (Streaming) [Thread: {thread_id}] ---")
    print(f"User: {request.message}")
    return StreamingResponse(
        chat_stream_generator(request.message, request.user_id or "user", thread_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
