from random import randint

import pygame

from entities.base_entity import Entity
from engine import load_image, cut_sheet
from config import TILE_SIZE


class WalkingMonster(Entity):
    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(x, y, *args)

        # Значения по-умолчанию
        self.speed = TILE_SIZE * 0.03
        self.visibility_range = TILE_SIZE * 7
        self.stopping_time = pygame.time.get_ticks() + randint(-750, 750)

    def update(self, player=None):
        if not player:
            return

        self_x, self_y = self.rect.centerx, self.rect.centery

        point_x, point_y = player.rect.centerx, player.rect.centery
        # Расстояние между врагом и игроком
        line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range:
            if pygame.time.get_ticks() - self.stopping_time < Entity.WAITING_TIME:
                super().update(2)
                return
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.stopping_time = pygame.time.get_ticks()
                self.point = self.start_position[0] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75), \
                             self.start_position[1] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75)
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3

        else:
            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) * 4 / part_move
            self.dy = (point_y - self_y) * 4 / part_move

        # Перемещение сущности относительно центра
        self.rect.centerx = self.rect.centerx + self.dx
        self.rect.centery = self.rect.centery + self.dy

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

        if self.dx or self.dy:
            self.update_frame_state()


# TODO: Shooting class must be initialized here
class ShootingMonster(Entity):
    pass


class Demon(WalkingMonster):
    frames = cut_sheet(load_image('demon_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('demon_idle.png', 'assets\\enemies'), 4, 2)

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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.025
        self.visibility_range = TILE_SIZE * 7


class GreenSlime(WalkingMonster):
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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5


class DirtySlime(WalkingMonster):
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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5


class Zombie(WalkingMonster):
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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.025
        self.visibility_range = TILE_SIZE * 5


# TODO: Shooting class must be here
class Wizard(WalkingMonster):
    frames = cut_sheet(load_image('wizard_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('wizard_idle.png', 'assets\\enemies'), 4, 2)

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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.022
        self.visibility_range = TILE_SIZE * 5


# TODO: Shooting class must be here
class LongWizard(WalkingMonster):
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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.025
        self.visibility_range = TILE_SIZE * 5


class Skeleton(WalkingMonster):
    size = (int(TILE_SIZE * 1.5),) * 2
    frames = cut_sheet(load_image('skelet.png', 'assets\\enemies'), 4, 4, size)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 1,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.028
        self.visibility_range = TILE_SIZE * 7


def random_monster(x, y, all_sprites, enemies_group, seed=None):
    n = randint(1, 7)
    args = (x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5,
            all_sprites, enemies_group)
    if n == 1:
        return Demon(*args)
    elif n == 2:
        return GreenSlime(*args)
    elif n == 3:
        return DirtySlime(*args)
    elif n == 4:
        return Zombie(*args)
    elif n == 5:
        return Wizard(*args)
    elif n == 6:
        return LongWizard(*args)
    elif n == 7:
        return Skeleton(*args)
    if seed:
        seed.append(str(n))
