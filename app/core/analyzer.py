# === File: analyzer.py ===
import os
import json
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from typing import List, Dict
import openai
from datetime import datetime
import logging
from functools import lru_cache

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize models
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load API key from .env file
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger.debug(f"OpenAI API Key loaded: {os.getenv('OPENAI_API_KEY')[:5]}...")

# Initialize FAISS index lazily
_faiss_index = None
_metadata = {}

def get_faiss_index():
    global _faiss_index, _metadata
    if _faiss_index is None:
        try:
            _faiss_index = faiss.read_index("faiss_index/vector.index")
            with open("faiss_index/metadata.json", "r") as f:
                _metadata = json.load(f)
            logger.debug("FAISS index and metadata loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load FAISS index: {str(e)}")
            _faiss_index = None
            _metadata = {}
    return _faiss_index, _metadata

# Initialize psychoanalytic profile
psycho_profile = {
    "psychoanalysis": {},
    "about_user": {}
}

# === Emotion Analysis ===
def analyze_emotions(user_input: str) -> Dict[str, float]:
    transformer_output = emotion_classifier(user_input)
    emotions = {item['label']: round(item['score'], 4) for item in transformer_output[0] if item['score'] > 0.01}

    with open("emotions.txt", "w", encoding="utf-8") as f:
        json.dump(emotions, f, indent=2)

    return emotions

# === RAG Retrieval ===
def retrieve_context(query: str, k: int = 3) -> List[str]:
    """
    Retrieve relevant context from memory using semantic search
    """
    index, metadata = get_faiss_index()
    if index is None:
        logger.warning("FAISS index is not loaded, returning empty list")
        return []
    
    try:
        query_embedding = get_embedding(query)
        query_embedding = np.array(query_embedding).astype('float32')
        query_embedding = query_embedding.reshape(1, -1)
        
        distances, indices = index.search(query_embedding, k)
        results = []
        
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(metadata):
                results.append(metadata[idx])
        
        with open("rag_output.txt", "w", encoding="utf-8") as f:
            for i, chunk in enumerate(results):
                f.write(f"Chunk {i + 1}:\n{chunk}\n\n")

        return results
    except Exception as e:
        logger.error(f"Error in retrieve_context: {str(e)}")
        return []

# === Update Psychoanalytic Profile ===
def update_psycho_profile(user_input: str, context_chunks: List[str]) -> None:
    prompt = f"""
You are a psychoanalyst AI. Based on the user input and context, provide:
1. Good/Bad thinking patterns
2. Axioms or core beliefs
3. Cognitive distortions
4. Defense mechanisms
5. Maladaptive patterns
6. Inferred beliefs / self-schema
7. Emotional regulation patterns

Input:
{user_input}

Context:
{''.join(context_chunks[:3])}
"""

    # Simulate psychoanalytic inference
    psychoanalysis_output = {
        "thinking_patterns": {"User demonstrates proactive optimism.": {"short_term": 0.7, "long_term": 0.6}},
        "axioms": {"Believes effort leads to success.": {"short_term": 0.8, "long_term": 0.7}},
        "cognitive_distortions": {"Possible minimization of potential risks.": {"short_term": 0.3, "long_term": 0.2}},
        "defense_mechanisms": {"Might intellectualize emotions when excited.": {"short_term": 0.4, "long_term": 0.3}},
        "maladaptive_patterns": {"Mild dependency on external validation for emotional uplift.": {"short_term": 0.35, "long_term": 0.25}},
        "inferred_beliefs": {"Views emotional connection as part of personal success.": {"short_term": 0.5, "long_term": 0.4}},
        "emotional_regulation": {"Utilizes positive feedback loops to maintain mood.": {"short_term": 0.6, "long_term": 0.5}}
    }

    psycho_profile["psychoanalysis"] = psychoanalysis_output

    with open("psychoanalysis.txt", "w", encoding="utf-8") as f:
        json.dump(psycho_profile["psychoanalysis"], f, indent=2)

# === Expose profile for external use ===
def get_psycho_profile() -> Dict[str, Dict]:
    return psycho_profile

@lru_cache(maxsize=100)
def get_embedding(text: str) -> List[float]:
    """
    Get embedding for text using OpenAI's API with caching
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding: {str(e)}")
        raise

def update_psychoanalytic_profile(user_text: str, current_profile: Dict) -> Dict:
    """
    Update psychoanalytic profile based on new user input
    """
    try:
        prompt = f"""
Analyze the following user message from a psychoanalytic perspective:
"{user_text}"

Current profile:
{json.dumps(current_profile, indent=2)}

Provide insights about:
1. Defense mechanisms
2. Transference patterns
3. Core conflicts
4. Emotional themes
5. Relationship patterns

Format the response as a JSON object with these keys.
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a psychoanalytic expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        new_insights = json.loads(response.choices[0].message.content)
        updated_profile = current_profile.copy()
        updated_profile.update(new_insights)
        updated_profile["last_updated"] = datetime.utcnow().isoformat()
        
        return updated_profile
    except Exception as e:
        logger.error(f"Error in update_psychoanalytic_profile: {str(e)}")
        return current_profile

# curl -X POST "http://localhost:8000/api/v1/chat/send" -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2N2ZhZDJkOTJjYjQ5NDA1NWVlNzcwZjAiLCJleHAiOjE3NDQ1MDU0NTF9.EXKHrd0c8tOg7Valh53R78KbL6roCVti5Zsx6xgBsVY" -d '{"message": "Hello, how are you?", "emotion": "neutral"}' | jq