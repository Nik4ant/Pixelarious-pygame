import os

import pygame

from entities.player import Player

from generation_map import generate_new_level, generate_level, load_level

from config import *
from engine import *


# TODO: В этом месте Никита впадает в ступор, т.к. куда запихать камеру,
#  вроде бы в entities не хочется, но здесь хранить её как-то странно, наверное
# FIXME: короче нужны идеи срочно
class Camera:
    """
    Класс отвечающий за поведение камеры в игровом цикле
    """

    def __init__(self):
        #
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        """
        Передвижение переданного объекта относительно смещения камеры
        :param obj: Объект для смещения
        """
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # TODO: remove comment down bellow
    # NOTE: на самом деле я вообще хз какого типа будет target (Никита)
    def update(self, target: pygame.sprite.Sprite):
        """
        Камера будет позиционированна относительно объекта target
        :param target: объект относительно которого будет происходить позиционирование
        """

        # FIXME: level_x и level_y надо бы откопать где-то
        if width * 0.5 // tile_width <= target.pos[0] < level_x - width * 0.5 // tile_width:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        else:
            self.dx = 0
        if height * 0.5 // tile_height <= target.pos[1] < level_y - height * 0.5 // tile_height:
            self.dy = -(target.rect.y + target.rect.h * 0.5 - height * 0.5)
        else:
            self.dy = 0


def start(screen: pygame.surface.Surface):
    is_game_open = True
    clock = pygame.time.Clock()  # Часы

    # Игровые объекты, которые должны инициализироваться отдельно
    # Игрок
    player = Player(screen.get_width() * 0.5, screen.get_height() * 0.5)
    # Камера
    camera = Camera()

    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player_sprites.add(player.scope)  # прицел игрока
    # Группа со спрайтами тайлов
    tiles_group = pygame.sprite.Group()

    # Текущий уровень и его сид
    current_level = load_level()
    # FIXME: почему-то падает вот тут
    generate_level(current_level, tiles_group, player)

    # Фоновая музыка
    pygame.mixer.music.load(concat_two_file_paths("assets/audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    # Игровой цикл
    while is_game_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = True
                break

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        # Обновление всех групп со спрайтами
        player_sprites.update()

        # Очистка экрана
        screen.fill((255, 255, 255))

        # TODO: возможно этот коммент можно улучшить, моя формулировка так себе
        # Отрисовка всех групп спрайтов в определённом порядке отрисовки
        player_sprites.draw(screen)
        tiles_group.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()

    # TODO: возможно забахать terminate, но ПОКА ЧТО он не нужен
    #  (если не понятно почему так писать Никите, либо посмотрите стек вызова)
