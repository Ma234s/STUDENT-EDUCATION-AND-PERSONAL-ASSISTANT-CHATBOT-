from flask import Blueprint, request, jsonify
from app.words_dataset import get_response

bp = Blueprint('chat', __name__)

@bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    user_message = data['message']
    bot_response = get_response(user_message)
    return jsonify({'response': bot_response})

