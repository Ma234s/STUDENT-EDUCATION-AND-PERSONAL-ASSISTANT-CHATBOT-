from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.models import Task, StudySession
from app import db
from datetime import datetime

@bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def get_tasks():
    if request.method == 'POST':
        # Extract form data and create a new task
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        if title:
            new_task = Task(
                user_id=current_user.id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority
            )
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'message': 'Task added successfully!'}), 201
        else:
            return jsonify({'error': 'Task title is required'}), 400

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'priority': task.priority
            }
            for task in tasks
        ]
    })

@bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None,
        status='pending',
        priority=data.get('priority', 'medium'),
        user_id=current_user.id
    )
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'status': task.status,
        'priority': task.priority
    }), 201

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    
    db.session.commit()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'status': task.status,
        'priority': task.priority
    })

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(task)
    db.session.commit()
    return '', 204

@bp.route('/study-sessions', methods=['GET'])
@login_required
def get_study_sessions():
    sessions = StudySession.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'study_sessions': [
            {
                'id': session.id,
                'subject': session.subject,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration': session.duration,
                'notes': session.notes
            }
            for session in sessions
        ]
    })

@bp.route('/study-sessions', methods=['POST'])
@login_required
def create_study_session():
    data = request.get_json()
    if not data or 'subject' not in data:
        return jsonify({'error': 'Subject is required'}), 400
    
    session = StudySession(
        subject=data['subject'],
        start_time=datetime.now(),
        notes=data.get('notes', ''),
        user_id=current_user.id
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'id': session.id,
        'subject': session.subject,
        'start_time': session.start_time.isoformat(),
        'end_time': None,
        'duration': None,
        'notes': session.notes
    }), 201

@bp.route('/study-sessions/<int:session_id>/end', methods=['POST'])
@login_required
def end_study_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if session.end_time:
        return jsonify({'error': 'Session already ended'}), 400
    
    session.end_time = datetime.now()
    session.duration = (session.end_time - session.start_time).seconds // 60  # Duration in minutes
    db.session.commit()
    
    return jsonify({
        'id': session.id,
        'subject': session.subject,
        'start_time': session.start_time.isoformat(),
        'end_time': session.end_time.isoformat(),
        'duration': session.duration,
        'notes': session.notes
    }) 