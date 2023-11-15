import requests, time
from config import SERVER, CAL_DIR
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import mimetypes

def ping_server():
    url = f"{SERVER}/{CAL_DIR}/meta/artists.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def load_artists():
    start_time = time.time()
    url = f"{SERVER}/{CAL_DIR}/meta/artists.json"
    response = requests.get(url)
    if response.status_code == 200:
        artists_list = response.json()
        time_taken = time.time() - start_time
        print(f"Got {len(artists_list)} artists in {round(time_taken, 2)} seconds.")
        return artists_list
    else:
        print("Could not load artists!!!")
        return [f"Error: {str(response.status_code)}"]

def load_artist_albums(artist_name: str):
    url = f"{SERVER}/{CAL_DIR}/albums/{artist_name}_albums.json"
    response = requests.get(url)
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

def play_song(artist_name, album_name, song, song_queue):
    player = mimetypes.mimetypes_list[song.rsplit(".", 1)[-1]]
    command = f'{player} "{SERVER}/{artist_name}/{album_name}/{song}"'
    for songy in song_queue:
        if songy == song:
            pass
        else:
            command += f' "{SERVER}/{artist_name}/{album_name}/{songy}"'
    print(player)
    subprocess.run("killall mplayer", shell=True)
    subprocess.run("killall mpv", shell=True)
    subprocess.Popen(command, shell=True)

def get_cover(artist_name, album_name):
    image_url = f"{SERVER}/{artist_name}/{album_name}/cover"
    response = requests.get(image_url + ".png")
    if response.status_code == 200:
        cover = response.content
    else:
        response = requests.get(image_url + ".jpg")
        if response.status_code == 200:
            cover = response.content
        else:
            print("Failed to fetch the album art. Status code:", response.status_code)
            cover = None
    return cover

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
