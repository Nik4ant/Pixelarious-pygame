import sys

import pygame

from UI.UIComponents import Button
from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY
from engine import load_image, check_any_joystick, get_joystick


def execute(screen: pygame.surface.Surface):
    """
    Функция запускает меню игры на паузе на переданном экране. В
    зависимости от действий закрывает всю игру, либо продолжает дальше
    :param screen: Экран на котором надо отрисовывать менюв
    :return: Возвращает -1, если игру надо закрыть, None если нет
    """
    is_open = True
    clock = pygame.time.Clock()
    joystick = get_joystick() if check_any_joystick() else None

    # Смещение между UI элементами
    UI_MARGIN = 20
    # Фоновое изображение для всего экрана
    background_image = load_image("pause_menu_BG.png", "assets/UI")
    background_image = pygame.transform.scale(background_image, screen.get_size())
    # Фоновое игображение
    ui_background_image = load_image("pause_menu_UI_BG.png", "assets/UI")
    # Центральная координата всего меню на экране
    menu_top_left = (screen.get_width() * 0.5 - ui_background_image.get_width() * 0.5,
                     screen.get_height() * 0.5 - ui_background_image.get_height() * 0.5)

    # Создание UI элементов
    next_y = menu_top_left[1] + ui_background_image.get_width() * 0.5 - UI_MARGIN * 2.5
    button_continue = Button((screen.get_width() // 2, next_y),
                             "Продолжить", 32,
                             base_button_filename="button_1.png",
                             hover_button_filename="button_1_hover.png")

    next_y += button_continue.rect.width * 0.5 + UI_MARGIN
    button_exit = Button((screen.get_width() // 2, next_y),
                         "Выйти из игры", 32,
                         base_button_filename="button_1.png",
                         hover_button_filename="button_1_hover.png")

    # Добавление в группу
    UI_sprites = pygame.sprite.Group()
    UI_sprites.add(button_continue)
    UI_sprites.add(button_exit)

    # Текущие диалог (может появлятся при нажатии кнопок)
    current_message_box = None
    # Изображение для курсора
    cursor_image = load_image("cursor.png", "assets/UI/icons")
    # координаты курсора
    cursor_x, cursor_y = screen.get_rect().center
    cursor_speed = 25  # скорость курсора (нужно если используется джойстик)

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

                # Продолжить
                if sender_text == button_continue.text:
                    is_open = False
                    UI_sprites.empty()  # удаление всех спрайтов в группе
                    break

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

        # Фоновое изображение окна
        screen.blit(background_image, (0, 0))
        # Фоновое изобраджение UI
        screen.blit(ui_background_image, menu_top_left)
        # Рисуем весь UI
        UI_sprites.draw(screen)
        # Если есть диалог, то его тоже обновляем и рисуем
        if current_message_box:
            current_message_box.update(was_click)
            if current_message_box.need_to_draw:
                current_message_box.draw(screen)

        # Рисуем курсор поверх всего
        screen.blit(cursor_image, cursor_position)
        pygame.display.flip()

        # Обновляем состояние джойстика
        joystick = get_joystick() if check_any_joystick() else None
        clock.tick(FPS)
