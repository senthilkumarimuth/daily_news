from langchain_community.utilities import SerpAPIWrapper
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_news_from_serpapi(query: str) -> str:
    """
    Fetch news using SerpAPI with Google News search engine
    
    Args:
        query (str): The search query for news
        
    Returns:
        str: Search results containing news headlines
    """
    try:
        search_tool = SerpAPIWrapper(
            serpapi_api_key=os.getenv('serp_api_key'),
            search_engine="google_news"
        )
        return search_tool.run(query)
    except Exception as e:
        print(f"Error fetching news from SerpAPI: {str(e)}")
        return "" 
    

if __name__ == "__main__":
    #print(get_news_from_serpapi("latest news headlines today in india and chennai"))
    #print(get_news_from_serpapi("latest news headlines today related to Artificial Intelligence"))
    print(get_news_from_serpapi("latest news about share market"))

