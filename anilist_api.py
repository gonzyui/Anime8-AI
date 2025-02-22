import requests

def fetch_anime_list(username):
    query = '''
    query ($username: String) {
      MediaListCollection(userName: $username, type: ANIME) {
        lists {
          entries {
            media {
              id
              title { romaji }
              genres
              description
            }
          }
        }
      }
    }
    '''
    variables = {"username": username}
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()['data']['MediaListCollection']['lists']
    else:
        raise Exception("Error fetching data from Anilist.")
