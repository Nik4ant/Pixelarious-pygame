from math import *
from random import randint

import pygame

from engine import load_image, cut_sheet
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME

from entities.base_entity import Collider


class Spell(pygame.sprite.Sprite):
    """
    Класс, отвечающий за предстовление базового заклинания в игре
    """
    FIRE = 'fire'
    FLASH = 'flash'
    ICE = 'ice'
    POISON = 'poison'
    VOID = 'void'

    UPDATE_TIME = 30
    frames = []
    damage = 40
    damage_frame = 0

    start_position = None

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(*groups)

        self.point = (object_x, object_y)
        dx = object_x - subject_x
        dy = object_y - subject_y
        if dx >= 0:
            self.angle = -degrees(atan(dy / max(dx, 0.00001)))
        else:
            self.angle = 180 - degrees(atan(dy / min(dx, -0.00001)))

        self.object_group = object_group
        self.cur_frame = 0
        self.cur_list = 0
        self.last_update_time = pygame.time.get_ticks()

        self.frames = [[pygame.transform.rotate(i, self.angle) for i in self.__class__.frames[0]],
                       self.__class__.frames[1]]

        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = subject_x, subject_y

        self.collider = Collider(self.rect.centerx, self.rect.centery)

        self.update()

    def update(self) -> None:
        ticks = pygame.time.get_ticks()
        if ticks - self.last_update_time < self.UPDATE_TIME:
            return
        self.speed *= 1.05
        self.last_update_time = ticks

        if (self.rect.centerx, self.rect.centery) == self.point:
            if self.cur_frame == self.damage_frame:
                self.collider.update(self.rect.centerx, self.rect.centery)
                for obj in pygame.sprite.spritecollide(self.collider, self.object_group, False):
                    obj.get_damage(self.damage)
            self.cur_frame += 1
            if self.cur_frame == len(self.__class__.frames[self.cur_list]):
                self.kill()
                return
            self.image = self.__class__.frames[self.cur_list][self.cur_frame]

        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[0])

            self_x, self_y = self.rect.centerx, self.rect.centery
            point_x, point_y = self.point
            distance_to_object = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
            part_move = max(distance_to_object / self.speed, 0.5)
            dx = round((point_x - self_x) / part_move)
            dy = round((point_y - self_y) / part_move)
            self.rect.x = self.rect.x + dx
            self.rect.y = self.rect.y + dy

            self.collider.update(self.rect.centerx, self.rect.centery)
            if pygame.sprite.spritecollideany(self.collider, self.object_group) and self.spell_type != Spell.FLASH:
                self.point = (self.rect.centerx, self.rect.centery)

            self.image = self.frames[0][self.cur_frame]

            if (self.rect.centerx, self.rect.centery) == self.point:
                self.cur_frame = 0
                self.cur_list = randint(1, len(self.__class__.frames) - 1)


class IceSpell(Spell):
    damage = 30
    spell_type = Spell.ICE
    UPDATE_TIME = 50
    speed = TILE_SIZE * 0.2

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('ice_laser.png', 'assets\\spells'), 30, 1, size)
    frames += cut_sheet(load_image('ice_explosion.png', 'assets\\spells'), 28, 1, size)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class FireSpell(Spell):
    damage = 50
    spell_type = Spell.FIRE
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.2

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('fire_laser.png', 'assets\\spells'), 6, 1, size)
    frames += cut_sheet(load_image('fire_explosion.png', 'assets\\spells'), 7, 8, size)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class FlashSpell(Spell):
    damage = 50
    spell_type = Spell.FLASH
    UPDATE_TIME = 60
    speed = TILE_SIZE * 10

    size = (TILE_SIZE // 4 * 5,) * 2
    frames = cut_sheet(load_image('EMPTY.png', 'assets\\tiles'), 1, 1, size)
    frames += cut_sheet(load_image('light.png', 'assets\\spells'), 15, 1, size)

    damage_frame = 5

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class PoisonSpell(Spell):
    damage = 30
    spell_type = Spell.POISON
    UPDATE_TIME = 50
    speed = TILE_SIZE * 0.2

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('poison_laser.png', 'assets\\spells'), 7, 1, size)
    frames += cut_sheet(load_image('poison_explosion.png', 'assets\\spells'), 11, 1, size)
    frames += cut_sheet(load_image('poison_explosion_1.png', 'assets\\spells'), 25, 1, size)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class VoidSpell(Spell):
    damage = 70
    spell_type = Spell.VOID
    speed = TILE_SIZE * 0.2

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('void_laser.png', 'assets\\spells'), 10, 1, size)
    frames += cut_sheet(load_image('void_explosion.png', 'assets\\spells'), 12, 2, size)
    frames += cut_sheet(load_image('void_explosions.png', 'assets\\spells'), 10, 5, size)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)
