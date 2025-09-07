import json
import sys, os

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

from pyinstaller_resource_path import resource_path

# Load Initial game screen and score file
game_font = 'trebuc.ttf'
    
menu_panel = Entity(
    parent=camera.ui,
    model='quad', scale=(2, 2),
    color=color.black,
    z=1
    )
title_text = Text(
    "You've awakened in a strange, desolate world ― no \nmemories, no allies...just a knife and a handful of bullets. \nSomething's out there. And it's hunting you. \nSurvive. Escape ― if you can.",
    scale=2,
    origin=(0, 0),
    position=(0, 0.3),
    parent=camera.ui,
    font=game_font
)
start_button = Button(
    text='Start Game',
    scale=(0.2, 0.1),
    position=(0, 0),
    parent=camera.ui,
    color=color.green,
    text_color=color.white,
    text_size=1.3,
    highlight_color = color.lime
    )
info_text = Text(
    "Note: If screen is flashing red, it means you are taking damage.\nBe on the alert, the enemy can appear from anywhere.\nPress 'Q' to quit at any time, 'Tab' key to pause/unpause the game and 'Shift' to sprint",
    scale=1.5,
    origin=(0, 0),
    position=(0, -0.3),
    color=color.green,
    font=game_font,
    )
credits = Text(
    "Game Developed By Nigel Chiputura ― Explore more projects at nigelchiputura.dev.",
    scale=1,
    origin=(0, 0),
    position=(0, -0.4),
    color=color.white,
    font=game_font,
    )

game_started = False

def start_game():
    global game_started
    game_started = True
    menu_panel.disable()
    start_button.disable()
    title_text.disable()
    info_text.disable()
    credits.disable()
    player.enable()
    gun.enable()
    knife.enable()
    muzzle_flash.enable()
    wave_label.enable()
    zombie_count_label.enable()
    bullet_count_label.enable()
    player_health_label.enable()
    score_label.enable()
    high_score_label.enable()

start_button.on_click = start_game

def load_high_score():
    with open(resource_path('score/high_score.json')) as f:
        high_score = json.load(f)['high_score']
    return high_score


app = Ursina()
Entity.default_shader = lit_with_shadows_shader
random.seed(0)

# Playlist of songs to play and their song durations in seconds
playlist = {
    'music/Barren Gates - Devil  Trap  NCS - Copyright Free Music.mp3': 176,
    'music/Barren Gates & M.I.M.E - Enslaved  Trap  NCS - Copyright Free Music.mp3': 243,
    'music/Blooom & Ghost\'n\'Ghost - Desire  Trap  NCS - Copyright Free Music.mp3': 184,
    'music/Last Heroes - Dimensions  Melodic Dubstep  NCS - Copyright Free Music.mp3': 231,
    'music/Retro Horror Synth Theme - Sanity Unravels  Royalty Free No Copyright Background Music.mp3': 201,
    'music/Robin Hustin x TobiMorrow - Light It Up (feat. Jex)  Future Bounce  NCS - Copyright Free Music.mp3': 185,
    'music/LXNGVX, Warriyo - Mortals Funk Remix  NCS - Copyright Free Music.mp3': 146,
    'music/Lost Sky - Lost  Trap  NCS - Copyright Free Music.mp3': 157
}

window.fullscreen = True

# Load game music from playlist dictionary
from imports.background_music import *
play_next_song(playlist)

# Load the game variables and flags
from imports.game_variables import *

high_score = load_high_score()

game_over_text = Text(text='GAME OVER!', scale=5, y=0, origin=(0, 0), enabled=False, font=game_font,)
restart_button = Button(text='Play Again', x=0, y=-0.2, scale=(0.2, 0.1), enabled=False)

def update():
    global current_playlist_index, background_music

    wave_label.text = f'Wave: {wave}'
    bullet_count_label.text = f'Bullets: {gun.bullets}'
    zombie_count_label.text = f'Enemies Left: {len(enemies)}'
    player_health_label.text = f'Health: {player.hp}'
    score_label.text = f'Score: {score}'
    high_score_label.text = f'High_Score: {high_score}'
    gun.cooldown()
    muzzle_flash.enabled=False

    if score > high_score:
        with open(resource_path('score/high_score.json'), 'w') as f:
            json.dump({'high_score': score}, f)

    if held_keys['q']:
        sys.exit()
    if held_keys['left mouse'] and gun.bullets and not restart_button.hovered and not start_button.hovered and game_started:
        gun.shoot()
        muzzle_flash.enabled=True
    elif held_keys['left mouse'] and not gun.bullets:
        notification.text = 'No Ammo!\n\nPress F to Malee'
        notification_display()
    if held_keys['right shift'] or held_keys['left shift']:
        player.speed = 15
    else:
        player.speed = 8
    if held_keys['f']:
        knife.stab()
    else:
        knife.default_position()
    if not enemies and game_started:
        spawn_wave()
    if not player.is_alive():
        game_over()

