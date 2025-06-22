from tavily import TavilyClient
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=TAVILY_API_KEY)

def tavily_search(query: str) -> dict:
    try:
        response = client.search(query=query, include_answer=True)
        return {
            "summary": response.get("answer", "No summary found."),
            "citations": [res.get("url") for res in response.get("results", []) if "url" in res]
        }
    except Exception as e:
        logger.error(f"Failed Tavily search for query: {query} | Error: {e}")
        return {"summary": "Error retrieving data", "citations": []}