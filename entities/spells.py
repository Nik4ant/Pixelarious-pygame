from math import *
from random import randint, choice

import pygame

from engine import load_image, cut_sheet, concat_two_file_paths
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME

from entities.base_entity import Collider, Entity


class Spell(pygame.sprite.Sprite):
    """
    Класс, отвечающий за предстовление базового заклинания в игре
    """
    FIRE = 'fire'
    FLASH = 'flash'
    ICE = 'ice'
    POISON = 'poison'
    VOID = 'void'
    TELEPORT = 'teleport'

    damage_frame = 0

    start_position = None

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(*groups)
        dx = object_x - subject_x
        dy = object_y - subject_y
        while (abs(dx) < 5000 and abs(dy) < 5000) and (self.spell_type != Spell.FLASH and
                                                       self.spell_type != Spell.TELEPORT):
            dx *= 2
            dy *= 2
            dy += 1
        self.point = (subject_x + dx, subject_y + dy)

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

        self.collider = Collider(self.rect.centerx, self.rect.centery, (self.rect.size[0] - TILE_SIZE * 0.5,) * 2)

        self.update()

    def update(self) -> None:
        if (self.rect.centerx, self.rect.centery) == self.point:
            ticks = pygame.time.get_ticks()
            if ticks - self.last_update_time < self.UPDATE_TIME:
                return
            self.last_update_time = ticks
            if self.cur_frame == self.damage_frame:
                if isinstance(self, TeleportSpell):
                    self.object_group[0].rect.center = self.rect.center
                else:
                    if isinstance(self, VoidSpell):
                        size = (round((self.rect.w / 3)),) * 2
                        self.collider.update(self.rect.centerx, self.rect.centery, size)
                    else:
                        self.collider.update(self.rect.centerx, self.rect.centery)
                    for obj in self.object_group:
                        if pygame.sprite.collide_circle(self.collider, obj):
                            obj.get_damage(self.damage, self.spell_type, self.action_time)
            self.cur_frame += 1
            if self.cur_frame == len(self.__class__.frames[self.cur_list]):
                self.kill()
                if isinstance(self, TeleportSpell):
                    self.start_sprite.kill()
                return
            self.image = self.__class__.frames[self.cur_list][self.cur_frame]
            pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = pos
            if isinstance(self, TeleportSpell):
                self.start_sprite.image = self.__class__.frames[self.cur_list][self.cur_frame]

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
            do_kill = False
            for obj in pygame.sprite.spritecollide(self.collider, self.object_group, False):
                if obj.alive:
                    do_kill = True
            for obj in pygame.sprite.spritecollide(self.collider, Spell.barrier_group, False):
                obj.collider.update(obj.rect.centerx, obj.rect.centery)
                if pygame.sprite.collide_rect(self.collider, obj.collider):
                    do_kill = True
            for obj in pygame.sprite.spritecollide(self.collider, Spell.doors_group, False):
                obj.collider.update(obj.rect.centerx, obj.rect.centery)
                if not obj.opened and pygame.sprite.collide_rect(self.collider, obj.collider):
                    do_kill = True

            if do_kill and self.spell_type != Spell.FLASH and self.spell_type != Spell.TELEPORT:
                self.point = (self.rect.centerx, self.rect.centery)

            if self.rect.center == self.point:
                self.cur_frame = 0
                self.cur_list = randint(1, len(self.__class__.frames) - 1)
                if not isinstance(self, TeleportSpell):
                    self.sounds_channel.play(choice(self.SPELL_SOUNDS))

            ticks = pygame.time.get_ticks()
            if ticks - self.last_update_time < self.UPDATE_TIME:
                return
            self.speed += self.acceleration
            self.last_update_time = ticks
            self.image = self.frames[0][self.cur_frame]
            if isinstance(self, TeleportSpell):
                self.start_sprite.image = self.frames[0][self.cur_frame]

    @staticmethod
    def set_global_collisions_group(barrier_group: pygame.sprite.Group, doors_group: pygame.sprite.Group):
        """
        Метод устанавливает группу со спрайтами, которые будут считаться
        физическими объектами для всех сущностей на уровне.
        (Кроме индивидуальных спрайтов у конкретных объектов,
        например у врагов будет отдельное взаимодействие с игроком).
        Метод нужен при инициализации
        :param barrier_group: Новая группа
        :param doors_group: Новая группа
        """
        Spell.barrier_group = barrier_group
        Spell.doors_group = doors_group


