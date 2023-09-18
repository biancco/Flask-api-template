from flask import Flask
import logging, sys, os 
from flask_cors import CORS

def register_blueprints(app):
    from . import templates
    app.register_blueprint(templates.blueprint)
        

def register_logger(app):
    # set logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def create_app(config):
    # Read debug flag
    DEBUG = (os.getenv('DEBUG', 'False') == 'True')

    # Contextual
    static_prefix = '/static' if DEBUG else '/'

    app = Flask(__name__,static_url_path=static_prefix)
    
    #CORS
    CORS(app)
    
    app.config.from_object(config)
    register_logger(app)
    register_blueprints(app)
    
    return app