import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from main import load_artists, load_artist_albums, load_album_songs
from config import PROGRAM_NAME, PROGRAM_SLOGAN, PROGRAM_VERSION
from main import play_song


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(f"{PROGRAM_NAME} {PROGRAM_VERSION} - {PROGRAM_SLOGAN}")
        self.set_default_size(800, 600)

        # Create a Gtk.Stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(275)
        self.set_child(self.stack)

        # Create a ScrolledWindow for the list of artists
        scrolled_window = Gtk.ScrolledWindow()
        self.stack.add_named(scrolled_window, "artists_list")

        # Create a Box to hold the buttons
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window.set_child(self.box1)

        artists_list = load_artists()
        for artist in artists_list:
            artist_name = artist["name"]
            if artist_name.startswith("."):
                pass
            else:
                button = Gtk.Button(label=artist_name)
                self.box1.append(button)
                button.connect('clicked', self.on_button_clicked, artist_name)

        # Create a Box for the artist details page
        self.artist_details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.stack.add_named(self.artist_details_box, "artist_details")

        # Create a Gtk.Box for the song listing page
        self.song_listing_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.stack.add_named(self.song_listing_box, "song_listing")

        # Create a back button for the song listing page
        back_button = Gtk.Button(label="Back")
        self.song_listing_box.append(back_button)
        back_button.connect('clicked', self.on_back_button_clicked)

    def on_button_clicked(self, button, artist_name):
        # Create a new Gtk.Box for the artist details page
        new_artist_details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        back_button = Gtk.Button(label=f"Back to Artists")
        new_artist_details_box.append(back_button)
        back_button.connect('clicked', self.on_back_to_artists_clicked)

        albums_list = load_artist_albums(artist_name)
        for album in albums_list:
            album_name = album["name"]
            if album_name.startswith("."):
                pass
            else:
                button = Gtk.Button(label=album_name)
                new_artist_details_box.append(button)
                button.connect('clicked', self.on_album_clicked, artist_name, album_name)

        # Remove the old artist details page from the stack
        if self.artist_details_box is not None:
            self.stack.remove(self.artist_details_box)

        # Add the new artist details page to the stack
        self.stack.add_named(new_artist_details_box, "artist_details")

        # Update the reference to the artist details box
        self.artist_details_box = new_artist_details_box

        # Switch to the artist details page
        self.stack.set_visible_child_name("artist_details")
        
    def on_album_clicked(self, button, artist_name, album_name):
        # Remove all children of the song_listing_box
        for child in list(self.song_listing_box):
            self.song_listing_box.remove(child)
        
        # Add the back button to the song_listing_box
        back_button = Gtk.Button(label=f"Back to {artist_name}'s Albums")
        self.song_listing_box.append(back_button)
        back_button.connect('clicked', self.on_back_to_albums_clicked)
        
        # Add the songs to the song_listing_box
        songs = load_album_songs(artist_name, album_name)
        for song in songs:
            song_name = song["name"]
            song_path = song["path"]
            if song_name.startswith("."):
                pass
            else:
                button = Gtk.Button(label=song_name)
                self.song_listing_box.append(button)
                button.connect('clicked', self.on_song_clicked, artist_name, album_name, song_path)
        
        # Switch to the song listing page
        self.stack.set_visible_child_name("song_listing")
                
    def on_song_clicked(self, button, artist_name, album_name, song_path):
        play_song(artist_name, album_name, song_path)

    def on_back_button_clicked(self, button):
        # Switch back to the artist details page
        self.stack.set_visible_child_name("artist_details")

    def on_back_to_albums_clicked(self, button):
        # Switch back to the artist details page
        self.stack.set_visible_child_name("artist_details")
        
    def on_back_to_artists_clicked(self, button):
        # Switch back to the artist list page
        self.stack.set_visible_child_name("artists_list")

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="io.davros.sonic")
app.run(sys.argv)
