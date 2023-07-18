# XBone-3
import os, random
import PySimpleGUI as sg
from pygame import mixer, error
from threading import Thread, Event
from mutagen.mp3 import MP3
from typing import List


thread_event = Event()
music_dict = dict()
music_files = list()
file_list = '-FILE_LIST-'
song_name = 'song name'
start_time = 'start time'
end_time = 'end time'
AUTHOR = 'M.Nagendra'
GitHub = 'github.com/XBone-3'



def list_music_files(folder_path: str, music_files: List[str], music_dict: dict):
    """
    Recursively lists all music files in a given folder and updates the provided 'music_files' list and 'music_dict' dictionary with the found files.

    Parameters:
        folder_path (str): The path of the folder to search for music files.
        music_files (List[str]): The list to store the names of the music files.
        music_dict (dict): The dictionary to store the mapping of music file names to their respective folder paths.

    Returns:
        None
    """
    for item in os.listdir(folder_path):
        destination = os.path.join(folder_path, item)
        if os.path.isdir(destination):
            list_music_files(destination, music_files, music_dict)
        elif item.lower().endswith(('.mp3', '.wav', '.ogg', '.aac')) and (item not in music_files):
            music_files.append(item)
            music_dict[item] = folder_path
            
def button(text):
    """
        Creates a button with the specified text.

        Parameters:
            text (str): The text to be displayed on the button.

        Returns:
            sg.Button: The created button.
    """
    return sg.Button(button_text=text, auto_size_button=True, key=text)

def layouts(name):
    """
    Generate the function comment for the given function body in a markdown code block with the correct language syntax.
    """
    file_list_layout = [
        [
            sg.Text('Folder', auto_size_text=True),
            sg.In(key='-PATH-', enable_events=True, size=(25, 1)),
            sg.FolderBrowse(button_text='Browse', auto_size_button=True)
        ],
        [sg.Listbox(values=[], enable_events=True,
                    size=(50, 20), key='-FILE_LIST-')]
    ]
    music_controls_layout = [
        [sg.Text('Choose a song from the list to play',
                 justification='center', auto_size_text=True)],
        [sg.Text('', size=(20, 1), auto_size_text=True,
                 justification='center', key='-TOUT-')],
        [sg.Text('', size=(20, 2), auto_size_text=True,
                 justification='center', key=song_name)],
        [
            sg.Text('00:00', auto_size_text=True, size=(6,1), key=start_time, justification='right'),
            sg.VSeparator(),
            sg.ProgressBar(max_value=1000,
                           size=(20, 5),
                           orientation='h',
                           key='progressbar'),
            sg.VSeparator(),
            sg.Text('00:00', auto_size_text=True, size=(6,1), key=end_time, justification='left')
        ],
        [sg.HSeparator(pad=10)],
        [
            button('Previous'),
            button('Pause'),
            button('Play'),
            button('Stop'),
            button('Restart'),
            button('Next')
        ],
        [
            sg.Checkbox(text='Repeat', key='repeat', enable_events=True),
            sg.Slider(range=(0, 100), default_value=50, resolution=1, enable_events=True, orientation='h', key='volume'),
            sg.Checkbox(text="Random", key='shuffle', enable_events=True)
        ]

    ]
    if name == 'vertical_layout':
        vertical_layout = [
            [sg.Text(text='MP3 Player', auto_size_text=True, font=("Helvetica", 19), justification='center')],
            [
                sg.In(default_text='Search', size=(50, 1), justification='center', key='search', enable_events=True)
            ],
            [file_list_layout],
            [sg.HSeparator()],
            [music_controls_layout],
            [sg.HSeparator()],
            [
                sg.Text('Description', auto_size_text=True, justification='center', text_color='black', background_color='white', enable_events=True, key='disc'),
                sg.Button(button_text='Exit', button_color='Black'),
                sg.Text(f'Made by {AUTHOR}', auto_size_text=True, justification='center', text_color='black', background_color='white', enable_events=True, key=AUTHOR)
            ]
        ]
        return vertical_layout
    elif name == 'horizontal_layout':
        horizontal_layout = [
            [sg.Text(text='MP3 Player', auto_size_text=True, font=("Helvetica", 19), justification='center')],
            [
                sg.Text(text='Search: '),
                sg.In(size=(50, 1), justification='center', key='search', enable_events=True)
            ],
            [
                sg.Column(file_list_layout, element_justification='center', vertical_alignment='center'),
                sg.VSeparator(),
                sg.Column(music_controls_layout, element_justification='center', vertical_alignment='center'),
            ],
            [sg.HSeparator()],
            [
                sg.Text('Description', auto_size_text=True, justification='center', text_color='black', background_color='white', enable_events=True, key='disc'),
                sg.Button(button_text='Exit', button_color='Black'),
                sg.Text(f'Made by {AUTHOR}', auto_size_text=True, justification='center', text_color='black', background_color='white', enable_events=True, key=AUTHOR)
            ]
        ]
        return horizontal_layout

