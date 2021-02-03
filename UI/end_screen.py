import os

import pygame

from UI.UIComponents import LogoImage, AnimatedBackground
from engine import concat_two_file_paths


def execute(screen: pygame.surface.Surface, is_win=False):
    """
    Функция запускает конечной экран (либо смерти, либо победы)
    :param screen: Экран на котором надо отрисовывать менюв
    :param is_win: Флаг, выиграл ли игрок
    """

    running = True
    # Фоновое изображение для всего экрана
    if is_win:
        # Фоновая музыка для победителя
        pygame.mixer.music.load(concat_two_file_paths("assets\\audio", "win_screen_BG.ogg"))
        pygame.mixer.music.play(-1)
        animated_background = AnimatedBackground("win_{0}.png", 1, 8, 60, screen.get_size())
    else:
        # Фоновая музыка для проигравшего
        pygame.mixer.music.load(concat_two_file_paths("assets\\audio", "fail_screen_BG.mp3"))
        pygame.mixer.music.play(-1)
        animated_background = AnimatedBackground("death_{0}.png", 1, 23, 100, screen.get_size())

    # Лого игры
    logo = LogoImage((screen.get_width() * 0.5, screen.get_height() * 0.1))

    # Т.к. игрок завершил игру, то файл с сохранением будет перезаписан
    if os.path.isfile("data\\save.txt"):
        with open('data\\save.txt', 'r+', encoding="utf-8") as file:
            file.truncate(0)

    # Цикл меню
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
                running = False

        animated_background.update()
        # Вывод текущего кадра фонового изображения
        screen.blit(animated_background.image, (0, 0))

        screen.blit(logo.image, logo.rect.topleft)

        pygame.display.flip()
