import os
import google.generativeai as genai
import random
from google.generativeai import GenerativeModel

# Setup Gemini API
def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# Generate basic content (used internally)
def generate_content(prompt):
    try:
        if not setup_gemini():
            return get_fallback_response(prompt)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return get_fallback_response(prompt)

# Chat-like interaction with memory
chat_model = None
chat_session = None

def gemini_chat(user_input):
    global chat_model, chat_session
    try:
        if not setup_gemini():
            return get_fallback_response(user_input)

        if chat_model is None:
            chat_model = genai.GenerativeModel("gemini-1.5-pro")
            chat_session = chat_model.start_chat(history=[])

        response = chat_session.send_message(user_input)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini chat error: {e}")
        return get_fallback_response(user_input)

# Generate financial advice
def generate_advice(emotional_state, financial_context):
    emotion = emotional_state["emotion"]
    confidence = emotional_state["confidence"]
    spending_trigger = financial_context.get("spending_trigger", "unknown")
    recent_spending = financial_context.get("recent_emotional_spending", 0)
    monthly_goal = financial_context.get("monthly_savings_goal", 0)
    primary_goal = financial_context.get("primary_goal", "better financial wellbeing")

    prompt = f"""
    You are Wellnest, an empathetic AI financial wellness coach.
    USER EMOTIONAL STATE:
    - Current feeling: {emotion}
    - Confidence: {confidence}
    - Typical spending trigger: {spending_trigger}
    FINANCIAL CONTEXT:
    - Recent emotional spending: ${recent_spending}
    - Monthly goal: ${monthly_goal}
    - Primary financial goal: {primary_goal}

    Generate a supportive, personalized response that:
    1. Acknowledges their emotional state with empathy
    2. Offers a specific no-spend alternative activity
    3. Provides a gentle reminder of their financial goals
    4. Keeps a warm, supportive tone throughout
    """

    return generate_content(prompt)

# Generate affirmation
def generate_affirmation(emotion, financial_goal=None):
    if not financial_goal:
        financial_goal = "improving financial wellbeing"

    prompt = f"""
    Create a short, powerful financial affirmation for someone who:
    - Is feeling: {emotion}
    - Has a financial goal of: {financial_goal}

    The affirmation should:
    - Be positive and empowering
    - Directly address their emotional state
    - Connect to their financial goals
    - Be 1-2 sentences maximum
    - Use simple, impactful language

    Return only the affirmation text with no additional commentary.
    """

    return generate_content(prompt).strip().strip('"')

# Handle fallback
def get_fallback_response(prompt):
    if "affirmation" in prompt.lower():
        return random.choice([
            "My financial choices today create my tomorrow. I have the power to make decisions aligned with my goals.",
            "I am in control of my spending and my future. Every mindful choice takes me closer to my dreams.",
            "I choose peace over impulse, and wisdom over instant gratification.",
            "Today's small decisions create tomorrow's financial freedom.",
            "I am stronger than momentary desires. My financial goals matter more than temporary pleasures."
        ])
    elif "emotional state" in prompt.lower():
        return random.choice([
            "It seems like you're feeling overwhelmed. Try journaling or going for a walk before making any big decisions.",
            "Feeling anxious is normal. Take a deep breath and revisit your goals — one step at a time.",
            "You're doing your best. Pause, prioritize, and trust your journey.",
            "Financial stress is tough, but every mindful choice counts toward your future."
        ])
    else:
        return random.choice([
            "Taking small steps each day leads to big financial changes over time.",
            "Remember: progress, not perfection.",
            "You are doing better than you think."
        ])

# Analyze emotion
def analyze_emotion(user_text):
    setup_gemini()
    prompt = f"""
    You are an AI emotion classifier specialized in financial wellbeing.

    Identify the user's emotional state from the following categories:
    - stressed
    - anxious
    - sad
    - motivated
    - happy
    - retail_therapy
    - neutral

    Message:
    "{user_text}"

    Respond only with the emotion from the list above.
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    emotion = response.text.strip().lower()
    confidence_map = {
        "stressed": 0.9,
        "anxious": 0.85,
        "sad": 0.8,
        "motivated": 0.95,
        "happy": 0.95,
        "retail_therapy": 0.88,
        "neutral": 0.75
    }
    confidence = confidence_map.get(emotion, 0.7)

    return {"emotion": emotion, "confidence": confidence}
