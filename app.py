import os
import random
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
#Add these new ones below your existing imports
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random

# --- Configuration ---
# IMPORTANT: Put your Google API Key here.
# You can get one from Google AI Studio.
API_KEY = 'AIzaSyD421npqFF62PGovdMu4C7T66ScwGp3i5c' # <--- CHANGE THIS
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Error configuring API Key: {e}")
    print("Please make sure you have a valid API_KEY in the script.")

# --- Model Initialization ---
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Content from your first script (Nova) ---
MENTAL_HEALTH_TIPS = [
    "Try a 5-minute breathing exercise: inhale 4s — hold 4s — exhale 6s.",
    "Break tasks into tiny steps. Even small progress reduces overwhelm.",
    "Move your body for 10 minutes. Short activity boosts mood.",
    "Keep a simple sleep routine: consistent bed & wake time helps regulate mood.",
    "Use grounding: name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
    "Write down one thing you’re grateful for today.",
    "Limit doom-scrolling: set a 20-minute cap and replace it with something calming.",
    "Talk to someone you trust, even briefly, about how you’re feeling."
]

# --- Combined & Improved Emergency Information ---
CRISIS_HELPLINES = (
    "It sounds like you are going through a very difficult time. Please know that immediate help is available. "
    "You can connect with someone right now by calling a 24/7 helpline.\n\n"
    "**For India:**\n"
    "- Vandrevala Foundation: 1860-266-2345\n"
    "- iCALL: 022-25521111\n"
    "- Aasra: +91-9820466726\n\n"
    "**International Examples:**\n"
    "- United States: 988 or 911\n"
    "- United Kingdom: 111 or 999\n"
    "- Australia: 000"
)

# --- Flask App Initialization ---
app = Flask(__name__)
CRISIS_KEYWORDS = [
    "Kill myself", "suicide", "want to die", "end of my life",
    "harm myself", "no reason to live", "cant't go on"
]
# --- This is the function that uses the crisis keywords ---
def check_for_crisis(user_message):
    """
    Checks if any crisis keywords are in the user's message.
    Returns True if a keyword is found, otherwise False.
    """
    for keyword in CRISIS_KEYWORDS:
        if keyword in user_message.lower():
            return True
    return False

# --- Initialize the sentiment analyzer ---
sid = SentimentIntensityAnalyzer()

# --- This is the function for sentiment analysis ---
def get_sentiment(user_message):
    """
    Analyzes the sentiment of a message.
    Returns 'positive', 'negative', or 'neutral'.
    """
    scores = sid.polarity_scores(user_message)
    if scores['compound'] >= 0.05:
        return 'positive'
    elif scores['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# --- This is the dictionary of all bot responses ---
RESPONSES = {
    'greeting': ["Hello! How are you feeling today?", "Hi there! What's on your mind?", "Hey! I'm here to listen."],
    'positive_response': ["That's great to hear! I'm happy for you.", "Awesome! Keep that positive energy going.", "That sounds wonderful."],
    'negative_response': ["I'm really sorry to hear that. Please know that it's okay to feel this way.", "That sounds incredibly tough. I'm here to listen if you want to talk about it.", "It takes strength to share that. Thank you for telling me."],
    'neutral_response': ["Thanks for sharing. Can you tell me a bit more?", "I see. How does that make you feel?", "Okay, let's talk through it."],
    'crisis_response': "It sounds like you are going through a very difficult time. It’s important to talk to someone who can help. Please reach out to a professional. You can call the National Suicide Prevention Lifeline at 988 or visit their website. You are not alone.",
    'default': ["I'm not sure I understand. Could you rephrase that?", "Tell me more about that."]
}


def get_bot_response(user_message):
    """
    This is the core hybrid function.
    1. It first checks for high-priority crisis keywords.
    2. Then, it checks for simple, direct commands from the 'Nova' script.
    3. If no simple match is found, it calls the Gemini AI from the 'NOVA🌼' script.
    """
    text = user_message.lower().strip()

    # --- Level 1: Immediate Crisis Check (Highest Priority) ---
    crisis_keywords = ["suicide", "kill myself", "end my life", "hurt myself", "want to die"]
    if any(keyword in text for keyword in crisis_keywords):
        return CRISIS_HELPLINES

    # --- Level 2: Simple Keyword Triggers from 'Nova' for fast responses ---
    if "tip" in text:
        return random.choice(MENTAL_HEALTH_TIPS)
    if text in ["thanks", "thank you"]:
        return "You're welcome! I'm here whenever you need support."
    if text in ["bye", "exit"]:
        return "Goodbye! Take care of yourself."
    if text in ["hello", "hi", "hey"]:
        return "Hello! How can I support you today?"

    # --- Level 3: AI-powered response from 'NOVA🌼' for conversational queries ---
    system_prompt = (
        "You are 'NOVA🌼', a caring and empathetic AI companion for students in India. "
        "Your role is to be a supportive listener, provide gentle encouragement, and offer practical, non-clinical advice for everyday student problems like stress, procrastination, and loneliness. "
        "Your tone should be warm, reassuring, and calm. Keep your responses concise (2-4 sentences). "
        "You can also suggest the user ask for a 'tip' for a simple, actionable idea. "
        "DO NOT provide medical advice, diagnoses, or therapy. "
        "If the user's problem seems serious or they mention self-harm, gently guide them to seek professional help and provide these helpline numbers: " + CRISIS_HELPLINES
    )
    
    full_prompt = system_prompt + "\n\nStudent says: " + user_message

    try:
        # Send the full prompt to the AI model
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return "I'm sorry, I'm having a little trouble connecting right now. Please try again in a moment."


@app.route('/')
def index():
    # This will render a file named 'index.html'
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # --- START of the code to paste INSIDE the function ---
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    bot_reply = ""

    # 1. First, check for a crisis.
    if check_for_crisis(user_message):
        bot_reply = RESPONSES['crisis_response']
    else:
        # 2. If no crisis, analyze sentiment.
        sentiment = get_sentiment(user_message)

        if "hello" in user_message.lower() or "hi" in user_message.lower():
            bot_reply = random.choice(RESPONSES['greeting'])
        elif sentiment == 'positive':
            bot_reply = random.choice(RESPONSES['positive_response'])
        elif sentiment == 'negative':
            bot_reply = random.choice(RESPONSES['negative_response'])
        else: # neutral
            bot_reply = random.choice(RESPONSES['neutral_response'])

    return jsonify({'response': bot_reply})
    # --- END of the code to paste INSIDE the function ---


if __name__ == '__main__':
    # To run this:
    # 1. Make sure your API_KEY is set.
    # 2. Run 'pip install Flask google-generativeai' in your terminal.
    # 3. Save the HTML code below in a 'templates' folder.
    # 4. Run 'python app.py' and open http://127.0.0.1:5000 in your browser.
    app.run(debug=True)