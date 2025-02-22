# Anim8 API Documentation

Anim8 is an anime recommendation system that uses data from Anilist and a content-based recommendation algorithm (TF-IDF and cosine similarity) to suggest anime titles. It incorporates user feedback (like/dislike) to adjust recommendation scores and "auto-train" the system over time.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
  - [GET `/`](#get-)
  - [POST `/get_recommendations`](#post-get_recommendations)
  - [GET `/recommendations`](#get-recommendations)
  - [POST `/feedback`](#post-feedback)
  - [POST `/retrain`](#post-retrain)
- [Notes](#notes)
- [Setup & Installation](#setup--installation)
- [Additional Notes](#additional-notes)

---

## Overview

Anim8 is an anime recommendation API that leverages data from Anilist. It uses a content-based approach (TF-IDF + cosine similarity) to calculate similarity scores between anime. Additionally, user feedback is integrated into the recommendation process so that the system continuously improves over time.

---

## Features

- **Content-Based Recommendations:**  
  Uses TF-IDF vectorization and cosine similarity to generate recommendations based on user-provided preferences or Anilist data.

- **Auto-Training via Feedback:**  
  Incorporates user feedback (likes/dislikes) into the scoring algorithm. The system retrieves average ratings from the feedback database and adjusts recommendation scores accordingly.

- **Exclusion of Duplicates:**  
  New recommendations exclude anime IDs that have already been shown to avoid repetition.

- **Randomization:**  
  A small random factor (±15%) is applied to recommendation scores to provide varied results on subsequent calls.

- **Chatbot Interface:**  
  A user-friendly, chatbot-style web interface displays recommendations as chat bubbles and allows users to submit feedback directly.

- **Multi-Theme Support:**  
  Users can toggle between light and dark themes, which affects the entire UI.

---

## API Endpoints

### GET `/`
- **Description:**  
  Returns the homepage (web interface) of the Anim8 chatbot.
- **Response:**  
  - **Status Code:** 200  
  - **Content:** HTML page with the Anim8 chatbot interface.

---

### POST `/get_recommendations`
- **Description:**  
  Returns anime recommendations in an HTML format based on form submission.
- **Parameters (form data):**
  - `username` (string, optional): The Anilist username.
  - `preferences` (string, optional): A free-text description of user preferences.
  
  *At least one of these must be provided.*
  
- **Response:**  
  - **Status Code:** 200  
  - **Content:** HTML page (`index.html`) displaying the recommendations.

---

### GET `/recommendations`
- **Description:**  
  Returns anime recommendations in JSON format.
- **Parameters (query string):**
  - `username` (string, required): The Anilist username.
- **Response:**  
  - **Status Code:** 200 (or 400 if the parameter is missing)
  - **Content (JSON):**
    ```json
    {
      "recommendations": [
        {
          "id": 12345,
          "title": "Anime Title",
          "similarity": 0.87
        },
        ...
      ]
    }
    ```

---

### POST `/feedback`
- **Description:**  
  Records user feedback for a given anime.
- **Parameters (JSON in request body):**
  - `username` (string, required): The username providing feedback.
  - `anime_id` (number, required): The anime's identifier.
  - `rating` (number, required): The feedback value (e.g., `1` for like, `-1` for dislike).
- **Response:**  
  - **Status Code:** 200 (or 400 if any parameter is missing)
  - **Content (JSON):**
    ```json
    {
      "message": "Feedback recorded"
    }
    ```

---

### POST `/retrain`
- **Description:**  
  Returns new anime recommendations, taking into account user feedback and excluding already displayed anime. This endpoint enables the system to "auto-train" and update recommendations over time.
- **Parameters (JSON in request body):**
  - `username` (string, optional): The Anilist username.
  - `preferences` (string, optional): A free-text description of user preferences.
  
  *At least one must be provided.*
  
  - `prev_ids` (array of strings, optional): A list of anime IDs that have already been displayed (to avoid duplicates).
- **Response:**  
  - **Status Code:** 200 (or 400 if no preference is provided)
  - **Content (JSON):**
    ```json
    {
      "recommendations": [
        {
          "id": 54321,
          "title": "Another Anime",
          "similarity": 0.92
        },
        ...
      ]
    }
    ```

## Notes 
**Notes:**
- **Database:** The SQLite database file is stored in the `/db` folder. Update all database connection strings to use `sqlite3.connect('db/feedback.db')`.
- **Templates:** All HTML files reside in the `/templates` folder.
- **Static Assets:** CSS and JavaScript files are in the `/static` folder.

---

## Setup & Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/gonzyui/Anime8-AI
   cd Anim8
   ```

2. **Install Dependencies: Ensure you have Python installed, then install the required packages:**

    ```bash
    pip install flask requests scikit-learn numpy
    ```

3. **Initialize the Database:** Create the `db`folder and initialize your SQLite database.

4. **Run the Application:** From the project root, start the Flask server:

    ```py
    python app.py
    ```

## Additional Notes

### Auto-Training Enhancements
- The recommendation functions accept an `exclude_ids` parameter to avoid displaying duplicate anime.
- A random factor (±15%) is applied to recommendation scores to vary the results.
- User feedback (likes/dislikes) is averaged and used to adjust scores, enabling the system to improve over time.

### User Interface
- The chatbot-style web interface displays a default message prompting the user to enter their Anilist username or preferences.
- Recommendations are shown as chat bubbles with like/dislike icons for feedback.
- A refresh button allows users to request new recommendations.
- A theme toggle button is provided for switching between light and dark modes, affecting the entire UI.

### API Usage
- For direct API calls, use the `/recommendations` endpoint with the required query parameters.
- The feedback and retraining endpoints accept JSON payloads as detailed above.
