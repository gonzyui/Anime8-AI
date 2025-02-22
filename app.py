from flask import Flask, request, jsonify, render_template
from anilist_api import fetch_anime_list
from corpus import fetch_corpus
from recommender import get_recommendations_from_corpus, get_recommendations_from_preferences
import sqlite3

app = Flask(__name__, static_folder='templates/static')

def insert_feedback(username, anime_id, rating):
    conn = sqlite3.connect('db/feedback.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (username, anime_id, rating) VALUES (?, ?, ?)', (username, anime_id, rating))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    username = request.form.get('username')
    preferences = request.form.get('preferences')
    try:
        corpus_data = fetch_corpus()
        if username:
            user_data = fetch_anime_list(username)
            recs = get_recommendations_from_corpus(user_data, corpus_data, n=5)
        elif preferences:
            recs = get_recommendations_from_preferences(preferences, corpus_data, n=5)
        else:
            return render_template('index.html', error="Provide a username or description.")
        return render_template('index.html', recommendations=recs)
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/recommendations', methods=['GET'])
def recommendations_api():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username required"}), 400
    try:
        user_data = fetch_anime_list(username)
        corpus_data = fetch_corpus()
        recs = get_recommendations_from_corpus(user_data, corpus_data, n=5)
        return jsonify({"recommendations": recs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    if not all(k in data for k in ['username', 'anime_id', 'rating']):
        return jsonify({"error": "username, anime_id, and rating required"}), 400
    try:
        insert_feedback(data['username'], data['anime_id'], data['rating'])
        return jsonify({"message": "Feedback recorded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    data = request.get_json(silent=True) or {}
    app.logger.info("Retrain data received: %s", data)
    username = data.get('username')
    preferences = data.get('preferences')
    prev_ids = data.get('prev_ids', [])
    if not username and not preferences:
        return jsonify({"error": "Provide username or preferences"}), 400
    try:
        corpus_data = fetch_corpus()
        if username:
            user_data = fetch_anime_list(username)
            recs = get_recommendations_from_corpus(user_data, corpus_data, n=5, randomize=True, exclude_ids=prev_ids)
        else:
            recs = get_recommendations_from_preferences(preferences, corpus_data, n=5, randomize=True, exclude_ids=prev_ids)
        return jsonify({"recommendations": recs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)