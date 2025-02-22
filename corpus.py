import requests

def fetch_corpus():
    query = '''
    query {
      Page(page: 1, perPage: 50) {
        media(type: ANIME, sort: POPULARITY_DESC) {
          id
          title { romaji }
          genres
          description
        }
      }
    }
    '''
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={'query': query})
    if response.status_code == 200:
        return response.json()['data']['Page']['media']
    else:
        raise Exception("Error fetching the anime corpus.")