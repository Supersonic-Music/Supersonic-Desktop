import json, curses, requests, subprocess, wget
import mimetypes

MUSIC_DIR = "http://localhost:8083/music"
CAL_DIR = ".cal_sonic_library"

def load_artists():
    url = f"{MUSIC_DIR}/{CAL_DIR}/meta/artists.json"

    response = requests.get(url)

    if response.status_code == 200:
        artists_list = response.json()
        return artists_list
    else:
        return [f"Error: {str(response.status_code)}"]

def load_artist_albums(artist_name: str):
    url = f"{MUSIC_DIR}/{CAL_DIR}/albums/{artist_name}_albums.json"
    response = requests.get(url)
    albums_list = response.json()
    return albums_list

def load_album_songs(artist_name: str, album_name: str):
    url = f"{MUSIC_DIR}/{CAL_DIR}/songs/{artist_name}_{album_name}_songs.json"
    print(url + "<<<<<<<<<<<<<<<<<<<<<<<<<")
    response = requests.get(url)
    songs_list = response.json()
    return songs_list

def load_albums():
    all_albums = []
    artists_list = load_artists()
    for artist in artists_list:
        albums_list = load_artist_albums(artist_name=artist["name"])
        all_albums.append(albums_list)

    all_albums_list = []
    for item in all_albums:
        for album in item:
            if 'name' in album:
                all_albums_list.append(album['name'])
    return all_albums_list


def list_stuff(list_of_stuff):
    for thing in list_of_stuff:
        print(thing["name"])

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