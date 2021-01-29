import os
import sys

import pygame


if __name__ == '__main__':
    sys.path.append(os.curdir)

    # Инициализация pygame
    pygame.init()
    # Инициализация mixer'а
    pygame.mixer.init(44100, -16, 12, 64)

    # Экран (он же будет использован везде)
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=True)

    # эти модули нужно импортировать именно тут,
    # т.к. в них происходит загрузка картинок, а в UI ещё и звуков.
    # (А это можно сделать только после инициализации pygame.mixer и экрана)
    import game
    from UI import start_screen

    # Выполнение действия по коду
    while 1:
        # Вызов начального экрана
        code = start_screen.execute(screen)
        if code == 0:
            break

        # Сид сохранения, который будет считан при запуске игры
        seed = None
        # Читаем файл сохранения, если он существует
        if os.path.isfile("data/save.txt"):
            with open('data/save.txt', 'r', encoding="utf-8") as file:
                seed = ' '.join(file.readlines())

        for level_number in range(1, 11):
            if not game.start(screen, level_number, seed):
                break

    # Закрытие pygame
    pygame.quit()
    pygame.mixer.quit()
