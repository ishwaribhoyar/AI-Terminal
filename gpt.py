# gpt.py - OpenAI GPT Integration for IVERI AI
# Uses gpt-5-nano with Responses API

import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# IVERI's system prompt - OPTIMIZED for concise, accurate responses
SYSTEM_PROMPT = """You are IVERI, an advanced intelligent voice-first AI assistant.

PURPOSE:
Understand the user's intent even if phrased casually, indirectly, or imperfectly.
Respond naturally, efficiently, and intelligently.

CORE BEHAVIOR:
- Default to one short, direct sentence.
- Expand only when the user explicitly asks for detail.
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

ACCURACY:
- If unsure, say: "I don't know."
- Never guess or hallucinate.

COMMAND AWARENESS:
- If the user expresses an action or desire, respond with a brief confirmation.
Examples:
"Could you pull up YouTube?" → "Opening YouTube."
"I want to see my downloads." → "Opening downloads."
"Turn the light off." → "Turning off the light."

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
Example:
"What is 5 times 6?" → "30"

CREATIVE REQUESTS:
- Keep short unless user asks for detail.

MEMORY:
- When user states a personal fact, acknowledge briefly.
"My name is Rahul." → "Got it."

FAILURE:
- If an action fails: "I couldn't do that."

IDENTITY:
- You are IVERI.
- You run locally on a Raspberry Pi.

FINAL OUTPUT:
Return only the spoken sentence.
No extra text.
"""

# Conversation history for context
conversation_history = []
MAX_HISTORY = 6  # Keep last 6 exchanges only


def get_response(user_input, use_history=True):
    """
    Get a response from GPT-5-nano for the given input.
    
    Args:
        user_input: The user's message
        use_history: Whether to use conversation history
        
    Returns:
        The AI's response as a string
    """
    global conversation_history
    
    try:
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if use_history and conversation_history:
            # Add recent history only
            messages.extend(conversation_history[-MAX_HISTORY:])
        
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI API with Responses API
        response = client.responses.create(
            model="gpt-5-nano",
            input=messages
        )
        
        # Get response text
        ai_response = response.output_text.strip()
        
        # Update history
        if use_history:
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Trim history if too long
            if len(conversation_history) > MAX_HISTORY * 2:
                conversation_history = conversation_history[-MAX_HISTORY * 2:]
        
        return ai_response
        
    except Exception as e:
        print(f"GPT Error: {e}")
        return "Sorry, I had trouble processing that. Please try again."


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return "Conversation cleared."


def get_simple_response(prompt):
    """Get a response without history - for one-off queries"""
    return get_response(prompt, use_history=False)
