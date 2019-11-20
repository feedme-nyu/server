from flask import Flask
from config import Config

def register_app_blueprints(app):
    print("__init__.py -> register_app_blueprints()")
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.feed import bp as feed_bp
    app.register_blueprint(feed_bp, url_prefix="/api")


def create_app(config_class=Config):
    print("__init__.py -> create_app()")
    app = Flask(__name__)
    app.config.from_object(config_class)
    register_app_blueprints(app)
    return app