def load_files(window, event, values):
    """
    Load files into the application based on the specified folder path.
    
    Parameters:
    - window: The window object representing the application window.
    - event: The event that triggered the function call.
    - values: The values associated with the event.
    
    Returns:
    None
    """
    if event == '-PATH-':
        folder_path = values['-PATH-']
        list_music_files(folder_path, music_files, music_dict)
        music_files.sort()
        window[file_list].update(music_files)
        window['-TOUT-'].update(f'{len(music_files)} songs found')

def search_song(window, event, values):
    """
    Perform a search for a song based on the given search string.

    Parameters:
    - window: The window object representing the GUI window.
    - event: The event that triggered the search.
    - values: The values dictionary containing the current state of the GUI.

    Returns:
    None
    """
    if event == 'search':
        search_str = values['search']
        new_list_music_files = [song for song in music_files if search_str.lower() in song.lower()]
        window[file_list].update(new_list_music_files)

def time_formatter(time_in_seconds):
    """
    Formats a given time in seconds into minutes and seconds.

    Parameters:
        time_in_seconds (int): The time in seconds to be formatted.

    Returns:
        tuple: A tuple containing the formatted minutes and seconds.
    """
    minutes = time_in_seconds // 60
    seconds = time_in_seconds % 60
    if minutes < 10:
        minutes = f'0{minutes}'
    if seconds < 10:
        seconds = f'0{seconds}'
    return minutes, seconds

def song_mixer(window, song, progress_bar):
    """
    Mixer function that plays a song, updates the progress bar, and returns the index of the song in the music files.

    Parameters:
        window (object): The window object representing the GUI window.
        song (str): The name of the song to be played.
        progress_bar (object): The progress bar object representing the progress bar in the GUI.

    Returns:
        int: The index of the song in the music files.

    """
    mixer.music.unload()
    mixer.music.load(os.path.join(music_dict[song], song))
    mixer.music.set_volume(0.5)
    mixer.music.play()
    try:
        song_length = int(mixer.Sound(os.path.join(music_dict[song], song)).get_length())
    except error:
        song_length = int(MP3(os.path.join(music_dict[song], song)).info.length)
    minutes, seconds = time_formatter(song_length)
    window[end_time].update(f'{minutes}:{seconds}')
    progress_bar.update(0, int(song_length))
    window[song_name].update(song)
    return music_files.index(song)

def automatic_next(window, current_song_index, shuffle, repeat, progress_bar):
    """
    Automatically selects the next song in the playlist based on the current song index and other settings.

    Parameters:
        window (Window): The main window of the music player.
        current_song_index (int): The index of the current song in the playlist.
        shuffle (bool): Flag indicating whether the songs should be played in random order.
        repeat (bool): Flag indicating whether the playlist should be repeated after reaching the end.
        progress_bar (ProgressBar): The progress bar widget displaying the current song's progress.

    Returns:
        int: The index of the next song in the playlist.
    """
    if 0 <= current_song_index < len(music_files):
        song = music_files[current_song_index]
        length_song_in_seconds = int(MP3(os.path.join(music_dict[song], song)).info.length)
        new_song_index = current_song_index
        if (int(mixer.music.get_pos() / 1000) >= length_song_in_seconds - 1):
            new_song_index = current_song_index + 1
        if not shuffle:
            if repeat and new_song_index == len(music_files):
                new_song_index = 0
            elif not repeat and new_song_index == len(music_files):
                mixer.music.stop()
                return current_song_index
            next_song = music_files[new_song_index]
        else:
            next_song = random.choice(music_files)
        if int(mixer.music.get_pos() / 1000) >= length_song_in_seconds - 1:
            return song_mixer(window, next_song, progress_bar)
    return current_song_index

def pause_play_stop(event):
    """
    Pause, play, stop, or restart the music based on the given event.

    Parameters:
    - event (str): The event to perform. Valid values are 'Pause', 'Play', 'Stop', and 'Restart'.

    Returns:
    - None
    """
    if event == 'Pause' and mixer.music.get_busy():
            mixer.music.pause()

    if event == 'Play':        
        mixer.music.unpause()

    if event == 'Stop' and mixer.music.get_busy():
        mixer.music.stop()
    
    if event == 'Restart':
        try:
            mixer.music.play()
        except error:
            pass

