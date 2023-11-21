import sys, gi, requests, tempfile, subprocess, time, vlc
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from PIL import Image
from io import BytesIO
from main import load_artists, load_artist_albums, load_album_songs, get_cover, ping_server, load_albums_only
from config import PROGRAM_NAME, PROGRAM_SLOGAN, PROGRAM_VERSION, SERVER, USE_BUILTIN_SERVER
from main import play_song, play_song_vlc, player


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(f"{PROGRAM_NAME} {PROGRAM_VERSION} - {PROGRAM_SLOGAN}")
        self.set_default_size(800, 600)

        # Create a Gtk.Stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(275)
        # Create a CssProvider
        css_provider = Gtk.CssProvider()

        # Load the CSS
        css_provider.load_from_data(b"""
            button {
                border-radius: 0px;
            }
        """)
        
        # Create a Gtk.Grid for the sidebar
        sidebar = Gtk.Grid()
        sidebar.set_column_homogeneous(True)

        sidebar_buttons = [
            {"name": "Artists", "icon": "avatar-default-symbolic", "action": "on_back_to_artists_clicked"}, 
            {"name": "Albums", "icon": "media-optical-symbolic", "action": "albums_view_clicked"}, 
            # {"name": "Songs", "icon": "folder-music-symbolic", "action": "show_about"}, 
            # {"name": "Decades", "icon": "emblem-synchronizing-symbolic", "action": "on_decades_clicked"}, 
            # {"name": "Playlists", "icon": "view-media-playlist-symbolic", "action": "show_about"}, 
            # {"name": "Settings", "icon": "emblem-system-symbolic", "action": "show_about"}, 
            {"name": "About", "icon": "dialog-information-symbolic", "action": "show_about"}
        ]
        
        for sidebar_button in sidebar_buttons:
            button = Gtk.Button()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            icon = Gtk.Image()
            icon.set_from_icon_name(sidebar_button["icon"])
            icon.set_pixel_size(16)  # Set the icon size in pixels
            label = Gtk.Label()
            label.set_text(sidebar_button["name"])
            box.append(icon)
            box.append(label)
            button.set_child(box)
            button.connect('clicked', getattr(self, sidebar_button["action"]))
            sidebar.attach(button, 0, sidebar_buttons.index(sidebar_button), 1, 1)

            style_context = button.get_style_context()
            self.css_provider = Gtk.CssProvider()
            self.css_provider.load_from_data(b"""
            button {
                border-radius: 0;
            }
            """)
            style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        controls_label = Gtk.Label()
        controls_label.set_text("Controls")
        self.controls_pause_play = Gtk.Button()
        controls_skip_forward = Gtk.Button()
        controls_skip_backward = Gtk.Button()
        controls_stop = Gtk.Button()
        behaviour_label = Gtk.Label()
        behaviour_label.set_text("Behaviour")
        controls_repeat_track = Gtk.Button()
        self.controls_pause_play.connect('clicked', self.controls_pause_play_clicked)
        controls_stop.connect('clicked', self.controls_stop_clicked)
        self.controls_pause_play.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        controls_skip_forward.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        controls_skip_backward.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        controls_stop.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        controls_repeat_track.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        pause_play_icon = Gtk.Image()
        skip_forward_icon = Gtk.Image()
        skip_backward_icon = Gtk.Image()
        stop_icon = Gtk.Image()
        repeat_track_icon = Gtk.Image()
        pause_play_icon.set_from_icon_name("media-playback-start-symbolic")
        skip_forward_icon.set_from_icon_name("media-skip-forward-symbolic")
        skip_backward_icon.set_from_icon_name("media-skip-backward-symbolic")
        repeat_track_icon.set_from_icon_name("media-playlist-repeat-song-symbolic")
        stop_icon.set_from_icon_name("media-playback-stop-symbolic")
        pause_play_icon.set_pixel_size(16)
        skip_forward_icon.set_pixel_size(16)
        skip_backward_icon.set_pixel_size(16)
        stop_icon.set_pixel_size(16)
        repeat_track_icon.set_pixel_size(16)
        self.controls_pause_play.set_child(pause_play_icon)
        controls_skip_forward.set_child(skip_forward_icon)
        controls_skip_backward.set_child(skip_backward_icon)
        controls_stop.set_child(stop_icon)
        controls_repeat_track.set_child(repeat_track_icon)
        sidebar.attach(controls_label, 0, 7, 1, 1)
        # sidebar.attach(controls_skip_forward, 0, 8, 1, 1)
        sidebar.attach(self.controls_pause_play, 0, 9, 1, 1)
        # sidebar.attach(controls_skip_backward, 0, 10, 1, 1)
        sidebar.attach(controls_stop, 0, 11, 1, 1)
        # sidebar.attach(behaviour_label, 0, 12, 1, 1)
        # sidebar.attach(controls_repeat_track, 0, 13, 1, 1)
        
        # Add the sidebar and the stack to the sidebar_box
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        sidebar_box.append(sidebar)
        sidebar_box.append(self.stack)

        # Make the stack expand to take up the rest of the space
        self.stack.set_hexpand(True)

        # Add the sidebar_box to the main window
        self.set_child(sidebar_box)

        # Create a ScrolledWindow for the list of artists
        scrolled_window = Gtk.ScrolledWindow()
        self.stack.add_named(scrolled_window, "artists_list")

        # Create a Box to hold the buttons
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window.set_child(self.box1)
        server_up = ping_server()
        if not server_up:
            if USE_BUILTIN_SERVER:
                subprocess.Popen("supersonic-server", shell=True)
                time.sleep(3)
                server_up = True
            else:
                print("Server is down")
                server_is_down = Gtk.Label(label="Server is Down")
                self.box1.append(server_is_down)
        if server_up:
            artists_list = load_artists()
            found_plugins = False
            first_artist = True
            for artist in artists_list:
                artist_name = artist["name"]
                if artist_name.startswith("."):
                    pass
                elif artist_name.endswith(".sonic"):
                    if not found_plugins:
                        plugins_label = Gtk.Label()
                        plugins_label.set_text("Add-ons")
                        self.box1.append(plugins_label)
                    found_plugins = True
                    plugin_name = artist_name.split(".")[-2]
                    print(f"Found {plugin_name} Add-on!")

                    # Create a button without a label
                    button = Gtk.Button()

                    # Create a label
                    label = Gtk.Label(label=plugin_name)

                    # Create an icon
                    cover = get_cover(artist_name, album_name="Plugins")
                    if cover is not None:
                        image = Image.open(BytesIO(cover))
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                        image.save(temp_file)
                        image = Gtk.Picture.new_for_filename(temp_file.name)
                    else:
                        print("Cover is None")
                        image = Gtk.Image.new_from_icon_name("application-x-addon-symbolic")
                        image.set_pixel_size(20)

                    # Create a box to hold the icon and label
                    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                    box.append(image)
                    box.append(label)

                    # Set the box as the child of the button
                    button.set_child(box)

                    button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                    self.box1.append(button)
                    button.connect('clicked', self.on_button_clicked, artist_name)
                else:
                    if first_artist:
                        first_artist = False
                        artists_label = Gtk.Label()
                        artists_label.set_text("Artists")
                        self.box1.append(artists_label)
                    # Create a button with a label
                    # Create a button without a label
                    button = Gtk.Button()
                    button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

                    # Create a label
                    label = Gtk.Label(label=artist_name)

                    # Create an icon
                    icon = Gtk.Image()
                    icon.set_from_icon_name("avatar-default-symbolic")
                    icon.set_pixel_size(20)

                    # Create a box to hold the icon and label
                    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                    box.append(icon)
                    box.append(label)

                    # Set the box as the child of the button
                    button.set_child(box)

                    # Add the button to the box
                    self.box1.append(button)

                    # Connect the 'clicked' signal to the 'on_button_clicked' method
                    button.connect('clicked', self.on_button_clicked, artist_name)
                    self.artist_details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_artist_window = Gtk.ScrolledWindow()
        scrolled_artist_window.set_child(self.artist_details_box)
        # self.stack.add_named(scrolled_artist_window, "artist_details")
        
        self.decades_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_decades_window = Gtk.ScrolledWindow()
        scrolled_decades_window.set_child(self.decades_box)
        self.stack.add_titled(self.decades_box, "decades_list", "Decades")

        self.song_listing_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.song_listing_box)
        self.stack.add_named(scrolled_window, "song_listing")
        
        self.albums_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.albums_view_box)
        self.stack.add_named(scrolled_window, "albums_view")

        back_button = Gtk.Button(label="Back")
        self.song_listing_box.append(back_button)
        back_button.connect('clicked', self.on_back_button_clicked)

    def on_button_clicked(self, button, artist_name):
        # Create a new Gtk.Box for the artist details page
        new_artist_details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        back_button = Gtk.Button(label=f"Back to Artists")
        back_button.get_style_context().add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        new_artist_details_box.append(back_button)
        back_button.connect('clicked', self.on_back_to_artists_clicked)

        albums_list = load_artist_albums(artist_name)
        for album in albums_list:
            album_name = album["name"]
            print(f"Found {album_name}")
            if album_name.startswith("."):
                pass
            else:
                button = Gtk.Button(label=album_name)
                button.set_size_request(-1, 100)
                cover = get_cover(artist_name, album_name)
                if cover is not None:
                    image = Image.open(BytesIO(cover))
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    image.save(temp_file)
                    image = Gtk.Picture.new_for_filename(temp_file.name)
                else:
                    print("Cover is None")
                    image = Gtk.Image.new_from_icon_name("media-optical-symbolic")
                    image.set_pixel_size(95)

                # Create a new Gtk.Box
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

                # Add the image and the label to the box
                box.append(image)
                box.append(Gtk.Label(label=album_name))

                # Add the box to the button
                button.set_child(box)

                new_artist_details_box.append(button)
                button.get_style_context().add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                new_artist_details_box.append(button)
                button.connect('clicked', self.on_album_clicked, artist_name, album_name)

        # Wrap the artist details box in a scrolled window
        scrolled_artist_details = Gtk.ScrolledWindow()
        scrolled_artist_details.set_child(new_artist_details_box)

        # Remove the old artist details page from the stack
        if self.artist_details_box is not None:
            self.stack.remove(self.artist_details_box)

        # Add the new artist details page to the stack
        self.stack.add_named(scrolled_artist_details, "artist_details")

        # Update the reference to the artist details box
        self.artist_details_box = scrolled_artist_details

        # Switch to the artist details page
        self.stack.set_visible_child_name("artist_details")
        
    def on_album_clicked(self, button, artist_name, album_name):
        # Remove all children of the song_listing_box
        for child in list(self.song_listing_box):
            self.song_listing_box.remove(child)
        
        # Add the back button to the song_listing_box
        if artist_name.startswith(".") and artist_name.endswith(".sonic"):
            back_to_albums_label = f"Back to {artist_name.split('.')[1]}'s Categories"
        else:
            back_to_albums_label = f"Back to {artist_name}'s Albums"
        back_button = Gtk.Button(label=back_to_albums_label)
        back_button.set_margin_bottom(5)

        # Create a CssProvider
        css_provider = Gtk.CssProvider()

        # Load the CSS
        css_provider.load_from_data(b"""
            button {
                border-radius: 0px;
            }
        """)

        # Add the CssProvider to the button's style context
        style_context = back_button.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.song_listing_box.append(back_button)
        back_button.connect('clicked', self.on_back_to_albums_clicked)
        
        cover = get_cover(artist_name, album_name)
        if cover is not None:
            image = Image.open(BytesIO(cover))
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            image.save(temp_file)
        else:
            print("Cover is None")
            image = Gtk.Image.new_from_icon_name("media-playback-start")
        
        # Add the songs to the song_listing_box
        songs = load_album_songs(artist_name, album_name)
        song_queue = []
        for song in songs:
            song_name = song["name"]
            song_path = song["path"]
            if song_name.startswith(".") or song_path.endswith(".jpg") or song_path.endswith(".png"):
                pass
            else:
                song_queue.append(song_path)
                # Create a new button
                button = Gtk.Button()
                button.set_size_request(-1, 50)  # Set the height to 50 pixels
                button.set_margin_top(5)  # Add 5 pixels of space at the top of the button
                button.set_margin_bottom(5)  # Add 5 pixels of space at the bottom of the button

                # Create a new box
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                
                # Create a new label and set its text
                label = Gtk.Label()
                label.set_text(song_name)

                if cover is not None:
                    image = Gtk.Picture.new_for_filename(temp_file.name)
                else:
                    image = Gtk.Image.new_from_icon_name("media-playback-start")
                    
                
                # Add the image and the label to the box
                box.append(image)
                box.append(label)

                # Set the box as the child of the button
                button.set_child(box)

                # Add the button to the song_listing_box
                self.song_listing_box.append(button)

                # Connect the button to a handler function
                button.connect('clicked', self.on_song_clicked, artist_name, album_name, song_path, song_queue)
        # Switch to the song listing page
        self.stack.set_visible_child_name("song_listing")
                
    def on_song_clicked(self, button, artist_name, album_name, song_path, song_queue):
        print(song_queue)
        self.controls_pause_play.set_child(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic"))
        play_song_vlc(artist_name, album_name, song_path, song_queue, repeat_track=False)

    def on_back_button_clicked(self, button):
        # Switch back to the artist details page
        self.stack.set_visible_child_name("artist_details")

    def on_back_to_albums_clicked(self, button):
        # Switch back to the artist details page
        self.stack.set_visible_child_name("artist_details")
        
    def on_back_to_artists_clicked(self, button):
        # Switch back to the artist list page
        self.stack.set_visible_child_name("artists_list")
        
    def on_decades_clicked(self, button):
        decades = ["1920", "1930", "1940", "1950", "1960", "1970", "1980", "1990", "2000", "2010", "2020"]
        for decade in decades:
            # Create a new label for each decade
            decade_label = Gtk.Label()
            decade_label.set_text(decade + "s")
            # Add the label to 'decades_box'
            self.decades_box.append(decade_label)
            # Show the label
            decade_label.show()

        # Switch to the 'decades_list' after it has been populated
        self.stack.set_visible_child_name("decades_list")
        
    def show_about(self, button):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)  # Makes the dialog always appear in from of the parent window
        self.about.set_modal(self)  # Makes the parent window unresponsive while dialog is showing

        self.about.set_program_name(PROGRAM_NAME)
        self.about.set_authors(["Ethan Martin"])
        self.about.set_copyright("Copyright 2023 Ethan Martin")
        self.about.set_license_type(Gtk.License.MIT_X11)
        self.about.set_website("https://github.com/yuckdevchan/Supersonic-Desktop")
        self.about.set_website_label("GitHub")
        self.about.set_version(PROGRAM_VERSION)
        self.about.set_logo_icon_name("io.davros.sonic")

        self.about.set_visible(True)
        
    def controls_stop_clicked(self, button):
        self.controls_pause_play.set_child(Gtk.Image.new_from_icon_name("media-playback-start-symbolic"))
        player.stop()
    
    def controls_pause_play_clicked(self, button):
        if player.is_playing():
            player.pause()
            # change icon
            button.set_child(Gtk.Image.new_from_icon_name("media-playback-start-symbolic"))
        else:
            player.play()
            button.set_child(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic"))
            
    def albums_view_clicked(self, button):
        albums_view_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Remove the old "albums_view" from the stack
        old_albums_view = self.stack.get_child_by_name("albums_view")
        if old_albums_view is not None:
            self.stack.remove(old_albums_view)

        self.stack.add_named(albums_view_box, "albums_view")  # Add the new albums_view_box to the stack

        albums_list = load_albums_only()
        for album in albums_list:
            first_bit_of_data = True
            for bit_of_data in album:
                if first_bit_of_data:
                    first_bit_of_data = False
                    artist_name = bit_of_data['artist']
                else:
                    if artist_name.startswith("."):
                        pass
                    else:
                        # make a button within its own box with the label being 'bit_of_data['name']' and the icon being media-optical-symbolic
                        button = Gtk.Button()
                        button.get_style_context().add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

                        # Create a label
                        label = Gtk.Label(label=bit_of_data['name'])

                        # Create an icon
                        icon = Gtk.Image()
                        icon.set_from_icon_name("media-optical-symbolic")
                        icon.set_pixel_size(20)

                        # Create a box to hold the icon and label
                        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                        box.append(icon)
                        box.append(label)

                        # Set the box as the child of the button
                        button.set_child(box)

                        # Add the button to the box
                        albums_view_box.append(button)  # Add the button to the new albums_view_box

                        # Connect the 'clicked' signal to the 'on_button_clicked' method
                        button.connect('clicked', self.on_album_clicked, artist_name, bit_of_data['name'])

        # Switch to the new albums_view_box
        self.stack.set_visible_child_name("albums_view")        
    def __del__(self):
        # Stop mplayer
        subprocess.run("killall mplayer", shell=True)
        print("killed mplayer")

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="io.davros.sonic")
app.run(sys.argv)