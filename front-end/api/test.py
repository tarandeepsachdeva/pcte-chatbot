import json
import os
import sys

def handler(event, context):
    try:
        # Debug information
        debug_info = {
            'message': 'API is working!',
            'python_version': sys.version,
            'environment_variables': {k: v for k, v in os.environ.items() if 'SECRET' not in k and 'KEY' not in k},
            'event': event,
            'context': str(context) if context else 'No context'
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(debug_info, indent=2),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true'
            }
        }
        
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        }
