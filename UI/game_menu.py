import pygame

from UI.UI_components import Button, AnimatedBackground
from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY
from engine import load_image, check_any_joystick, get_joystick, scale_frame


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
    margin = 20
    # Фоновое изображение для всего экрана
    background_image = AnimatedBackground("pause_menu_BG_{0}.png", "assets/sprites/UI/backgrounds/pause_BG",
                                          1, 45, 25, screen.get_size())
    menu_width, menu_height = 280, 360
    # Фоновое игображение
    background_menu_image = scale_frame(load_image("assets/sprites/UI/backgrounds/pause_menu_UI_BG.png"),
                                        (menu_width, menu_height))
    # Центральная координата всего меню на экране
    menu_top_left = (screen.get_width() * 0.5 - menu_width * 0.5,
                     screen.get_height() * 0.25)
    # Группа со спрайтами интерфейса
    UI_sprites = pygame.sprite.Group()
    # Создание кнопок
    next_y = menu_top_left[1] + margin * 3.5  # позиция y следущего элемента
    titles = ("Продолжить", "Начать заново", "Выйти в меню")  # заголовки кнопок
    for number in range(len(titles)):
        # Текущая кнопка
        button = Button((screen.get_width() // 2, next_y), titles[number], 32,
                        base_button_filename="button_1.png",
                        hover_button_filename="button_1_hover.png")
        # Высчитывание следущей позиции по y со смещением
        next_y += button.rect.height + margin
        # Добавление в группу
        UI_sprites.add(button)
    # Изображение для курсора
    cursor_image = load_image("assets/sprites/UI/icons/cursor.png")
    # координаты курсора
    cursor_x, cursor_y = screen.get_rect().center
    cursor_speed = 40  # скорость курсора (нужно если используется джойстик)
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

            if event.type == pygame.KEYDOWN:
                if event.key == CONTROLS["KEYBOARD_PAUSE"]:
                    is_open = False
                    UI_sprites.empty()  # удаление всех спрайтов в группе
                    break

            if event.type == Button.PRESS_TYPE:
                # Текст нажатой кнопки
                # (гарантированно есть, т.к. устанавливается при инициализации)
                sender_text = event.dict["sender_text"]

                # Продолжить
                if sender_text == titles[0]:
                    is_open = False
                    UI_sprites.empty()  # удаление всех спрайтов в группе
                    break
                # Начать заного
                if sender_text == titles[1]:
                    return 1
                # Выход
                if sender_text == titles[-1]:
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
        background_image.update()
        screen.blit(background_image.image, (0, 0))
        # Фоновое изобраджение UI
        screen.blit(background_menu_image, menu_top_left)
        # Рисуем весь UI
        UI_sprites.draw(screen)
        # Рисуем курсор поверх всего
        screen.blit(cursor_image, cursor_position)
        pygame.display.flip()
        # Обновляем состояние джойстика
        joystick = get_joystick() if check_any_joystick() else None
        clock.tick(FPS)
