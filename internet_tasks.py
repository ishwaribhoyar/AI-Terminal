# internet_tasks.py - Internet Tasks for IVERI AI (Weather, News, Search)

import requests
import webbrowser
import os

# API Keys from environment
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
    webbrowser.open(f'https://www.google.com/search?q={query}')
    return f"I've opened Google search for '{query}' in your browser."


def get_weather(city="London"):
    """
    Get current weather for a city using OpenWeatherMap API.
    
    Args:
        city: City name
    
    Returns:
        Weather description string
    """
    if not WEATHER_API_KEY:
        return ("Weather service is not configured. "
                "Get a free API key from openweathermap.org and set WEATHER_API_KEY in your .env file.")
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            
            return (f"The weather in {city} is currently {description} "
                    f"with a temperature of {temp}°C, feels like {feels_like}°C. "
                    f"Humidity is at {humidity}%.")
        else:
            return f"I couldn't find weather information for {city}. Please check the city name."
            
    except requests.exceptions.Timeout:
        return "The weather service is taking too long to respond. Please try again."
    except Exception as e:
        print(f"Weather API error: {e}")
        return "I'm having trouble getting the weather right now. Please try again later."


def get_news(category="general", country="us"):
    """
    Get top news headlines using NewsAPI.
    
    Args:
        category: News category (business, technology, sports, entertainment, health, science)
        country: Country code (us, gb, in, au, etc.)
    
    Returns:
        News summary string
    """
    if not NEWS_API_KEY:
        return ("News service is not configured. "
                "Get a free API key from newsapi.org and set NEWS_API_KEY in your .env file.")
    
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "category": category,
            "pageSize": 3,
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('articles'):
            articles = data['articles']
            
            news_text = f"Here are the top {len(articles)} {category} headlines: "
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'No title')
                # Clean up title - remove source suffix
                if ' - ' in title:
                    title = title.rsplit(' - ', 1)[0]
                news_text += f"{i}. {title}. "
            
            return news_text
        else:
            return "I couldn't fetch the news right now. Please try again later."
            
    except requests.exceptions.Timeout:
        return "The news service is taking too long to respond. Please try again."
    except Exception as e:
        print(f"News API error: {e}")
        return "I'm having trouble getting the news right now. Please try again later."


def handle_internet_task(user_input):
    """
    Check if user input is an internet task.
    
    Args:
        user_input: User's spoken text
    
    Returns:
        tuple: (handled: bool, response: str)
    """
    text = user_input.lower()
    
    # === WEATHER COMMANDS ===
    if 'weather' in text:
        # Try to extract city name
        city = "London"  # Default
        
        if ' in ' in text:
            city = text.split(' in ')[-1].strip().rstrip('?')
        elif ' for ' in text:
            city = text.split(' for ')[-1].strip().rstrip('?')
        elif ' at ' in text:
            city = text.split(' at ')[-1].strip().rstrip('?')
        
        # Clean up common words
        for word in ['the', 'today', 'now', 'please', 'weather']:
            city = city.replace(word, '').strip()
        
        if not city:
            city = "London"
        
        return True, get_weather(city)
    
    # === NEWS COMMANDS ===
    if 'news' in text:
        if 'tech' in text or 'technology' in text:
            return True, get_news(category="technology")
        elif 'sport' in text:
            return True, get_news(category="sports")
        elif 'business' in text or 'finance' in text:
            return True, get_news(category="business")
        elif 'entertainment' in text or 'celebrity' in text:
            return True, get_news(category="entertainment")
        elif 'health' in text:
            return True, get_news(category="health")
        elif 'science' in text:
            return True, get_news(category="science")
        else:
            return True, get_news()
    
    # === GOOGLE SEARCH ===
    if 'google ' in text and 'open google' not in text:
        query = text.replace('google ', '').strip()
        if query:
            return True, google_search(query)
    
    return False, None
