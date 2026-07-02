from langchain_searchapi import SearchApiSearch, SearchApiRetriever

tool = SearchApiSearch()

print("=== Google Search ===")
result = tool.invoke({"query": "LangChain AI agents", "num": 3})
for r in result.get("organic_results", [])[:3]:
    print(f"  {r['position']}. {r['title']}")
    print(f"     {r['link']}")
    print()

print("=== YouTube ===")
result = tool.invoke({"query": "python async tutorial", "engine": "youtube", "num": 3})
for v in result.get("videos", [])[:3]:
    print(f"  - {v['title']}")
    print(f"    {v['link']}")
    print()

print("=== Google News ===")
result = tool.invoke({"query": "artificial intelligence", "engine": "google_news", "num": 3})
for r in result.get("organic_results", [])[:3]:
    print(f"  - {r['title']} ({r.get('source', '')})")
    print()

print("=== RAG Retriever ===")
retriever = SearchApiRetriever(num=5)
docs = retriever.invoke("best python web frameworks")
print(f"Retrieved {len(docs)} documents")
for doc in docs[:3]:
    print(f"  {doc.metadata['title']}")
    print(f"  {doc.page_content[:80]}...")
    print()
