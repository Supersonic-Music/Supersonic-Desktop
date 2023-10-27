import json, curses, requests

MUSIC_DIR = "http://localhost:8083/music"
CAL_DIR = ".cal_sonic_library"

def load_artists():
    url = f"{MUSIC_DIR}/{CAL_DIR}/meta/artists.json"

    response = requests.get(url)

    if response.status_code == 200:
        artists_list = response.json()
        return artists_list
    else:
        return f"Error: {str(response.status_code)}"

def load_albums(artist_name):
    url = f"{MUSIC_DIR}/{CAL_DIR}/albums/{artist_name}_albums.json"
    response = requests.get(url)
    albums_list = response.json()
    return albums_list

def load_songs(artist_name, album_name):
    url = f"{MUSIC_DIR}/{CAL_DIR}/songs/{artist_name}_{album_name}_songs.json"
    response = requests.get(url)
    songs_list = response.json()
    return songs_list

def list_stuff(list_of_stuff):
    for thing in list_of_stuff:
        print(thing["name"])

if __name__ == "__main__":
    artists_list = load_artists()
    list_stuff(artists_list)
    artist_name = input("Choose an artist: ")
    albums_list = load_albums(artist_name)
    list_stuff(albums_list)
    album_name_fr = input("Choose an album: ")
    # album_name_fr = albums_list[int(album_name) - 1]
    print(album_name_fr)
    songs_list = load_songs(artist_name, album_name_fr)
    list_stuff(songs_list)
    song_name = input("Choose a song: ")
    import subprocess
    subprocess.run(f"mplayer '{MUSIC_DIR}/{artist_name}/{album_name_fr}/{song_name}'" ,shell=True)
