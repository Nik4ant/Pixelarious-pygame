import os

import pygame

from entities.player import Player
from config import *
from engine import *


def start(screen: pygame.surface.Surface):
    is_game_open = True
    clock = pygame.time.Clock()  # Часы

    # Игрок
    player = Player(screen.get_width() * 0.5, screen.get_height() * 0.5)
    # Группа со спрайтами игрока и объектами, которые к нему относятся
    # TODO: сами объекты в эту группу, ближе к организации mainloop'а посмотреть?
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player_sprites.add(player.scope)  # прицел игрока

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

        # Очистка экрана
        screen.fill((255, 255, 255))
        # Обновляем и выводим все спрайты
        player_sprites.update()
        player_sprites.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
