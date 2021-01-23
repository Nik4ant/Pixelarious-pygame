import pygame
from engine import load_image, cut_sheet
from config import TILE_SIZE

from random import randint

WAITING_TIME = 2000
UPDATE_TIME = 120
HEALTH_LINE_WIDTH = 4
HEALTH_LINE_TIME = 10000


class Entity(pygame.sprite.Sprite):
    """
    Класс отвечающий за игрока и врагов в игре
    """

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*args)

        # Изображение
        self.cur_frame = 0
        self.image = self.__class__.frames[0][self.cur_frame]
        self.last_update = pygame.time.get_ticks()
        self.width, self.height = self.image.get_size()

        self.last_damage_time = -HEALTH_LINE_TIME

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

    def update(self, n=0):
        tick = pygame.time.get_ticks()
        if tick - self.last_update > UPDATE_TIME:
            self.last_update = tick
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            look += n
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[look])
            self.image = self.__class__.frames[look][self.cur_frame]

    def draw(self, screen):
        if abs(pygame.time.get_ticks() - self.last_damage_time) < HEALTH_LINE_TIME:
            line_width = HEALTH_LINE_WIDTH
            x, y = self.rect.centerx, self.rect.centery
            width, height = self.rect.size
            pygame.draw.rect(screen, 'grey', (x - width * 0.5, y - height * 0.5 - 10, width, line_width))
            health_length = width * self.health / self.full_health
            pygame.draw.rect(screen, 'red', (x - width * 0.5, y - height * 0.5 - 10, health_length, line_width))

    def get_damage(self, damage):
        self.last_damage_time = pygame.time.get_ticks()
        self.health -= damage


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
            if pygame.time.get_ticks() - self.stopping_time < WAITING_TIME:
                super().update(2)
                return
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.stopping_time = pygame.time.get_ticks()
                self.point = self.start_posision[0] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75), \
                             self.start_posision[1] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75)
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
            super().update()


# TODO: Shooting class must be initialized here
class ShootingMonster(Entity):
    pass


class Demon(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 7),) * 2
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
        self.speed = TILE_SIZE * 0.03
        self.visibility_range = TILE_SIZE * 7
        self.health = 40
        self.full_health = 60


class GreenSlime(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 10),) * 2
    frames = cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2, size)

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
        self.health = 80
        self.full_health = self.health


class DirtySlime(WalkingMonster):
    size = (int(TILE_SIZE // 8 * 10),) * 2
    frames = cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2, size)

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
        self.health = 100
        self.full_health = self.health


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
        self.health = 80
        self.full_health = self.health


# TODO: Shooting class must be here
class Wizard(WalkingMonster):
    size = (TILE_SIZE // 8 * 7, ) * 2
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

    def __init__(self, x, y, *args):
        super().__init__(x, y, *args)
        self.speed = TILE_SIZE * 0.025
        self.visibility_range = TILE_SIZE * 5
        self.health = 60
        self.full_health = self.health


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
        self.health = 80
        self.full_health = self.health


class Skeleton(WalkingMonster):
    size = (int(TILE_SIZE * 1), int(TILE_SIZE * 2))
    frames = cut_sheet(load_image('skelet_any.png', 'assets\\enemies'), 4, 4, size)

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
        self.speed = TILE_SIZE * 0.03
        self.visibility_range = TILE_SIZE * 7
        self.health = 150
        self.full_health = self.health


def random_monster(x, y, all_sprites, enemies_group, seed=None):
    n = randint(1, 20)
    args = (x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5,
            all_sprites, enemies_group)

    if n in (1, 2):
        return Demon(*args)
    elif n in (3, 4, 5):
        return GreenSlime(*args)
    elif n in (6,):
        return DirtySlime(*args)
    elif n in (7, 8):
        return Zombie(*args)
    elif n in (9, 10, 11):
        return Wizard(*args)
    elif n in (12,):
        return LongWizard(*args)
    elif n in (13,):
        return Skeleton(*args)

    if seed:
        seed.append(str(n))
