import requests, time
from config import SERVER, CAL_DIR
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

def ping_server(host=SERVER):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def load_artists():
    start_time = time.time()
    url = f"{SERVER}/{CAL_DIR}/meta/artists.json"

    print("EWPROJGIOWRKGOIWEHFIUERHGIUERHGEHRu")
    response = requests.get(url)
    print(response.status_code)
    
    if response.status_code == 200:
        artists_list = response.json()
        return artists_list
    else:
        print("FRGIUOERGIUHERGIUERGBIWRHGIJWRHGIU")
        return [f"Error: {str(response.status_code)}"]

def load_artist_albums(artist_name: str):
    if artist_name == "Plugins":
        artists_list = load_artists()
        albums_list = []
        for artist in artists_list:
            if artist["name"].endswith(".sonic"):
                albums_list.append(artist)
    else:
        url = f"{SERVER}/{CAL_DIR}/albums/{artist_name}_albums.json"
        response = requests.get(url)
        print(url)
        albums_list = response.json()
    return albums_list

def load_album_songs(artist_name: str, album_name: str):
    url = f"{SERVER}/{CAL_DIR}/songs/{artist_name}_{album_name}_songs.json"
    response = requests.get(url)
    songs_list = response.json()
    return songs_list

def load_albums():
    all_albums = []
    artists_list = load_artists()
    for artist in artists_list:
        albums_list = load_artist_albums(artist_name=artist["path"])
        all_albums.append(albums_list)

    all_albums_list = []
    for item in all_albums:
        for album in item:
            if 'name' in album:
                all_albums_list.append(album['name'])
    return all_albums_list

# def load_playlists():
#     url = f"{SERVER}/{CAL_DIR}/meta/playlists.json"

#     response = requests.get(url)

#     if response.status_code == 200:
#         all_playlists = response.json()
#         return all_playlists
#     else:
#         return [f"Error: {str(response.status_code)}"]
    
def load_albums_only():
    url = f"{SERVER}/{CAL_DIR}/meta/albums.json"

    response = requests.get(url)

    if response.status_code == 200:
        list_of_albums_only = response.json()
        return list_of_albums_only
    else:
        return [f"Error: {str(response.status_code)}"]


def list_stuff(list_of_stuff):
    for thing in list_of_stuff:
        print(thing["name"])
        
from config import FALLBACK_SERVER
if not ping_server():
    print("Falling Back to Public Server")
    SERVER = SERVER

# if __name__ == "__main__":
#     artists_list = load_artists()
#     list_stuff(artists_list)
#     artist_name = input("Choose an artist: ")
#     albums_list = load_artist_albums(artist_name)
#     list_stuff(albums_list)
#     album_name_fr = input("Choose an album: ")
#     # album_name_fr = albums_list[int(album_name) - 1]
#     print(album_name_fr)
#     songs_list = load_album_songs
#(artist_name, album_name_fr)
#     list_stuff(songs_list)
#     song_name = input("Choose a song: ")
#     if mimetypes.mimetypes_list[song_name.split('.')[1]] == "f3d":
#         url = f"{MUSIC_DIR}/{artist_name}/{album_name_fr}/{song_name}"
#         directory = f".paperback_cache/{song_name}"
#         wget.download(url, out=directory)
#         subprocess.run(f"f3d .paperback_cache/{song_name}'", shell=True)
#     else:
#         subprocess.run(f"{mimetypes.mimetypes_list[song_name.split('.')[1]]} '{MUSIC_DIR}/{artist_name}/{album_name_fr}/{song_name}'", shell=True)
