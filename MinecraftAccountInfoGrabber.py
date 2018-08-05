import requests
from json import JSONDecodeError
from BotErrors import UsernameLookupFailed


uuid_lookup_url = 'https://api.mojang.com/users/profiles/minecraft/{}'
username_lookup_url = 'https://api.mojang.com/user/profiles/{}/names'


def grab_json(url):
    try:
        json = requests.get(url).json()
        if 'error' in json:
            raise UsernameLookupFailed

    except JSONDecodeError:
        raise UsernameLookupFailed

    return json

def grab_UUID(username):
    player_data = grab_json(uuid_lookup_url.format(username))
    return player_data['id']

def grab_playername(uuid):
    player_data = grab_json(username_lookup_url.format(uuid))

    if len(player_data) == 0:
        raise UsernameLookupFailed
    else:
        last_index = len(player_data)-1

    return player_data[last_index]['name']

