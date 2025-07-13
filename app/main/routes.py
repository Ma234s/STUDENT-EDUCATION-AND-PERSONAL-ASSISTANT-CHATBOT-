from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Task, StudySession, Schedule
from datetime import datetime, time
from app.words_dataset import get_response

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    return render_template('index.html')

@bp.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@bp.route('/chat/message', methods=['POST'])
@login_required
def chat_message():
    message = request.json.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get response from the chatbot
    response = get_response(message)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        priority = request.form.get('priority')

        # Convert due_date string to a Python date object
        due_date = None
        if due_date_str:
            try:
                # Adjust the format string to match your input (e.g., '20/7/2025')
                due_date = datetime.strptime(due_date_str.strip(), '%d/%m/%Y').date()
            except ValueError:
                flash('Due date format should be DD/MM/YYYY.', 'error')
                return redirect(url_for('main.tasks'))

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
            flash('Task added successfully!', 'success')
        else:
            flash('Task title is required.', 'error')
        return redirect(url_for('main.tasks'))

    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=user_tasks)

@bp.route('/study-sessions', methods=['GET'])
@login_required
def study_sessions():
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).all()
    return render_template('study_sessions.html', sessions=sessions)

@bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/lms-integration')
@login_required
def lms_integration():
    return render_template('lms_integration.html')

@bp.route('/schedule', methods=['GET'])
@login_required
def schedule():
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    subject_colors = {
        'IT01': '#FFE0E0',  # Light red
        'IT02': '#E0FFE0',  # Light green
        'IT03': '#E0E0FF',  # Light blue
        'IT04': '#FFE0FF',  # Light purple
        'IT05': '#FFFFE0',  # Light yellow
        'IT06': '#E0FFFF'   # Light cyan
    }
    return render_template('schedule.html', schedules=schedules, subject_colors=subject_colors)

@bp.route('/add_schedule', methods=['POST'])
@login_required
def add_schedule():
    try:
        # Parse form data
        subject_code = request.form.get('subject_code')
        day_of_week = request.form.get('day_of_week')
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        topic = request.form.get('topic')
        location = request.form.get('location')
        is_recurring = 'is_recurring' in request.form

        # Create new schedule
        schedule = Schedule(
            user_id=current_user.id,
            subject_code=subject_code,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            topic=topic,
            location=location,
            is_recurring=is_recurring
        )

        # Add to database
        db.session.add(schedule)
        db.session.commit()

        flash('Schedule added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding schedule: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('main.schedule'))

@bp.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check if the schedule belongs to the current user
    if schedule.user_id != current_user.id:
        flash('You do not have permission to delete this schedule.', 'error')
        return redirect(url_for('main.schedule'))

    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting schedule: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('main.schedule'))

@bp.route('/start-session', methods=['POST'])
@login_required
def start_session():
    try:
        subject = request.form.get('subject')
        duration = int(request.form.get('duration', 25))
        goals = request.form.get('goals')
        
        session = StudySession(
            user_id=current_user.id,
            subject=subject,
            duration=duration,
            goals=goals,
            start_time=datetime.utcnow(),
            status='active'
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash('Study session started successfully!', 'success')
    except Exception as e:
        flash(f'Error starting study session: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.study_sessions'))

@bp.route('/end-session/<int:session_id>', methods=['POST'])
@login_required
def end_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    if session.user_id != current_user.id:
        flash('You do not have permission to end this session.', 'error')
        return redirect(url_for('main.study_sessions'))
    
    try:
        session.end_time = datetime.utcnow()
        session.status = 'completed'
        db.session.commit()
        flash('Study session ended successfully!', 'success')
    except Exception as e:
        flash(f'Error ending study session: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.study_sessions'))

@bp.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task.', 'error')
        return redirect(url_for('main.tasks'))
    # If marking as complete, delete the task
    if task.status != 'completed':
        task.status = 'completed'
        db.session.commit()
        flash('Task marked as completed and removed.', 'success')
        db.session.delete(task)
        db.session.commit()
    else:
        flash('Task was already completed and has been removed.', 'info')
    return redirect(url_for('main.tasks'))

@bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'error')
        return redirect(url_for('main.tasks'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.tasks')) 