import json
import os
import google.generativeai as genai
import random
import logging
from datetime import datetime
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from pdf_processor import get_pdf_processor
except ImportError:
    from .pdf_processor import get_pdf_processor

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

def get_gemini_response(message, use_pdf_context=True):
    try:
        context = ""
        if use_pdf_context:
            try:
                pdf_processor = get_pdf_processor()
                context = pdf_processor.get_context_for_query(message)
            except Exception as e:
                logger.error(f"Error getting PDF context: {str(e)}")
                context = "[PDF context not available]"
        
        prompt = f"""You are a helpful college assistant chatbot for PCTE (Punjab College of Technical Education).
        Use the context below to answer the user's question. If the context doesn't contain the answer,
        use your general knowledge but indicate that the information might not be specific to PCTE.
        
        Context:
        {context}
        
        User question: {message}
        
        Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip(), "gemini"
    except Exception as e:
        logger.error(f"Error in get_gemini_response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later.", "gemini"

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_error(400, 'No message provided')
            return
            
        try:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            user_message = data.get('message', '').strip()
            if not user_message:
                self._send_error(400, 'Message cannot be empty')
                return
            
            # Check if query is about PCTE (use PDF context)
            is_about_pcte = any(term in user_message.lower() for term in 
                              ['pcte', 'punjab college', 'admission', 'course', 'faculty', 'campus', 'fee', 'scholarship'])
            
            # Try local intents first for simple queries
            local_response, source, confidence = get_local_response(user_message)
            
            if local_response and confidence >= 0.8:
                final_response = local_response
                response_source = source
            else:
                # Use Gemini with PDF context for PCTE-related queries
                final_response, response_source = get_gemini_response(
                    user_message, 
                    use_pdf_context=is_about_pcte
                )
                confidence = 0.7  # Medium confidence for AI-generated responses
            
            response_data = {
                'message': final_response,
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'user_input': user_message,
                'response_source': response_source,
                'local_confidence': confidence if response_source == "local_intents" else None,
                'hybrid_mode': True
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode())
            
        except json.JSONDecodeError:
            self._send_error(400, 'Invalid JSON')
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def _send_error(self, status_code, message):
        self._set_headers(status_code)
        response = {
            'error': message,
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        self.wfile.write(json.dumps(response).encode())

def handler(event, context):
    # This is for Vercel's serverless function compatibility
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'status': 'ok'})
        }
    
    try:
        body = json.loads(event['body'])
        user_message = body.get('message', '').strip()
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Message cannot be empty',
                    'status': 'error',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
            }
        
        # Check if query is about PCTE (use PDF context)
        is_about_pcte = any(term in user_message.lower() for term in 
                          ['pcte', 'punjab college', 'admission', 'course', 'faculty', 'campus', 'fee', 'scholarship'])
        
        # Try local intents first for simple queries
        local_response, source, confidence = get_local_response(user_message)
        
        if local_response and confidence >= 0.8:
            final_response = local_response
            response_source = source
        else:
            # Use Gemini with PDF context for PCTE-related queries
            final_response, response_source = get_gemini_response(
                message, 
                use_pdf_context=is_about_pcte
            )
            confidence = 0.7  # Medium confidence for AI-generated responses
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': final_response,
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'user_input': message,
                'response_source': response_source,
                'local_confidence': confidence if response_source == "local_intents" else None,
                'hybrid_mode': True
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        }
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        }