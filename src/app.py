from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Dict, TypedDict

# Define state schema
class AgentState(TypedDict):
    messages: list
    next: str

# Initialize Ollama model and search tool
model = Ollama(model="gemma3:1b", base_url="http://localhost:11434")
search_tool = DuckDuckGoSearchRun()

# Create workflow graph
workflow = StateGraph(AgentState)

# Define news fetching function
def get_news(state: AgentState) -> AgentState:
    messages = state["messages"]
    
    # Search for latest news
    search_results = search_tool.run("latest news headlines today in india and chennai")
    
    # Have the model summarize the search results
    prompt = f"Please summarize these news headlines in a concise format: {search_results}"
    response = model.invoke(prompt)
    
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

# Write results to index.html with enhanced styling
with open('index.html', 'w') as f:
    f.write('''
<html>
<head>
    <title>Latest News</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        p {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            line-height: 1.6;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: right;
        }
    </style>
</head>
<body>
    <h1>Latest News Headlines</h1>
''')
    
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for message in result["messages"]:
        f.write(f'    <p>{message.content}</p>\n')
    
    f.write(f'    <p class="timestamp">Last updated: {current_time}</p>\n')
    f.write('</body>\n</html>')

