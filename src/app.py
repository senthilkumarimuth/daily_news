from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langchain_community.llms import Ollama
from typing import Dict, TypedDict

# Define state schema
class AgentState(TypedDict):
    messages: list
    next: str

# Initialize Ollama model
model = Ollama(model="gemma3:1b")

# Create workflow graph
workflow = StateGraph(AgentState)

# Define news fetching function
def get_news(state: AgentState) -> AgentState:
    messages = state["messages"]
    response = model.invoke(
        "Please provide me with the latest news headlines in a concise format."
    )
    messages.append(HumanMessage(content=response))
    return {"messages": messages, "next": "end"}

# Add node and edge to graph
workflow.add_node("get_news", get_news)
workflow.set_entry_point("get_news")
#workflow.add_edge("get_news", "end")

# Compile graph
app = workflow.compile()

# Run the workflow
result = app.invoke({
    "messages": [],
    "next": "get_news"
})

# Print results
for message in result["messages"]:
    print(message.content)