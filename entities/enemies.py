import pygame
from engine import load_image
from config import TILE_SIZE

from random import randint


class Entity(pygame.sprite.Sprite):
    """
    Класс отвечающий за игрока и врагов в игре
    """
    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 0.95
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 1
    # сила с которой игрок будет набирать/уменьшать свою скорость
    delta_changer = 0.05

    # Канал для звуков
    # TODO: если не будет так много звуков может быть просто выпилить эту штуку?
    sounds_channel = pygame.mixer.Channel(1)

    # Звуки
    # FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/audio", "footstep.ogg"))
    # FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)
    #
    # DASH_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/audio", "dash.wav"))
    # DASH_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x: float, y: float, *args):
        # Конструктор класса Sprite
        super().__init__(*args)

        # TODO: заменить на spritesheet
        # Изображение
        self.image = load_image("test_monster.png", "assets")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.width, self.height = self.image.get_size()

        self.start_posision = x, y
        self.point = None

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Скорость
        self.speed = TILE_SIZE * 0.03
        self.dx = self.dy = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

    def update(self, player=None):
        if not player:
            return

        self_x, self_y = self.rect.centerx, self.rect.centery

        point_x, point_y = player.rect.centerx, player.rect.centery
        # Расстояние между врагом и игроком
        line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= 6 * TILE_SIZE:
            if not self.point or self.point == (self.rect.centerx, self.rect.centery):
                self.point = self.start_posision[0] + randint(-TILE_SIZE * 0.5, TILE_SIZE * 0.5), \
                             self.start_posision[1] + randint(-TILE_SIZE * 0.5, TILE_SIZE * 0.5)
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 1)
            self.dx = int((point_x - self_x) / part_move)
            self.dy = int((point_y - self_y) / part_move)
        else:
            part_move = max(line / self.speed, 1)
            self.dx = int((point_x - self_x) * 3 / part_move)
            self.dy = int((point_y - self_y) * 3 / part_move)

        # Направления движения по x и y

        '''
        Управление игрока сделано так, что при начале движения игрок не сразу
        получает максимальную скорость, а постепеноо разгоняется. При этом
        если во время набора скорости игрок меняет направление, то разгон будет
        продолжаться. Но если игрок уже достиг своей максимальной скорости, он
        может моментально менять направления, а не крутиться как черепаха (это
        повышает динамичность геймплея и заставляет игрока больше двигаться, а
        не стоять на месте). Но при этом, нельзя просто взять отпустить кнопку, 
        зажать другую и ожидать, что скорость сохранится, если бы так всё 
        работало, то это было бы неправильно, поэтому чтобы при изменении 
        направления сохранить скорость, надо не отпуская текущую клавишу, 
        зажать другие клавиши, а затем отпустить текущие.
        '''

        # Если игрок движется и при этом не совершается дэш,
        # то воспроизводится звук ходьбы
        # (При этом проверяется текущий канал со звуками, чтобы не
        # было наложения эффекта "наложения" звуков)
        # if (self.dx != 0 or self.dy != 0) and not Entity.sounds_channel.get_busy():
        #     Entity.sounds_channel.play(Entity.FOOTSTEP_SOUND)

        # Перемещение сущности относительно центра
        self.rect.centerx = self.rect.centerx + self.dx
        self.rect.centery = self.rect.centery + self.dy


def random_monster(x, y, all_sprites, enemies_group):
    return Entity(x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5, all_sprites, enemies_group)
