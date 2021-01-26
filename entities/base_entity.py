import pygame
from engine import load_image, cut_sheet
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME


class Entity(pygame.sprite.Sprite):
    """
    Класс отвечающий за предстовлении базовой сущности в игре
    """

    # Группа со спрайтами, которые считаются физическими объектами
    # общими для всех сущностей.
    collisions_group: pygame.sprite.Group

    WAITING_TIME = 2000
    UPDATE_TIME = 120
    HEALTH_LINE_WIDTH = 5
    HEALTH_LINE_TIME = 10000

    size = (TILE_SIZE,) * 2
    sleeping_frames = cut_sheet(load_image('sleep_icon_spritesheet.png', 'assets\\enemies\\'), 4, 1, size)

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*args)

        # Изображение
        self.cur_frame = 0
        self.image = self.__class__.frames[0][self.cur_frame]
        self.last_update = pygame.time.get_ticks()
        self.width, self.height = self.image.get_size()

        self.last_damage_time = -Entity.HEALTH_LINE_TIME
        self.sleeping_time = None

        self.start_position = x, y
        self.point = None

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.collider = Collider(self.rect.centerx, self.rect.centery)

        # Скорость
        self.dx = self.dy = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

    def move(self, dx, dy):
        """
        Метод передвижения
        Сдвинется на указанные параметры, если там свободно

        :param dx: Изменение координаты по Х
        :param dy: Изменение координаты по Y
        :return: None
        """
        # Запоминаем координаты
        pos = self.rect.x, self.rect.y

        self.rect.x = self.rect.x + dx
        self.collider.update(self.rect.centerx, self.rect.centery)

        # Если плохо, возвращаем к исходному
        if pygame.sprite.spritecollide(self.collider, Entity.collisions_group, False):
            self.rect.x = pos[0]

        self.rect.y = self.rect.y + dy
        self.collider.update(self.rect.centerx, self.rect.centery)

        # Если плохо, возвращаем к исходному
        if pygame.sprite.spritecollide(self.collider, Entity.collisions_group, False):
            self.rect.y = pos[1]

    def update_frame_state(self, n=0):
        """
        Воспроизводит звук и сменяет кадр анимации

        :param n: если есть, сдвигает номер анимации (стояние вместо движения)
        :return: None
        """
        tick = pygame.time.get_ticks()
        if tick - self.last_update > self.UPDATE_TIME:
            self.last_update = tick
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
        Функция отрисовки полоски здоровья

        :param screen: Экран отрисовки
        :return: None
        """
        if abs(pygame.time.get_ticks() - self.last_damage_time) > Entity.HEALTH_LINE_TIME:
            return
        line_width = Entity.HEALTH_LINE_WIDTH
        x, y = self.rect.centerx, self.rect.centery
        width, height = self.rect.size
        x1, y1 = x - width * 0.5, y - height * 0.5
        pygame.draw.rect(screen, 'grey', (x1 - 1, y1 - 10 - 1, width + 2, line_width + 2))
        health_length = width * self.health / self.full_health
        color = 'green' if str(self.__class__.__name__) == 'Player' else 'red'
        pygame.draw.rect(screen, color, (x1, y1 - 10, health_length, line_width))

    def draw_sign(self, screen):
        # TODO: оставить что-нибудь одно
        if self.player_observed:
            font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 96)
            text = font.render("!", True, (250, 20, 20))
            screen.blit(text, (self.rect.centerx, self.rect.y - 60))

        if not self.player_observed:
            if not self.sleeping_time or pygame.time.get_ticks() - self.sleeping_time >= 250:
                if not self.sleeping_time:
                    self.cur_sleeping_frame = 0
                self.cur_sleeping_frame = (self.cur_sleeping_frame + 1) % len(Entity.sleeping_frames[0])
                self.sleeping_time = pygame.time.get_ticks()
            screen.blit(Entity.sleeping_frames[0][self.cur_sleeping_frame], (self.rect.centerx + 10, self.rect.y - 35))

    def get_damage(self, damage):
        self.last_damage_time = pygame.time.get_ticks()
        self.health -= damage

    def set_first_frame(self):
        look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
        self.cur_frame = 0
        self.image = self.__class__.frames[look][self.cur_frame]

    def apply_base_collisions(self):
        hits = pygame.sprite.spritecollide(self, Entity.collisions_group, False)
        # FIXME: Никита сделал тут совсем сырой метод копипасту, т.к. попытка сделать как я писал в группе не удалась
        # FIXME: Тем неменее нормальный способ для колизий всё ещё нужен, поэтому SOS
        if hits:
            if self.dx > 0:
                self.x = hits[0].rect.left - self.rect.width
            if self.dx < 0:
                self.x = hits[0].rect.right
            self.dx = 0
            self.rect.x = self.x

            if self.dy > 0:
                self.y = hits[0].rect.top - self.rect.height
            if self.dy < 0:
                self.y = hits[0].rect.bottom
            self.dy = 0
            self.rect.y = self.y

    @staticmethod
    def set_global_collisions_group(group: pygame.sprite.Group):
        """
        Метод устанавливает группу со спрайтами, которые будут считаться
        физическими объектами для всех сущностей на уровне.
        (Кроме индивидуальных спрайтов у конкретных объектов,
        например у врагов будет отдельное взаимодействие с игроком).
        Метод нужен при инициализации
        :param group: Новая группа
        """
        Entity.collisions_group = group


class Collider(pygame.sprite.Sprite):
    """
    Класс, который будет невидимым, но будет использоваться для просчёта колизий у сущности
    """
    def __init__(self, x: float, y: float, size=(round(TILE_SIZE * 0.5), round(TILE_SIZE * 0.5))):
        self.image = pygame.surface.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = x, y

    def update(self, x: float, y: float):
        self.rect.centerx, self.rect.centery = x, y
