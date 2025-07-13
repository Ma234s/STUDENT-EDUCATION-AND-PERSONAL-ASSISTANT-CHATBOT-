from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from app.models import Conversation, Message, Task
from app.nlp.processor import NLPProcessor
from app import db
from datetime import datetime
import json
import spacy
from app.words_dataset import get_response

bp = Blueprint('chat', __name__)
nlp_processor = NLPProcessor()
nlp = spacy.load('en_core_web_sm')

@bp.route('/message', methods=['POST'])
@login_required
def process_message():
    """Handle incoming chat messages"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create conversation
    conversation_id = data.get('conversation_id')
    if conversation_id:
        conversation = Conversation.query.get_or_404(conversation_id)
    else:
        conversation = Conversation(
            user=current_user,
            context=data.get('context', 'general')
        )
        db.session.add(conversation)
        db.session.commit()
    
    # Process the message
    user_message = data['message']
    nlp_result = nlp_processor.process_text(user_message, conversation.context)
    
    # Store user message
    message = Message(
        conversation=conversation,
        content=user_message,
        role='user',
        sentiment=nlp_result['sentiment']['compound']
    )
    db.session.add(message)
    
    # Generate and store assistant response
    response = generate_response(nlp_result, conversation)
    assistant_message = Message(
        conversation=conversation,
        content=response['message'],
        role='assistant'
    )
    db.session.add(assistant_message)
    
    # Handle any actions (e.g., task creation)
    if response.get('actions'):
        handle_actions(response['actions'], conversation)
    
    db.session.commit()
    
    return jsonify({
        'conversation_id': conversation.id,
        'response': response['message'],
        'actions': response.get('actions', []),
        'context': conversation.context
    })

def generate_response(nlp_result, conversation):
    """Generate appropriate response based on NLP analysis"""
    intent = nlp_result['intent']
    response_type = nlp_processor.get_response_type(
        intent,
        nlp_result['sentiment']
    )
    
    response = {
        'message': '',
        'actions': []
    }
    
    if response_type == 'emotional_support':
        response['message'] = generate_emotional_support_response(nlp_result)
    
    elif response_type == 'academic_explanation':
        response['message'] = generate_academic_response(nlp_result)
    
    elif response_type == 'task_creation':
        task_info = extract_task_info(nlp_result)
        response['message'] = f"I'll help you create a task for that. "
        response['actions'].append({
            'type': 'create_task',
            'data': task_info
        })
    
    else:
        response['message'] = generate_general_response(nlp_result)
    
    return response

def generate_emotional_support_response(nlp_result):
    """Generate empathetic response for emotional support"""
    sentiment = nlp_result['sentiment']
    if sentiment['negative'] > 0.5:
        return ("I understand you're feeling stressed. Remember, it's normal to feel "
                "this way, and we'll work through it together. Would you like to "
                "break this down into smaller, manageable steps?")
    elif sentiment['neutral'] > 0.5:
        return ("I'm here to help you stay on track. Let's focus on what we can "
                "do to make progress. Would you like to create a study plan?")
    else:
        return ("That's great to hear! Let's maintain this positive momentum. "
                "What would you like to focus on next?")

def generate_academic_response(nlp_result):
    """Generate response for academic queries"""
    entities = nlp_result['entities']
    subjects = entities.get('subjects', [])
    
    if subjects:
        return (f"I'll help you understand {subjects[0]}. Let's break this down "
                "into key concepts and create a study plan. What specific aspect "
                "would you like to focus on first?")
    else:
        return ("I'll help you with that. Could you specify the subject or topic "
                "you'd like to focus on?")

def extract_task_info(nlp_result):
    """Extract task information from NLP result"""
    entities = nlp_result['entities']
    dates = entities.get('dates', [])
    
    task_info = {
        'title': ' '.join(nlp_result['noun_phrases'][:1]) if nlp_result['noun_phrases'] else 'New Task',
        'due_date': dates[0]['text'] if dates else None,
        'priority': 3,  # Default priority
        'category': 'academic' if nlp_result['intent']['type'] == 'academic_query' else 'personal'
    }
    
    return task_info

def handle_actions(actions, conversation):
    """Handle any actions generated from the response"""
    for action in actions:
        if action['type'] == 'create_task':
            task = Task(
                user=conversation.user,
                title=action['data']['title'],
                due_date=action['data'].get('due_date'),
                priority=action['data']['priority'],
                category=action['data']['category'],
                status='pending'
            )
            db.session.add(task)

def generate_general_response(nlp_result):
    """Generate general response when no specific intent is matched"""
    return ("I'm here to help with your studies and productivity. Would you like "
            "help with studying, task management, or something else?")

@bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    user_message = data['message']
    bot_response = get_response(user_message)
    return jsonify({'response': bot_response})

@bp.route('/history/<int:conversation_id>')
@login_required
def get_history(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if conversation.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    return jsonify({
        'conversation_id': conversation_id,
        'messages': [
            {
                'content': msg.content,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    })

@bp.route('/conversations')
@login_required
def get_conversations():
    conversations = Conversation.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'conversations': [
            {
                'id': conv.id,
                'created_at': conv.created_at.isoformat(),
                'last_message': conv.messages[-1].content if conv.messages else None
            }
            for conv in conversations
        ]
    }) 