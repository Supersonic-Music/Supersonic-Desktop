import customtkinter, os, subprocess
from PIL import Image


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
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "song_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "song_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
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

        def song_pressed(artist, album, song):
            from main import MUSIC_DIR
            command = f"mplayer '{MUSIC_DIR}/{artist}/{album['name']}/{song['name']}'"
            print(command)
            subprocess.run("killall mplayer", shell=True)
            subprocess.Popen(command, shell=True)

        def album_pressed(artist_name, album_name):
            print(f"Button pressed for artist: {album_name}")
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            back_button = customtkinter.CTkButton(self.home_frame, text=f"Back to {artist_name}'s Albums", command=lambda: back_to_albums(artist_name))
            back_button.grid(row=0)
            from main import load_album_songs
            songs_list = load_album_songs(artist_name, album_name['name'])
            row = 1
            for song in songs_list:
                print("Got from Sonic Screwdriver: Song - " + song["name"])
                button = customtkinter.CTkButton(self.home_frame, text=f"{song['name']}", image=self.home_image, command=lambda song=song: song_pressed(artist_name, album_name, song))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1
        
        def artist_pressed(artist_name):
            print(f"Button pressed for artist: {artist_name}")
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            back_button = customtkinter.CTkButton(self.home_frame, text="Back to Artists", command=lambda: back_to_artists())
            back_button.grid(row=0)
            from main import load_artist_albums
            albums_list = load_artist_albums(artist_name)
            row = 1
            for album in albums_list:
                print("Got from Sonic Screwdriver: Album - " + album["name"])
                button = customtkinter.CTkButton(self.home_frame, text=f"{album['name']}", image=self.home_image, command=lambda album_name=album['name']: album_pressed(artist_name, album))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1
        
        def back_to_albums(artist_name):
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            list_albums(artist_name)

        def back_to_artists():
            for widget in self.home_frame.grid_slaves():
                widget.grid_forget()
            list_artists()
        
        def list_artists():
            row = 2
            for artist in artists_list:
                print("Got from Sonic Screwdriver: Artist - " + artist["name"])
                button = customtkinter.CTkButton(self.home_frame, text=f"{artist['name']}", image=self.home_image, command=lambda artist_name=artist['name']: artist_pressed(artist_name))
                button.grid(row=row, column=0, padx=20, pady=5, sticky="nsew")
                row += 1

        def list_albums(artist_name):
            back_button = customtkinter.CTkButton(self.home_frame, text="Back to Artists", command=lambda: back_to_artists())
            back_button.grid(row=0)
            row = 1
            from main import load_artist_albums
            albums_list = load_artist_albums(artist_name)
            for album in albums_list:
                print("Got from Sonic Screwdriver: Album - " + album["name"])
                button = customtkinter.CTkButton(self.home_frame, text=f"{album['name']}", image=self.home_image, command=lambda album_name=album['name']: album_pressed(artist_name, album))
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

