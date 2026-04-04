from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Store chat history
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    # Simple AI response (replace with your AI backend)
    ai_response = f"Echo: {user_message}"
    
    chat_history.append({'user': user_message, 'ai': ai_response})
    
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)
