from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes 

from flask import Flask

def create_app():
    app = Flask(__name__)
    # ... your config and other setup ...

    from app.chat.routes import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')

    return app 