# Load main functions for game logic

def spawn_wave():
    global enemies, wave, cooling_down
    wave += 1
    
    messages = [
        "You've survived the onslaught...\nbut it only gets worse from here.",
        f"Wave {wave - 1} cleared. Take a breath.\nThey're regrouping.",
        "Still alive? Impressive.But the\ndarkness hasn't given up yet.",
        "You're becoming a problem.\nThey're sending stronger ones.",
        f"Rest while you can...\nWave {wave} will test everything.",
        "Temporary calm...but \nsomething bigger is coming.",
    ]

    if wave > 1 and (wave-1) % 5:
        notification.text = f'Wave {wave - 1} complete\n\nPrepare for the next wave'
        notification_display()
        start_cooldown(6)
        
    if wave*3 < max_enemy_number:
        for i in range(wave*3):
            enemy = Enemy(iteration=i, state=True)
            enemies.append(enemy)
    elif not (wave-1) % 5:
        notification.text = random.choice(messages)
        notification_display(5)
        player_reward()
        start_cooldown(15, stronger_enemies=True)
        generate_stronger_enemies()
        enemies = [Enemy(iteration=i, state=True) for i in range(max_enemy_number)]
    else:
        enemies = [Enemy(iteration=i, state=True) for i in range(max_enemy_number)]
        
def pause_input(key):
    if key == 'tab' and game_started:
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        knife.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        pause_label.enabled = editor_camera.enabled
        info_text.color = color.white
        info_text.enabled = editor_camera.enabled
        application.paused = editor_camera.enabled

def deal_enemy_damage(object:Entity, damage_amount:int, volume:int):
    from ursina.prefabs.ursfx import ursfx
    ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=volume, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
    invoke(setattr, object, 'on_cooldown', False, delay=.15)
    if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
        mouse.hovered_entity.blink(color.red)
        mouse.hovered_entity.hp -= damage_amount

def start_cooldown(seconds, stronger_enemies = False):
    global cooling_down, cooldown_timer
    cooling_down = True
    cooldown_timer = seconds
    cooldown_text.enabled = True
    update_cooldown_text()
    invoke(end_cooldown, stronger_enemies, delay=seconds)
    

def update_cooldown_text():
    global cooldown_text, cooldown_timer
    if cooldown_timer > 0:
        cooldown_text.text = f"Next wave in: {cooldown_timer}s"
        cooldown_timer -= 1
        invoke(update_cooldown_text, delay = 1)
    else:
        cooldown_text.text = ""

def end_cooldown(stronger_enemies:bool):
    global cooling_down
    cooling_down = False
    cooldown_text.enabled = False
    if stronger_enemies:
        notification.text = 'Enemies are stronger now!'
        notification_display()

def game_over():
    player.disable()
    game_over_text.enabled = True
    restart_button.enabled = True

def restart():
    global high_score
    
    reset_stats()
    player.enable()
    high_score = load_high_score()
    game_over_text.enabled = False
    restart_button.enabled = False

restart_button.on_click = restart

def reset_stats():
    global wave, score

    player.hp = 100
    player.position = (0, 0)
    gun.bullets = 10
    score = 0
    Enemy.max_hp = 100
    Enemy.speed = 0.8
    Enemy.damage_dealt = 10
    Enemy.bullets_per_kill = 5
    wave = 0
    for enemy in enemies:
        destroy(enemy)
    enemies.clear()

def generate_stronger_enemies():
    Enemy.speed += 0.1
    Enemy.max_hp += 25
    Enemy.damage_dealt += 10

def player_reward():
    gun.bullets += 10
    player.hp += 25
    Enemy.bullets_per_kill += 2

def notification_display(delay_seconds=3):
    global notification
    notification.enabled = True
    invoke(setattr, notification, 'enabled', False, delay=delay_seconds)
    return

def show_damage_flash():
    damage_overlay.color = color.rgba(255, 0, 0, 0.3)
    invoke(hide_damage_flash, delay=0.2)

def hide_damage_flash():
    damage_overlay.color = color.rgba(255, 0, 0, 0)

# Load custom game entities (Player, Gun, etc)

class Player(FirstPersonController):
    """Player class"""
    hp = 100

    def __init__(self):
        FirstPersonController.__init__(
            self,
            origin_y=-.5,
            position=(0, 0),
            speed=8,
            collider='box',
        )

    def is_alive(self):
        if self.hp > 0:
            return True
        return False


