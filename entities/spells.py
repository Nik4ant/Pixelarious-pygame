from math import *

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

    UPDATE_TIME = 30
    speed = TILE_SIZE * 0.2
    frames = []
    damage = 40

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
        self.last_update_time = ticks

        if (self.rect.centerx, self.rect.centery) == self.point:
            self.cur_frame += 1
            if self.cur_frame == len(self.frames[1]):
                self.kill()
                return
            self.image = self.frames[1][self.cur_frame]

        else:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[0])

            self_x, self_y = self.rect.centerx, self.rect.centery
            point_x, point_y = self.point
            distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
            part_move = max(distance_to_player / self.speed, 0.5)
            dx = round((point_x - self_x) / part_move)
            dy = round((point_y - self_y) / part_move)
            self.rect.x = self.rect.x + dx
            self.rect.y = self.rect.y + dy

            if (self.rect.centerx, self.rect.centery) == self.point:
                self.collider.update(self.rect.centerx, self.rect.centery)
                for obj in pygame.sprite.spritecollide(self.collider, self.object_group, False):
                    obj.get_damage(self.damage)
                self.cur_frame = 0
                self.image = self.frames[1][0]

            self.image = self.frames[0][self.cur_frame]


class FireSpell(Spell):
    damage = 40
    spell_type = Spell.FIRE

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('ice_lazer.png', 'assets\\spells'), 30, 1, size)
    frames += cut_sheet(load_image('ice_explosion.png', 'assets\\spells'), 28, 1, size)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)
