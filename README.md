<div align="center">
  <a href="https://anime8.tech"><img src="https://anime8.tech/logo.png" alt="logo" /></a>
</div>

# [Anime8 API](https://anime8.tech)

Anime8 API is an asynchronous API built with Flask that provides personalized recommendations for anime and manga. It retrieves a user's media list from Anilist and/or uses provided textual preferences to generate recommendations. The API leverages a simple AI model implemented in PyTorch to score and rank media items based on their genre features and user feedback.

## Table of Contents

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Get Recommendations](#get-recommendations)
  - [Submit Feedback](#submit-feedback)
  - [Trigger Auto Training](#trigger-auto-training)
- [Model Explanation](#model-explanation)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)

## Overview

The Anime8 API provides personalized recommendations for anime and manga. It fetches data from the Anilist GraphQL API and uses user-provided preferences or a user's media list to generate recommendations. The recommendation engine is powered by a custom PyTorch model (named **Luminet**) that uses genre information to compute a suitability score for each media item. Feedback from users is stored in a SQLite database and can be used to retrain the model via an auto-training endpoint.

## API Endpoints

### Get Recommendations

**Endpoint:** `GET /recommendations`

**Description:**
Returns a list of recommendations based on either an Anilist username or a preferences text.  
If a username is provided, the API retrieves the user's media list from Anilist and excludes items that have been recommended before (with a small chance for repeats). Otherwise, recommendations are generated solely based on the provided preferences.

**Query Parameters:**
- `username` (string, optional): The Anilist username.
- `preferences` (string, optional): A textual description of the user's media preferences.
- `media_type` (string, optional, default: `ANIME`): The type of media, either `ANIME` or `MANGA`.

**Response Example:**

```json
{
  "recommendations": [
    {
      "id": 12345,
      "title": "Example Anime",
      "score": 8.75,
      "cover_image": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/bx21459-RoPwgrZ32gM3.jpg",
      "description": "What would the world be like if 80 percent of the population manifested extraordinary superpowers called “Quirks” at age four? Heroes and villains would be battling it out everywhere! Becoming a hero would mean learning to use your power, but where would you go to study? U.A. High's Hero Program of course! But what would you do if you were one of the 20 percent who were born Quirkless?<br><br>\n\nMiddle school student Izuku Midoriya wants to be a hero more than anything, but he hasn't got an ounce of power in him. With no chance of ever getting into the prestigious U.A. High School for budding heroes, his life is looking more and more like a dead end. Then an encounter with All Might, the greatest hero of them all gives him a chance to change his destiny…<br><br>\n\n(Source: Viz Media)"
    }
  ]
}
```

### Submit Feedback

**Endpoint:** `POST /feedback`

**Description:**
Records user feedback for a recommended media item. 
The feedback data is used later to retrain the recommendation model.

**Request Body (JSON):**
```json
{
  "username": "example",
  "anime_id": 1273,
  "rating": 8
}
```
**Response Example:**
```json
{
  "message": "Feedback recorded"
}
```

### Trigger Auto Training

**Endpoint:** `POST /auto_train`

**Description:**
Triggers auto-training of the recommendation model using stored user feedback.
This endpoint is protected by an API key (via the `x-api-key` header) and is exempt from rate limits if a valid key is provided.

**Headers:**

- `X-API-KEY` (string, required): API key for authorization

**Response Example:**
```json
{
  "message": "Training completed",
  "loss": 0.0543
}
```

### Get Statistics

**Endpoint:** `GET /stats`

**Description:**
Sends the current program statistics, cpu usage, memory usage, uptime.

**Headers:**

  - `X-API-KEY` (string, required): Api key for authorization

**Response Example:**

```json
{
    "cpu": "23.7 %",
    "memory": {
        "available": "17.09 GB",
        "percentage": "46.6 %",
        "total": "32.00 GB",
        "used": "14.91 GB"
    },
    "uptime": "01:14:02"
}
```

### Model Explanation

The recommendation model, **Luminet**, is implemented in PyTorch as a simple feed-forward neural network:

- **Input:**

  The model receives a concatenated vector consisting of:
  - A user profile vector derived from the user's media list or preferences.
  - A candidate media's genre vector, where each genre is represented as a binary indicator (1 if present, 0 if not).
- **Architecture:**

  - **Hidden Layer:** 16 units with ReLU activation.
  - **Output Layer:** A single linear unit that produces a score.
- **Training**

  The model is trained by using Mean Squared Error (MSE) loss. User feedback ratings (ranging from 0 for poor to 10 for perfect) are used as target values. The training process adjusts the model's parameters so that its predicted scores reflect the quality of the media as perceived by users.

## Setup and Installation

1. **Clone the repository:**
```bash
git clone https://github.com/gonzyui/Anime8-AI
cd Anime8-AI
```
2. **Create a virtual environment and activate it:**
```bash
python -m venv venv
source /venv/bin/active # On windows: venv\Scripts\activate
```
3. **Install dependencies:**
```bash
pip install -r requirements.txt
```
4. **Configure environment variables:**
Create a `.env` file at the root of the project with:
```env
SECRET_KEY=your_secret_key
AUTO_TRAIN_API_KEY=your_api_key
DB_NAME=media_feedback.db
```
5. **Set up the database:**
```bash
python db/setup.py
```

## Usage

- **Start the API:**

  Run the application:
  ```bash
  python run.py
  ```
- **Access API Endpoints:**
  
  Use your preferred API client (e.g., cURL, Postman) to send requests to endpoints such as:
    - `GET https://api.anime8.tech/recommendations`
    - `GET https://api.anime8.tech/stats`
    - `POST https://api.anime8.tech/feedback`
    - `POST https://api.anime8.tech/auto_train`