from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
#from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain_community.utilities import SerpAPIWrapper
from typing import Dict, TypedDict
from dotenv import load_dotenv
import os
import subprocess
import time
import sys
import requests
from custom_dirs import RootDirectory

# Load environment variables
load_dotenv()

# Function to check if Ollama is running
def is_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to start Ollama
def start_ollama():
    print("Starting Ollama server...")
    # For Windows
    if sys.platform.startswith('win'):
        ollama_process = subprocess.Popen(["ollama", "serve"], 
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        # For Linux/Mac
        ollama_process = subprocess.Popen(["ollama", "serve"])
    
    # Wait for Ollama to start
    max_retries = 10
    for i in range(max_retries):
        if is_ollama_running():
            print("Ollama server is running.")
            return ollama_process
        print(f"Waiting for Ollama to start... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("Failed to start Ollama server.")
    sys.exit(1)

# Start Ollama if not running
ollama_process = None
if not is_ollama_running():
    ollama_process = start_ollama()
else:
    print("Ollama server is already running.")

try:
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

finally:
    # Shutdown Ollama if we started it
    if ollama_process:
        print("Shutting down Ollama server...")
        if sys.platform.startswith('win'):
            subprocess.call(["taskkill", "/F", "/T", "/PID", str(ollama_process.pid)])
        else:
            ollama_process.terminate()
            ollama_process.wait()
        print("Ollama server shut down successfully.")
