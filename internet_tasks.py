# internet_tasks.py - Internet Tasks for IVERI AI (Weather, News, Search, Wikipedia)

import os
import requests
import webbrowser
import urllib.parse
import online_rag

try:
    import config
    WEATHER_API_KEY = getattr(config, 'WEATHER_API_KEY', '') or os.getenv('WEATHER_API_KEY', '')
    NEWS_API_KEY = getattr(config, 'NEWS_API_KEY', '') or os.getenv('NEWS_API_KEY', '')
except Exception:
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')


def google_search(query):
    """
    Open Google search in browser.
    
    Args:
        query: Search query
    
    Returns:
        Status message
    """
    webbrowser.open(f'https://www.google.com/search?q={urllib.parse.quote(query)}')
    return f"I've opened Google search for '{query}' in your browser."


def get_weather(city="London"):
    """
    Get current weather for a city using OpenWeatherMap API,
    or falls back to zero-key wttr.in service.
    
    Args:
        city: City name
    
    Returns:
        Weather description string
    """
    clean_city = city.strip()
    
    # 1. If OpenWeatherMap API key is present, use it
    if WEATHER_API_KEY and not WEATHER_API_KEY.startswith('your'):
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": clean_city,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                temp = round(data['main']['temp'])
                feels_like = round(data['main']['feels_like'])
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                return (f"The weather in {clean_city} is currently {description} "
                        f"with a temperature of {temp}°C, feels like {feels_like}°C. "
                        f"Humidity is at {humidity}%.")
        except Exception as e:
            print(f"OpenWeatherMap API note: {e}. Trying fallback provider...")
    
    # 2. Zero-config fallback via wttr.in
    try:
        url = f"https://wttr.in/{urllib.parse.quote(clean_city)}?format=j1"
        response = requests.get(url, timeout=8, headers={"User-Agent": "IVERI-Assistant/1.0"})
        if response.status_code == 200:
            data = response.json()
            curr = data['current_condition'][0]
            temp = curr['temp_C']
            feels = curr['FeelsLikeC']
            desc = curr['weatherDesc'][0]['value']
            humidity = curr['humidity']
            return (f"The weather in {clean_city} is currently {desc} "
                    f"at {temp}°C (feels like {feels}°C) with {humidity}% humidity.")
    except Exception as e:
        print(f"Weather fallback error: {e}")

    return f"I'm having trouble getting the weather for {clean_city} right now. Please check your internet connection."


def get_news(category="general", country="us"):
    """
    Get top real-time headlines using Online RAG (Google News RSS) with NewsAPI fallback.
    
    Args:
        category: News category (general, business, technology, sports, entertainment, health, science)
        country: Country code
    
    Returns:
        News summary string
    """
    # 1. Use real-time Online RAG news feed (instant & free, no key required)
    topic_map = {
        "general": None,
        "technology": "technology",
        "tech": "technology",
        "sports": "sports",
        "business": "business finance",
        "finance": "finance",
        "entertainment": "entertainment",
        "health": "health",
        "science": "science",
    }
    
    search_topic = topic_map.get(category.lower(), category)
    articles = online_rag.retrieve_live_news(topic=search_topic, limit=3)
    
    if articles:
        category_label = "general" if category == "general" else category
        news_text = f"Here are the latest {category_label} headlines: "
        for i, article in enumerate(articles, 1):
            source_tag = f" ({article['source']})" if article['source'] and article['source'] != "Unknown" else ""
            news_text += f"{i}. {article['title']}{source_tag}. "
        return news_text.strip()
        
    # 2. Fallback to NewsAPI if configured
    if NEWS_API_KEY and not NEWS_API_KEY.startswith('your'):
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": country,
                "category": category,
                "pageSize": 3,
                "apiKey": NEWS_API_KEY
            }
            response = requests.get(url, params=params, timeout=8)
            data = response.json()
            if response.status_code == 200 and data.get('articles'):
                articles = data['articles']
                news_text = f"Here are the top {len(articles)} {category} headlines: "
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    if ' - ' in title:
                        title = title.rsplit(' - ', 1)[0]
                    news_text += f"{i}. {title}. "
                return news_text
        except Exception as e:
            print(f"NewsAPI error: {e}")

    return "I'm having trouble fetching live news right now. Please check your internet connection."


def search_wikipedia(query, open_browser=True):
    """
    Get a concise Wikipedia summary and optionally open the article in browser.
    
    Args:
        query: Topic to search
        open_browser: Whether to also open in browser
        
    Returns:
        Concise summary string
    """
    clean_query = query.strip()
    if not clean_query:
        return "What would you like me to look up on Wikipedia?"
    
    formatted_title = clean_query.replace(' ', '_')
    summary_text = None
    
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted_title)}"
        resp = requests.get(url, timeout=6, headers={"User-Agent": "IVERI-Assistant/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get('extract')
            if extract:
                sentences = extract.split('. ')
                summary_text = '. '.join(sentences[:2])
                if not summary_text.endswith('.'):
                    summary_text += '.'
    except Exception as e:
        print(f"Wikipedia lookup note: {e}")
    
    if open_browser:
        webbrowser.open(f'https://en.wikipedia.org/wiki/{urllib.parse.quote(formatted_title)}')
        
    if summary_text:
        return f"{summary_text}"
    return f"Opening Wikipedia for {clean_query}."


def handle_internet_task(user_input):
    """
    Check if user input is an internet task.
    
    Args:
        user_input: User's spoken text
    
    Returns:
        tuple: (handled: bool, response: str)
    """
    text = user_input.lower().strip()
    
    # === WEATHER COMMANDS ===
    if 'weather' in text:
        city = "London"
        if ' in ' in text:
            city = text.split(' in ')[-1].strip().rstrip('?')
        elif ' for ' in text:
            city = text.split(' for ')[-1].strip().rstrip('?')
        elif ' at ' in text:
            city = text.split(' at ')[-1].strip().rstrip('?')
        
        for word in ['the', 'today', 'now', 'please', 'weather']:
            city = city.replace(word, '').strip()
        
        if not city:
            city = "London"
        
        return True, get_weather(city)
    
    # === NEWS COMMANDS (Online RAG Enabled) ===
    # If the user specifically asks "what's the news", "tech news", etc.
    # Note: If they ask detailed questions ("what is the latest news about X"),
    # gpt.get_response() handles it with deep Online RAG synthesis!
    if text in ['news', "what's the news", 'what is the news', 'tell me the news', 'headlines', "what's happening"]:
        return True, get_news()
    if 'tech news' in text or 'technology news' in text:
        return True, get_news(category="technology")
    if 'sports news' in text or 'sport news' in text:
        return True, get_news(category="sports")
    if 'business news' in text or 'finance news' in text:
        return True, get_news(category="business")
    if 'entertainment news' in text or 'celebrity news' in text:
        return True, get_news(category="entertainment")
    if 'health news' in text:
        return True, get_news(category="health")
    if 'science news' in text:
        return True, get_news(category="science")
    
    # === GOOGLE SEARCH ===
    if 'google ' in text and 'open google' not in text:
        query = text.replace('google ', '').strip()
        if query:
            return True, google_search(query)
    
    return False, None
