import pgzrun
import math
import random

WIDTH = 1280
HEIGHT = 720
TITLE = "Kodlike"

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"

HERO_IDLE_SPRITES = ["hero_idle_0", "hero_idle_1", "hero_idle_2", "hero_idle_3"]
HERO_MOVE_SPRITES = ["hero_move_0", "hero_move_1", "hero_move_2", "hero_move_3"]
ENEMY_IDLE_SPRITES = ["enemy_idle_0", "enemy_idle_1", "enemy_idle_2", "enemy_idle_3"]
ENEMY_MOVE_SPRITES = ["enemy_move_0", "enemy_move_1", "enemy_move_2", "enemy_move_3"]
BACKGROUND_MUSIC = "background"
FLOOR_TILE_NAME = "floor_tile"
WALL_TILE_NAME = "wall_tile"

TILE_WIDTH, TILE_HEIGHT = 16, 16
TILE_TYPE_FLOOR, TILE_TYPE_WALL = 0, 1
MAP_NUM_COLS, MAP_NUM_ROWS = WIDTH // TILE_WIDTH, HEIGHT // TILE_HEIGHT
INV_SQRT2 = 1 / math.sqrt(2)
NUM_ENEMIES = 5

game_state = GAME_STATE_MENU
music_on = True
hero = None
enemies = []
game_map = []

BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING = 220, 50, 20
menu_button_x = WIDTH // 2 - BUTTON_WIDTH // 2
current_y = HEIGHT // 2 - 80
start_button_rect = Rect(menu_button_x, current_y, BUTTON_WIDTH, BUTTON_HEIGHT)
current_y += BUTTON_HEIGHT + BUTTON_SPACING
music_button_rect = Rect(menu_button_x, current_y, BUTTON_WIDTH, BUTTON_HEIGHT)
current_y += BUTTON_HEIGHT + BUTTON_SPACING
exit_button_rect = Rect(menu_button_x, current_y, BUTTON_WIDTH, BUTTON_HEIGHT)

def play_music_if_on():
    if music_on and not music.is_playing(BACKGROUND_MUSIC):
        try:
            music.play(BACKGROUND_MUSIC)
            music.set_volume(0.15)
        except Exception: pass # Silently ignore music errors

def stop_all_music():
    music.stop()

