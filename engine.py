import os
import sys
import pygame
from PIL import Image
from random import randint, random

from config import TILE_SIZE, BACKGROUND_COLOR


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


def loading_screen(screen):
    width, height = screen.get_size()

    font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 48)
    for _ in range(1):
        for i in range(4):
            text = font.render('Загрузка' + '.' * i, True, (240, 240, 240))
            text_x = width // 2 - text.get_width() // 2
            text_y = height // 2 - text.get_height() // 2

            screen.fill(BACKGROUND_COLOR)
            screen.blit(text, (text_x, text_y))
            pygame.display.flip()

            pygame.time.wait(100)


def cut_sheet(sheet, columns, rows, size=(TILE_SIZE, TILE_SIZE)):
    frames = [[] for _ in range(rows)]
    rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            image = sheet.subsurface(pygame.Rect(frame_location, rect.size))
            image = pygame.transform.scale(image, size)
            frames[j].append(image)
    return frames


def load_image(filename: str, path_to_folder="assets", colorkey=None):
    fullname = concat_two_file_paths(path_to_folder, filename)
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


def load_tile(filename: str, size=(TILE_SIZE, TILE_SIZE)) -> pygame.surface.Surface:
    """
    Функция нужна для загрузки тайлов и их расширения до TILE_SIZE.
    (отдельно, т.к. при использовании load_image код выглядел бы некрасиво)
    :param filename: Имя файла с тайлом
    :param size: Размер возвращаемого изображения
    :return: Поверхность, растянутого изображение
    """
    image = load_image(filename, path_to_folder='assets\\tiles')
    image = pygame.transform.scale(image, size)
    return image


def scale_frame(image: pygame.surface.Surface, size: (int, int), k: int = 40):
    image = Image.frombytes('RGBA', image.get_size(), pygame.image.tostring(image, 'RGBA'))
    pix = image.load()

    new_image = Image.new('RGBA', size)
    new_pix = new_image.load()
    for j in range(size[1]):
        for i in range(size[0]):
            if i <= k:
                a = i
            elif k <= i <= size[0] - k:
                a = k + randint(0, 10)
            else:
                a = i - size[0] + image.size[0]

            if j <= k:
                b = j
            elif k <= j <= size[1] - k:
                b = k + randint(0, 10)
            else:
                b = j - size[1] + image.size[1]
            new_pix[i, j] = pix[a, b]

    return pygame.image.fromstring(new_image.tobytes(), size, 'RGBA')


# Функция, возвращающая случайное булевое значение с вводящимся шансом
def true_with_chance(percentage_chance: int = 50, seed: list = None, user_seed: list = None) -> bool:
    """
    Функция принимает целое число и переводит в коэффицент, 0 <= k <= 1.
    Затем генерирует случайное число с помощью функции рандом.
    Если случайное число меньше либо равно коэффиценту, функция возвращает True.
    Получившееся значение записывается в переданный сид (в виде числа 1 или 0, для краткости).

    :param percentage_chance: шанс выпадания значения True, в процентах
    :param seed: в сид записывается полученное значение
    :param user_seed: если пользовательский сид передан, значение берётся из него
    :return: булевое значение (True/False)
    """
    if user_seed and seed:
        is_true = int(user_seed[0])
        seed.append(user_seed[0])
        del user_seed[0]
    else:
        is_true = [0, 1][round(random() * 100) <= percentage_chance]
        if seed:
            seed.append(str(is_true))
    return is_true
