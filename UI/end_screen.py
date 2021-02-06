import os

import pygame

from UI.UIComponents import LogoImage, AnimatedBackground
from engine import concat_two_file_paths, load_image
from UI.start_screen import AUTHORS


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
        animated_background = AnimatedBackground("triumph_screen\\win_{0}.png", 1, 8, 60, screen.get_size())

        title_you_win = load_image('you_win.png', 'assets\\UI')
        you_win_rect = title_you_win.get_rect()
        you_win_rect.center = screen.get_rect().centerx, int(screen.get_rect().centery * 0.7)
    else:
        # Фоновая музыка для проигравшего
        pygame.mixer.music.load(concat_two_file_paths("assets\\audio", "fail_screen_BG.mp3"))
        pygame.mixer.music.play(-1)
        animated_background = AnimatedBackground("fail_screen\\death_{0}.png", 1, 23, 100, screen.get_size())

    # Лого игры
    logo = LogoImage((screen.get_width() * 0.5, screen.get_height() * 0.1))

    title_font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 64)
    # Текст для диалога
    texts = ('created by\n' + AUTHORS).split('\n')
    # Так нужно для вывода сразу нескольких строк
    text_surfaces = [title_font.render(part.strip(), True, (255, 184, 50)) for part in texts]
    text_surfaces_1 = [title_font.render(part.strip(), True, (179, 64, 16)) for part in texts]
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

        # Вывод текста
        margin = title_font.get_height() * 0.9
        # Чтобы избежать пустого отступа
        next_y = 20

        if is_win:
            screen.blit(title_you_win, you_win_rect)

            for text_surface in text_surfaces_1:
                y_pos = screen.get_height() * 0.6 + next_y
                screen.blit(text_surface, text_surface.get_rect(midtop=(screen.get_rect().centerx + 2, y_pos + 2)))
                next_y += margin

            next_y = 20
            for text_surface in text_surfaces:
                y_pos = screen.get_height() * 0.6 + next_y
                screen.blit(text_surface, text_surface.get_rect(midtop=(screen.get_rect().centerx, y_pos)))
                next_y += margin

        screen.blit(logo.image, logo.rect.topleft)

        pygame.display.flip()
