import requests, time, tempfile, subprocess, mimetypes, os, platform, vlc
from colorama import Fore
from config import SERVER, CAL_DIR
from mpris2 import Player, get_players_uri
from gi.repository import GLib
from urllib.parse import quote

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

def play_song(artist_name, album_name, song, song_queue, repeat_track):
    player = mimetypes.mimetypes_list[song.rsplit(".", 1)[-1]]
    command = f'{player} "{SERVER}/{artist_name}/{album_name}/{song}"'
    if repeat_track:
        command = command + " -loop 0"
    else:
        for songy in song_queue:
            if songy == song:
                pass
            else:
                command += f' "{SERVER}/{artist_name}/{album_name}/{songy}"'
    print(player)
    subprocess.run("killall mplayer", shell=True)
    subprocess.run("killall mpv", shell=True)
    subprocess.Popen(command, shell=True)

def play_song_mpris(artist_name, album_name, song, song_queue, repeat_track):
    # Download the song data
    song_url = f"{SERVER}/{artist_name}/{album_name}/{song}"
    response = requests.get(song_url)
    response.raise_for_status()  # Raise an exception if the request failed

    # Save the song data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(response.content)
        song_path = temp_file.name

    # Get the URI of the first available player
    player_uri = next(get_players_uri(), None)

    if player_uri is None:
        print("No available player found.")
        return

    # Create a Player instance
    player = Player(dbus_interface_info={'dbus_uri': player_uri})

    # Set the metadata for the song
    player.Metadata = {
        'mpris:trackid': GLib.Variant('s', '/org/mpris/MediaPlayer2/Track/0'),
        'mpris:length': GLib.Variant('x', 60 * 1e6),  # 60 seconds
        'xesam:title': GLib.Variant('s', song),
        'xesam:album': GLib.Variant('s', album_name),
        'xesam:artist': GLib.Variant('as', [artist_name]),
    }

    # Set the song to play
    player.Uri = 'file://' + song_path

    # Play the song
    player.Play()

player = vlc.MediaPlayer()
song_queue = []

def play_song_vlc(artist_name_param, album_name_param, song_path_param, song_queue_param, repeat_track=False):
    global player, song_queue, artist_name, album_name, song_path
    song_queue = song_queue_param
    artist_name = artist_name_param
    album_name = album_name_param
    song_path = song_path_param
    if player.is_playing():
        player.stop()
    song_url = f"{SERVER}/{quote(artist_name)}/{quote(album_name)}/{quote(song_path)}"
    print(Fore.BLUE + song_url + Fore.RESET)
    player.set_mrl(song_url)
    player.play()

def get_cover(artist_name, album_name):
    if album_name == "Plugins":
        image_url = f"{SERVER}/{artist_name}/cover"
    else:
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