class Gun(Entity):
    """Gun class"""
    bullets = 10

    def __init__(self):
        Entity.__init__(
            self,
            parent=camera.ui,
            model='assets/models/AK-47.glb',
            scale=0.2,
            rotation=Vec3(-3, -30, 0),
            position=(0.75, -0.2, 0),
            on_cooldown=False,
            enabled=False
        )

    def shoot(self):            
        # gun_shot.play()
        self.position = (0.8, -0.2, 0)
        self.bullets -= 1
        deal_enemy_damage(self, 25, 0.6)

    def cooldown(self):
        self.position = (0.75, -0.2, 0)


class Knife(Entity):
    """Knife class"""
    def __init__(self):
        Entity.__init__(
            self,
            parent=camera.ui,
            model='assets/models/Knife.obj',
            texture='assets/models/KnifeTexture..jpg',
            rotation=Vec3(10, 189, 0),
            scale=0.15,
            enabled=False
            )

    def stab(self):
        self.position = (-0.5, -0.4, 0)
        for enemy in enemies:
            dist = distance_xz(player.position, enemy.position)
            if dist < 2:
                deal_enemy_damage(self, 10, 0)

    def default_position(self):
        self.position = (-0.5, -0.6, 0)

    
shootables_parent = Entity()
class Enemy(Entity):
    """Enemy class"""
    max_hp = 100
    speed = 0.8
    damage_dealt = 10
    bullets_per_kill = 5
    points_per_kill = 500

    def __init__(self, iteration, state=False, **kwargs):
        super().__init__(
            parent=shootables_parent,
            model='assets/models/zombie.glb',
            collider='box',
            color=color.dark_gray,
            scale=5, rotation=(0, 180, 0),
            x=random.randint(-iteration*4,
            iteration*4),
            z=random.randint(-30,10),
            y=1,
            enabled=state,
            **kwargs
            )
        self.health_bar = Entity(parent=self, y=.5, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.hp = self.max_hp
        self.attack_cooldown = 1
        self.time_since_last_attack = 0

    def update(self):
        self.time_since_last_attack += time.dt

        dist = distance_xz(player.position, self.position)
        self.visible = not cooling_down
        if dist > 1:
            self.position += self.forward * time.dt * (self.speed - 0.5) * int(not cooling_down)
        if dist < 2 and self.time_since_last_attack >= self.attack_cooldown and player.is_alive() and not cooling_down:
            player.hp -= self.damage_dealt
            self.time_since_last_attack = 0
            show_damage_flash()

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 1:
                self.position += self.forward * time.dt * self.speed * int(not cooling_down)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global score
        self._hp = value
        if value <= 0:
            destroy(self)
            enemies.remove(self)
            gun.bullets += self.bullets_per_kill
            score += self.points_per_kill
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1


mouse.traverse_target = shootables_parent
pause_handler = Entity(ignore_paused=True, input=pause_input)
editor_camera = EditorCamera(enabled=False, ignore_paused=True)
damage_overlay = Entity(parent=camera.ui, model='quad', color=color.rgba(255, 0, 0, 0), scale=2, z=-1)

# Load the game scene
ground = Entity(model='plane', collider='box', scale=64, texture='grass', color=color.orange, texture_scale=(4, 4))
wall1 = Entity(model='cube', collider='box', scale=(100, 10, 5), texture='brick', position=(0, 5, 30), color=color.black)
wall2 = duplicate(wall1, z=-30)
wall3 = duplicate(wall1, rotation_y=90, x=-30, z=0)
wall4 = duplicate(wall3, x=30)
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky(color=color.brown)

# Load the main game character
player = Player()
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
player.disable()

# Load the gun model
gun = Gun()
gun.disable()

# Load the knife model
knife = Knife()
knife.disable()

# Simulate gun muzzle flash
muzzle_flash = Entity(parent=camera.ui, color=color.orange, model='quad', scale=0.03, position = (0, 0, 0), z=1, enabled=False)
muzzle_flash.disable()

# Load game UI labels
wave_label = Text(font=game_font,text=f'Wave: {wave}', scale=3, x=0, y=0.5, color=color.yellow, size = 0.02, enabled=False)
zombie_count_label = Text(font=game_font,text=f'Enemies Left: {len(enemies)}', scale=1.5, x=-0.85, y=0.5, color=color.yellow, enabled=False)
bullet_count_label = Text(font=game_font,text=f'Bullets: {gun.bullets}', scale=1.5, x=-0.85, y=-0.45, color=color.yellow, enabled=False)
player_health_label = Text(font=game_font,text=f'Health: {player.hp}', scale=1.5, x=0, y=-0.45, color=color.yellow, enabled=False)
score_label = Text(font=game_font,text=f'Score: {score}', scale=2, x=-0.85, y=0.4, color=color.yellow, enabled=False)
high_score_label = Text(font=game_font,text=f'High_Score: {high_score}', scale=1.5, x=0.4, y=0.5, color=color.yellow, enabled=False)
pause_label = Text(font=game_font,text='GAME PAUSED', scale=5, x=-0.4, y=0, enabled=False)

app.run()