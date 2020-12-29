# FIXME: I need something like that (maybe): https://stackoverflow.com/a/64791087/13940541
import os
import sys

import pygame


if __name__ == '__main__':
    sys.path.append(os.curdir)

    # Инициализация pygame
    pygame.init()
    # Инициализация mixer'а
    pygame.mixer.init()

    # этот модуль нужно импортировать именно тут,
    # т.к. в нём происходит загрузка звуков (а это можно делать только
    # после инициализации pygame.mixer)
    import start_screen

    # Экран (он же будет использован везде)
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)

    # этот модуль нужно импортировать именно тут,
    # т.к. в нём происходит загрузка изображений (а это можно делать только
    # после установки экрана выше)
    import game

    # Вызов начального экрана
    code = start_screen.execute(screen)
    # Словарь с действиями, которые зависят от кода из главного меню
    ACTIONS = {
        1: lambda: game.start(screen),
        # TODO:
        2: lambda: None,
        # TODO:
        3: lambda: None,
        # так и должно быть, т.к. это выход из игры
        -1: lambda: None,
    }
    # Выполнение действия по коду
    ACTIONS[code]()
    # Закрытие pygame
    pygame.quit()