def progressbar_update(progress_bar):
    """
    Update the progress bar based on the current position of the music playing.

    Parameters:
    - progress_bar (ProgressBar): The progress bar object to be updated.

    Returns:
    - None
    """
    while True:
        if mixer.music.get_busy():
            progress_bar.UpdateBar(mixer.music.get_pos()/1000)
        if thread_event.is_set():
            break

def volume_setter(event, values):
    """
    Sets the volume of the music player.

    Parameters:
        event (str): The name of the event that triggered the function.
        values (dict): A dictionary containing the values of different controls in the GUI.

    Returns:
        None
    """
    if event == 'volume':
        volume = values['volume']
        mixer.music.set_volume(volume/100)

def next_previous(window, event, current_song_index, progress_bar):
    """
    Given a window object, an event, the current song index, and a progress bar, 
    this function determines the next or previous song index based on the event. 
    If the event is 'Next' and there are music files available, the function 
    increments the current song index and returns it. If the event is 'Previous' 
    and there are music files available, the function decrements the current song 
    index and returns it. If the event is neither 'Next' nor 'Previous', the 
    function returns the current song index.

    :param window: The window object.
    :type window: object
    :param event: The event triggering the function.
    :type event: str
    :param current_song_index: The index of the current song.
    :type current_song_index: int
    :param progress_bar: The progress bar object.
    :type progress_bar: object
    :return: The updated current song index after processing the event.
    :rtype: int
    """
    if event == 'Next' and len(music_files) > 0:
        if current_song_index >= len(music_files) - 1:
            current_song_index = -1
        song = music_files[current_song_index + 1]
        current_song_index = song_mixer(window, song, progress_bar)
        return current_song_index
    if event == 'Previous' and len(music_files) > 0:
        if current_song_index <= 0:
            current_song_index = len(music_files)
        song = music_files[current_song_index - 1]
        current_song_index = song_mixer(window, song, progress_bar)
        return current_song_index
    return current_song_index

def update_time(window):
    """
    Update the time in the specified window.

    Parameters:
        window (Window): The window object to update the time in.

    Returns:
        None
    """
    if mixer.music.get_busy():
        current_pos = mixer.music.get_pos()
        position_in_seconds = int(current_pos / 1000)
        minutes, seconds = time_formatter(position_in_seconds)
        stringify_pos = f'{minutes}:{seconds}'
        window[start_time].update(stringify_pos)

def popup(event):
    """
    Displays a popup window based on the given event.

    Parameters:
        event (str): The event that triggers the popup. Can be 'AUTHOR' or 'disc'.

    Returns:
        None
    """
    if event == AUTHOR:
        sg.popup(f"Made with love by {AUTHOR}\n\nYou can follow me at {GitHub}", title="Author")
    if event == 'disc':
        sg.popup('explanation of each element not updated still.')

def player_loop(window):
    """
    The player loop function is responsible for continuously running the main loop of the player.
    It takes in a window object as a parameter.

    Parameters:
    - window: The window object representing the player's user interface.

    Returns:
    - None

    This function initializes a progress bar and starts a separate thread to update the progress bar.
    It then enters into an infinite loop, continuously reading events from the window.
    The loop breaks if the window is closed or the 'Exit' event is triggered.
    Within the loop, it performs various operations based on the received event and values.
    It handles events related to file loading, song searching, volume setting, pause/play/stop actions,
    updating the time display, navigating to next/previous songs, and automatic song switching.
    The function also handles pop-up events.
    """
    progress_bar = window['progressbar']
    progress_bar_thread = Thread(target=progressbar_update, args=(progress_bar, ), daemon=True)
    progress_bar_thread.start()
    curr_song_index = -1
    while True:
        event, values = window.read(timeout=20)
        if event in (sg.WIN_CLOSED, 'Exit'):
            thread_event.set()
            break
        shuffle, repeat = values['shuffle'], values['repeat']
        load_files(window, event, values)
        search_song(window, event, values)
        if event == file_list and len(music_files) > 0:
            song = values[file_list][0]
            curr_song_index = song_mixer(window, song, progress_bar)
            
        volume_setter(event, values)
        pause_play_stop(event)
        update_time(window)
        curr_song_index = next_previous(window, event, curr_song_index, progress_bar)
        curr_song_index = automatic_next(window, curr_song_index, shuffle, repeat, progress_bar)
        popup(event)


if __name__ == '__main__':
    mixer.init()
    sg.theme('Dark')
    layout = layouts('vertical_layout')
    window = sg.Window(title='Music Player V-1.0', layout=layout, location=(400, 100), element_justification='center', resizable=False, finalize=True, auto_size_buttons=True, auto_size_text=True)
    player_loop(window)
    window.close()
