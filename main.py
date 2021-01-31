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
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN |pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=True)

    # эти модули нужно импортировать именно тут,
    # т.к. в них происходит загрузка картинок, а в UI ещё и звуков.
    # (А это можно сделать только после инициализации pygame.mixer и экрана)
    import game
    from UI import start_screen

    # До тех пор, пока игрок не выйдет из игры...
    code = -1
    while code != 0:
        # Вызов начального экрана
        code = start_screen.execute(screen)

        # Выполнение действия по коду
        if code != 0:
            # Сид сохранения, который будет считан при запуске игры
            seed = None
            # Номер уровня с которого начнётся игра
            level_number = 1

            # Читаем файл сохранения, если он существует
            if os.path.isfile("data\\save.txt"):
                with open('data\\save.txt', 'r', encoding="utf-8") as file:
                    seed = ' '.join(file.readlines())
                # Если seed пустой, то присваем ему None
                if not seed:
                    seed = None
                else:
                    data = seed.split('\n')
                    seed, level_number = '\n'.join(data[:-1]), int(data[-1])

            # Результат того, чем закончилась игра
            code = game.start(screen, level_number=level_number, user_seed=seed)

    # Закрытие pygame
    pygame.quit()
    pygame.mixer.quit()
