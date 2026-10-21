# gpt.py - AI Integration for IVERI AI
# Powered by Google Gemini Flash with Online RAG (Retrieval-Augmented Generation)

import os
import json
import urllib.request
import urllib.error
import config
import online_rag

# IVERI's system prompt - OPTIMIZED for concise, accurate voice/text responses
SYSTEM_PROMPT = """You are IVERI, an advanced intelligent voice-first AI assistant.

PURPOSE:
Understand the user's intent even if phrased casually, indirectly, or imperfectly.
Respond naturally, efficiently, and intelligently.

CORE BEHAVIOR:
- Default to one to two short, direct sentences.
- When answering questions based on real-time news or live web search, communicate the key facts clearly and conversationally.
- Never repeat the user's question.
- Never explain reasoning.
- Never use emojis.
- Never use markdown, bullets, or lists.
- Never ask follow-up questions unless absolutely required for clarity.

INTELLIGENCE RULES:
- Interpret meaning, not just keywords.
- Handle paraphrasing, slang, and incomplete sentences.
- Infer simple context from conversation history.
- If multiple interpretations exist, choose the most reasonable one.

ONLINE RAG & LIVE WEB AWARENESS:
- Ground your answer in the real-time online web context provided.
- Do not repeat the context literally or use markdown bolding (e.g. no ** or *).
- State the latest developments conversationally in 1 to 3 clear, spoken sentences.

CONVERSATION STYLE:
- Calm, confident, professional.
- Slightly futuristic tone.
- No personality exposition.
- No self references.

GREETING:
- Single short greeting.
Example: "Hello. How can I help?"

FACTUAL QUESTIONS:
- Answer with the fact only.

IDENTITY:
- You are IVERI.
- Powered by Gemini Flash with live Online RAG capabilities.

FINAL OUTPUT:
Return only the spoken sentence.
No extra text.
"""

# Conversation history for context
conversation_history = []
MAX_HISTORY = getattr(config, 'MAX_CONVERSATION_HISTORY', 6)

# Flash model preference list (fastest active models first)
FLASH_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
]


def _call_gemini_api(prompt, api_key):
    """Call Google Gemini REST endpoint directly with automatic Flash model fallback"""
    rate_limited = False
    for model_name in FLASH_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": getattr(config, 'MAX_TOKENS', 1000),
                "temperature": getattr(config, 'TEMPERATURE', 0.5),
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            if e.code == 404 and ("not found" in err_body.lower() or "no longer available" in err_body.lower()):
                continue
            elif e.code == 400 and "API_KEY_INVALID" in err_body:
                return "Your Gemini API key appears invalid. Please check your .env file."
            elif e.code == 429:
                rate_limited = True
                continue
            elif e.code in (500, 502, 503, 504):
                continue
            else:
                print(f"Gemini HTTP {e.code} for {model_name}: {err_body[:100]}")
        except Exception as e:
            continue
            
    if rate_limited:
        return "Gemini API rate limit reached. Please wait a moment."
    return None


def get_response(user_input, use_history=True, force_rag=False):
    """
    Get an intelligent response from Gemini Flash, augmented with real-time Online RAG.
    
    Args:
        user_input: The user's query or instruction
        use_history: Whether to use conversation history
        force_rag: Force online retrieval regardless of heuristic
        
    Returns:
        The AI's response as a string
    """
    global conversation_history
    
    api_key = getattr(config, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    if not api_key or api_key.startswith('your'):
        return ("I need a Google Gemini API key to answer general questions. "
                "Get your free key at https://aistudio.google.com/app/apikey "
                "and set GEMINI_API_KEY in your .env file.")
    
    try:
        # Check if query needs real-time online RAG
        should_rag, topic = online_rag.should_use_rag(user_input)
        online_context = ""
        if should_rag or force_rag:
            search_query = topic if topic else user_input
            online_context = online_rag.retrieve_online_context(search_query)

        # Build prompt including real-time web context and recent history
        context_blocks = []
        if online_context:
            context_blocks.append(f"REAL-TIME ONLINE WEB INFORMATION (Retrieved live from the internet):\n{online_context}\n")
        
        if use_history and conversation_history:
            for item in conversation_history[-MAX_HISTORY:]:
                context_blocks.append(f"{item['role'].capitalize()}: {item['content']}")
        context_blocks.append(f"User: {user_input}")
        full_prompt = "\n".join(context_blocks)
        
        ai_response = _call_gemini_api(full_prompt, api_key)
        
        if not ai_response:
            return "Sorry, I had trouble processing that with Gemini. Please try again."
        
        # Update history
        if use_history:
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": ai_response})
            if len(conversation_history) > MAX_HISTORY * 2:
                conversation_history = conversation_history[-MAX_HISTORY * 2:]
                
        return ai_response

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Sorry, I had trouble processing that. Please try again."


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return "Conversation cleared."


def get_simple_response(prompt):
    """Get a response without history - for one-off queries"""
    return get_response(prompt, use_history=False)
