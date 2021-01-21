import pygame
from engine import load_image, cut_sheet
from config import TILE_SIZE

from random import randint, choice


class Entity(pygame.sprite.Sprite):
    """
    Класс отвечающий за игрока и врагов в игре
    """

    look_directions = {
        (-1, -1): 3,
        (-1, 0): 3,
        (-1, 1): 3,
        (0, -1): 1,
        (0, 0): -1,
        (0, 1): 0,
        (1, -1): 2,
        (1, 0): 2,
        (1, 1): 2
    }

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*args)

        # Изображение
        self.cur_frame = 0
        self.image = self.__class__.frames[0][self.cur_frame]
        self.last_update = pygame.time.get_ticks()
        self.width, self.height = self.image.get_size()

        self.start_posision = x, y
        self.point = None

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Скорость
        self.dx = self.dy = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

    def update(self):
        tick = pygame.time.get_ticks()
        if tick - self.last_update > 100:
            self.last_update = tick
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[look])
            self.image = self.__class__.frames[look][self.cur_frame]


class WalkingMonster(Entity):
    sheet = load_image('player_spritesheet.png')
    columns, rows = 4, 4

    frames = cut_sheet(sheet, columns, rows)

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
                self.point = self.start_posision[0] + choice((-TILE_SIZE * 0.5, TILE_SIZE * 0.5)), \
                             self.start_posision[1] + randint(-TILE_SIZE * 0.5, TILE_SIZE * 0.5)
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 1)
            self.dx = int((point_x - self_x) / part_move)
            self.dy = int((point_y - self_y) / part_move)
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3

        else:
            part_move = max(line / self.speed, 1)
            self.dx = int((point_x - self_x) * 4 / part_move)
            self.dy = int((point_y - self_y) * 4 / part_move)

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
            super().update()


class Ghost(WalkingMonster):
    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.03
        self.visibility_range = TILE_SIZE * 7


def random_monster(x, y, all_sprites, enemies_group):
    return Ghost(x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5, all_sprites, enemies_group)
