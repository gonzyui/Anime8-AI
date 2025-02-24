import os
import sqlite3
from flask import Blueprint, request, jsonify, current_app

feedback_bp = Blueprint('feedback', __name__)

def get_db_path():
    return os.path.join(os.getcwd(), 'db', current_app.config.get('DB_NAME', 'media_feedback.db'))

def insert_feedback(username, media_id, rating):
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO feedback (username, anime_id, rating) VALUES (?, ?, ?)',
            (username, media_id, rating)
        )
        conn.commit()

@feedback_bp.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    if not data or not all(k in data for k in ['username', 'anime_id', 'rating']):
        return jsonify({"error": "username, anime_id, rating required"}), 400
    try:
        insert_feedback(data['username'], data['anime_id'], data['rating'])
        return jsonify({"message": "Feedback recorded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500