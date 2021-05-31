from math import *
from random import randint, choice

import pygame

from engine import load_image, load_sound, cut_sheet
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME

from entities.base_entities import Collider, Entity


class Spell(pygame.sprite.Sprite):
    """
    Класс, отвечающий за предстовление базового заклинания в игре
    """
    FIRE = "fire"
    FLASH = "flash"
    ICE = "ice"
    POISON = "poison"
    VOID = "void"
    TELEPORT = "teleport"

    # Номер кадра анимации, на котором происходит действие (телепортация, урон, хил)
    damage_frame = 0

    start_position = None

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, extra_damage: float,
                 object_group, all_spites, *groups):
        super().__init__(all_spites, *groups)
        dx = object_x - subject_x
        dy = object_y - subject_y
        # Увеличиваем расстояние пропорционально
        # Чтобы заклинание летело далеко за пределы экрана, а не просто к курсору
        while (abs(dx) < 5000 and abs(dy) < 5000) and (self.spell_type != Spell.FLASH and
                                                       self.spell_type != Spell.TELEPORT):
            dx *= 2
            dy *= 2
            dy += 1
        self.point = (subject_x + dx, subject_y + dy)

        # Увеличения урона/времени действия в зависимости от уровня существа
        if self.spell_type != Spell.TELEPORT:
            self.damage = self.__class__.damage * extra_damage

        if self.spell_type in (self.ICE, self.POISON):
            self.action_time = self.__class__.action_time * extra_damage

        # Угол, под которым пущено заклинание (для поворота картинки)
        if dx >= 0:
            self.angle = -degrees(atan(dy / max(dx, 0.00001)))
        else:
            self.angle = 180 - degrees(atan(dy / min(dx, -0.00001)))

        self.object_group = object_group
        self.cur_frame = 0
        self.cur_list = 0
        self.last_update_time = pygame.time.get_ticks()

        # Поворачиваем картинку
        self.frames = [[pygame.transform.rotate(i, self.angle) for i in self.__class__.frames[0]],
                       self.__class__.frames[1:]]

        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = subject_x, subject_y

        self.collider = Collider(*self.rect.center, (TILE_SIZE * 0.2, TILE_SIZE * 0.2))

        self.update()

    def update(self) -> None:
        if self.rect.center == self.point:
            # Значит заклинание достигло цели (либо врезалось)
            # Теперь оно должно нанести урон и уничтожиться после показа анимации
            ticks = pygame.time.get_ticks()
            if ticks - self.last_update_time < self.UPDATE_TIME:
                return
            self.last_update_time = ticks

            if self.cur_frame == self.damage_frame:
                # Производим действие
                if isinstance(self, TeleportSpell):
                    self.object_group[0].rect.center = self.rect.center
                else:
                    if isinstance(self, VoidSpell):
                        # Сделаем, чтоб коллайдер был ровно по границы анимации
                        # Чтоб не было расхождения и не вводить в ступор игрока
                        size = (round((self.rect.w / 3)),) * 2
                        self.collider.update(*self.rect.center, size)
                    else:
                        size = (round((self.rect.w / 2)),) * 2
                        self.collider.update(*self.rect.center, size)

                    # Убиваем все заклинание-ломаемые вещи, которые задеваем
                    pygame.sprite.spritecollide(self.collider, Spell.furniture_group, True)
                    pygame.sprite.spritecollide(self.collider, Spell.doors_group, True)

                    # Наносим урон группе объектов, на которых направлено заклинание
                    for obj in self.object_group:
                        if pygame.sprite.collide_circle(self.collider, obj):
                            obj.get_damage(self.damage, self.spell_type, self.action_time)

            # Меняем номер кадра анимации
            self.cur_frame += 1
            if self.cur_frame == len(self.__class__.frames[self.cur_list]):
                # Если кадр последний, убиваем заклинание
                self.kill()
                if isinstance(self, TeleportSpell):
                    # Подчищаем
                    self.start_sprite.kill()
                return

            # Меняем кадр анимации
            self.image = self.__class__.frames[self.cur_list][self.cur_frame]
            # Выравниваем центр изображения
            pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = pos
            if isinstance(self, TeleportSpell):
                self.start_sprite.image = self.image

        else:
            # Иначе ещё летим
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[0])

            # Вычисляем перемещение
            self_x, self_y = self.rect.center
            point_x, point_y = self.point
            distance_to_object = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
            part_move = max(distance_to_object / self.speed, 0.5)
            dx = round((point_x - self_x) / part_move)
            dy = round((point_y - self_y) / part_move)
            self.rect.x = self.rect.x + dx
            self.rect.y = self.rect.y + dy

            # Обновляем позицию коллайдера
            self.collider.update(*self.rect.center)
            do_kill = False
            # Проверяем на всевозможные соприкосновения, от которых заклинание может умереть
            for obj in pygame.sprite.spritecollide(self.collider, self.object_group, False):
                if obj.alive:
                    do_kill = True
            for obj in pygame.sprite.spritecollide(self.collider, Spell.barrier_group, False):
                obj.collider.update(*obj.rect.center)
                if pygame.sprite.collide_rect(self.collider, obj.collider):
                    do_kill = True

            for obj in pygame.sprite.spritecollide(self.collider, Spell.doors_group, False):
                obj.collider.update(*obj.rect.center)
                if not obj.opened:
                    do_kill = True
            for obj in pygame.sprite.spritecollide(self.collider, Spell.furniture_group, False):
                obj.collider.update(*obj.rect.center)
                if pygame.sprite.collide_rect(self.collider, obj.collider):
                    do_kill = True

            if do_kill and self.spell_type != Spell.FLASH and self.spell_type != Spell.TELEPORT:
                self.point = self.rect.center

            # Проверяем, достигли ли объекта
            if self.rect.center == self.point:
                self.cur_frame = 0
                self.cur_list = randint(1, len(self.__class__.frames) - 1)
                # Нужно, чтоб не задваивался звук
                # Т.к. воспроизводится и в месте каста, и в месте попадания
                if not isinstance(self, TeleportSpell):
                    pass
                self.sounds_channel.play(choice(self.SPELL_SOUNDS))

            ticks = pygame.time.get_ticks()
            if ticks - self.last_update_time < self.UPDATE_TIME:
                return
            # Обновляем кадр анимации
            self.last_update_time = ticks
            self.image = self.frames[0][self.cur_frame]
            if isinstance(self, TeleportSpell):
                self.start_sprite.image = self.image

    @staticmethod
    def set_global_collisions_group(barrier_group: pygame.sprite.Group):
        """
        Метод устанавливает группу со спрайтами, которые будут считаться
        физическими объектами для всех сущностей на уровне.
        (Кроме индивидуальных спрайтов у конкретных объектов,
        например у врагов будет отдельное взаимодействие с игроком).
        Метод нужен при инициализации
        :param barrier_group: Новая группа
        """
        Spell.barrier_group = barrier_group

    @staticmethod
    def set_global_breaking_group(doors_group, furniture_group):
        """
        Метод устанавливает группы со спрайтами, которые ломаются от соприкосновений с заклинанием
        :param doors_group: Группа дверей
        :param furniture_group: Группа ящиков и бочек
        :return: None
        """
        Spell.doors_group = doors_group
        Spell.furniture_group = furniture_group


