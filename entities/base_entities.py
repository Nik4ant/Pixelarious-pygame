from random import randint

import pygame

from engine import load_image, cut_sheet, load_game_font
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME


class Entity(pygame.sprite.Sprite):
    """
    Класс, отвечающий за предстовление базовой сущности в игре
    """

    # Группа со спрайтами, которые считаются физическими объектами
    # общими для всех сущностей.
    collisions_group: pygame.sprite.Group
    all_sprites: pygame.sprite.Group
    player = None

    # Группа со всеми сущностями (экземплярами этого класса)
    # Нужна в основном для коллизий между существами
    entities_group = pygame.sprite.Group()
    damages_group = pygame.sprite.Group()
    spells_group = pygame.sprite.Group()

    default_speed = TILE_SIZE * 0.2

    WAITING_TIME = 2000
    UPDATE_TIME = 120
    HEALTH_LINE_WIDTH = 10
    HEALTH_LINE_TIME = 5000

    POISON_DAMAGE = 5
    BETWEEN_POISON_DAMAGE = 1000

    size = (int(TILE_SIZE),) * 2
    sleeping_frames = cut_sheet(load_image('assets/sprites/enemies/sleep_icon_spritesheet.png'), 4, 1, size)
    poison_frames = cut_sheet(load_image('assets/sprites/spells/poison_static.png'), 5, 1, size)[0]

    small_font = load_game_font(15)
    font = load_game_font(24)

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*((Entity.entities_group,) + args))
        self.alive = True

        # Изображение
        self.cur_frame = 0
        self.image = self.__class__.frames[0][self.cur_frame]
        self.last_update = pygame.time.get_ticks()
        self.width, self.height = self.image.get_size()

        self.last_damage_time = -Entity.HEALTH_LINE_TIME
        self.last_poison_damage = 0
        self.sleeping_time = None
        self.cur_sleeping_frame = 0
        self.cur_poison_frame = 0
        self.poison_static_time = 0
        self.ice_buff = 0
        self.poison_buff = 0

        self.start_position = x, y
        self.point = None
        self.speed = 0.0001

        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.collider = Collider(*self.rect.center)

        # Скорость
        self.dx = self.dy = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

    def update(self) -> None:
        if self.ice_buff:
            self.ice_buff -= 1
            self.speed = self.__class__.default_speed * 0.2
        else:
            self.speed = self.__class__.default_speed

        ticks = pygame.time.get_ticks()
        if self.poison_buff and ticks - self.last_poison_damage > Entity.BETWEEN_POISON_DAMAGE:
            self.last_poison_damage = ticks
            self.poison_buff -= 1
            self.get_damage(Entity.POISON_DAMAGE, 'poison')

    def move(self, dx, dy):
        """
        Метод передвижения. Сущность сдвинется на указанные параметры,
        если там свободно.
        :param dx: Изменение координаты по Х
        :param dy: Изменение координаты по Y
        """
        if not self.alive:
            return
        # Координаты до движения
        pos = self.rect.x, self.rect.y
        # Перемещение по x и обновление столкновений
        self.rect.x = round(self.rect.x + dx)
        self.collider.update(*self.rect.center)

        # Если сущность врезалась во что-то, возвращаем к исходному x
        if pygame.sprite.spritecollide(self.collider, Entity.collisions_group, False):
            self.rect.x = pos[0]
            self.dx = 0
            if self.__class__.__name__ == 'Player':
                self.dash_force_x *= 0.8
                self.dash_direction_x = self.look_direction_x
            elif self.__class__.__name__ == 'PlayerAssistant':
                self.point = None
        # Перемещение по y и обновление столкновений
        self.rect.y = round(self.rect.y + dy)
        self.collider.update(*self.rect.center)

        # Если сущность врезалась во что-то, возвращаем к исходному y
        if pygame.sprite.spritecollide(self.collider, Entity.collisions_group, False):
            self.rect.y = pos[1]
            self.dy = 0
            if self.__class__.__name__ == 'Player':
                self.dash_force_y *= 0.8
                self.dash_direction_y = self.look_direction_y
            elif self.__class__.__name__ == 'PlayerAssistant':
                self.point = None

    def update_frame_state(self, n=0):
        """
        Воспроизводит звук и сменяет кадр анимации

        :param n: если есть, сдвигает номер анимации (стояние вместо движения)
        
        """
        tick = pygame.time.get_ticks()
        if tick - self.last_update > self.UPDATE_TIME:
            self.last_update = tick

            if not self.alive:
                self.cur_frame = self.cur_frame + 1
                if self.cur_frame >= len(self.__class__.death_frames) - 1:
                    if self.__class__.__name__ == 'Player':
                        self.destroyed = True
                    else:
                        for group in self.groups():
                            group.remove(self)
                if self.cur_frame < len(self.__class__.death_frames):
                    self.image = self.__class__.death_frames[self.cur_frame]
                return

            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            look += n
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[look])
            self.image = self.__class__.frames[look][self.cur_frame]
            if (self.__class__.__name__ != 'Player' and DEFAULT_SOUNDS_VOLUME * 200 / self.distance_to_player > 0.1
                    and (look < 2 or 'Slime' in self.__class__.__name__ or 'Demon' in self.__class__.__name__)
                    and not self.sounds_channel.get_busy()):
                self.FOOTSTEP_SOUND.set_volume(min(DEFAULT_SOUNDS_VOLUME / (self.distance_to_player / TILE_SIZE) * 3, 1))
                self.sounds_channel.play(self.FOOTSTEP_SOUND)

    def draw_health_bar(self, screen):
        """
        Отрисовка полоски здоровья и отрисовка знака сна (Z-Z-Z).
        :param screen: Экран
        """
        line_width = Entity.HEALTH_LINE_WIDTH  # длинна полоски здоровья
        x, y = self.rect.center  # текущая позиция сущности
        width, height = self.rect.size  # текущие размеры сущности
        # Позиция над сущностью
        x1, y1 = x - width * 0.5, y - height * 0.5
        # При получении урона или наведении прицелом выводиться шкала здоровья
        if pygame.time.get_ticks() - self.last_damage_time < Entity.HEALTH_LINE_TIME or \
                pygame.sprite.collide_rect(self, Entity.player.scope):
            # Обводка вокруг шкалы здоровья
            pygame.draw.rect(screen, 'dark grey', (x1 - 1, y1 - 10 - 1, width + 2, line_width + 2))
            # Длинная полоски здоровья
            health_length = width * max(self.health, 0) / self.full_health
            # Для игрока и его помошника зелёный цвет, для остальных красный
            color = '#00b300' if self.__class__.__name__ in ('Player', 'PlayerAssistant') else 'red'
            # Сама полоска здоровья
            pygame.draw.rect(screen, color, (x1, y1 - 10, health_length, line_width))
            # Текст с текущем здоровьем
            health_text = f'{round(self.health + 0.5)}/{self.full_health}'
            health = self.small_font.render(health_text, True, (255, 255, 255))
            # Отцентровка текста по середине
            rect = health.get_rect()
            rect.center = (x1 + width // 2, y1 - 5)
            # Вывод на экран
            screen.blit(health, rect.topleft)
        # Для всех сущностей кроме игрока выводиться их название
        if self.__class__.__name__ not in ('Player',):
            name = self.font.render(self.name, True, (255, 255, 255))
            rect = name.get_rect()
            rect.center = (x1 + width // 2, y1 - 12 - line_width)
            screen.blit(name, rect.topleft)

        if not self.alive:
            return
        # Отрисовка эффетка яда и обновление параметров
        ticks = pygame.time.get_ticks()
        if self.poison_buff:
            if ticks - self.poison_static_time > Entity.UPDATE_TIME:
                self.poison_static_time = ticks
                self.cur_poison_frame = (self.cur_poison_frame + 1) % len(Entity.poison_frames)
            screen.blit(Entity.poison_frames[self.cur_poison_frame], (self.rect.x, self.rect.y))
        # Отрисовка анимации сна и обновление параметров
        if self.__class__.__name__ not in ('Player',) and not self.target_observed:
            if not self.sleeping_time or ticks - self.sleeping_time >= 250:
                self.cur_sleeping_frame = (self.cur_sleeping_frame + 1) % len(self.sleeping_frames[0])
                self.sleeping_time = ticks
            screen.blit(self.sleeping_frames[0][self.cur_sleeping_frame], (self.rect.centerx + 10, self.rect.y - 35))

    def get_damage(self, damage, spell_type='', action_time=0):
        """
        Получение дамага

        :param damage: Столько здоровья надо отнять
        :param spell_type: Тип урона, чтоб узнавать, на кого он действует сильнее
        :param action_time: Время действия (для льда и отравления)
        
        """

        if not self.alive:
            return
        if spell_type == 'ice':
            self.ice_buff += action_time
        if spell_type == 'poison' and damage >= 5:
            self.poison_buff += action_time

        if damage >= 0:
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            self.image = self.get_damage_frames[look]
            self.last_update = pygame.time.get_ticks() + 75
            self.last_damage_time = pygame.time.get_ticks()

        if (self.__class__.__name__ == 'Demon' and spell_type == 'ice' or
                self.__class__.__name__ == 'GreenSlime' and spell_type == 'flash' or
                self.__class__.__name__ == 'DirtySlime' and spell_type == 'void' or
                self.__class__.__name__ == 'Zombie' and spell_type == 'fire' or
                self.__class__.__name__ == 'FireWizard' and spell_type == 'poison' or
                self.__class__.__name__ == 'VoidWizard' and spell_type == 'fire'):
            damage *= 2

        if (self.__class__.__name__ == 'Demon' and spell_type == 'fire' or
                self.__class__.__name__ == 'GreenSlime' and spell_type == 'poison' or
                self.__class__.__name__ == 'DirtySlime' and spell_type == 'ice' or
                self.__class__.__name__ == 'Zombie' and spell_type == 'flash' or
                self.__class__.__name__ == 'FireWizard' and spell_type == 'fire' or
                self.__class__.__name__ == 'VoidWizard' and spell_type == 'void'):
            damage *= 0.25

        damage *= 1000
        damage += randint(-abs(round(-damage * 0.2)), abs(round(damage * 0.2)))
        damage /= 1000

        x, y = self.rect.midtop
        colors = {
            'poison': (100, 230, 125),
            'ice':    (66, 170, 255),
            'void':   (148, 0, 211),
            'flash':  (255, 255, 0),
            'fire':   (226, 88, 34),
        }
        ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages_group, color=colors[spell_type])

        self.health = min(self.health - damage, self.full_health)
        if self.health <= 0:
            self.health = 0
            self.death()

    def set_first_frame(self):
        """Установка первого спрайта"""
        tick = pygame.time.get_ticks()
        if tick - self.last_update > self.UPDATE_TIME:
            self.last_update = tick

            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            self.cur_frame = 0
            self.image = self.__class__.frames[look][self.cur_frame]

    @staticmethod
    def set_global_groups(collisions_group: pygame.sprite.Group, all_sprites: pygame.sprite.Group):
        """
        Метод устанавливает группу со спрайтами, которые будут считаться
        физическими объектами для всех сущностей на уровне.
        (Кроме индивидуальных спрайтов у конкретных объектов,
        например у врагов будет отдельное взаимодействие с игроком).
        Метод нужен при инициализации
        :param collisions_group: Новая группа
        :param all_sprites: Группа всех спрайтов
        """
        Entity.collisions_group = collisions_group
        Entity.all_sprites = all_sprites


class Collider(pygame.sprite.Sprite):
    """
    Класс, который будет невидимым, но будет использоваться для просчёта колизий у сущности
    """
    def __init__(self, x: float, y: float, size=(round(TILE_SIZE * 0.5), round(TILE_SIZE * 0.5))):
        self.image = pygame.surface.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def update(self, x: float, y: float, size=None):
        self.rect.center = x, y
        if size:
            self.rect.size = size


class ReceivingDamage(pygame.sprite.Sprite):
    update_time = 40
    delta_up = 1
    delta_transparent = -5

    def __init__(self, x: float, y: float, damage: float, *groups, color=(255, 255, 255)):
        super().__init__(*groups)
        self.font = load_game_font(min(round(24 + abs(damage) / 3), 64))
        self.last_update_time = 0

        self.damage = abs(round(damage))
        self.alpha = 500
        self.image = self.font.render(str(self.damage), True, color).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = x + randint(-TILE_SIZE // 1.5, TILE_SIZE // 1.5), y + randint(-20, 20)

    def update(self):
        self.rect.y -= self.delta_up
        self.alpha += self.delta_transparent
        if self.alpha < 5:
            self.kill()
            return
        self.image.set_alpha(min(255, self.alpha))
