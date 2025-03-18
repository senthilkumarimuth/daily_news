from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
#from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain_community.utilities import SerpAPIWrapper
from typing import Dict, TypedDict
from dotenv import load_dotenv
import os
from custom_dirs import RootDirectory

# Load environment variables
load_dotenv()

# Define state schema
class AgentState(TypedDict):
    messages: list
    next: str

# Initialize Ollama model and search tool
model = OllamaLLM(model="llama3.1", base_url="http://localhost:11434")
search_tool = SerpAPIWrapper(serpapi_api_key=os.getenv('serp_api_key'), search_engine="google_news") # Configure SerpAPI to use Google News

# Create workflow graph
workflow = StateGraph(AgentState)

# Define news fetching function
def get_news(state: AgentState) -> AgentState:
    messages = state["messages"]
    
    # Search for latest news
    search_results = search_tool.run("latest news headlines today in india and chennai")
    print(search_results)
    # Have the model summarize the search results
    prompt = f"Please summarize these news headlines in a concise format, with each headline on a new line: {search_results}"
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
with open(os.path.join(RootDirectory.path,'index.html'), 'w') as f:
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
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            line-height: 1.6;
        }
        p:nth-child(1) {
            background: #e8f4f8;
            font-size: 1.2em;
            font-weight: bold;
        }
        p:nth-child(2n) {
            background: #fff3e6;
        }
        p:nth-child(2n+3) {
            background: #e6ffe6;
        }
        .timestamp {
            color: #7f8c8d;
            font-size: 0.8em;
            text-align: right;
            background: white !important;
        }
    </style>
</head>
<body>
    <h1>Latest News Headlines</h1>
''')
    
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for message in result["messages"]:
        # Split content by newlines and create paragraph for each line
        for line in message.content.split('\n'):
            if line.strip():  # Only create paragraph for non-empty lines
                f.write(f'    <p>{line.strip()}</p>\n')
    
    f.write(f'    <p class="timestamp">Last updated: {current_time}</p>\n')
    f.write('</body>\n</html>')
