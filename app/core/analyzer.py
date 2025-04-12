# === File: analyzer.py ===
import json
from transformers import pipeline
from typing import Dict, Any
from dotenv import load_dotenv
import os
import openai

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)

def clamp_probability(value, min_val=0.01, max_val=0.95):
    return max(min_val, min(value, max_val))

def initialize_category_memory():
    return {
        "cognitive_distortions": {},
        "defense_mechanisms": {},
        "maladaptive_patterns": {},
        "inferred_beliefs": {},
        "emotional_regulation": {},
        "axioms": {},
        "thinking_patterns": {}
    }

def initialize_about_user_memory():
    return {
        "certain": {},
        "unsure": {}
    }

def update_about_user_memory(text: str, emotions: Dict[str, float], about_user: AboutUser) -> AboutUser:
    # This is a placeholder for the actual analysis logic
    # In a real implementation, you would use an LLM or other analysis tools
    # to generate insights about the user based on their input and emotions
    
    # Example analysis (replace with actual analysis logic)
    certain = {
        "expresses_emotions": True,
        "seeks_understanding": True
    }
    
    unsure = {
        "self_awareness": UnsureTrait(short_term=0.7, long_term=0.6),
        "emotional_maturity": UnsureTrait(short_term=0.5, long_term=0.4)
    }
    
    # Update the existing about_user with new insights
    updated_about = AboutUser(
        certain={**about_user.certain, **certain},
        unsure={**about_user.unsure, **unsure},
        last_updated=datetime.utcnow()
    )
    
    return updated_about


def analyze_user_input(
    user_text: str,
    about_user_memory: Dict[str, Any]
) -> Dict[str, Any]:
    transformer_output = classifier(user_text)[0]
    emotions = {item['label']: round(item['score'], 4) for item in transformer_output if item['score'] > 0.01}
    about_user = update_about_user_memory(user_text, emotions, about_user_memory)
    psycho = update_psychoanalysis_memory(user_text, emotions)
    
    return {
        "psychoanalysis": psycho,
        "emotions": emotions,
        "about_user": about_user,
        "updated_global_memory": global_memory
    }