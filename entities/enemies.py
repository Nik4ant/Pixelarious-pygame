from random import randint

import pygame

from entities.base_entity import Entity
from engine import load_image, cut_sheet, concat_two_file_paths
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME


class WalkingMonster(Entity):
    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(x, y, *args)

        self.player_observed = False

        # Значения по-умолчанию
        self.speed = TILE_SIZE * 0.016
        self.visibility_range = TILE_SIZE * 6
        self.stopping_time = pygame.time.get_ticks() + randint(-750, 750)

    def update(self, player=None):
        if not player:
            return

        self_x, self_y = self.rect.centerx, self.rect.centery
        previous_pos = (self_x, self_y)
        delta = 0

        point_x, point_y = player.rect.centerx, player.rect.centery
        # Расстояние между врагом и игроком
        self.distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
        line = self.distance_to_player

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range:
            if pygame.time.get_ticks() - self.stopping_time < Entity.WAITING_TIME:
                super().update_frame_state(2)
                return
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.stopping_time = pygame.time.get_ticks()
                self.point = (self.start_position[0] + randint(-TILE_SIZE * 1, TILE_SIZE * 1),
                              self.start_position[1] + randint(-TILE_SIZE * 1, TILE_SIZE * 1))
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3
            self.player_observed = False

        else:
            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) * 4 / part_move
            self.dy = (point_y - self_y) * 4 / part_move
            self.player_observed = True

        self.move(Entity.collisions_group, self.dx, self.dy)

        if self.dx > 0:
            self.look_direction_x = 1
        elif self.dx < 0:
            self.look_direction_x = -1
        else:
            self.look_direction_x = 0
        if self.dy > 0:
            self.look_direction_y = 1
        elif self.dy < 0:
            self.look_direction_y = -1
        else:
            self.look_direction_y = 0

        if previous_pos == (self.rect.centerx, self.rect.centery):
            delta = 2
            self.point = None
            self.stopping_time = pygame.time.get_ticks()

        if self.dx or self.dy:
            super().update_frame_state(delta)


class ShootingMonster(Entity):
    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(x, y, *args)

        # Значения по-умолчанию
        self.speed = TILE_SIZE * 0.012
        self.visibility_range = TILE_SIZE * 13
        self.close_range = TILE_SIZE * 5

        self.player_observed = False

        self.last_shot = pygame.time.get_ticks()
        self.reload_time = 3000

        self.stopping_time = pygame.time.get_ticks() + randint(-750, 750)

    def update(self, player=None):
        if not player:
            return

        self_x, self_y = self.rect.centerx, self.rect.centery
        previous_pos = self_x, self_y
        delta = 0

        point_x, point_y = player.rect.centerx, player.rect.centery
        # Расстояние между врагом и игроком
        self.distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
        line = self.distance_to_player

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range:
            if pygame.time.get_ticks() - self.stopping_time < Entity.WAITING_TIME:
                super().update_frame_state(2)
                return
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.stopping_time = pygame.time.get_ticks()
                self.point = (self.start_position[0] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75),
                              self.start_position[1] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75))
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3
            self.player_observed = False

        elif line <= self.close_range:
            part_move = max(line / self.speed, 1)
            self.dx = -(point_x - self_x) * 4 / part_move
            self.dy = -(point_y - self_y) * 4 / part_move
            self.player_observed = True

        elif line >= self.visibility_range - 2 * TILE_SIZE:
            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) * 4 / part_move
            self.dy = (point_y - self_y) * 4 / part_move

        else:
            self.dx = self.dy = 0
            self.player_observed = True

        self.move(Entity.collisions_group, self.dx, self.dy)

        if previous_pos == (self.rect.centerx, self.rect.centery):
            delta = 2
            if pygame.time.get_ticks() - self.last_shot < self.reload_time:
                self.shoot(player)

        if self.dx > 0:
            self.look_direction_x = 1
        elif self.dx < 0:
            self.look_direction_x = -1
        else:
            self.look_direction_x = 0
        if self.dy > 0:
            self.look_direction_y = 1
        elif self.dy < 0:
            self.look_direction_y = -1
        else:
            self.look_direction_y = 0

        super().update_frame_state(delta)

    def shoot(self, player):
        pass


class Demon(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 5),) * 2
    frames = cut_sheet(load_image('demon_run.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('demon_idle.png', 'assets\\enemies'), 4, 2, size)

    UPDATE_TIME = 60

    look_directions = {
        (-1, -1): 1,
        (-1, 0):  1,
        (-1, 1):  1,
        (0, -1):  1,
        (0, 0):   0,
        (0, 1):   0,
        (1, -1):  0,
        (1, 0):   0,
        (1, 1):   0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "little_steps.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.023
        self.visibility_range = TILE_SIZE * 7

        self.health = 40
        self.full_health = self.health


class GreenSlime(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 7),) * 2
    frames = cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(4)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "slime_sound.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5

        self.health = 80
        self.full_health = self.health


class DirtySlime(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 7),) * 2
    frames = cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(5)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "slime_sound_1.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5

        self.health = 100
        self.full_health = self.health


class Zombie(WalkingMonster):
    size = (int(TILE_SIZE // 4 * 3),) * 2
    frames = cut_sheet(load_image('zombie_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('zombie_idle.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(6)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "stone_steps_1.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5

        self.health = 80
        self.full_health = self.health


class Wizard(ShootingMonster):
    size = (TILE_SIZE // 8 * 7,) * 2
    frames = cut_sheet(load_image('wizard_run.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('wizard_idle.png', 'assets\\enemies'), 4, 2, size)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(7)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "wizard_rustle.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.022
        self.visibility_range = TILE_SIZE * 9

        self.health = 60
        self.full_health = self.health


class LongWizard(ShootingMonster):
    size = (int(TILE_SIZE // 8 * 7),) * 2
    frames = cut_sheet(load_image('long_wizard_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('long_wizard_idle.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(2)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/enemies/audio", "wizard_rustle.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)

        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 13

        self.health = 80
        self.full_health = self.health

        self.reload_time = 5000


def random_monster(x, y, all_sprites, enemies_group, seed, user_seed=None):
    if user_seed:
        n = int(user_seed[0])
        del user_seed[0]
    else:
        n = randint(1, 20)
    seed.append(str(n))
    args = (x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5,
            all_sprites, enemies_group)

    if n in (1, 2):
        monster = Demon(*args)
    elif n in (3, 4, 5):
        monster = GreenSlime(*args)
    elif n in (6,):
        monster = DirtySlime(*args)
    elif n in (7, 8):
        monster = Zombie(*args)
    elif n in (9, 10, 11):
        monster = Wizard(*args)
    elif n in (12,):
        monster = LongWizard(*args)
    else:
        return None
    monster.index_in_seed = len(seed) - 1
    return monster
