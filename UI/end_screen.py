import os

import pygame

from UI.UI_components import LogoImage, AnimatedBackground
from engine import load_image, load_game_font, get_joystick, check_any_joystick
from config import JOYSTICK_CURSOR_SPEED, JOYSTICK_SENSITIVITY, CONTROLS


def execute(screen: pygame.surface.Surface, money: int,
            count_of_alive_assistants: int, is_win=False):
    """
    Функция запускает конечной экран (либо смерти, либо победы)
    :param screen: Экран на котором надо отрисовывать менюв
    :param is_win: Флаг, выиграл ли игрок
    :param money: Количество собранных игроком и асистентом денег
    :param count_of_alive_assistants: Количетсво всех живых осистентов к концу игры
    игры
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
    # Получение джойстика (если есть) и определение начальной позиции курсора
    if check_any_joystick():
        joystick = get_joystick()
        cursor_x, cursor_y = screen.get_rect().center
    else:
        joystick = None
        # Т.к. джойстика нет позиция будет сразу переопределна далее,
        # поэтому тут начальная позиция не задаётся
        cursor_x, cursor_y = 0, 0
    # Т.к. игрок завершил игру, то файл с сохранением будет перезаписан
    if os.path.isfile("data/save.txt"):
        with open('data/save.txt', 'r+', encoding="utf-8") as file:
            file.truncate(0)
    # Кортеж с текстом который надо вывести (каждый элемент на новой строке)
    texts = (f"Деньги собранные игроком вместе с асистентом: {money}",
             f"Количество живых асистентов: {count_of_alive_assistants}")
    # Шрифт для поверхностей ниже
    title_font = load_game_font(64)
    # Поверхности с одним и тем же текстом, но разный цвет делает крассивый эффект
    text_surfaces_yellow = [title_font.render(part.strip(), True, (255, 184, 50))
                            for part in texts]
    text_surfaces_red = [title_font.render(part.strip(), True, (179, 64, 16))
                         for part in texts]
    # Смещение между наложенными поверхностями для красивого эффекта
    surfaces_offset = 3
    margin = title_font.get_height() * 0.9  # отступ между двумя поверхностями
    # События, которые активируют закрытие экрана с концном
    QUITING_EVENTS = (pygame.QUIT, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, )
    # Цикл меню
    while is_open:
        # Обработка событий
        for event in pygame.event.get():
            if event.type in QUITING_EVENTS:
                is_open = False
                break
        # Обновление позиции курсора
        if joystick is not None:
            # Проверка на выход
            if joystick.get_button(CONTROLS["JOYSTICK_UI_CLICK"]):
                break
            # Значение осей на левом стике
            axis_x, axis_y = joystick.get_axis(0), joystick.get_axis(1)
            # Перемещение курсора при движении оси
            if abs(axis_x) >= JOYSTICK_SENSITIVITY:
                cursor_x += JOYSTICK_CURSOR_SPEED * axis_x
            if abs(axis_y) >= JOYSTICK_SENSITIVITY:
                cursor_y += JOYSTICK_CURSOR_SPEED * axis_y
        else:
            cursor_x, cursor_y = pygame.mouse.get_pos()
        # На экране проигрыша есть фон, которого нет на экране победы
        if not is_win:
            screen.fill((31, 30, 36))
        # Вывод текущего кадра фонового изображения
        animated_background.update()
        screen.blit(animated_background.image,
                    animated_background.image.get_rect(center=screen.get_rect().center))
        # Вывод картинки победного заголовка, если игрок выиграл
        if is_win:
            # Анализатор может ругаться, но если is_win истина, то
            # переменные 100% объявлены выше
            screen.blit(title_you_win, you_win_rect)
        # следущая позиция по y (будет нужно при вычислении смещения)
        next_y = 20
        # Вывод красного текста
        for text_surface in text_surfaces_red:
            y_pos = screen.get_height() * 0.6 + next_y
            screen.blit(text_surface, text_surface.get_rect(midtop=(screen.get_rect().centerx + surfaces_offset,
                                                                    y_pos + surfaces_offset)))
            next_y += margin
        next_y = 20
        # Вывод жёлтого текста
        for text_surface in text_surfaces_yellow:
            y_pos = screen.get_height() * 0.6 + next_y
            screen.blit(text_surface, text_surface.get_rect(midtop=(screen.get_rect().centerx, y_pos)))
            next_y += margin
        # Вывод логотипа игры
        screen.blit(logo.image, logo.rect.topleft)
        # Вывод изображения курсора
        screen.blit(cursor_image, (cursor_x, cursor_y))

        # Обновление состояния джойстика
        joystick = get_joystick() if check_any_joystick() else None
        pygame.display.flip()
