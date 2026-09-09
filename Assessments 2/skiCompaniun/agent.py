import os
import json
from typing import Annotated, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from models import llm, analyze_sentiment
from tools import sky_tools

def load_rules_json():
    rules_path = os.path.join(os.path.dirname(__file__), "rules.json")
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "persona": "You are SKY Companion, a warm, friendly, exceptionally helpful, and open conversational AI companion. You love engaging with users, discussing any topic they are interested in, answering questions, sharing ideas, and providing thoughtful, engaging conversation.",
            "rules": [
                "Be friendly, approachable, open-minded, and enthusiastic. Speak naturally and conversationally.",
                "Keep answers short, concise, and brief. Avoid long-winded paragraphs unless the user specifically asks for detailed elaboration.",
                "Feel free to discuss any topic the user brings up—whether it's general knowledge, creative ideas, science, entertainment, daily life, philosophy, technology, or personal interests.",
                "Do not reference or depend on image analysis or image data files; focus entirely on conversing with and assisting the user.",
                "Keep all technical backend code details invisible to the user unless explicitly requested."
            ],
            "guidelines": "Always be welcoming, interactive, and helpful. Keep responses concise and to the point while staying warm, and ask brief open follow-up questions to keep the conversation engaging!"
        }

def get_system_prompt(user_id: Optional[str] = "user", sentiment: str = "Neutral") -> str:
    data = load_rules_json()
    persona = data.get("persona", "")
    rules_list = data.get("rules", [])
    guidelines = data.get("guidelines", "")

    rules_str = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules_list))
    
    return (
        f"{persona}\n\n"
        f"CRITICAL ASSISTANT RULES:\n"
        f"{rules_str}\n\n"
        f"{guidelines}\n"
        f"User Sentiment: {sentiment}."
    )

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: Optional[str]
    sentiment: str
    escalate_to_human: bool

llm_with_tools = llm.bind_tools(sky_tools) if sky_tools else llm

def input_processor_node(state: AgentState):
    latest_message = state["messages"][-1].content
    sentiment = analyze_sentiment(latest_message)
    escalate = True if sentiment == "Angry/Frustrated" else False
    return {"sentiment": sentiment, "escalate_to_human": escalate}

def companion_router_node(state: AgentState):
    if state["escalate_to_human"]:
        return {"messages": [SystemMessage(content="SYSTEM: Routing to Support Agent...")]}
    user_id = state.get("user_id", "user")
    prompt_content = get_system_prompt(user_id, state["sentiment"])
    system_prompt = SystemMessage(content=prompt_content)
    return {"messages": [llm_with_tools.invoke([system_prompt] + state["messages"])]}

def tool_executor_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_outputs = []
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            for t in sky_tools:
                if t.name == tool_call["name"]:
                    args = dict(tool_call["args"])
                    result = t.invoke(args)
                    tool_outputs.append(HumanMessage(content=f"Tool output: {result}"))
    return {"messages": [llm.invoke(state["messages"] + tool_outputs)]}

def route_next_node(state: AgentState):
    if state["escalate_to_human"]: return "human_escalation"
    if hasattr(state["messages"][-1], "tool_calls") and state["messages"][-1].tool_calls: return "execute_tools"
    return END

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

workflow = StateGraph(AgentState)
workflow.add_node("processor", input_processor_node)
workflow.add_node("companion", companion_router_node)
workflow.add_node("execute_tools", tool_executor_node)

workflow.add_edge(START, "processor")
workflow.add_edge("processor", "companion")
workflow.add_conditional_edges("companion", route_next_node, {"execute_tools": "execute_tools", "human_escalation": END, END: END})
workflow.add_edge("execute_tools", END)
sky_companion_app = workflow.compile(checkpointer=memory)