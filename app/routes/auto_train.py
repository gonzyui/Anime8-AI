from flask import Blueprint, request, jsonify, current_app
from app.models.auto_trainer import auto_train
import logging

auto_train_bp = Blueprint('auto_train', __name__)

@auto_train_bp.route('/auto_train', methods=['POST'])
def auto_train_endpoint():
    api_key = request.headers.get('X-API-KEY')
    if api_key != current_app.config.get('AUTO_TRAIN_API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.get_json() or {}
        logging.info("Starting auto_train.")
        result = auto_train(data)
        logging.info("Auto-Training complete.")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error while trying to auto_train: {e}")
        return jsonify({"error": str(e)}), 500