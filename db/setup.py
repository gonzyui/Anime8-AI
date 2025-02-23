import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def create_feedback_table():
    db_name = os.getenv('DB_NAME', 'media_feedback.db')
    db_path = os.path.join(os.getcwd(), 'db', db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        anime_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        anime_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_feedback_table()
