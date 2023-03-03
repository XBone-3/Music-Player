import os, random, time
import PySimpleGUI as sg
from pygame import mixer, error
from threading import Thread, Event
from mutagen.mp3 import MP3

music_dict = dict()
music_files = list()
path_tracker = list()
play_music = 'Player must be playing a music'
file_list = '-FILE_LIST-'
song_name = 'song name'
start_time = 'start time'
end_time = 'end time'
AUTHOR = 'XBone-3'
GitHub = 'github.com/XBone-3'
thread_event = Event()

def list_music_files(folder_path):
    items = os.listdir(folder_path)
    if folder_path not in music_dict.keys():
        music_dict[folder_path] = []
    for item in items:
        destination = os.path.join(folder_path, item)
        if os.path.isdir(destination):
            list_music_files(destination)
        elif item.lower().endswith(('.mp3')) and (item not in music_files):
            music_files.append(item)
            music_dict[item] = folder_path
            
def button(text):
    return sg.Button(button_text=text, auto_size_button=True, key=text)

def layouts():
    file_list_column = [
        [
            sg.Text('Folder', auto_size_text=True),
            sg.In(key='-PATH-', enable_events=True, size=(25, 1)),
            sg.FolderBrowse(button_text='Browse', auto_size_button=True)
        ],
        [sg.Listbox(values=[], enable_events=True,
                    size=(40, 20), key='-FILE_LIST-')]
    ]
    music_player_column = [
        [sg.Text('Choose a song from the list to play or press start to start a random song',
                 justification='center', auto_size_text=True)],
        [sg.Text('', size=(20, 1), auto_size_text=True,
                 justification='center', key='-TOUT-')],
        [sg.Text('', size=(20, 2), auto_size_text=True,
                 justification='center', key=song_name)],
        [
            sg.Text('00:00', auto_size_text=True, size=(6,1), key=start_time, justification='right'),
            sg.VSeparator(),
            sg.ProgressBar(max_value=1000,
                           size=(20, 10),
                           orientation='h',
                           key='progressbar'
                           ),
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
    layout = [
        [
            sg.Text(text='Search: '),
            sg.In(size=(50, 1), justification='center', key='search', enable_events=True)
        ],
        # [sg.HSeparator()],
        [
            # sg.VSeparator(),
            sg.Column(file_list_column, element_justification='center', vertical_alignment='center'),
            sg.VSeparator(),
            sg.Column(music_player_column, element_justification='center', vertical_alignment='center'),
            # sg.VSeparator()
        ],
        [sg.HSeparator()],
        [
            sg.Button(button_text='Exit', button_color='Black'),
            sg.Text('Made by XBone-3', auto_size_text=True, justification='right', text_color='black', background_color='white', enable_events=True, key=AUTHOR)
        ]
    ]
    return layout

def load_files(window, event, values):
    if event == '-PATH-':
        folder_path = values['-PATH-']
        list_music_files(folder_path)
        music_files.sort()
        window[file_list].update(music_files)
        window['-TOUT-'].update(f'{len(music_files)} songs found')

def search_song(window, event, values):
    if event == 'search':
        search_str = values['search']
        new_list_music_files = [song for song in music_files if search_str.lower() in song.lower()]
        window[file_list].update(new_list_music_files)

def song_mixer(window, song, progress_bar):
    mixer.music.load(os.path.join(music_dict[song], song))
    mixer.music.set_volume(0.5)
    mixer.music.play()
    try:
        song_length = mixer.Sound(os.path.join(music_dict[song], song)).get_length()
    except error:
        song_length = MP3(os.path.join(music_dict[song], song)).info.length
    window[end_time].update(f'{int(song_length // 60)}:{int(song_length % 60)}')
    progress_bar.update(0, int(song_length))
    window[song_name].update(song)
    return music_files.index(song)

def automatic_next(window, current_song_index, shuffle, progress_bar):
    if 0 <= current_song_index < len(music_files) - 1:
        song = music_files[current_song_index]
        if not shuffle:
            next_song = music_files[current_song_index + 1]
        else:
            next_song = random.choice(music_files)
        if int(mixer.music.get_pos() / 1000) == int(MP3(os.path.join(music_dict[song], song)).info.length):
            current_song_index = song_mixer(window, next_song, progress_bar)
    return current_song_index

def pause_play_stop(event):
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
    while True:
        if mixer.music.get_busy():
            progress_bar.UpdateBar(mixer.music.get_pos()/1000)
        if thread_event.is_set():
            break

def volume_setter(event, values):
    if event == 'volume':
        volume = values['volume']
        mixer.music.set_volume(volume/100)

def next_previous(window, event, current_song_index, progress_bar):
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
    if mixer.music.get_busy():
        current_pos = mixer.music.get_pos()
        seconds = int(current_pos / 1000)
        stringify_pos = f'{seconds // 60}:{seconds % 60}'
        window[start_time].update(stringify_pos)

def popup(event):
    if event == AUTHOR:
        sg.popup(f"Made with love by {AUTHOR}\n\nYou can follow me at {GitHub}", title="Author")

def player_loop(window):
    progress_bar = window['progressbar']
    progress_bar_thread = Thread(target=progressbar_update, args=(progress_bar, ), daemon=True)
    progress_bar_thread.start()
    curr_song_index = -1
    while True:
        event, values = window.read(timeout=20)
        shuffle = values['shuffle']
        load_files(window, event, values)
        search_song(window, event, values)
        if event == file_list and len(music_files) > 0:
            song = values[file_list][0]
            curr_song_index = song_mixer(window, song, progress_bar)
            
        volume_setter(event, values)
        pause_play_stop(event)
        update_time(window)
        curr_song_index = next_previous(window, event, curr_song_index, progress_bar)
        curr_song_index = automatic_next(window, curr_song_index, shuffle, progress_bar)
        popup(event)
                
        if event in (sg.WIN_CLOSED, 'Exit'):
            thread_event.set()
            break


if __name__ == '__main__':
    mixer.init()
    sg.theme('Dark')
    layout = layouts()
    window = sg.Window(title='Music Player', layout=layout, location=(400, 100), element_justification='center', resizable=False, finalize=True, auto_size_buttons=True, auto_size_text=True)
    player_loop(window)
    window.close()
