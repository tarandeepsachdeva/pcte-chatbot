from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime, timedelta
import json
import torch
import random
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Timezone support (uses IANA zone names like "Asia/Kolkata")
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None  # Fallback handled at runtime

app = Flask(__name__)
# Enable CORS for all routes to allow frontend access
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

# Configure Gemini API
# You'll need to set your API key as an environment variable
# export GOOGLE_API_KEY="your_api_key_here"
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize the Gemini model
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# Load intents and trained model
with open('intents.json', 'r') as f:
    intents = json.load(f)

# Load the trained model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
FILE = "data.pth"

try:
    data = torch.load(FILE, weights_only=True)
except TypeError:
    data = torch.load(FILE)

input_size = data["input_size"]
output_size = data["output_size"]
hidden_size = data["hidden_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

# Initialize the neural network
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Helper to get "now" in the desired timezone
# Priority: request-provided tz -> TIMEZONE env -> Asia/Kolkata -> system local
# Returns a timezone-aware datetime when possible

def get_now(tz_name=None):
    tz = None
    # Request-provided or explicit timezone
    if tz_name and ZoneInfo:
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = None

    # Environment variable fallback
    if tz is None:
        env_tz = os.getenv('TIMEZONE')
        if env_tz and ZoneInfo:
            try:
                tz = ZoneInfo(env_tz)
            except Exception:
                tz = None

    # Preferred default for this project (PCTE in India)
    if tz is None and ZoneInfo:
        try:
            tz = ZoneInfo('Asia/Kolkata')
        except Exception:
            tz = None

    if tz is not None:
        return datetime.now(tz)

    # Last-resort fallbacks
    try:
        return datetime.now().astimezone()
    except Exception:
        return datetime.now()

def should_use_gemini(user_message):
    """
    Check if the query should be routed directly to Gemini AI
    """
    gemini_keywords = [
        'what is', 'explain', 'tell me about', 'how does', 'define',
        'artificial intelligence', 'machine learning', 'quantum', 'physics',
        'chemistry', 'biology', 'history', 'cooking', 'recipe', 'weather',
        'news', 'sports', 'entertainment', 'technology', 'programming',
        'philosophy', 'psychology', 'economics', 'politics', 'science',
        'travel', 'health', 'fitness', 'music', 'movies', 'books'
    ]
    
    user_lower = user_message.lower()
    return any(keyword in user_lower for keyword in gemini_keywords)

def get_local_response(user_message, tz_name=None):
    """
    Get response from local trained model and intents
    """
    try:
        # Tokenize and process the input
        tokens = tokenize(user_message)
        X = bag_of_words(tokens, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        with torch.no_grad():
            output = model(X)
            probs = torch.softmax(output, dim=1)[0]
            top_prob, top_idx = torch.max(probs, dim=0)

        tag = tags[top_idx.item()]
        confidence = top_prob.item()

        # Check confidence threshold - increased to 0.8 for better accuracy
        confidence_threshold = 0.8
        if confidence >= confidence_threshold:
            # Handle dynamic responses for date/time/day
            now = get_now(tz_name)
            if tag == 'current_time':
                return f"The current time is {now.strftime('%I:%M %p')}", confidence, "local"
            if tag == 'current_date':
                return f"Today's date is {now.strftime('%d %B %Y')}", confidence, "local"
            if tag == 'day_today':
                return f"Today is {now.strftime('%A')}", confidence, "local"
            if tag == 'day_tomorrow':
                return f"Tomorrow is {(now + timedelta(days=1)).strftime('%A')}", confidence, "local"

            # Find matching intent
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    return random.choice(intent['responses']), confidence, "local"
        
        return None, confidence, "local"
    except Exception as e:
        return None, 0.0, "local"

def get_gemini_response(user_message):
    """
    Get response from Gemini API
    """
    try:
        prompt = f"""You are a helpful college assistant chatbot for PCTE (Punjab College of Technical Education). 
        Respond to the following question in a friendly and informative way. 
        Keep your response concise and helpful. If you don't know something specific about the college, say so politely.
        
        User question: {user_message}
        
        Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip(), "gemini"
    except Exception as e:
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later.", "gemini"

@app.route('/chat', methods=['POST'])
def chat():
    """
    API endpoint with hybrid approach: local intents first, then Gemini fallback
    """
    try:
        # Get the input text from the request
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
        
        # Determine preferred timezone from client or environment
        tz_name = None
        if isinstance(data, dict):
            tz_val = data.get('timezone')
            if isinstance(tz_val, str):
                tz_name = tz_val
        if not tz_name:
            tz_name = request.headers.get('X-Timezone')
        
        # Step 1: Check if query should go directly to Gemini
        if should_use_gemini(user_message):
            final_response, response_source = get_gemini_response(user_message)
            confidence = 0.0  # No local confidence for Gemini responses
            source = "gemini"
        else:
            # Step 2: Try local model first
            local_response, confidence, source = get_local_response(user_message, tz_name)
            
            if local_response and confidence >= 0.8:
                # Use local response if confidence is high enough
                final_response = local_response
                response_source = "local_intents"
            else:
                # Step 3: Fall back to Gemini API
                final_response, response_source = get_gemini_response(user_message)
                source = "gemini"
        
        # Return the response with metadata
        return jsonify({
            'message': final_response,
            'status': 'success',
            'timestamp': get_now(tz_name).isoformat(),
            'user_input': user_message,
            'response_source': response_source,
            'local_confidence': confidence if source == "local" else None,
            'hybrid_mode': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
'timestamp': get_now().isoformat(),
        'service': 'Chatbot API with Gemini'
    })

@app.route('/PCTE-BROCHURE-2023-1.pdf', methods=['GET'])
def serve_brochure():
    """
    Serve the college brochure PDF file
    """
    try:
        return send_file('PCTE-BROCHURE-2023-1.pdf', as_attachment=False)
    except FileNotFoundError:
        return jsonify({'error': 'Brochure not found'}), 404

@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with API information
    """
    return jsonify({
        'message': 'Chatbot API with Gemini Integration',
        'endpoints': {
            'POST /chat': 'Send a message and get AI response',
            'GET /health': 'Check API health status',
            'GET /PCTE-BROCHURE-2023-1.pdf': 'Download college brochure'
        },
        'usage': {
            'method': 'POST',
            'url': '/chat',
            'body': {'message': 'Your question here'}
        }
    })

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("Warning: GOOGLE_API_KEY environment variable not set!")
        print("Please set your Google API key: export GOOGLE_API_KEY='your_key_here'")
    
    print("Starting Chatbot API server...")
    print("API Documentation:")
    print("- POST /chat: Send message and get AI response")
    print("- GET /health: Health check")
    print("- GET /: API information")
    
    # Use PORT environment variable for deployment platforms
    port = int(os.getenv('PORT', 8000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
