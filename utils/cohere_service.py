import os
import cohere
import re

# Examples for emotion classification
EMOTION_EXAMPLES = [
    {"text": "I'm so overwhelmed with all these bills piling up", "label": "stressed"},
    {"text": "I can't handle the pressure of my finances right now", "label": "stressed"},
    {"text": "I feel like I'm drowning in financial problems", "label": "stressed"},
    
    {"text": "I'm worried I won't be able to pay rent this month", "label": "anxious"},
    {"text": "I keep checking my bank account and stressing about money", "label": "anxious"},
    {"text": "I have this constant fear about my financial future", "label": "anxious"},
    
    {"text": "I just want to buy something to make myself feel better", "label": "retail_therapy"},
    {"text": "Shopping helps me forget about my problems", "label": "retail_therapy"},
    {"text": "I deserve to treat myself after the week I've had", "label": "retail_therapy"},
    
    {"text": "I'm excited about my budget progress this month", "label": "motivated"},
    {"text": "I managed to save more than I expected", "label": "motivated"},
    {"text": "I feel like I'm finally getting my finances under control", "label": "motivated"},
    
    {"text": "I paid my regular bills today", "label": "neutral"},
    {"text": "I'm thinking about my monthly budget", "label": "neutral"},
    {"text": "I need to check my account balance", "label": "neutral"}
]

def analyze_emotion(text):
    """Analyzes the emotional content of text using Cohere's API"""
    try:
        # Get API key from environment
        api_key = os.environ.get("COHERE_API_KEY")
        
        if not api_key:
            # For hackathon, provide fallback mechanism
            return fallback_emotion_detection(text)
        
        # Initialize Cohere client
        co = cohere.Client(api_key)
        
        # Send classification request
        response = co.classify(
            model="large",
            inputs=[text],
            examples=EMOTION_EXAMPLES
        )
        
        return {
            "emotion": response.classifications[0].prediction,
            "confidence": response.classifications[0].confidence,
            "all_predictions": response.classifications[0].confidences
        }
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return fallback_emotion_detection(text)

def fallback_emotion_detection(text):
    """Simple keyword-based emotion detection as backup"""
    text = text.lower()
    
    # Simple keyword-based analysis as backup
    emotion_keywords = {
        "stressed": ['overwhelm', 'stress', 'pressure', 'too much', 'cant handle'],
        "anxious": ['worry', 'anxious', 'anxiety', 'fear', 'afraid', 'uncertain'],
        "retail_therapy": ['treat myself', 'deserve', 'shopping', 'buy something'],
        "motivated": ['excited', 'progress', 'control', 'achieving', 'saving'],
        "happy": ['happy', 'glad', 'pleased', 'delighted', 'joy'],
        "neutral": ['regular', 'normal', 'usual', 'typical']
    }
    
    # Count keyword matches for each emotion
    scores = {}
    for emotion, keywords in emotion_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        scores[emotion] = score
    
    # Find highest scoring emotion
    if max(scores.values()) > 0:
        highest_emotion = max(scores, key=scores.get)
        confidence = min(scores[highest_emotion] * 0.2, 0.9)  # Simple scaling
    else:
        highest_emotion = "neutral"
        confidence = 0.5
    
    return {
        "emotion": highest_emotion,
        "confidence": confidence,
        "all_predictions": scores
    }