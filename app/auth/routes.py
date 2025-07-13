from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.auth import bp
from app.models import User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        logger.debug(f"Login attempt for username: '{username}'")
        
        user = User.query.filter_by(username=username).first()
        if user is None:
            logger.debug(f"User not found: '{username}'")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.check_password(password):
            logger.debug(f"Invalid password for user: '{username}'")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        logger.debug(f"Successful login for user: '{username}'")
        login_user(user, remember=remember_me)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        
        logger.debug(f"Registration attempt for username: '{username}', email: '{email}'")
        
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password2:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.debug(f"Successfully registered user: '{username}'")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        username = current_user.username
        logger.debug(f"Logging out user: '{username}'")
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/check')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })
    return jsonify({'authenticated': False}) 