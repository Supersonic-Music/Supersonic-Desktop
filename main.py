import json
import curses
import os

MUSIC_DIR = "/home/deck/Music"
CAL_DIR = ".cal_sonic_library"

# Load the list of artists
with open(f"{MUSIC_DIR}/{CAL_DIR}/meta/artists.json", "r") as file:
    artists_list = json.load(file)

def load_artist_data(artist_name):
    artist_file = os.path.join(MUSIC_DIR, CAL_DIR, "artists", f"{artist_name}.json")
    if os.path.isfile(artist_file):
        with open(artist_file, "r") as file:
            return json.load(file)
    else:
        return []

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()

    height, width = stdscr.getmaxyx()
    start_row = 0
    selected_row = 0

    while True:
        stdscr.clear()

        for i in range(start_row, min(start_row + height, len(artists_list))):
            artist = artists_list[i]
            if i - start_row == selected_row:
                stdscr.addstr(i - start_row, 0, artist["name"], curses.A_REVERSE)
            else:
                stdscr.addstr(i - start_row, 0, artist["name"])

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_DOWN and selected_row < height - 1:
            selected_row += 1
        elif key == curses.KEY_UP and selected_row > 0:
            selected_row -= 1
        elif key == curses.KEY_DOWN and selected_row == height - 1 and start_row < len(artists_list) - height:
            start_row += 1
        elif key == curses.KEY_UP and selected_row == 0 and start_row > 0:
            start_row -= 1
        elif key == ord('q'):
            break
        elif key == 10:  # Enter key
            selected_artist = artists_list[selected_row + start_row]
            artist_name = selected_artist["name"]
            artist_data = load_artist_data(artist_name)
            
            # Create a new curses window to display the artist's data
            artist_data_window = curses.newwin(height, width, 0, 0)
            artist_data_window.clear()
            
            for i, data_item in enumerate(artist_data):
                artist_data_window.addstr(i, 0, data_item)
            
            artist_data_window.refresh()
            artist_data_window.getch()

curses.wrapper(main)
