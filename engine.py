import os
from random import randint, random

import pygame
from PIL import Image

from config import TILE_SIZE, BACKGROUND_COLOR, DEFAULT_SOUNDS_VOLUME


def check_any_joystick() -> bool:
    """
    Отдельная функция по проверке на наличие хоть одного джойстика
    :return: True, если джойстик подключён, False, если нет
    """
    return pygame.joystick.get_count() != 0


def get_joystick() -> pygame.joystick.Joystick:
    """
    Функция по получению одного иницилизированного джойстика
    :return: Джойстик
    """
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    return joystick


def loading_screen(screen: pygame.surface.Surface) -> None:
    """
    Функция, устанавливающая псевдо загрузочный экран
    :param screen: Поверхность с экраном, где отрисовывается экран загрузки
    """
    # Центральная точка на экране для вывода текста
    central_point = (screen.get_width() * 0.5, screen.get_height() * 0.5)
    # Шрифт для текста
    font = load_game_font(font_size=48)
    for i in range(4):
        text = font.render('Загрузка' + '.' * i, True, (240, 240, 240))
        # Вывод фона и текста
        screen.fill(BACKGROUND_COLOR)
        screen.blit(text, (central_point[0] - text.get_width() * 0.5,
                           central_point[1] - text.get_height() * 0.5))
        pygame.display.flip()
        # Задержка в милисекундах
        pygame.time.wait(100)


def cut_sheet(sheet: pygame.surface.Surface,
              columns: int, rows: int, size=(TILE_SIZE, TILE_SIZE)) -> list:
    """
    Функция нарезает spritesheet на кадры по переданным пвраметрам
    :param sheet: Поверхность с загруженным spritesheet'ом
    :param columns: Количество колонок для нарезки
    :param rows: Количество строк для нарезки
    :param size: Размер к которому маштабируется каждый кадр
    (по умолчанию размер тайла)
    :return: Вложенный список с кадрами
    """
    # Ширина и длинна по которой будет делаться вырезка
    cut_size = (sheet.get_width() // columns, sheet.get_height() // rows)
    # Нарезанные кадры
    frames = [[cut_sprite(sheet, i, j, size, cut_size) for i in range(columns)]
              for j in range(rows)]
    return frames


def cut_sprite(sheet: pygame.surface.Surface, col: int,
               row: int, sprite_size: tuple, cut_size: tuple) -> pygame.surface.Surface:
    """
    Функция вырезает один спрайт из spritesheet'а
    :param sheet: Сам spritesheet
    :param col: Номер колонки спрайта
    :param row: Номер строки спрайта
    :param sprite_size: Размер к которому надо отмаштабировать спрайт
    :param cut_size: Размер вырезаемой части из spritesheet'а
    :return: Поверхность вырезанного спрайта
    """
    # Позиция левого верхнего угла спрайта
    frame_location = (cut_size[0] * col, cut_size[1] * row)
    # Вырезка спрайта и его масштабирование
    image = sheet.subsurface(pygame.Rect(frame_location, cut_size))
    return pygame.transform.scale(image, sprite_size)


def load_image(path_to_image: str, size=None, colorkey=None) -> pygame.surface.Surface:
    """
    Функция загружает изображение
    :param path_to_image: Путь до изображения
    :param size: Рамзер для маштабирования (по умолчанию оригинальный размер)
    :param colorkey: Цветовой ключ для фона (по умолчанию используется alpha канал)
    :return: Поверхность загруженного изображения
    """
    # Если файла не существует, то исключение
    if not os.path.isfile(path_to_image):
        raise FileNotFoundError(f"""Не удалось загрузить изображение по пути {path_to_image}""")
    image = pygame.image.load(path_to_image)
    # Если цветовой ключ для фона не передан, используется alpha канал
    if colorkey is not None:
        image = image.convert()
        # Если не передан цвет, а -1, то берётся цвет левого верхнего пикселя
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    # Если передан размер, то масшабируем изображение под него
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


def load_game_font(font_size: int) -> pygame.font.Font:
    """
    Функция загружает игровой шрифт, который везде одинаковый
    :param font_size: Размер шрифта
    :return: Шрифт
    """
    return pygame.font.Font('assets\\pixel_font.ttf', font_size)


def load_sound(path_to_sound: str, volume: float = DEFAULT_SOUNDS_VOLUME) -> pygame.mixer.Sound:
    """
    Функция загружает звук и устанавливаем ему громкость
    (нужно для частоты кода)
    :param path_to_sound: Путь до файла со звуком
    :param volume: Уровень громкости (по умолчанию громкость из config.py)
    :return: Загруженный звук
    """
    sound = pygame.mixer.Sound(path_to_sound)
    sound.set_volume(volume)
    return sound


def scale_frame(image: pygame.surface.Surface,
                size: (int, int), k: int = 40) -> pygame.surface.Surface:
    """
    Функция масшабирует фон (рамку) к размеру <= размеру image, добавляя
    ему красивую текстуру
    :param image: Изображение фона
    :param size: Размер, к которому будет приведено изображение (но при этом
    этот размер <= размеру image
    :param k: Параметр для задания текстуры
    :return: Новое изображение
    """
    # Получение пикселец текущего изображения
    image = Image.frombytes('RGBA', image.get_size(),
                            pygame.image.tostring(image, 'RGBA'))
    pix = image.load()
    # Новое иизображение
    new_image = Image.new('RGBA', size)
    new_pix = new_image.load()
    # Итерация по пикселям текущего изображения и придание им текстуры
    # + масштабирование к размеру <= размеру image
    for j in range(size[1]):
        for i in range(size[0]):
            # Вычисления ниже нужны для придачи текстуры изображению. Так, в
            # сравнении с обычным уменьшеным изображением, оно будет выглядит красивее

            # Вычисление ряда пикселя
            if i <= k:
                a = i
            elif k <= i <= size[0] - k:
                a = k + randint(0, 10)
            else:
                a = i - size[0] + image.size[0]
            # Вычесление колонки пикселя
            if j <= k:
                b = j
            elif k <= j <= size[1] - k:
                b = k + randint(0, 10)
            else:
                b = j - size[1] + image.size[1]
            # Запись пикселя по вычисленной позиции
            new_pix[i, j] = pix[a, b]
    return pygame.image.fromstring(new_image.tobytes(), size, 'RGBA')


# Функция, возвращающая случайное булевое значение с переданным шансом
def true_with_chance(percentage_chance: float = 50.0,
                     seed: list = None, user_seed: list = None) -> bool:
    """
    Функция принимает целое число и переводит в коэффицент, 0 <= k <= 1.
    Затем генерирует случайное число с помощью функции рандом.
    Если случайное число меньше либо равно коэффиценту, функция возвращает True.
    Получившееся значение записывается в переданный сид (в виде числа 1 или 0, для краткости).
    :param percentage_chance: шанс получения значения True, в процентах
    :param seed: Сид, куда записывается полученное значение
    :param user_seed: пользовательский сид (если передан, значение берётся
    из него, по умолчанию None)
    :return: True либо False
    """
    if user_seed and seed:
        is_true = int(user_seed[0])
        seed.append(user_seed[0])
        del user_seed[0]
    else:
        is_true = [0, 1][random() * 100 <= percentage_chance]
        if seed:
            seed.append(str(is_true))
    return bool(is_true)
