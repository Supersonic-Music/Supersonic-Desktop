import customtkinter, os, subprocess, mimetypes, requests
from PIL import Image
from io import BytesIO


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Paperback - Sonic Screwdriver")
        self.geometry("1000x1000")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "artist_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "artist_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "album_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "album_light.png")), size=(20, 20))
        self.album_placeholder = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "album_light.png")),size=(60, 60))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "song_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "song_light.png")), size=(20, 20))
        self.song_placeholder = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "song_light.png")), size=(30, 30))
        self.plugin = customtkinter.CTkImage(dark_image=Image.open(os.path.join(image_path, "plugin_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=25)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Paperback", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Artists",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Albums",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Songs",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.frame_4_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Songs",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_4_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["System", "Dark", "Light"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.bind_all("<Button-4>", lambda e: self.home_frame._parent_canvas.yview("scroll", -1, "units"))
        self.home_frame.bind_all("<Button-5>", lambda e: self.home_frame._parent_canvas.yview("scroll", 1, "units"))
        self.home_frame.grid_columnconfigure(0, weight=1)

        # stuff
        from main import load_artists
        artists_list = load_artists()

        label = customtkinter.CTkLabel(self.home_frame, text="Search Artists")
        label.grid(row=0, column=0, padx=20, pady=5, sticky="w")  # Place label in row 0

        searchbox = customtkinter.CTkTextbox(self.home_frame, height=1, wrap="none")
        searchbox.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")  # Place search box in row 0

        # Remove the following line to enable user interaction with the search box
        # searchbox.configure(state="disabled")

        # Bind the click event to clear the default text
        searchbox.bind("<Button-1>", lambda event: searchbox.delete("1.0", "end"))
        text = searchbox.get("0.0", "end")  # get text from line 0 character 0 till the end
        searchbox.delete("0.0", "end")  # delete all text
        searchbox.configure(state="normal")  # configure textbox to be read-only
        row = 2

        def song_pressed(artist, album, song, songs_list):
            from main import MUSIC_DIR
            player = mimetypes.mimetypes_list[song["name"].rsplit(".", 1)[-1]]
            if artist == "Plugins":
                command = f'{player} "{MUSIC_DIR}/.{album}.sonic/{song["name"]}"'
            else:
                command = f'{player} "{MUSIC_DIR}/{artist}/{album}/{song["name"]}"'
            for song_name in songs_list:
                if artist == "Plugins":
                    if not song_name == song["name"]:
                        command = command + f' "{MUSIC_DIR}/.{album}.sonic/{song_name}"'
                else:
                    if not song_name == song["name"]:
                        command = command + f' "{MUSIC_DIR}/{artist}/{album}/{song_name}"'
            print(command)
            if player == "mplayer" or player == "mpv":
                subprocess.run("killall mplayer", shell=True)
                subprocess.run("killall mpv", shell=True)
            subprocess.Popen(command, shell=True)

        def album_pressed(artist_name, album_name):
            print(f"Button pressed for album: {album_name}")
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            back_button = customtkinter.CTkButton(self.home_frame, text=f"Back to {artist_name}'s Albums", command=lambda: back_to_albums(artist_name))
            back_button.grid(row=0)
            from main import load_album_songs
            songs_list = load_album_songs(artist_name, album_name)
            row = 1
            from main import MUSIC_DIR
            if artist_name == "Plugins":
                image_url = f"{MUSIC_DIR}/.{album_name}.sonic/cover"
            else:
                image_url = f"{MUSIC_DIR}/{artist_name}/{album_name}/cover"
            response = requests.get(image_url + ".png")
            print("Image URL:", image_url)
            print("Status code:", response.status_code)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                self.song_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(30, 30))
                self.song_image_big = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(145, 145))
                self.song_image_big_label = customtkinter.CTkLabel(self.home_frame, image=self.song_image_big)
                print("song_image_big_label created")
                row += 1
            else:
                print("Could not get PNG, Trying JPG instead")
                response = requests.get(image_url + ".jpg")
                print("Status code:", response.status_code)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    self.song_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(30, 30))
                    self.song_image_big = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(145, 145))
                    self.song_image_big_label = customtkinter.CTkLabel(self.home_frame, image=self.song_image_big)
                    print("song_image_big_label created")
                    row += 1
                else:
                    print(f"Failed to fetch the album art for {album_name}. Status code:", response.status_code)
                    self.song_image = self.song_placeholder
            songs_list_fr = []
            for song in songs_list:
                print("Got from Sonic Screwdriver: Song - " + song["name"])
                songs_list_fr.append(song['name'])
                button = customtkinter.CTkButton(self.home_frame, text=f"{song['name']}", image=self.song_image, anchor="w", command=lambda song=song: song_pressed(artist_name, album_name, song, songs_list_fr))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1
        
        def artist_pressed(artist_name):
            print(f"Button pressed for artist: {artist_name}")
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            if artist_name.endswith(".sonic"):
                back_button = customtkinter.CTkButton(self.home_frame, text="Back to Plugin Selection", command=lambda: back_to_artists())
            else:
                print("back to artists button !")
                back_button = customtkinter.CTkButton(self.home_frame, text="Back to Artists", command=lambda: back_to_artists())
            back_button.grid(row=0, pady=5)
            from main import load_artist_albums
            artist_name_text(artist_name)
            if artist_name == "Plugins":
                list_plugins()
            else:
                list_albums(artist_name)
        
        def list_plugins():
            row = 3
            from main import load_artists
            from main import MUSIC_DIR
            artists_list = load_artists()
            for artist in artists_list:
                if artist["name"].endswith(".sonic"):
                    print(f"Found Plugin: {artist['name']}")
                    image_url = f"{MUSIC_DIR}/{artist['name']}/cover"
                    print(image_url)
                    response = requests.get(image_url + ".png")
                    print(image_url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        self.album_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(60, 60))
                    else:
                        response = requests.get(image_url + ".jpg")
                        if response.status_code == 200:
                            image = Image.open(BytesIO(response.content))
                            self.album_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(60, 60))
                        else:
                            print("Failed to fetch the album art. Status code:", response.status_code)
                            self.album_image = self.album_placeholder
                    button = customtkinter.CTkButton(self.home_frame, text=f"{artist['name'].split('.')[1]}", image=self.album_image, anchor="w", command=lambda artist_name=artist['name']: artist_pressed(artist_name))
                    button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                    row += 1



        def back_to_albums(artist_name):
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            artist_name_text(artist_name)
            list_albums(artist_name)

        def back_to_artists():
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            searchbox = customtkinter.CTkTextbox(self.home_frame, height=1, wrap="none")
            searchbox.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")  # Place search box in row 0
            searchbox.bind("<Button-1>", lambda event: searchbox.delete("1.0", "end"))
            text = searchbox.get("0.0", "end")  # get text from line 0 character 0 till the end
            searchbox.delete("0.0", "end")  # delete all text
            searchbox.configure(state="normal")  # configure textbox to be read-only
            list_artists()
        
        def list_artists():
            row = 3
            found_plugins = False
            for artist in artists_list:
                if artist["name"].endswith(".sonic"):
                    print("Detected Plugin!")
                    if not found_plugins:
                        found_plugins = True
                        button = customtkinter.CTkButton(self.home_frame, text=f"Plugins", image=self.plugin, anchor="w", fg_color="#c90306", hover_color="#800001", command=lambda artist_name="Plugins": artist_pressed(artist_name))
                        button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                        row += 1
            for artist in artists_list:
                if artist["name"].startswith("."):
                    continue
                print("Got from Sonic Screwdriver: Artist - " + artist["name"])
                button = customtkinter.CTkButton(self.home_frame, text=f"{artist['name']}", image=self.home_image, anchor="w", command=lambda artist_name=artist['name']: artist_pressed(artist_name))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1

        def artist_name_text(artist_name):
            if artist_name.endswith(".sonic"):
                artist_text = customtkinter.CTkLabel(self.home_frame, text=artist_name.split(".")[1], anchor="w")
            else:
                artist_text = customtkinter.CTkLabel(self.home_frame, text=artist_name, anchor="w")
            artist_text.grid(row=1)
            row = 2

        def list_albums(artist_name):
            back_button = customtkinter.CTkButton(self.home_frame, text="Back to Artists", command=lambda: back_to_artists())
            back_button.grid(row=0, pady=5)
            row = 2
            from main import load_artist_albums
            albums_list = load_artist_albums(artist_name)
            for album in albums_list:
                print("Got from Sonic Screwdriver: Album - " + album["name"])
                from main import MUSIC_DIR
                if artist_name == "Plugins":
                    print("doing plugins")
                    image_url = f"{MUSIC_DIR}/{album['name']}/cover"
                    print(image_url)
                else:
                    image_url = f"{MUSIC_DIR}/{artist_name}/{album['name']}/cover"
                response = requests.get(image_url + ".png")
                print(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    self.album_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(60, 60))
                else:
                    response = requests.get(image_url + ".jpg")
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        self.album_image = customtkinter.CTkImage(Image.open(BytesIO(response.content)), size=(60, 60))
                    else:
                        print("Failed to fetch the album art. Status code:", response.status_code)
                        self.album_image = self.album_placeholder
                if artist_name == "Plugins":
                    print(album["name"] + "is the album name")
                    button = customtkinter.CTkButton(self.home_frame, text=f"{album['name']}", image=self.album_image, anchor="w", command=lambda album_name=album['name']: artist_pressed(album["name"]))
                else:
                    button = customtkinter.CTkButton(self.home_frame, text=f"{album['name']}", image=self.album_image, anchor="w", command=lambda album_name=album['name']: album_pressed(artist_name, album_name))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1

        list_artists()

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.fourth_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.frame_4_button.configure(fg_color=("gray75", "gray25") if name == "frame_4" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
            row = 0
            from main import load_albums
            all_albums_list = load_albums()
            for album in all_albums_list:
                print("Got from Sonic Screwdriver: Album - " + album)
                button = customtkinter.CTkButton(self.second_frame, text=f"{album}", image=self.home_image, anchor="w")
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        if name == "frame_4":
            self.fourth_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()

