# online_rag.py - Online Retrieval-Augmented Generation (RAG) for IVERI AI
# Retrieves real-time news, live events, and web knowledge, then augments Gemini responses.

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def retrieve_live_news(topic=None, limit=5):
    """
    Retrieve real-time updated news headlines and summaries from Google News RSS.
    
    Args:
        topic: Specific query or topic (e.g. 'technology', 'artificial intelligence', 'SpaceX').
               If None, retrieves general top world headlines.
        limit: Maximum number of articles to return.
        
    Returns:
        list of dicts containing title, source, publication date, and snippet.
    """
    if topic:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}&hl=en-US&gl=US&ceid=US:en"
    else:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        
    articles = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=7) as response:
            if response.status == 200:
                root = ET.fromstring(response.read())
                channel = root.find("channel")
                if channel is not None:
                    items = channel.findall("item")[:limit]
                    for item in items:
                        title_elem = item.find("title")
                        pub_elem = item.find("pubDate")
                        desc_elem = item.find("description")
                        
                        raw_title = title_elem.text if title_elem is not None else ""
                        pub_date = pub_elem.text if pub_elem is not None else ""
                        
                        # Clean title and separate source if present
                        source = "Unknown"
                        clean_title = raw_title
                        if " - " in raw_title:
                            clean_title, source = raw_title.rsplit(" - ", 1)
                            
                        # Clean description snippet (strip HTML tags)
                        desc_text = ""
                        if desc_elem is not None and desc_elem.text:
                            desc_text = re.sub(r"<[^>]+>", "", desc_elem.text).strip()
                            # Avoid duplicate title in description
                            if desc_text.startswith(clean_title):
                                desc_text = desc_text[len(clean_title):].strip()
                        
                        articles.append({
                            "title": clean_title.strip(),
                            "source": source.strip(),
                            "date": pub_date[:16] if pub_date else "Recent",
                            "snippet": desc_text[:150] if desc_text else ""
                        })
    except Exception as e:
        print(f"Online RAG News retrieval note: {e}")
        
    return articles


def retrieve_wikipedia_knowledge(query, limit=3):
    """
    Retrieve encyclopedic context and summaries from Wikipedia Search API.
    
    Args:
        query: Topic to search.
        limit: Maximum number of search snippets.
        
    Returns:
        list of strings containing encyclopedic snippets.
    """
    snippets = []
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8="
        req = urllib.request.Request(url, headers={"User-Agent": "IVERI-Assistant/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                search_results = data.get("query", {}).get("search", [])[:limit]
                for item in search_results:
                    title = item.get("title", "")
                    raw_snippet = item.get("snippet", "")
                    clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
                    if clean_snippet:
                        snippets.append(f"{title}: {clean_snippet}")
    except Exception as e:
        print(f"Online RAG Wikipedia retrieval note: {e}")
        
    return snippets


def should_use_rag(user_query):
    """
    Detect whether the query requires real-time / current online information.
    
    Args:
        user_query: The user's input text.
        
    Returns:
        tuple: (should_rag: bool, search_topic: str)
    """
    if not user_query:
        return False, ""
        
    text = user_query.lower().strip()
    
    # 1. Direct news requests
    news_patterns = [
        r"news (about|on|regarding|for) (.+)",
        r"(latest|current|updated|recent) news (on|about|for)? ?(.+)?",
        r"(what's|what is|tell me) the (latest|current|new|trending) (.+)",
        r"(latest|recent|current) updates? (on|about|regarding)? ?(.+)?",
        r"what happened (with|to|in|at) (.+)",
        r"who (is|won|leads) the (current|latest|new) (.+)",
        r"stock market (today|now|update)",
    ]
    
    for pat in news_patterns:
        m = re.search(pat, text)
        if m:
            groups = [g for g in m.groups() if g and g not in ['about', 'on', 'regarding', 'for', 'the']]
            topic = groups[-1].strip() if groups else text
            return True, topic
            
    # Keywords that indicate need for live online data
    live_keywords = [
        "latest", "current", "updated", "recent", "today", "yesterday",
        "right now", "news", "headlines", "trending", "stock price",
        "crypto price", "who won", "score of", "who is the current"
    ]
    
    for kw in live_keywords:
        if kw in text:
            # Extract topic by removing common filler words
            clean_topic = text
            for remove in ["what is the", "what are the", "tell me about", "can you tell me", "give me", "the"]:
                if clean_topic.startswith(remove):
                    clean_topic = clean_topic[len(remove):].strip()
            return True, clean_topic
            
    return False, ""


def retrieve_online_context(query, max_items=5):
    """
    Retrieve real-time online context from live sources.
    
    Args:
        query: Search query or user prompt.
        max_items: Number of items to retrieve.
        
    Returns:
        Structured context string ready for prompt injection, or empty string.
    """
    context_lines = []
    
    # 1. Retrieve fresh live news
    news_items = retrieve_live_news(topic=query, limit=max_items)
    if news_items:
        context_lines.append("--- LIVE ONLINE NEWS & WEB ARTICLES ---")
        for item in news_items:
            date_info = f" [{item['date']}]" if item['date'] else ""
            source_info = f" (Source: {item['source']})" if item['source'] else ""
            snippet_info = f" - {item['snippet']}" if item['snippet'] else ""
            context_lines.append(f"• {item['title']}{source_info}{date_info}{snippet_info}")
            
    # 2. If news returned fewer than 2 items, supplement with Wikipedia knowledge
    if len(news_items) < 2:
        wiki_snippets = retrieve_wikipedia_knowledge(query, limit=2)
        if wiki_snippets:
            context_lines.append("\n--- BACKGROUND KNOWLEDGE ---")
            for ws in wiki_snippets:
                context_lines.append(f"• {ws}")
                
    return "\n".join(context_lines)
