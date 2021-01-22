from random import randint, choice

import pygame

from engine import load_image, cut_sheet
from entities.base_entity import Entity
from config import TILE_SIZE


class WalkingMonster(Entity):
    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(x, y, *args)

        # Значения по-умолчанию
        self.speed = TILE_SIZE * 0.03
        self.visibility_range = TILE_SIZE * 7

    def update(self, player=None):
        if not player:
            return

        self_x, self_y = self.rect.centerx, self.rect.centery

        point_x, point_y = player.rect.centerx, player.rect.centery
        # Расстояние между врагом и игроком
        line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range:
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.point = self.start_position[0] + choice((-TILE_SIZE * 0.5, TILE_SIZE * 0.5)), \
                             self.start_position[1] + randint(-TILE_SIZE * 0.5, TILE_SIZE * 0.5)
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) / part_move
            self.dy = (point_y - self_y) / part_move
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3
        else:
            part_move = max(line / self.speed, 10)
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


class Demon(WalkingMonster):
    frames = cut_sheet(load_image('demon_run.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0):  1,
        (-1, 1):  1,
        (0, -1):  1,
        (0, 0):   2,
        (0, 1):   0,
        (1, -1):  0,
        (1, 0):   0,
        (1, 1):   0
    }

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.022
        self.visibility_range = TILE_SIZE * 7


class GreenSlime(WalkingMonster):
    frames = cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2)

    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 2,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.02
        self.visibility_range = TILE_SIZE * 5


def random_monster(x, y, all_sprites, enemies_group):
    n = randint(1, 2)
    args = (x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5,
            all_sprites, enemies_group)
    if n == 1:
        return Demon(*args)
    elif n == 2:
        return GreenSlime(*args)
