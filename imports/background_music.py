from ursina import *

from pyinstaller_resource_path import resource_path

current_playlist_index = 0

background_music = ''

def play_next_song(playlist:dict, index=0):
    global background_music
    songs = list(playlist.keys())
    duration_times = list(playlist.values())
    if index < len(songs):
        background_music = Audio(songs[index], autoplay=True, volume=0.7)
        invoke(play_next_song, playlist, index + 1, delay=duration_times[index])
    else:
        index = 0
        play_next_song(playlist)
