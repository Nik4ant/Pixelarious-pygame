import os

import pygame

from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY, DEFAULT_MUSIC_VOLUME

from engine import load_image, check_any_joystick, get_joystick
from UI.UIComponents import Button


# TODO: возврат в main того, что будет регулировать дальнейшие действия?
def execute(screen: pygame.surface.Surface) -> int:
    """
    Функция запускает главное меню игры на переданном экране. В
    зависимости от действий возвращает свой код\n
    0 - была нажата кнопка выйти\n
    1 - была нажата кнопка играть\n
    2 - была нажата кнопка туториал\n
    3 - была нажата кнопка найстроки\n
    :param screen: Экран на котором надо отрисовывать менюв
    :return: Код
    """
    is_open = True
    clock = pygame.time.Clock()
    joystick = get_joystick() if check_any_joystick() else None

    # Создание UI элементов
    # Кнопки
    BUTTONS_MARGIN = 55

    button_play = Button((screen.get_width() // 2, screen.get_height() // 4), "Играть", 32)
    next_y = button_play.rect.y + button_play.rect.height + BUTTONS_MARGIN

    button_tutorial = Button((screen.get_width() // 2, next_y), "Обучение", 32)
    next_y = button_tutorial.rect.y + button_tutorial.rect.height + BUTTONS_MARGIN

    button_settings = Button((screen.get_width() // 2, next_y), "Настройки", 32)
    next_y = button_settings.rect.y + button_settings.rect.height + BUTTONS_MARGIN

    button_exit = Button((screen.get_width() // 2, next_y), "Выйти", 32)

    # Добавление в группу
    UI_sprites = pygame.sprite.Group()
    UI_sprites.add(button_play)
    UI_sprites.add(button_tutorial)
    UI_sprites.add(button_settings)
    UI_sprites.add(button_exit)

    # Фоновое изоюражение
    background_image = load_image("main_menu_BG.png", "assets/UI")
    # Меняем размер картинки в зависимости от размера экрана
    pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    # Делаем курсор мыши невидимым и загружаем вместо него своё изображение
    pygame.mouse.set_visible(False)
    cursor_image = load_image("cursor.png", "assets/UI/icons")
    # координаты курсора
    cursor_x, cursor_y = screen.get_width() * 0.5, screen.get_height() * 0.1
    cursor_speed = 30  # скорость курсора (нужно если используется джойстик)

    # Фоновая музыка
    pygame.mixer.music.load(os.path.join("assets/audio", "main_menu.ogg"))
    # Воспроизведение музыки вечно
    pygame.mixer.music.play(-1)
    # Установка громкости
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    # Цикл окна
    while is_open:
        # Переменная, которая становится True если была нажата левая клавиша
        # или соответствующая кнопка на геймпаде
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
                # Музыка затухает (1 секунду), т.к. главный экран закроется
                pygame.mixer.music.fadeout(1000)

                # Текст нажатой кнопки
                # (гарантированно есть, т.к. устанавливается при инициализации)
                sender_text = event.dict["sender_text"]
                # Проверяем какая кнопка была нажата
                if sender_text == button_play.text:
                    return 1
                elif sender_text == button_tutorial.text:
                    return 2
                elif sender_text == button_settings.text:
                    # TODO: либо вызывать меню с настройками явно (но это потом)
                    return 3
                elif sender_text == button_exit.text:
                    return 0

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

        # Фоновое изобраджение
        screen.blit(background_image, (0, 0))

        # Рисуем весь UI
        UI_sprites.draw(screen)

        # Рисуем курсор поверх всего
        screen.blit(cursor_image, cursor_position)

        pygame.display.flip()

        # Обноыляем состояние джойстика
        joystick = get_joystick() if check_any_joystick() else None

        clock.tick(FPS)