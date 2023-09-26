from dotenv import load_dotenv
import os
import numpy as np 
import re
import base64
from requests import post, get
import json
import string

load_dotenv()


#Client ID & Secret
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    """
    Returns a token that can be used to make requests to Spotify's API.
    The token is valid for 1 hour. 
    """
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64, 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token 

spotify_token = get_token()

def get_auth_header(token):
    """
    Given a Spotify token, this function returns the authorization header 
    that is neccessary to make requests to Spotify's API.
    """
    return {"Authorization": "Bearer " + token}

def get_random_search():
    """
    Returns a random wildcard search. A wildcard can be any character 
    and it is used in a search query to get tracks, artists, and other 
    information that resembles the query. For example, "My %" will 
    return all tracks that begin with "My". 
    """
    letters = list(string.ascii_lowercase)
    rand_letter = np.random.choice(letters)
    searches = [f"{rand_letter}%", f"%{rand_letter}%"]
    rand_search = np.random.choice(searches)
    return rand_search

def random_artist(token):
    """
    Given a Spotify token, this function returns a dictionary containing 
    information about a random artist such as the artist's id and name.
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={get_random_search()}&type=artist&country=US&limit=50"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)['artists']['items']
    rand_artist = np.random.choice(json_result)
    return rand_artist

def get_song_by_artist(token, artist): 
    """
    Given a Spotify token and an artist dictionary, this function returns 
    a list containing the artist's name as the first element, and a random
    top track from the artist as the second element. In other words, the return 
    value is ['artist name', 'track name'].
    """
    artist_id = artist["id"]
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    random_track = np.random.choice(json_result)["name"]
    return [artist['name'], random_track]

def song_rec_handler(token):
    """
    Given a Spotify token, this function returns a random song to recommend. 
    """
    beginning = ["Have a listen to", "Check out the song", "You know which song is amazing?", 
                 "A great song is", "A song I enjoy is"]
    artist = random_artist(token)
    artist_and_song = get_song_by_artist(token, artist)
    resp = np.random.choice(beginning) + " " + artist_and_song[1] + " " + "by " + artist_and_song[0]
    return resp

responses = { r"^no$": ["You are entitled to your opinion.", "That's fair."],
         r"yes": "Why yes?",
         r"[a-z\s]+you[a-z\s]+?": "I don't think that's appropriate",
         r"ok": "Music is incredibly inspiring, don't you agree?",
         r"i have (.+)": ["Please tell me more.",'Go ahead and elaborate further for me.'],
         r"i listen to (.+)": "I also listen to {0}.",
         r"([a-z0-9\s]+) is my favorite song": "How many times do you listen to {0} a day?",
         r".*because (.+)" : 'Have you always felt {0}?', 
         r"i recommend (.+)": 'Why do you recommend {0}?',
         r"([0-9]+)\s*(times)*": "{0} times! I literally cannot believe that.",
         r"([a-z]+) like ([a-z\s]+)": 'Why do you like {1}?',
         r"([a-z0-9\s]+),\s*([a-z0-9\s]+),\s*and\s*([a-z0-9\s]+)": ["That's great! {2}, {1}, and {0} are talented artists.", "{1} is better than {2}, and {0} is better than {1}, don't you think?"], 
         r"([a-z]+) hate (.+)": "Hate is a strong word, don't you think? Give {1} another shot.",
         r"([a-z0-9]+) is (.*)": "How is {0} {1}?",
         r"([a-z]+)\s+and\s+([a-z]+)?": "{1} over {0}!",
         r"i dislike (.+)": "No way! Why?" ,
         r"^[\s]*recommend[\s]*a[\s]*song[\s]*$": "" 
        }

helpers = ['Name three artists that you like?',
           'Give me two genres to compare.',
           'Who do you listen to?', 
           'Would you say life is meaningless without music?',
           'Do you listen to music everday?', 
           'Any song recomendations?',
           'What genres do you dislike?', 
           'Music is a universal charm.',
           'Music truly speaks to the soul.',
           'Tell me more. I am all ears!',
           'Music ever make you think of anyone?',
           'What is your favorite song?',
           'Which song do you hate?', 
           'Ever been to an awesome live concert? Tell me about it.',
           'Do you like to dance to your favorite songs?',
           'Any musical instruments you play or wish you could play?',
           'Have a funny or memorable story related to music? Let me know!',
           'Do you think music has the power to change your mood?',
           
          ]

def HARMONY():
    intro = """
    Hello! My name is HARMONY and I love music. We will be having a conversation about music 
    so feel free to recommend (I recommend ...) any song at any point during our convo. If 
    you would like me to recommend a song simply type in "recommend a song". To end our convo, 
    please enter END.
    """
    print(intro) 
    print("HARMONY: First off, what is your name?") 
    name = input("USER: ") 
    if name.lower() != 'end': 
        print('HARMONY: Nice to meet you ' + name + '!') 
        user_input = input("HARMONY: What kind of music do you like? ").lower() 
        while user_input != 'end': 
            resp_to_user = '' 
            for pattern in responses: 
                extracted_text = re.search(pattern, user_input) 
                if extracted_text: 
                    extracted_words = extracted_text.groups() 
                    if type(responses[pattern]) is list: 
                        resp_to_user= np.random.choice(responses[pattern]).format(*extracted_words)
                    elif pattern == r"^[\s]*recommend[\s]*a[\s]*song[\s]*$":
                        resp_to_user = song_rec_handler(spotify_token)
                    else: 
                        resp_to_user = responses[pattern].format(*extracted_words) 
                    break 
            if resp_to_user:
                print('HARMONY: ' + resp_to_user) 
            else: 
                print("HARMONY: " + np.random.choice(helpers)) 
            user_input = input(name + ': ').lower() 
        print("It was great talking to you " + name + '. We should do it again soon!') 
    else: 
        print("Goodbye.")

#Executes chatbot:
#HARMONY()


