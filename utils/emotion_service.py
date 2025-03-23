import os
import re
import google.generativeai as genai
from utils.emotion_utils import EMOTION_EMOJIS

# Initialize Gemini
def setup_gemini():
    """Setup Gemini API with API key"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def analyze_emotion(text):
    """Analyzes the emotional content of text using Gemini API"""
    try:
        # Get API key and set up Gemini
        gemini_available = setup_gemini()
        
        if not gemini_available:
            # For hackathon, provide fallback mechanism
            return fallback_emotion_detection(text)
        
        # Generate prompt for emotion detection
        prompt = f"""
        Analyze the following text and classify the primary emotion expressed about finances.
        
        Text: "{text}"
        
        Choose EXACTLY ONE of these emotions:
        - stressed (feeling overwhelmed by financial pressure)
        - anxious (worried about financial future)
        - retail_therapy (desire to spend to feel better)
        - motivated (positive about financial progress)
        - happy (satisfied with financial situation)
        - neutral (no strong emotion about finances)
        
        Respond with ONLY the emotion name and a confidence score from 0.0 to 1.0, in this format:
        emotion: [emotion]
        confidence: [score]
        """
        
        # Generate content
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        # Parse response to extract emotion and confidence
        emotion_match = re.search(r'emotion:\s*(\w+)', response.text, re.IGNORECASE)
        confidence_match = re.search(r'confidence:\s*(\d+\.\d+)', response.text, re.IGNORECASE)
        
        if emotion_match and confidence_match:
            emotion = emotion_match.group(1).lower()
            confidence = float(confidence_match.group(1))
            
            # Ensure emotion is in allowed list
            allowed_emotions = ["stressed", "anxious", "retail_therapy", "motivated", "happy", "neutral"]
            if emotion not in allowed_emotions:
                emotion = "neutral"
                
            return {
                "emotion": emotion,
                "confidence": confidence,
                "all_predictions": {e: 0.1 for e in allowed_emotions}  # Placeholder
            }
        else:
            return fallback_emotion_detection(text)
            
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