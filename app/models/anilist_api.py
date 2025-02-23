import requests

def fetch_media_list(username, media_type="ANIME"):
    query = '''
    query ($username: String, $mediaType: MediaType) {
      MediaListCollection(userName: $username, type: $mediaType) {
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
    variables = {"username": username, "mediaType": media_type}
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()['data']['MediaListCollection']['lists']
    else:
        raise Exception("Error fetching media list")
