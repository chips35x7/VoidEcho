from ursina import *
from pyinstaller_resource_path import resource_path

game_font = 'assets/fonts/trebuc.ttf'

wave = 0
enemies = []
max_enemy_number = 15
cooling_down = False
cooldown_timer = 0
cooldown_text = Text('', position=(0, 0.2), origin=(0,0), scale=2, font=game_font)
notification = Text(
        text='',
        scale=3,
        x=-0.2, y=0,
        enabled=False,
        color=color.yellow,
        size = 0.02
    )
score = 0