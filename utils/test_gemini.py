from gemini_service import analyze_emotion
from dotenv import load_dotenv

load_dotenv()

#sample_input = "I just want to buy something nice to feel better about my day."
sample_input = "I am feeling so much elated today"
emotion = analyze_emotion(sample_input)

print(f"Gemini detected emotion: {emotion}")
