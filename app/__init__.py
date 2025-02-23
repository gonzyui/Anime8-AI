import os
from flask import Flask, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder="../docs", static_url_path="/static")
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
    app.config['AUTO_TRAIN_API_KEY'] = os.getenv('AUTO_TRAIN_API_KEY', 'my_secret_key')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'media_feedback.db')

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "20 per hour"],
    )

    @app.before_request
    def exempt_rate_limit():
        if request.headers.get("X-API-KEY") == app.config.get("AUTO_TRAIN_API_KEY"):
            request.environ["flask_limiter.enabled"] = False


    @app.route('/docs')
    def asyncapi_docs():
        return send_from_directory(os.path.join(app.root_path, '../docs'), "docs.html")

    from app.routes.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    from app.routes.auto_train import auto_train_bp
    app.register_blueprint(auto_train_bp)
    from app.routes.feedback import feedback_bp
    app.register_blueprint(feedback_bp)

    return app