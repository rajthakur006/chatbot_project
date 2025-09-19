import os
import json
import uuid # Used to create unique IDs for each chat session
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template

# --- Configuration ---
API_KEY = 'AIzaSyCf4tfyj5PTcTUY9FFrFhsVdtLybDDYWk0' 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- History Management ---
HISTORY_DIR = "chat_histories"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# (Your knowledge base - no changes needed)
LOCAL_KNOWLEDGE_BASE = """
You have specialized knowledge... (and so on)
"""

app = Flask(__name__)

def get_chat_history_path(session_id):
    return os.path.join(HISTORY_DIR, f"{session_id}.json")

def get_bot_response(user_message, session_id):
    history_path = get_chat_history_path(session_id)
    
    # Load history for this specific session
    try:
        with open(history_path, 'r') as f:
            session_history = json.load(f)
    except FileNotFoundError:
        session_history = []

    # (Your crisis keywords logic - no changes)
    crisis_keywords = ["kill myself", "want to die", "hurt myself", "suicide"]
    if any(keyword in user_message.lower() for keyword in crisis_keywords):
        return "It sounds like you are going through a very difficult time..."

    # (Your system prompt - no changes)
    system_prompt = (
        "You are 'Saathi', an AI companion... (and so on)"
    )
    
    # Format the history for the AI prompt
    prompt_history = [f"{msg['sender']}: {msg['text']}" for msg in session_history[-6:]]
    history_for_prompt = "\n".join(prompt_history)
    
    full_prompt = system_prompt + "\n\n--- Conversation History ---\n" + history_for_prompt + "\n\n--- Current Question ---\nStudent says: " + user_message

    try:
        response = model.generate_content(full_prompt)
        ai_response = response.text
        
        # Add to this session's history
        session_history.append({"sender": "user", "text": user_message})
        session_history.append({"sender": "bot", "text": ai_response})
        
        # Save this session's history to its own file
        with open(history_path, 'w') as f:
            json.dump(session_history, f, indent=4)
            
        return ai_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return "I'm sorry, I'm having a little trouble connecting right now."

@app.route('/')
def index():
    return render_template('index.html')

# --- NEW ROUTES FOR SESSION MANAGEMENT ---
@app.route('/start_chat', methods=['POST'])
def start_chat():
    session_id = str(uuid.uuid4()) # Create a new unique ID
    return jsonify({'session_id': session_id})

@app.route('/load_chat/<session_id>', methods=['GET'])
def load_chat(session_id):
    history_path = get_chat_history_path(session_id)
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
        return jsonify(history)
    except FileNotFoundError:
        return jsonify([]) # Return empty if it's a new chat

# --- UPDATED CHAT ROUTE ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "Session ID is missing"}), 400
    
    bot_response = get_bot_response(user_message, session_id)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)