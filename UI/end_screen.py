import sys

import pygame

from UI.UIComponents import Button, LogoImage, AnimatedBackground
from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY
from engine import load_image, check_any_joystick, get_joystick


def execute(screen: pygame.surface.Surface, is_win=False):
    """
    Функция запускает конечной экран (либо смерти, либо победы)
    :param screen: Экран на котором надо отрисовывать менюв
    :param is_win: Флаг, выиграл ли игрок
    """

    is_open = True
    clock = pygame.time.Clock()
    joystick = get_joystick() if check_any_joystick() else None

    # Фоновое изображение для всего экрана
    if not is_win:
        animated_background = AnimatedBackground("death_{0}.png", 1, 23, 60, screen.get_size())
    else:
        animated_background = AnimatedBackground("win_{0}.png", 1, 23, 60, screen.get_size())

    # Лого игры
    logo = LogoImage((screen.get_width() * 0.5, screen.get_height() * 0.1))

    # Кнопка возвращения в меню
    button_exit = Button((screen.get_width() // 2, screen.get_height() * 0.9),
                         "Вернутся в меню", 32,
                         base_button_filename="button_1.png",
                         hover_button_filename="button_1_hover.png")

    # Добавление в группу
    UI_sprites = pygame.sprite.Group()
    UI_sprites.add(logo)
    UI_sprites.add(button_exit)

    # Изображение для курсора
    cursor_image = load_image("cursor.png", "assets/UI/icons")
    # координаты курсора
    cursor_x, cursor_y = screen.get_rect().center
    cursor_speed = 15  # скорость курсора (нужно если используется джойстик)

    # Цикл меню
    while is_open:
        # Переменная, становящайся True если было нажатие курсора
        # (предусмотрен как джойстик, так и обычная мышка)
        was_click = False

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_open = False
                break

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    was_click = True

            if event.type == Button.PRESS_TYPE:
                # Текст нажатой кнопки
                # (гарантированно есть, т.к. устанавливается при инициализации)
                sender_text = event.dict["sender_text"]

                # Выход
                if sender_text == button_exit.text:
                    return -1

        # Определение местоположения для курсора
        if joystick:
            axis_x, axis_y = joystick.get_axis(0), joystick.get_axis(1)
            cursor_x += cursor_speed * axis_x if abs(axis_x) >= JOYSTICK_SENSITIVITY else 0
            cursor_y += cursor_speed * axis_y if abs(axis_y) >= JOYSTICK_SENSITIVITY else 0
            # Проверка на нажатие
            was_click = joystick.get_button(CONTROLS["JOYSTICK_UI_CLICK"])
        else:
            cursor_x, cursor_y = pygame.mouse.get_pos()

        cursor_position = (cursor_x, cursor_y)
        # Обновляем все UI элементы
        UI_sprites.update(cursor_position, was_click)

        # Очистка экрана
        screen.fill((0, 0, 0))

        animated_background.update()
        # Вывод текущего кадра фонового изображения
        screen.blit(animated_background.image, (0, 0))

        # Рисуем весь UI
        UI_sprites.draw(screen)

        # Рисуем курсор поверх всего
        screen.blit(cursor_image, cursor_position)
        pygame.display.flip()

        # Обновляем состояние джойстика
        joystick = get_joystick() if check_any_joystick() else None
        clock.tick(FPS)
