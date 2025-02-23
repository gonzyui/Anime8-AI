import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import sqlite3

GENRES = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Mystery",
          "Slice of Life", "Supernatural", "Sports", "Ecchi", "Mecha"]


def genres_to_vector(genres_list):
    vec = np.zeros(len(GENRES), dtype=np.float32)
    for genre in genres_list:
        if genre in GENRES:
            vec[GENRES.index(genre)] = 1.0
    return vec


class RecommenderNet(nn.Module):
    def __init__(self, input_dim):
        super(RecommenderNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 1)

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))


MODEL_PATH = os.path.join(os.getcwd(), 'model.pth')


def load_model():
    input_dim = 2 * len(GENRES)
    model = RecommenderNet(input_dim)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH))
    return model


def save_model(model):
    torch.save(model.state_dict(), MODEL_PATH)


def get_recommendations_from_corpus(user_data, corpus_data, n=5, randomize=False, exclude_ids=None):
    if exclude_ids is None:
        exclude_ids = []
    user_vectors = []
    for media_list in user_data:
        for entry in media_list.get('entries', []):
            media = entry.get('media', {})
            vec = genres_to_vector(media.get('genres', []))
            user_vectors.append(vec)
    if len(user_vectors) == 0:
        user_profile = np.zeros(len(GENRES), dtype=np.float32)
    else:
        user_profile = np.mean(user_vectors, axis=0)

    candidate_list = []
    candidate_vectors = []
    for media in corpus_data:
        if str(media.get('id')) in exclude_ids and np.random.rand() < 0.8:
            continue
        vec = genres_to_vector(media.get('genres', []))
        candidate_list.append(media)
        candidate_vectors.append(vec)

    if not candidate_vectors:
        raise Exception("No media available in corpus after exclusion")

    inputs = [np.concatenate([user_profile, vec]) for vec in candidate_vectors]
    inputs_tensor = torch.tensor(np.array(inputs), dtype=torch.float32)

    model = load_model()
    model.eval()
    with torch.no_grad():
        scores = model(inputs_tensor).squeeze().numpy()

    recs = []
    for media, score in zip(candidate_list, scores):
        recs.append({'id': media.get('id'), 'title': media.get('title', {}).get('romaji'), 'score': float(score)})

    if randomize:
        for rec in recs:
            rec['score'] *= (1 + np.random.uniform(-0.15, 0.15))

    return sorted(recs, key=lambda x: x['score'], reverse=True)[:n]


def get_recommendations_from_preferences(preferences_text, corpus_data, n=5, randomize=False, exclude_ids=None):
    if exclude_ids is None:
        exclude_ids = []
    preferences_text = preferences_text.lower()
    user_profile = np.zeros(len(GENRES), dtype=np.float32)
    for i, genre in enumerate(GENRES):
        if genre.lower() in preferences_text:
            user_profile[i] = 1.0
    candidate_list = []
    candidate_vectors = []
    for media in corpus_data:
        if str(media.get('id')) in exclude_ids and np.random.rand() < 0.8:
            continue
        vec = genres_to_vector(media.get('genres', []))
        candidate_list.append(media)
        candidate_vectors.append(vec)
    if not candidate_vectors:
        raise Exception("No media available in corpus")
    inputs = [np.concatenate([user_profile, vec]) for vec in candidate_vectors]
    inputs_tensor = torch.tensor(np.array(inputs), dtype=torch.float32)

    model = load_model()
    model.eval()
    with torch.no_grad():
        scores = model(inputs_tensor).squeeze().numpy()

    recs = []
    for media, score in zip(candidate_list, scores):
        recs.append({'id': media.get('id'), 'title': media.get('title', {}).get('romaji'), 'score': float(score)})

    if randomize:
        for rec in recs:
            rec['score'] *= (1 + np.random.uniform(-0.15, 0.15))

    return sorted(recs, key=lambda x: x['score'], reverse=True)[:n]


def train_model(epochs=10, lr=0.01):
    db_path = os.path.join(os.getcwd(), 'db', 'media_feedback.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT username, anime_id, rating FROM feedback')
    data = cursor.fetchall()
    conn.close()
    if not data:
        return {"message": "No feedback data available for training."}

    from app.models.corpus import fetch_corpus
    corpus_data = fetch_corpus("ANIME")
    corpus_dict = {str(media.get('id')): media for media in corpus_data}

    X, y = [], []
    for username, anime_id, rating in data:
        anime = corpus_dict.get(str(anime_id))
        if anime:
            vec = genres_to_vector(anime.get('genres', []))
            user_profile = vec
            features = np.concatenate([user_profile, vec])
            X.append(features)
            y.append(rating)
    if len(X) == 0:
        return {"message": "No valid feedback data for training."}
    X = np.array(X)
    y = np.array(y, dtype=np.float32)
    inputs_tensor = torch.tensor(X, dtype=torch.float32)
    targets_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    model = load_model()
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(inputs_tensor)
        loss = criterion(outputs, targets_tensor)
        loss.backward()
        optimizer.step()
    save_model(model)
    return {"message": "Training completed", "loss": loss.item()}
