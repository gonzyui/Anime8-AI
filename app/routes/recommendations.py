import os
import sqlite3
from flask import Blueprint, request, jsonify, current_app
from app.models.anilist_api import fetch_media_list
from app.models.corpus import fetch_corpus
from app.models.recommender import get_recommendations_from_corpus, get_recommendations_from_preferences

recommendations_bp = Blueprint('recommendations', __name__)

def get_db_path():
    return os.path.join(os.getcwd(), 'db', current_app.config.get('DB_NAME', 'media_feedback.db'))

def get_previous_recommendations(username):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT anime_id FROM recommendations_log WHERE username = ?', (username,))
    rows = cursor.fetchall()
    conn.close()
    return [str(row[0]) for row in rows]

def log_recommendations(username, recs):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for rec in recs:
        cursor.execute('INSERT INTO recommendations_log (username, anime_id) VALUES (?, ?)', (username, rec['id']))
    conn.commit()
    conn.close()

@recommendations_bp.route('/recommendations', methods=['GET'])
def recommendations_api():
    username = request.args.get('username')
    preferences = request.args.get('preferences')
    media_type = request.args.get('media_type', 'ANIME').upper()
    if not username and not preferences:
        return jsonify({"error": "username or preferences required"}), 400
    try:
        corpus_data = fetch_corpus(media_type)
        if username:
            user_data = fetch_media_list(username, media_type)
            exclude_ids = get_previous_recommendations(username)
            recs = get_recommendations_from_corpus(user_data, corpus_data, n=5, exclude_ids=exclude_ids)
            log_recommendations(username, recs)
        else:
            recs = get_recommendations_from_preferences(preferences, corpus_data, n=5)
        return jsonify({"recommendations": recs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
