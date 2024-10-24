import boto3
import json
from flask import Flask, render_template, request, jsonify
import random
import os

app = Flask(__name__)

# Initialize Amazon Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')  # Replace with your AWS region

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/<page>')
def render_page(page):
    if page + '.html' in os.listdir('templates'):
        return render_template(f'{page}.html')
    return "Page not found", 404

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    # Try calling Bedrock API to generate a dynamic response
    try:
        bot_reply = get_bedrock_response(user_message)
    except Exception as e:
        print(f"Error using Bedrock API: {e}")
        # If Bedrock API fails, fall back to existing response logic
        bot_reply = fallback_response(user_message)

    return jsonify({'reply': bot_reply})

def get_bedrock_response(user_message):
    # Send the user message to Bedrock for processing
    model_id = 'anthropic.claude-v2'  # Replace with your Bedrock model ID

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "prompt": user_message,
            "max_tokens_to_sample": 300,
            "temperature": 0.7,
            "top_p": 0.9,
        }),
        contentType="application/json"
    )

    response_body = json.loads(response['body'].read())
    bot_reply = response_body['completions'][0]['data']['text']
    
    return bot_reply

def fallback_response(user_message):
    """ Simulated response logic when Bedrock API is not available """
    if "team" in user_message.lower():
        bot_reply = "To build a balanced team, consider selecting agents from different roles: Duelist, Sentinel, Initiator, and Controller. What's your preferred playstyle?"
    elif "player" in user_message.lower():
        bot_reply = "I can provide information about various VALORANT players. Which specific player or aspect of their performance are you interested in?"
    elif "map" in user_message.lower():
        maps = ["Ascent", "Bind", "Haven", "Split", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus"]
        bot_reply = f"VALORANT has several maps. A random map suggestion for you is {random.choice(maps)}. Would you like tips for this map?"
    elif "agent" in user_message.lower():
        bot_reply = "VALORANT has a diverse roster of agents. Are you looking for information on a specific agent or role?"
    elif "strategy" in user_message.lower():
        bot_reply = "Strategies in VALORANT can vary based on the map, team composition, and playstyle. Could you specify which aspect of strategy you're interested in?"
    else:
        bot_reply = "I'm here to help with VALORANT-related questions. Feel free to ask about teams, players, maps, agents, or strategies!"

    return bot_reply

if __name__ == '__main__':
    app.run(debug=True)
