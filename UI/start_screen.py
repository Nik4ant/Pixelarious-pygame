import pygame
from os.path import exists

from UI.UI_components import Button, LogoImage, MessageBox
from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY, JOYSTICK_CURSOR_SPEED, DEFAULT_MUSIC_VOLUME
from engine import load_image, check_any_joystick, get_joystick


def execute(screen: pygame.surface.Surface) -> int:
    """
    Функция запускает главное меню игры на переданном экране. В
    зависимости от действий возвращает свой код, описанный в main.py
    :param screen: Экран, на котором надо отрисовывать меню
    :return: Код
    """
    is_open = True
    clock = pygame.time.Clock()
    joystick = get_joystick() if check_any_joystick() else None

    # Смещение между ui элементами
    button_margin = 55

    screen_center = screen.get_width() // 2
    # Создание ui элементов
    game_logo = LogoImage((screen_center, screen.get_height() // 6 - button_margin))
    next_y = game_logo.rect.y + game_logo.rect.height + button_margin * 2

    button_play = Button((screen_center, next_y), "Играть", 32)
    next_y = button_play.rect.y + button_play.rect.height + button_margin
    # Если файла сохранения нет (т.е. игрок играет в первый раз), то эта кнопка
    # выделяется caps lock'ом (выделяются кнопки "управление" и "об игре")
    button_controls = Button((screen_center, next_y), "Управление" if exists('data/save.txt') else "УПРАВЛЕНИЕ", 32)
    next_y = button_controls.rect.y + button_controls.rect.height + button_margin

    button_about = Button((screen_center, next_y), "Об игре" if exists('data/save.txt') else "ОБ ИГРЕ", 32)
    next_y = button_about.rect.y + button_about.rect.height + button_margin

    button_exit = Button((screen_center, next_y), "Выйти", 32)
    # Добавление в группу
    ui_sprites = pygame.sprite.Group()
    ui_sprites.add(game_logo)
    ui_sprites.add(button_play)
    ui_sprites.add(button_controls)
    ui_sprites.add(button_about)
    ui_sprites.add(button_exit)
    # Текущие диалог (может появлятся при нажатии кнопок)
    current_message_box = None
    # Текст появляющийся в сообщении при нажатии на кнопку "управление"
    control_text = """На клавиатуре: 
    WASD/Стрелки направлений - Двигаться
    Shift - Рывок
    1-5 - Заклинания атаки
    Space - Заклинание телепорта

    На джойстике PS4 (проводном): 
    PADS - Двигаться
    R1 - Рывок
    Заклинания см. на иконках
    """
    control_message_box = MessageBox(control_text, 32, (screen_center, screen.get_height() * 0.5))
    # Текст появляющийся в сообщении при нажатии на кнопку "об игре"
    about_text = """
    Pixelarious
Игра была создана как проект на тему PyGame для Яндекс Лицея.
Игра жанра Rogulite, поэтому смерть в игре перманентна.
Чтобы победить, надо пройти 10 уровней подземелья.
Чтобы убивать врагов, нужно использовать заклинания (см. управление).
Играть можно как на клавиутуре, так и на проводном джойстике от PS4.
Управление показывается внутри игры на главном окне при нажатии на кнопку "Управление". 
Его РЕКОМЕНДУЕТСЯ прочитать перед началом игры.
Ещё ОБЯЗАТЕЛЬНО посмотрите ОСОБЕННОСТИ заклинаний, НАВЕДЯ НА ИКОНКУ заклинания внизу.

Удачи в прохождении!
"""
    about_message_box = MessageBox(about_text, 32, (screen_center, screen.get_height() * 0.5))
    # Фоновое изоюражение
    background_image = load_image("assets/sprites/UI/backgrounds/main_menu_BG.png")
    # Меняем размер картинки в зависимости от размера экрана
    background_image = pygame.transform.scale(background_image, screen.get_size())
    # Делаем курсор мыши невидимым и загружаем вместо него своё изображение
    pygame.mouse.set_visible(False)
    cursor_image = load_image("assets/sprites/UI/icons/cursor.png")
    # координаты курсора
    cursor_x, cursor_y = screen_center, screen.get_height() * 0.1
    # Фоновая музыка
    pygame.mixer.music.load("assets/audio/music/main_menu.ogg")
    # Воспроизведение музыки вечно
    pygame.mixer.music.play(-1)
    # Установка громкости
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)
    # Цикл окна
    while is_open:
        # Переменная, становящайся True если было нажатие курсора
        # (предусмотрен как джойстик, так и обычная мышка)
        was_click = False
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_open = False
            # Мышь
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                was_click = True
            # Клавиши
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_RETURN):
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
                    return 1
                if event.key == CONTROLS["KEYBOARD_PAUSE"]:
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
                    return 0
            # Кастомное событие нажатия на кнопку
            if event.type == Button.PRESS_TYPE:
                # Текст нажатой кнопки (нужно для определения какая кнопка нажата
                # (гарантированно есть, т.к. устанавливается при инициализации)
                sender_text = event.dict["sender_text"]
                # Управление
                if sender_text == button_controls.text:
                    current_message_box = control_message_box
                    current_message_box.need_to_draw = True
                # Об игре
                elif sender_text == button_about.text:
                    current_message_box = about_message_box
                    current_message_box.need_to_draw = True
                # Играть
                elif sender_text == button_play.text:
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
                    return 1
                # Выход
                elif sender_text == button_exit.text:
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
                    return 0

        # Определение местоположения для курсора
        if joystick:
            axis_x, axis_y = joystick.get_axis(0), joystick.get_axis(1)
            if abs(axis_x) >= JOYSTICK_SENSITIVITY:
                cursor_x += JOYSTICK_CURSOR_SPEED * axis_x
            if abs(axis_y) >= JOYSTICK_SENSITIVITY:
                cursor_y += JOYSTICK_CURSOR_SPEED * axis_y
            # Проверка на нажатие
            was_click = joystick.get_button(CONTROLS["JOYSTICK_UI_CLICK"])
        else:
            cursor_x, cursor_y = pygame.mouse.get_pos()
        cursor_position = cursor_x, cursor_y

        # Обновляем все ui элементы
        ui_sprites.update(cursor_position, was_click)
        # Фоновое изобраджение
        screen.blit(background_image, (0, 0))
        # Рисуем весь ui
        ui_sprites.draw(screen)
        # Если есть диалог, то его тоже обновляем и рисуем
        if current_message_box:
            if current_message_box.need_to_draw:
                current_message_box.draw(screen)
            current_message_box.update(was_click)
        # Рисуем курсор поверх всего
        screen.blit(cursor_image, cursor_position)
        pygame.display.flip()
        # Обновляем состояние джойстика
        joystick = get_joystick() if check_any_joystick() else None
        clock.tick(FPS)
    return 0
