from http.server import BaseHTTPRequestHandler
import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'API is working!'}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    }
