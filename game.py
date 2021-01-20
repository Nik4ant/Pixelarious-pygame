import os
import pygame

from generation_map import initialise_level, generate_new_level
from config import *
from engine import *


# TODO: В этом месте Никита впадает в ступор, т.к. куда запихать камеру,
#  вроде бы в entities не хочется, но здесь хранить её как-то странно, наверное
# FIXME: короче нужны идеи срочно
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, screen_width, screen_height):
        self.dx = 0
        self.dy = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def apply_point(self, obj):
        obj.start_posision = obj.start_posision[0] + self.dx, obj.start_posision[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w * 0.5 - self.screen_width * 0.5)
        self.dy = -(target.rect.y + target.rect.h * 0.5 - self.screen_height * 0.5)


def start(screen: pygame.surface.Surface):
    loading_screen(screen)
    
    screen_width, screen_height = screen.get_size()

    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов
    collidable_tiles_group = pygame.sprite.Group()
    # Группа со спрайтами врагов
    enemies_group = pygame.sprite.Group()
    # Группа со спрайтами дверей
    doors_group = pygame.sprite.Group()

    is_game_open = True
    clock = pygame.time.Clock()  # Часы

    level, new_seed = generate_new_level()
    player, monsters = initialise_level(level, all_sprites, collidable_tiles_group, enemies_group, doors_group)
    camera = Camera(screen_width, screen_height)

    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player_sprites.add(player.scope)  # прицел игрока
    all_sprites.add(player)

    # Фоновая музыка
    pygame.mixer.music.load(os.path.join("assets/audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    # Игровой цикл
    while is_game_open:
        # Очистка экрана
        screen.fill((20, 20, 20))
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

        # Обновление спрайтов игрока
        player_sprites.update()
        all_sprites.update()
        enemies_group.update(player)

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        for enemy in enemies_group:
            camera.apply_point(enemy)

        # Отрисовка всех спрайтов
        all_sprites.draw(screen)
        enemies_group.draw(screen)
        player_sprites.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()

    # TODO: возможно забахать terminate, но ПОКА ЧТО он не нужен
    #  (если не понятно почему так писать Никите, либо посмотрите стек вызова)
