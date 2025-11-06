from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# Simple intents for serverless (reduced set)
COLLEGE_INTENTS = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "namaste"],
        "responses": [
            "Hello! Welcome to PCTE Helpdesk. How can I assist you today?",
            "Hi there! I'm here to help with your PCTE queries. What do you need?",
            "Hey! How can I help you with college information?"
        ]
    },
    "thanks": {
        "keywords": ["thanks", "thank you", "appreciate"],
        "responses": [
            "You're welcome!",
            "Happy to help!",
            "Anytime! Feel free to ask more questions."
        ]
    },
    "goodbye": {
        "keywords": ["bye", "goodbye", "see you"],
        "responses": [
            "Goodbye! Feel free to reach out if you have more questions.",
            "Have a great day! Don't hesitate to ask if you need help again.",
            "Take care! I'm here whenever you need assistance."
        ]
    }
}

def get_local_response(message):
    message_lower = message.lower()
    
    for intent, data in COLLEGE_INTENTS.items():
        if any(keyword in message_lower for keyword in data["keywords"]):
            return random.choice(data["responses"]), "local_intents", 0.9
    
    return None, None, 0.0

def should_use_gemini(message):
    gemini_keywords = [
        'what is', 'explain', 'tell me about', 'how does', 'define',
        'artificial intelligence', 'machine learning', 'quantum', 'physics',
        'chemistry', 'biology', 'history', 'technology', 'programming'
    ]
    return any(keyword in message.lower() for keyword in gemini_keywords)

def get_gemini_response(message):
    try:
        prompt = f"""You are a helpful college assistant chatbot for PCTE (Punjab College of Technical Education). 
        Respond to the following question in a friendly and informative way. 
        Keep your response concise and helpful.
        
        User question: {message}
        
        Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip(), "gemini"
    except Exception as e:
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later.", "gemini"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message field',
                'status': 'error'
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'status': 'error'
            }), 400
        
        # Get current timestamp in ISO format
        current_timestamp = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        # Check if query should go directly to Gemini
        if should_use_gemini(user_message):
            final_response, response_source = get_gemini_response(user_message)
            confidence = 0.0
        else:
            # Try local intents first
            local_response, source, confidence = get_local_response(user_message)
            
            if local_response and confidence >= 0.8:
                final_response = local_response
                response_source = "local_intents"
            else:
                final_response, response_source = get_gemini_response(user_message)
        
        return jsonify({
            'message': final_response,
            'status': 'success',
            'timestamp': current_timestamp,  # Include server timestamp in the response
            'user_input': user_message,
            'response_source': response_source,
            'local_confidence': confidence if response_source == "local_intents" else None,
            'hybrid_mode': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'PCTE Chatbot API'
    })

# For Vercel
app = app