def generate_map():
    global game_map
    game_map = []
    for r in range(MAP_NUM_ROWS):
        row = []
        for c in range(MAP_NUM_COLS):
            is_wall = (r in (0, MAP_NUM_ROWS - 1) or c in (0, MAP_NUM_COLS - 1) or
                       (5 <= r <= 7 and MAP_NUM_COLS // 2 - 5 < c < MAP_NUM_COLS // 2 + 5) or
                       (MAP_NUM_ROWS // 2 - 3 <= r <= MAP_NUM_ROWS // 2 + 3 and \
                        (c == MAP_NUM_COLS // 4 or c == 3 * MAP_NUM_COLS // 4)) or
                       (r == MAP_NUM_ROWS - 10 and 10 < c < MAP_NUM_COLS - 10))
            row.append(TILE_TYPE_WALL if is_wall else TILE_TYPE_FLOOR)
        game_map.append(row)
    
    center_r, center_c = MAP_NUM_ROWS // 2, MAP_NUM_COLS // 2
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            if 0 <= center_r + dr < MAP_NUM_ROWS and 0 <= center_c + dc < MAP_NUM_COLS:
                game_map[center_r + dr][center_c + dc] = TILE_TYPE_FLOOR

def get_wall_collisions(actor_rect):
    collided = []
    start_c = max(0, int(actor_rect.left / TILE_WIDTH))
    end_c = min(MAP_NUM_COLS - 1, int(actor_rect.right / TILE_WIDTH))
    start_r = max(0, int(actor_rect.top / TILE_HEIGHT))
    end_r = min(MAP_NUM_ROWS - 1, int(actor_rect.bottom / TILE_HEIGHT))
    for r_idx in range(start_r, end_r + 1):
        for c_idx in range(start_c, end_c + 1):
            if game_map[r_idx][c_idx] == TILE_TYPE_WALL:
                wall_r = Rect(c_idx * TILE_WIDTH, r_idx * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
                if actor_rect.colliderect(wall_r):
                    collided.append(wall_r)
    return collided

def find_valid_spawn_location(prefer_center=False):
    for attempt in range(1000):
        r = random.randint(MAP_NUM_ROWS//2 - 5, MAP_NUM_ROWS//2 + 5) if prefer_center and attempt < 20 else random.randint(1, MAP_NUM_ROWS - 2)
        c = random.randint(MAP_NUM_COLS//2 - 5, MAP_NUM_COLS//2 + 5) if prefer_center and attempt < 20 else random.randint(1, MAP_NUM_COLS - 2)
        r, c = max(0, min(r, MAP_NUM_ROWS - 1)), max(0, min(c, MAP_NUM_COLS - 1))
        if game_map[r][c] == TILE_TYPE_FLOOR and all(
            0 <= r + dr < MAP_NUM_ROWS and 0 <= c + dc < MAP_NUM_COLS and \
            game_map[r+dr][c+dc] == TILE_TYPE_FLOOR for dr in range(-1,2) for dc in range(-1,2)):
            return c * TILE_WIDTH + TILE_WIDTH / 2, r * TILE_HEIGHT + TILE_HEIGHT / 2
    return WIDTH / 2, HEIGHT / 2

class Character:
    def __init__(self, sprite_name, pos_x, pos_y, speed, idle_sprites, move_sprites, anchor=('center', 'center')):
        self.actor = Actor(sprite_name, (pos_x, pos_y), anchor=anchor)
        self.speed = speed
        self.idle_sprites, self.move_sprites = idle_sprites, move_sprites
        self.current_sprites, self.sprite_index = self.idle_sprites, 0
        self.animation_timer, self.animation_interval = 0.0, 0.15
        self.is_moving = False

    def update_animation(self, dt):
        if not self.current_sprites: return
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0.0
            self.sprite_index = (self.sprite_index + 1) % len(self.current_sprites)
            self.actor.image = self.current_sprites[self.sprite_index]

    def set_moving_state(self, is_moving_now):
        if self.is_moving != is_moving_now:
            self.is_moving = is_moving_now
            self.current_sprites = self.move_sprites if self.is_moving else self.idle_sprites
            self.sprite_index, self.animation_timer = 0, 0.0
            if self.current_sprites: self.actor.image = self.current_sprites[0]

    def draw(self): self.actor.draw()

    def handle_map_collision(self, move_x_dt, move_y_dt):
        self.actor.x += move_x_dt
        for wall_rect in get_wall_collisions(self.actor):
            if move_x_dt > 0: self.actor.right = wall_rect.left
            elif move_x_dt < 0: self.actor.left = wall_rect.right
        self.actor.y += move_y_dt
        for wall_rect in get_wall_collisions(self.actor):
            if move_y_dt > 0: self.actor.bottom = wall_rect.top
            elif move_y_dt < 0: self.actor.top = wall_rect.bottom

class Enemy(Character):
    def __init__(self, sprite_name, pos_x, pos_y, speed, idle_sprites, move_sprites,
                 detection_radius=250, lose_aggro_radius=400):
        super().__init__(sprite_name, pos_x, pos_y, speed, idle_sprites, move_sprites)
        self.detection_radius, self.lose_aggro_radius = detection_radius, lose_aggro_radius
        self.is_chasing_player = False
        self.patrol_decision_timer = random.uniform(0.0, 1.5)
        self.patrol_decision_interval = random.uniform(1.5, 3.0)
        self.target_dx, self.target_dy = 0, 0

    def update_ai_and_move(self, dt, player_actor):
        if not player_actor:
            self.set_moving_state(False); return
        dx_p, dy_p = player_actor.x - self.actor.x, player_actor.y - self.actor.y
        dist_p = math.hypot(dx_p, dy_p)
        if not self.is_chasing_player and dist_p < self.detection_radius: self.is_chasing_player = True
        elif self.is_chasing_player and dist_p > self.lose_aggro_radius:
            self.is_chasing_player = False; self.target_dx, self.target_dy = 0, 0
        if self.is_chasing_player:
            self.target_dx = (dx_p > 0) - (dx_p < 0) if dist_p > self.actor.width / 2 else 0
            self.target_dy = (dy_p > 0) - (dy_p < 0) if dist_p > self.actor.width / 2 else 0
        else:
            self.patrol_decision_timer += dt
            if self.patrol_decision_timer >= self.patrol_decision_interval:
                self.patrol_decision_timer = 0.0
                self.patrol_decision_interval = random.uniform(2.0, 4.0)
                if random.random() < 0.3: self.target_dx, self.target_dy = 0, 0
                else:
                    self.target_dx, self.target_dy = random.choice([-1,0,1]), random.choice([-1,0,1])
                    if self.target_dx == 0 and self.target_dy == 0:
                        if random.random() < 0.5: self.target_dx = random.choice([-1,1])
                        else: self.target_dy = random.choice([-1,1])
        mx, my = self.target_dx * self.speed, self.target_dy * self.speed
        if self.target_dx != 0 and self.target_dy != 0: mx *= INV_SQRT2; my *= INV_SQRT2
        self.handle_map_collision(mx * dt, my * dt)
        self.set_moving_state(self.target_dx != 0 or self.target_dy != 0)

def initialize_game_elements():
    global hero, enemies, game_state
    generate_map()
    hero_spawn_x, hero_spawn_y = find_valid_spawn_location(prefer_center=True)
    hero = Character(HERO_IDLE_SPRITES[0], hero_spawn_x, hero_spawn_y, 200, HERO_IDLE_SPRITES, HERO_MOVE_SPRITES)
    enemies = []
    for _ in range(NUM_ENEMIES):
        ex, ey = find_valid_spawn_location()
        enemies.append(Enemy(ENEMY_IDLE_SPRITES[0], ex, ey, random.randint(70,110),
                             ENEMY_IDLE_SPRITES, ENEMY_MOVE_SPRITES,
                             detection_radius=random.randint(150,220),
                             lose_aggro_radius=random.randint(250,350)))
    play_music_if_on()
    game_state = GAME_STATE_PLAYING

def draw_map_tiles():
    for r in range(MAP_NUM_ROWS):
        for c in range(MAP_NUM_COLS):
            screen.blit(FLOOR_TILE_NAME, (c * TILE_WIDTH, r * TILE_HEIGHT))
            if game_map[r][c] == TILE_TYPE_WALL:
                screen.blit(WALL_TILE_NAME, (c * TILE_WIDTH, r * TILE_HEIGHT))

def draw_menu():
    screen.fill((20, 20, 80))
    screen.draw.text(TITLE, center=(WIDTH / 2, HEIGHT / 4), fontsize=60, color="yellow", owidth=1, ocolor="black")
    screen.draw.filled_rect(start_button_rect, "green")
    screen.draw.text("Iniciar Jogo", center=start_button_rect.center, fontsize=32, color="white", owidth=0.5, ocolor="black")
    music_text = f"Musica: {'ON' if music_on else 'OFF'}"
    screen.draw.filled_rect(music_button_rect, "orange" if music_on else "gray")
    screen.draw.text(music_text, center=music_button_rect.center, fontsize=32, color="black")
    screen.draw.filled_rect(exit_button_rect, "darkred")
    screen.draw.text("Sair", center=exit_button_rect.center, fontsize=32, color="white", owidth=0.5, ocolor="black")

def draw_game_over():
    screen.fill("black")
    screen.draw.text("FIM DE JOGO", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=70, color="red", owidth=1, ocolor="darkred")
    screen.draw.text("Clique para o Menu", center=(WIDTH / 2, HEIGHT / 2 + 40), fontsize=35, color="white")

def draw_playing_state():
    draw_map_tiles()
    if hero: hero.draw()
    for enemy in enemies: enemy.draw()

def draw():
    screen.clear()
    if game_state == GAME_STATE_MENU: draw_menu()
    elif game_state == GAME_STATE_PLAYING: draw_playing_state()
    elif game_state == GAME_STATE_GAME_OVER: draw_game_over()

def update_hero_movement(dt):
    if not hero: return
    hero_dx = (keyboard.right or keyboard.d) - (keyboard.left or keyboard.a)
    hero_dy = (keyboard.down or keyboard.s) - (keyboard.up or keyboard.w)
    mx, my = hero_dx * hero.speed, hero_dy * hero.speed
    if hero_dx != 0 and hero_dy != 0: mx *= INV_SQRT2; my *= INV_SQRT2
    hero.handle_map_collision(mx * dt, my * dt)
    hero.set_moving_state(hero_dx != 0 or hero_dy != 0)
    hero.update_animation(dt)

def update_playing_state(dt):
    global game_state
    if not hero: game_state = GAME_STATE_MENU; return
    update_hero_movement(dt)
    for enemy in enemies:
        enemy.update_ai_and_move(dt, hero.actor)
        enemy.update_animation(dt)
        if hero.actor.colliderect(enemy.actor):
            game_state = GAME_STATE_GAME_OVER
            if music_on: music.fadeout(1.0)
            break

def update(dt):
    if game_state == GAME_STATE_PLAYING: update_playing_state(dt)
    elif game_state == GAME_STATE_MENU: play_music_if_on()

def on_mouse_down(pos, button):
    global game_state, music_on
    if button == mouse.LEFT:
        if game_state == GAME_STATE_MENU:
            if start_button_rect.collidepoint(pos): initialize_game_elements()
            elif music_button_rect.collidepoint(pos):
                music_on = not music_on
                if music_on: play_music_if_on()
                else: stop_all_music()
            elif exit_button_rect.collidepoint(pos): exit()
        elif game_state == GAME_STATE_GAME_OVER:
            game_state = GAME_STATE_MENU
            play_music_if_on()
pgzrun.go()