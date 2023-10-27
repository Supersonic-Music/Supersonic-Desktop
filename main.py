import json
import curses

MUSIC_DIR = "/home/deck/Music"
CAL_DIR = ".cal_sonic_library"

with open(f"{MUSIC_DIR}/{CAL_DIR}/meta/artists.json", "r") as file:
    artists_list = json.load(file)

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

curses.wrapper(main)
