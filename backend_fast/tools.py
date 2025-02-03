from typing import Dict, List
import os
from crewai_tools import SerperDevTool

# Ensure the API key is set
if not os.environ['SERPER_API_KEY']:
    raise EnvironmentError("SERPER_API_KEY is not set in the environment.")

def search_keywords(keywords: List[str]) -> List[Dict[str, str]]:
    """
    Search for keywords on Google and retrieve top results.

    Args:
        keywords (List[str]): List of keywords to search for.

    Returns:
        List[Dict[str, str]]: List of search result dictionaries for each keyword.
    """
    # Initialize the Serper tool
    search_tool = SerperDevTool(n_results=1)
    results = []

    # Perform searches for each keyword
    for keyword in keywords:
        search_result = search_tool.run(search_query= "what is {keyword}")
        results.append({"keyword": keyword, "result": search_result})

    return results


if __name__ == '__main__':
    # Example keywords to search
    keywords = ['Apache Hadoop']#, 'LangChain', 'Hive']
    results = search_keywords(keywords)
    for res in results:
        print(f"Keyword: {res['keyword']}")
        print(f"Result: {res['result']}\n")
