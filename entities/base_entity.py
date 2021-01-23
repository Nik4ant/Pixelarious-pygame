import pygame


class Entity(pygame.sprite.Sprite):
    """
    Класс отвечающий за предстовлении базовой сущности в игре
    """

    # Группа со спрайтами, которые считаются физическими объектами
    # общими для всех сущностей.
    collisions_group: pygame.sprite.Group

    WAITING_TIME = 2000
    UPDATE_TIME = 100
    HEALTH_LINE_WIDTH = 4
    HEALTH_LINE_TIME = 10000

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*args)

        # Изображение
        self.cur_frame = 0
        self.image = self.__class__.frames[0][self.cur_frame]
        self.last_update = pygame.time.get_ticks()
        self.width, self.height = self.image.get_size()

        self.last_damage_time = -Entity.HEALTH_LINE_TIME

        self.start_position = x, y
        self.point = None

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Скорость
        self.dx = self.dy = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

    def update_frame_state(self, n=0):
        tick = pygame.time.get_ticks()
        if tick - self.last_update > Entity.UPDATE_TIME:
            self.last_update = tick
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            look += n
            self.cur_frame = (self.cur_frame + 1) % len(self.__class__.frames[look])
            self.image = self.__class__.frames[look][self.cur_frame]

    def draw_health_bar(self, screen):
        # TODO: Никита пока временно убрал это, для тестов
        # if abs(pygame.time.get_ticks() - self.last_damage_time) < Entity.HEALTH_LINE_TIME:
        line_width = Entity.HEALTH_LINE_WIDTH
        x, y = self.rect.centerx, self.rect.centery
        width, height = self.rect.size
        pygame.draw.rect(screen, 'grey', (x - width * 0.5, y - height * 0.5 - 10, width, line_width))
        health_length = width * self.health / self.full_health
        pygame.draw.rect(screen, 'red', (x - width * 0.5, y - height * 0.5 - 10, health_length, line_width))

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
