# === File: responder.py ===
import openai
from dotenv import load_dotenv
import os
import json
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load API key from .env file
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
# logger.debug(f"OpenAI API Key loaded: {openai.api_key[:5]}...")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger.debug(f"OpenAI API Key loaded: {os.getenv('OPENAI_API_KEY')[:5]}...")

SYSTEM_RESPONSES = [
    "I understand how you're feeling. Would you like to tell me more about that?",
    "That sounds challenging. How are you coping with it?",
    "I'm here to listen. What else is on your mind?",
    "Thank you for sharing that with me. How does it make you feel?",
    "I appreciate you opening up about this. What support do you need right now?",
    "I hear you. Let's explore that further together.",
    "That's an important observation. How long have you been feeling this way?",
    "I can see this is meaningful to you. Would you like to discuss it more?",
    "Your feelings are valid. What would help you feel better?",
    "I'm here to support you through this. What's the next step you'd like to take?"
]

def generate_response(user_text: str,
                     psycho_profile: Dict[str, Dict],
                     retrieved_chunks: List[str] = None) -> str:
    """
    Generate a thoughtful response using GPT-4, considering the psychoanalytic profile and retrieved memory.
    """
    try:
        logger.debug("Starting response generation...")
        logger.debug(f"User text: {user_text}")
        logger.debug(f"Psycho profile: {json.dumps(psycho_profile, indent=2)}")

        prompt = f"""
You are a deeply compassionate, emotionally intelligent AI therapist.
Here is the user's message:
"{user_text}"

Here are psychoanalytic observations about the user:
{json.dumps(psycho_profile.get("psychoanalysis", {}), indent=2)}

Please respond like a therapist would — warm, curious, open-minded, and reflective. Use their language when possible.
"""

        logger.debug("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an insightful and compassionate AI therapist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )
        logger.debug("Received response from OpenAI API")
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise