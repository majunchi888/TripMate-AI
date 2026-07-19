from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query):
    response = client.search(query=query, max_results=5)

    results = []

    for i, r in enumerate(response["results"], 1):
        title = r.get("title", "Unknown") # 比r["title"]更安全
        url = r.get("url", "")
        snippet = r.get("content", "").strip()
        # 每段文字小于300字符，避免wall-of-text
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."  #.rsplit(" ", 1)[0]:从右边开始按空格分割，取第一个，舍弃最后一个空格后的部分，防止截断在半个单词

        results.append(f"{i}. **{title}**\n  {snippet}\n  {url}")    

    return "\n\n".join(results)