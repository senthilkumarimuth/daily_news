from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langchain_ollama import OllamaLLM
from langchain_community.utilities import SerpAPIWrapper
from typing import Dict, TypedDict
from dotenv import load_dotenv
import os
import sys
import json
from datetime import datetime
from custom_dirs import RootDirectory
from custom_utils.gnews_headlines import get_news_from_gnews
from custom_utils.serpapi_utils import get_news_from_serpapi

# Load environment variables
load_dotenv()

try:
    # Define state schema
    class AgentState(TypedDict):
        messages: list
        next: str

    # Initialize Ollama model and search tool
    try:
        print("Initializing Ollama model...")
        model = OllamaLLM(model="gemma3:1b", base_url="http://localhost:11434", timeout=300)
        print("Model initialized successfully")
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        sys.exit(1)

    print("Initializing search tool...")
    search_tool = SerpAPIWrapper(serpapi_api_key=os.getenv('serp_api_key'), search_engine="google_news")
    print("Search tool initialized successfully")

    # Create workflow graph
    print("Creating workflow graph...")
    workflow = StateGraph(AgentState)

    # Define news fetching function
    def get_news(state: AgentState) -> AgentState:
        messages = state["messages"]
        
        print("Fetching news from search tool...")
        # Search for latest news
        search_results = get_news_from_serpapi("latest news headlines today in india and chennai")
        print("Search results received")
        
        print("Fetching news from gnews...")
        gnews_headlines = get_news_from_gnews()
        print("Gnews headlines received")
        
        print("Fetching AI news...")
        search_results_ai = get_news_from_serpapi("latest news headlines today related to Artificial Intelligence")
        print("AI news received")

        print("Fetching share market news...")
        search_results_share_market = get_news_from_serpapi("latest news about indian share market")
        print("Share market news received")
        
        news = search_results + gnews_headlines + search_results_ai + str(search_results_share_market)
        print("Combining all news sources...")
        print(news)
        
        print("Generating summary with model...")
        # Have the model summarize the search results
        prompt = f"Please summarize these news headlines in a concise format, with each headline on a new line: {news}"
        response = model.invoke(prompt)
        print("Summary generated successfully")
        
        messages.append(HumanMessage(content=response))
        return {"messages": messages, "next": "end"}

    # Add node and edge to graph
    workflow.add_node("get_news", get_news)
    workflow.set_entry_point("get_news")

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

    # Process news lines
    news_lines = []
    for message in result["messages"]:
        for line in message.content.split('\n'):
            if line.strip():  # Only include non-empty lines
                news_lines.append(line.strip())

    # Create data directory if it doesn't exist
    data_dir = os.path.join(RootDirectory.path, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Prepare data for JSON
    news_data = {
        'news_lines': news_lines,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Write data to JSON file
    json_path = os.path.join(data_dir, 'news_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)

except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)