class FireSpell(Spell):
    """Огненное заклинание

    Обычное
    Эффективно против:
    Зомби, Древних магов
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
    frames = cut_sheet(load_image("assets/sprites/spells/fire_laser.png"), 6, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/fire_explosion.png"), 7, 9, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/cast_sound_2.ogg")
    SPELL_SOUNDS = (
        load_sound("assets/audio/sfx/spells/spell_sound_1.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_3.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_4.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_5.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_14.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_24.ogg"),
    )


class IceSpell(Spell):
    """Ледяное заклинание

    На время замедляет противника
    (включая перезарядку заклинаний)
    Эффективно против:
    Демонов
    Неэффективно против:
    Грязных слизней"""
    damage = 25
    spell_type = Spell.ICE
    mana_cost = 40
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.3
    acceleration = 4
    action_time = 500

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image("assets/sprites/spells/ice_laser.png"), 30, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/ice_explosion.png"), 28, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)
    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/cast_sound_1.ogg")
    SPELL_SOUNDS = (
        load_sound("assets/audio/sfx/spells/spell_sound_2.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_12.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_18.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_19.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_20.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_21.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_22.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_26.ogg"),
    )


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
    action_time = 10
    extra_damage = Entity.POISON_DAMAGE * action_time
    mana_cost = 50
    UPDATE_TIME = 40
    speed = TILE_SIZE * 0.2
    acceleration = 0.5

    size = (TILE_SIZE // 4 * 3,) * 2
    frames = cut_sheet(load_image("assets/sprites/spells/poison_laser.png"), 7, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/poison_explosion.png"), 11, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/poison_explosion_1.png"), 25, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/cast_sound_3.ogg")
    SPELL_SOUNDS = (
        load_sound("assets/audio/sfx/spells/spell_sound_1.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_12.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_13.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_17.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_23.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_24.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_26.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_27.ogg"),
    )


class VoidSpell(Spell):
    """Заклинание пустоты

    Урон по площади
    Эффективно против:
    Грязных слизеней
    Неэффективно против:
    Древних магов"""
    damage = 60
    spell_type = Spell.VOID
    mana_cost = 100
    speed = TILE_SIZE * 0.24
    acceleration = 3
    UPDATE_TIME = 40
    damage_frame = 2
    action_time = 0

    size = (TILE_SIZE * 3,) * 2
    frames = cut_sheet(load_image("assets/sprites/spells/void_laser.png"), 10, 1)
    frames += cut_sheet(load_image("assets/sprites/spells/void_explosion.png"), 12, 2, size)
    frames += cut_sheet(load_image("assets/sprites/spells/void_explosions.png"), 10, 5, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/cast_sound_5.ogg")
    SPELL_SOUNDS = (
        load_sound("assets/audio/sfx/spells/spell_sound_2.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_5.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_14.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_15.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_16.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_17.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_18.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_25.ogg"),
    )


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
    speed = TILE_SIZE * 3
    acceleration = 1
    damage_frame = 2
    action_time = 0

    size = (TILE_SIZE // 2 * 2, TILE_SIZE // 2 * 5)
    frames = cut_sheet(load_image("assets/sprites/tiles/EMPTY.png"), 1, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/light.png"), 15, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/cast_sound_4.ogg")
    SPELL_SOUNDS = (
        load_sound("assets/audio/sfx/spells/spell_sound_3.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_4.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_5.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_6.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_7.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_8.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_9.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_10.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_11.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_14.ogg"),
        load_sound("assets/audio/sfx/spells/spell_sound_26.ogg"),
    )


class TeleportSpell(Spell):
    """Заклинание телепортации

    Переносит игрока в позицию прицела"""
    spell_type = Spell.TELEPORT
    damage = "---"
    mana_cost = 250
    UPDATE_TIME = 40
    speed = TILE_SIZE * 3
    acceleration = 0
    damage_frame = 2
    action_time = 0

    size = (TILE_SIZE // 4 * 7,) * 2
    frames = cut_sheet(load_image("assets/sprites/tiles/EMPTY.png"), 1, 1, size)
    frames += cut_sheet(load_image("assets/sprites/spells/teleport_puf.png"), 8, 1, size)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/teleport_sound.ogg")
    SPELL_SOUNDS = (load_sound("assets/audio/sfx/spells/teleport_sound.ogg"), )

    def __init__(self, subject_x: float, subject_y: float, object_x: float, object_y: float, extra_damage: float,
                 object_group, *groups):
        super().__init__(subject_x, subject_y, object_x, object_y, extra_damage, object_group, *groups)

        self.start_sprite = pygame.sprite.Sprite()
        self.start_sprite.start_position = None
        self.start_sprite.point = None
        self.start_sprite.image = TeleportSpell.frames[0][0]
        self.start_sprite.rect = self.start_sprite.image.get_rect()
        self.start_sprite.rect.center = object_group[0].rect.center


class CallZombiesSpell(Spell):
    """
    Заклинание спавна монстров (2-4). Самой реализации спавна тут нет,
    это просто спецэффект (в данном случае звуки)
    """
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)
    # Звуки
    CAST_SOUND = load_sound("assets/audio/sfx/spells/call_zombies.ogg",
                            volume=DEFAULT_SOUNDS_VOLUME * 1.5)
