from anilist_api import fetch_anime_list
from corpus import fetch_corpus
from recommender import get_recommendations_from_corpus

def main():
    username = input("Enter your Anilist username: ")
    try:
        user_data = fetch_anime_list(username)
        corpus_data = fetch_corpus()
        recs = get_recommendations_from_corpus(user_data, corpus_data, n=5)
        print("\nYour anime recommendations (not in your list):")
        for rec in recs:
            print(f" - {rec['title']} (score: {rec['similarity']:.2f})")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()