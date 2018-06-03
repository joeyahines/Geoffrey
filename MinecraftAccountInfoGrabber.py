import requests
from json import JSONDecodeError
from BotErrors import UsernameLookupFailed

uuid_lookup_url = 'https://api.mojang.com/users/profiles/minecraft/{}'
username_lookup_url = 'https://api.mojang.com/user/profiles/{}/names'


def grab_json(url):
    return requests.get(url).json()


def grab_UUID(username):
    try:
        player_data = grab_json(uuid_lookup_url.format(username))
        return player_data['id']
    except JSONDecodeError:
        raise UsernameLookupFailed

def grab_playername(uuid):
    player_data = grab_json(username_lookup_url.format(uuid))
    return player_data[0]['name']