class FireSpell(Spell):
    """Огненное заклинание

    Обычное
    Эффективно против:
    Зомби, Пустотных магов
    Неэффективно против:
    Демонов, Огненных магов"""
    damage = 50
    spell_type = Spell.FIRE
    mana_cost = 60
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.22
    acceleration = 2
    action_time = 0

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('fire_laser.png', 'assets\\spells'), 6, 1, size)
    frames += cut_sheet(load_image('fire_explosion.png', 'assets\\spells'), 7, 8, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "cast_sound_2.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_1.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_3.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_4.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_5.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_14.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_24.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class IceSpell(Spell):
    """Ледяное заклинание

    На время замедляет противника
    (включая перезарядку заклинаний)
    Эффективно против:
    Демонов
    Неэффективно против:
    Грязных слизней"""
    damage = 20
    spell_type = Spell.ICE
    mana_cost = 40
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.3
    acceleration = 4
    action_time = 500

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('ice_laser.png', 'assets\\spells'), 30, 1, size)
    frames += cut_sheet(load_image('ice_explosion.png', 'assets\\spells'), 28, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "cast_sound_1.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_2.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_12.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_18.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_19.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_20.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_21.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_22.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_26.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class PoisonSpell(Spell):
    """Заклинание отравления

    Отравляет противника,
    постепенно нанося урон
    Эффективно против:
    Огненных магов
    Неэффективно против:
    Зеленых слизеней"""
    spell_type = Spell.POISON
    damage = 10
    action_time = 1000
    extra_damage = Entity.POISON_DAMAGE * action_time
    mana_cost = 50
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.2
    acceleration = 0.5

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image('poison_laser.png', 'assets\\spells'), 7, 1, size)
    frames += cut_sheet(load_image('poison_explosion.png', 'assets\\spells'), 11, 1, size)
    frames += cut_sheet(load_image('poison_explosion_1.png', 'assets\\spells'), 25, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "cast_sound_3.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_1.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_12.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_13.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_17.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_23.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_24.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_26.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_27.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class VoidSpell(Spell):
    """Заклинание пустоты

    Урон по площади
    Эффективно против:
    Грязных слизеней
    Неэффективно против:
    Пустотных магов"""
    damage = 60
    spell_type = Spell.VOID
    mana_cost = 100
    speed = TILE_SIZE * 0.24
    acceleration = 3
    UPDATE_TIME = 40
    damage_frame = 5
    action_time = 0

    size = (TILE_SIZE * 3,) * 2
    frames = cut_sheet(load_image('void_laser.png', 'assets\\spells'), 10, 1)
    frames += cut_sheet(load_image('void_explosion.png', 'assets\\spells'), 12, 2, size)
    frames += cut_sheet(load_image('void_explosions.png', 'assets\\spells'), 10, 5, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "cast_sound_5.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_2.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_5.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_14.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_15.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_16.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_17.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_18.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_25.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class FlashSpell(Spell):
    """Заклинание молнии

    Бьёт через стены
    Эффективно против:
    Зеленых слизеней
    Неэффективно против:
    Зомби"""
    damage = 50
    spell_type = Spell.FLASH
    mana_cost = 150
    UPDATE_TIME = 60
    speed = TILE_SIZE * 0.5
    acceleration = 1
    damage_frame = 5
    action_time = 0

    size = (TILE_SIZE // 2 * 2, TILE_SIZE // 2 * 5)
    frames = cut_sheet(load_image('EMPTY.png', 'assets\\tiles'), 1, 1, size)
    frames += cut_sheet(load_image('light.png', 'assets\\spells'), 15, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "cast_sound_4.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_3.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_4.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_5.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_6.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_7.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_8.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_9.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_10.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_11.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_14.ogg")),
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "spell_sound_26.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)


class TeleportSpell(Spell):
    """Заклинание телепортации

    Переносит игрока в позицию прицела"""
    spell_type = Spell.TELEPORT
    damage = '---'
    mana_cost = 200
    UPDATE_TIME = 40
    speed = TILE_SIZE * 1
    acceleration = 0
    damage_frame = 2
    action_time = 0

    size = (TILE_SIZE // 4 * 7,) * 2
    frames = cut_sheet(load_image('EMPTY.png', 'assets\\tiles'), 1, 1, size)
    frames += cut_sheet(load_image('teleport_puf.png', 'assets\\spells'), 8, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "teleport_sound.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "teleport_sound.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)

        self.start_sprite = pygame.sprite.Sprite()
        self.start_sprite.start_position = None
        self.start_sprite.point = None
        self.start_sprite.image = TeleportSpell.frames[0][0]
        self.start_sprite.rect = self.start_sprite.image.get_rect()
        self.start_sprite.rect.center = object_group[0].rect.center


class HealingSpell(Spell):
    """Заклинание восстановления

    ЕГО ЕЩЕ НЕТ
    РАЗРАБАТЫВАЕТСЯ
    (если будет вообще)

    Увеличивает количество жизней, забирая ману"""
    spell_type = Spell.TELEPORT
    damage = '---'
    mana_cost = 1
    UPDATE_TIME = 40
    speed = 1
    acceleration = 0
    damage_frame = 0
    action_time = 0

    size = (TILE_SIZE // 4 * 7,) * 2
    frames = cut_sheet(load_image('EMPTY.png', 'assets\\tiles'), 1, 1, size)
    frames += cut_sheet(load_image('healing.png', 'assets\\spells'), 20, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "teleport_sound.ogg"))
    CAST_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    SPELL_SOUNDS = (
        pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "teleport_sound.ogg")),
    )
    for sound in SPELL_SOUNDS:
        sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, object_group, *groups)

        self.start_sprite = pygame.sprite.Sprite()
        self.start_sprite.start_position = None
        self.start_sprite.point = None
        self.start_sprite.image = TeleportSpell.frames[0][0]
        self.start_sprite.rect = self.start_sprite.image.get_rect()
        self.start_sprite.rect.center = object_group[0].rect.center

