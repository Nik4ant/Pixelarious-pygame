import os
import sys

import pygame


if __name__ == '__main__':
    sys.path.append(os.curdir)

    # Инициализация pygame
    pygame.init()
    # Инициализация mixer'а
    pygame.mixer.init(44100, -16, 12, 64)

    # этот модуль нужно импортировать именно тут,
    # т.к. в нём происходит загрузка звуков (а это можно делать только
    # после инициализации pygame.mixer)
    from UI import start_screen

    # Экран (он же будет использован везде)
    # screen = pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=True)
    screen = pygame.display.set_mode((2200, 1200))

    # этот модуль нужно импортировать именно тут,
    # т.к. в нём происходит загрузка изображений (а это можно делать только
    # после установки экрана выше)
    import game

    # Вызов начального экрана
    code = start_screen.execute(screen)
    # Кортеж с действиями, которые зависят от кода из главного меню
    ACTIONS = (
        # выход из игры
        lambda: None,
        # Запуск игры
        lambda: game.start(screen),
        # TODO: туториал
        lambda: None,
        # TODO: настройки
        lambda: None,
    )
    # Выполнение действия по коду
    ACTIONS[code]()

    # Закрытие pygame
    pygame.quit()
    pygame.mixer.quit()
