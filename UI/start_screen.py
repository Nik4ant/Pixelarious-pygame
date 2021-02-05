import pygame

from UI.UIComponents import Button, LogoImage, MessageBox
from config import FPS, CONTROLS, JOYSTICK_SENSITIVITY, DEFAULT_MUSIC_VOLUME
from engine import load_image, check_any_joystick, get_joystick, concat_two_file_paths

AUTHORS = """Никита Сошнев (Nik4ant)
Максим Рудаков (Massering)"""


def execute(screen: pygame.surface.Surface) -> int:
    """
    Функция запускает главное меню игры на переданном экране. В
    зависимости от действий возвращает свой код
    0 - была нажата кнопка выйти
    1 - была нажата кнопка играть
    :param screen: Экран на котором надо отрисовывать менюв
    :return: Код
    """
    is_open = True
    clock = pygame.time.Clock()
    joystick = get_joystick() if check_any_joystick() else None

    # Смещение между UI элементами
    button_margin = 55

    # Создание UI элементов
    game_logo = LogoImage((screen.get_width() // 2, screen.get_height() // 6 - button_margin))
    next_y = game_logo.rect.y + game_logo.rect.height + button_margin * 2

    button_play = Button((screen.get_width() // 2, next_y), "Играть", 32)
    next_y = button_play.rect.y + button_play.rect.height + button_margin

    button_controls = Button((screen.get_width() // 2, next_y), "Управление", 32)
    next_y = button_controls.rect.y + button_controls.rect.height + button_margin

    button_about = Button((screen.get_width() // 2, next_y), "Об игре", 32)
    next_y = button_about.rect.y + button_about.rect.height + button_margin

    button_authors = Button((screen.get_width() // 2, next_y), "Авторы", 32)
    next_y = button_authors.rect.y + button_authors.rect.height + button_margin

    button_exit = Button((screen.get_width() // 2, next_y), "Выйти", 32)

    # Добавление в группу
    UI_sprites = pygame.sprite.Group()
    UI_sprites.add(game_logo)
    UI_sprites.add(button_play)
    UI_sprites.add(button_controls)
    UI_sprites.add(button_about)
    UI_sprites.add(button_authors)
    UI_sprites.add(button_exit)

    # Текущие диалог (может появлятся при нажатии кнопок)
    current_message_box = None

    text = """На клавиатуре: 
    WASD - двигаться; Q - рывок;
    1-5 - заклинания; E - телепорт;

    На джойстике: 
    PADS - двигаться; R1 - рывок;
    Остальное я не знаю, подберите там;"""
    control_message_box = MessageBox(text, 32, (screen.get_width() * 0.5, screen.get_height() * 0.5))
    text = """
    Игра жанра Roguelite с видом сверху,
    в которой Вам предстоит пройти
    сквозь подземелье, заполненное врагами.
    Желаем удачи!"""
    about_message_box = MessageBox(text, 32, (screen.get_width() * 0.5, screen.get_height() * 0.5))

    authors_message_box = MessageBox(AUTHORS, 32, (screen.get_width() * 0.5, screen.get_height() * 0.5))

    # Фоновое изоюражение
    background_image = load_image("main_menu_BG.png", "assets/UI")
    # Меняем размер картинки в зависимости от размера экрана
    background_image = pygame.transform.scale(background_image,
                                              (screen.get_width(), screen.get_height()))

    # Делаем курсор мыши невидимым и загружаем вместо него своё изображение
    pygame.mouse.set_visible(False)
    cursor_image = load_image("cursor.png", "assets/UI/icons")
    # координаты курсора
    cursor_x, cursor_y = screen.get_width() * 0.5, screen.get_height() * 0.1
    cursor_speed = 30  # скорость курсора (нужно если используется джойстик)

    # Фоновая музыка
    pygame.mixer.music.load(concat_two_file_paths("assets/audio", "main_menu.ogg"))
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

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    was_click = True

            if event.type == Button.PRESS_TYPE:
                # Текст нажатой кнопки
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

                # Авторы
                elif sender_text == button_authors.text:
                    current_message_box = authors_message_box
                    current_message_box.need_to_draw = True

                # Проверяем какая кнопка была нажата
                elif sender_text == button_play.text:
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
                    return 1
                elif sender_text == button_exit.text:
                    # Музыка затухает (1 секунду), т.к. главный экран закроется
                    pygame.mixer.music.fadeout(1000)
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
