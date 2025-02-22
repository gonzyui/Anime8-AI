import sqlite3
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_text(anime):
    return " ".join(anime.get('genres', [])) + " " + (anime.get('description') or "")

def get_average_rating(anime_id):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(rating) FROM feedback WHERE anime_id = ?', (anime_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0

def get_recommendations_from_corpus(user_data, corpus_data, n=5, randomize=False, exclude_ids=None):
    if exclude_ids is None: exclude_ids = []
    user_ids, user_texts = [], []
    for anime_list in user_data:
        for entry in anime_list['entries']:
            media = entry['media']
            user_ids.append(media['id'])
            user_texts.append(build_text(media))
    corpus_items, corpus_texts = [], []
    for anime in corpus_data:
        if anime['id'] in user_ids or str(anime['id']) in exclude_ids: continue
        corpus_items.append(anime)
        corpus_texts.append(build_text(anime))
    if not corpus_texts: raise Exception("No anime available in corpus after exclusion.")
    all_texts = user_texts + corpus_texts
    tfidf_matrix = TfidfVectorizer(stop_words='english').fit_transform(all_texts)
    user_vectors = tfidf_matrix[:len(user_texts)]
    corpus_vectors = tfidf_matrix[len(user_texts):]
    user_profile = np.asarray(user_vectors.mean(axis=0)).flatten()
    similarities = cosine_similarity([user_profile], corpus_vectors)[0]
    recs = []
    for idx, anime in enumerate(corpus_items):
        score = similarities[idx] * (1 + get_average_rating(anime['id']) / 10)
        if randomize: score *= (1 + random.uniform(-0.15, 0.15))
        recs.append({'id': anime['id'], 'title': anime['title']['romaji'], 'similarity': score})
    return sorted(recs, key=lambda x: x['similarity'], reverse=True)[:n]

def get_recommendations_from_preferences(preferences_text, corpus_data, n=5, randomize=False, exclude_ids=None):
    if exclude_ids is None: exclude_ids = []
    corpus_items, corpus_texts = [], []
    for anime in corpus_data:
        if str(anime['id']) in exclude_ids: continue
        corpus_items.append(anime)
        corpus_texts.append(build_text(anime))
    if not corpus_texts: raise Exception("No anime available in corpus.")
    all_texts = [preferences_text] + corpus_texts
    tfidf_matrix = TfidfVectorizer(stop_words='english').fit_transform(all_texts)
    user_profile = tfidf_matrix[0]
    corpus_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(user_profile, corpus_vectors)[0]
    recs = []
    for idx, anime in enumerate(corpus_items):
        score = similarities[idx]
        if randomize: score *= (1 + random.uniform(-0.15, 0.15))
        recs.append({'id': anime['id'], 'title': anime['title']['romaji'], 'similarity': score})
    return sorted(recs, key=lambda x: x['similarity'], reverse=True)[:n]