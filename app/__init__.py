from flask import Flask, request, send_from_directory, g, jsonify
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from dotenv import load_dotenv
from flask_cors import CORS
from redis import Redis
import logging
import time
import os

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__, static_folder="../docs", static_url_path="/static")
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
    app.config['AUTO_TRAIN_API_KEY'] = os.getenv('AUTO_TRAIN_API_KEY', 'my_secret_key')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'media_feedback.db')
    app.config['CORS_HEADERS'] = 'Content-Type'


    redis_client = Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0)

    def rate_limit_key():
        api_key = request.headers.get('X-API-KEY')
        if api_key and api_key == app.config['AUTO_TRAIN_API_KEY']:
            return "unlimited"
        return get_remote_address()

    limiter = Limiter(
        app=app,
        key_func=rate_limit_key,
        storage_uri="redis://" + os.getenv("REDIS_HOST") + ":6379",
        default_limits=["200 per day", "20 per hour"],
    )
    limiter.limit("200 per day")(lambda: None)
    logging.info("Limiter configured with Redis")

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        start = getattr(g, 'start_time', None)
        if start is not None:
            process_time = time.time() - start
            response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    @app.errorhandler(404)
    def page_not_found(error):
        response = {
            "error": "Not found",
            "message": "Resource not found.",
        }
        return jsonify(response), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        response = {
            "error": "Internal server error",
            "message": "Internal server error.",
        }
        return jsonify(response), 500

    @app.errorhandler(401)
    def unauthorized(error):
        response = {
            "error": "Unauthorized",
            "message": "Unauthorized.",
        }
        return jsonify(response), 401

    @app.errorhandler(429)
    def forbidden(error):
        response = {
            "error": "Forbidden",
            "message": "You are being rate-limited.",
        }
        return jsonify(response), 403

    from app.routes.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    from app.routes.auto_train import auto_train_bp
    app.register_blueprint(auto_train_bp)
    from app.routes.feedback import feedback_bp
    app.register_blueprint(feedback_bp)
    from app.routes.stats import stats_bp
    app.register_blueprint(stats_bp)

    logging.info("Endpoints and IA initialized.")
    return app
