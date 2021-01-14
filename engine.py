import os
import sys
import pygame


def check_any_joystick() -> bool:
    """
    Отдельная функция по проверке на наличие хоть одного джойстика
    :return: True, если джойстик подключён, False, если нет
    """
    return pygame.joystick.get_count() != 0


def get_joystick() -> pygame.joystick.Joystick:
    """
    Отдельная функция по получению одного подключённого джойстика
    :return: Джойстик
    """
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick


def concat_two_file_paths(path_to_folder: str, filename: str):
    """
    Т.к. в разных файлах очень часто нужно загрузить что-либо из ассетов, то
    для объединения пути до папки сделан отдельный метод здесь (чтобы каждый раз
    не импортировать модуль os)
    :param path_to_folder: Путь до папки с файлом
    :param filename: Название файла
    :return: Объединённый путь
    """
    return os.path.join(path_to_folder, filename)


# TODO: эта функция вводит Никиту в ступор, но он пока не придумал, что с ней сделать поэтому пусть будет тут
def loading_screen(screen):
    width, height = screen.get_size()
    screen.fill((20, 20, 20))
    # font = pygame.font.SysFont('Harrington', 35)
    font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 48)
    text = font.render('Loading...', True, (240, 240, 240))
    # text = load_image('loading_text.png', 'assets\\UI')
    # text = pygame.transform.scale(text, (192, 64))
    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))
    pygame.display.flip()
    pygame.time.wait(1000)


def load_image(filename: str, path_to_folder="assets", colorkey=None):
    fullname = os.path.join(path_to_folder, filename)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"ОШИБКА! Не удалось загрузить изображение {filename}")
        print(f"По пути {fullname}")
        sys.exit(-1)
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
