import os

import pygame

from UI.UI_components import LogoImage, AnimatedBackground
from engine import load_image


def execute(screen: pygame.surface.Surface, is_win=False):
    """
    Функция запускает конечной экран (либо смерти, либо победы)
    :param screen: Экран на котором надо отрисовывать менюв
    :param is_win: Флаг, выиграл ли игрок
    :return None
    """
    is_open = True
    # Фоновое изображение для всего экрана
    if is_win:
        # Фоновая музыка при победе
        pygame.mixer.music.load("assets/audio/music/win_screen_BG.ogg")
        pygame.mixer.music.play(-1)
        animated_background = AnimatedBackground("win_{0}.png", "assets/sprites/UI/backgrounds/triumph_screen",
                                                 1, 8, 80, screen.get_size())
        # Картигка с заголовком победы
        title_you_win = load_image('assets/sprites/UI/you_win.png')
        you_win_rect = title_you_win.get_rect()
        you_win_rect.center = screen.get_rect().centerx, int(screen.get_rect().centery * 0.7)
    else:
        # Фоновая музыка при проигрыше
        pygame.mixer.music.load("assets/audio/music/fail_screen_BG.mp3")
        pygame.mixer.music.play(-1)
        # Высчитывание размера для фона и сам фон
        size = screen.get_width() // 3, screen.get_height() // 3
        animated_background = AnimatedBackground("death_{0}.png", "assets/sprites/UI/backgrounds/fail_screen",
                                                 1, 23, 140, size, scale_2n=True)
    # Лого игры
    logo = LogoImage((screen.get_width() * 0.5, screen.get_height() * 0.1))
    # Изображение курсора
    cursor_image = load_image("assets/sprites/UI/icons/cursor.png")
    # Т.к. игрок завершил игру, то файл с сохранением будет перезаписан
    if os.path.isfile("data/save.txt"):
        with open('data/save.txt', 'r+', encoding="utf-8") as file:
            file.truncate(0)
    # Цикл меню
    while is_open:
        # Обработка событий
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
                is_open = False
        # На экране проигрыша есть фон, которого нет на экране победы
        if not is_win:
            screen.fill((31, 30, 36))
        # Вывод текущего кадра фонового изображения
        animated_background.update()
        screen.blit(animated_background.image, animated_background.image.get_rect(center=screen.get_rect().center))
        # Вывод картинки победного заголовка, если игрок выиграл
        if is_win:
            # IDE может ругаться, но если is_win истина, то
            # переменные 100% объявлены выше
            screen.blit(title_you_win, you_win_rect)
        # Вывод логотипа игры
        screen.blit(logo.image, logo.rect.topleft)
        # Вывод изображения курсора
        screen.blit(cursor_image, pygame.mouse.get_pos())

        pygame.display.flip()
