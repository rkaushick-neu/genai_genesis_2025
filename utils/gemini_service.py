import os
import google.generativeai as genai
import random

def setup_gemini():
    """Setup Gemini API with API key"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def generate_content(prompt):
    """Generate content using Gemini API"""
    try:
        # Try to set up Gemini
        gemini_available = setup_gemini()
        
        if not gemini_available:
            return get_fallback_response(prompt)
        
        # Generate content
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return get_fallback_response(prompt)

def generate_advice(emotional_state, financial_context):
    """Generate personalized financial advice based on emotional state"""
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
  
    Your response should be 3-5 sentences, conversational, and directly address the user.
    """
    
    response = generate_content(prompt)
    return response

def generate_affirmation(emotion, financial_goal=None):
    """Generate a financial affirmation tailored to the emotional state"""
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
    
    response = generate_content(prompt)
    return response.strip().strip('"')

def get_fallback_response(prompt):
    """Provide fallback responses when API is unavailable"""
    if "affirmation" in prompt.lower():
        affirmations = [
            "My financial choices today create my tomorrow. I have the power to make decisions aligned with my goals.",
            "I am in control of my spending and my future. Every mindful choice takes me closer to my dreams.",
            "I choose peace over impulse, and wisdom over instant gratification.",
            "Today's small decisions create tomorrow's financial freedom.",
            "I am stronger than momentary desires. My financial goals matter more than temporary pleasures."
        ]
        return random.choice(affirmations)
    
    elif "emotional state" in prompt.lower():
        advice = [
            "I understand you might be feeling stressed about your finances. Consider taking a moment to reflect on your priorities before making any decisions.",
            "It seems like you're experiencing some financial anxiety. Remember that small steps lead to big progress, and each mindful decision helps build a more secure future.",
            "I notice you're feeling uncertain about your financial situation. Consider creating a simple list of your priorities to help focus your attention on what truly matters.",
            "When financial pressure builds up, it helps to break things down into small, manageable steps. Focus on just one small action you can take today."
        ]
        return random.choice(advice)
    
    else:
        general = [
            "Taking small steps each day leads to big financial changes over time. Focus on progress, not perfection.",
            "Remember that financial wellness is a journey, not a destination. Each mindful choice is a step forward.",
            "Small, consistent habits often have a bigger impact than grand gestures. What small habit can you build today?"
        ]
        return random.choice(general)