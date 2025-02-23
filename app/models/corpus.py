import requests

def fetch_corpus(media_type="ANIME"):
    query = '''
    query ($mediaType: MediaType) {
      Page(page: 1, perPage: 50) {
        media(type: $mediaType, sort: POPULARITY_DESC) {
          id
          title { romaji }
          genres
          description
        }
      }
    }
    '''
    variables = {"mediaType": media_type}
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()['data']['Page']['media']
    else:
        raise Exception("Error fetching corpus")
