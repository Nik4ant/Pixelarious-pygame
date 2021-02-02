import pygame

from engine import load_image, concat_two_file_paths, scale_frame
from config import DEFAULT_HOVER_SOUND_VOLUME


class Button(pygame.sprite.Sprite):
    """
    Класс отвечающий за кнопку в UI элементах
    """

    # Типы событий
    PRESS_TYPE = pygame.USEREVENT + 1
    HOVER_TYPE = pygame.USEREVENT + 2
    # Звук при наведении
    HOVER_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "button_hover.wav"))
    HOVER_SOUND.set_volume(DEFAULT_HOVER_SOUND_VOLUME)

    def __init__(self, position: tuple, text: str, text_size: int,
                 base_button_filename="button.png",
                 hover_button_filename="button_hover.png", *args):
        super().__init__(*args)

        # События, которые будут вызываться pygame внутри update
        # (с помощью sender_text будет определено какая кнопка нажата)
        self.PRESS_EVENT = pygame.event.Event(Button.PRESS_TYPE, {"sender_text": text})
        self.HOVER_EVENT = pygame.event.Event(Button.HOVER_TYPE, {"sender_text": text})

        # Свойство, чтобы при наведении звук воспроизводился только один раз
        self.was_sound_played = False

        # Базовое изображение
        self.base_image = load_image(base_button_filename, path_to_folder="assets\\UI")
        # Изображение при наведении
        self.hover_image = load_image(hover_button_filename, path_to_folder="assets\\UI")
        # Текущее изображение
        self.image = self.base_image
        # Текст
        self.text = text
        self.font = pygame.font.Font("assets\\UI\\pixel_font.ttf", text_size)
        self.text_surface = self.font.render(text, True, pygame.Color("white"))
        # Выводим текст поверх кнопки
        self.image.blit(self.text_surface, self.text_surface.get_rect(center=self.image.get_rect().center))
        self.rect = self.image.get_rect()
        # Двигаем кнопку, но с учётом размера
        self.rect = self.rect.move(position[0] - self.rect.width / 2, position[1] - self.rect.height / 2)

    def update(self, scope_position: tuple, was_click: bool, *args) -> None:
        """
        Метод обновляет состояние кнопки. Если что-то произошло, то вызывается
        соответствующий метод, и меняется sprite (если нужно)
        :param scope_position: Кортеж координат курсора или
        прицела, если подключён джойстик
        :param was_click: Было ли произведено нажатие
        """
        # Проверяем наличие колизии курсора с кнопкой
        if self.rect.collidepoint(*scope_position):
            # Добавляем нужное событие в конец списка событий
            if was_click:
                pygame.event.post(self.PRESS_EVENT)
            else:
                # Если звук наведения не был воспроизведён, то он воспроизводится
                if not self.was_sound_played:
                    Button.HOVER_SOUND.play()
                    self.was_sound_played = True

                pygame.event.post(self.HOVER_EVENT)
            # Меняем изображение
            self.image = self.hover_image
        else:
            self.image = self.base_image
            # Т.к. на кнопку наведения нет, то сбрасываем свойство
            self.was_sound_played = False

        # Заного выводим текст поверх кнопки
        self.image.blit(self.text_surface, self.text_surface.get_rect(center=self.image.get_rect().center))


class MessageBox:
    """
    Класс представляющий диалог с сообщением, который закрывается
    при нажатии в любую область экрана
    """
    # Загружаем фоновое изображение
    background_image = load_image("dialog_box.png", "assets\\UI")

    def __init__(self, text: str, text_size: int, position: tuple):
        self.font = pygame.font.Font("assets\\UI\\pixel_font.ttf", text_size)

        # Фон
        self.image = self.background_image
        indent = 50
        size = (max(int(text_size * 0.38 * max(map(len, text.split('\n')))), 300),
                round(indent + len(text.split('\n')) * self.font.get_height() * 0.9))
        self.image = scale_frame(self.image, size, indent)

        self.rect = self.image.get_rect()
        # Корректирование позиции в соответствии с размерами фона
        self.rect.center = position

        # Текст для диалога
        self.texts = text.split('\n')
        # Так нужно для вывода сразу нескольких строк
        self.text_surfaces = [self.font.render(part, True, (255, 255, 255)) for part in self.texts]

        # Флаг для отрисовки (если True, то диалог рисуется)
        self.need_to_draw = True

    def update(self, was_click):
        if was_click:
            self.need_to_draw = False

    def draw(self, screen: pygame.surface.Surface):
        # Фоновое изображение
        screen.blit(self.image, self.rect.topleft)

        # Вывод текста
        margin = self.font.get_height() * 0.9
        # Чтобы избежать пустого отступа
        next_y = 20

        for text_surface in self.text_surfaces:
            y_pos = self.rect.top + next_y
            screen.blit(text_surface, text_surface.get_rect(midtop=(self.rect.centerx, y_pos)))
            next_y += margin


class SpellContainer:
    """
    Класс представляет UI элемент с отображением данных о заклинании.
    """

    # В этом случае фонт всегда будет общий у всех, поэтому это атрибут класса
    font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 32)
    mini_font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 16)

    delay_time = 50

    # Иконки кнопок джойстика, чтобы отображать кнопки для переключения заклиананий
    size = (13, 13)
    JOYSTICK_ICONS = {
        "o": pygame.transform.scale(load_image("joystick_o.png", "assets\\UI\\icons"), size),
        "x": pygame.transform.scale(load_image("joystick_x.png", "assets\\UI\\icons"), size),
        "triangle": pygame.transform.scale(load_image("joystick_triangle.png", "assets\\UI\\icons"), size),
        "square": pygame.transform.scale(load_image("joystick_square.png", "assets\\UI\\icons"), size),
        "L1": pygame.transform.scale(load_image("joystick_L1.png", "assets\\UI\\icons"), size),
    }
    LOCKED = load_image('transparent_grey.png', 'assets\\UI\\icons')
    FRAME = load_image('spell_icon_frame.png', 'assets\\UI\\icons')

    def __init__(self, icon_filename: str, spell_class, player):
        self.spell_icon = load_image(icon_filename, "assets\\UI\\icons")
        self.rect = self.spell_icon.get_rect()
        self.w, self.h = self.spell_icon.get_size()
        self.locked = pygame.transform.scale(SpellContainer.LOCKED, (self.w, self.h))
        self.mana_cost = spell_class.mana_cost
        self.player = player
        self.information = f'''{spell_class.__doc__}
        Урон: {spell_class.damage}{f' + {spell_class.extra_damage}' if spell_class.__name__ == 'PoisonSpell' else ''}
        Затраты маны: {spell_class.mana_cost}'''.strip()
        self.massage_box = MessageBox(self.information, 30, (0, 0))
        self.hover_time = 0

    def draw(self, screen: pygame.surface.Surface, position: tuple, is_joystick: bool, spell_key: str):
        """
        Рисует UI элемент на экране screen
        :param screen: Экран для отрисовки
        :param position: Позиция отрисовки
        :param is_joystick: Подключен ли джойстик
        :param spell_key: Строка, представляющая либо ключ для вывода иконки
        для джойстика, либо текст для вывода возле иконки заклинания
        """
        # Иконка заклинания
        x1, y1 = position
        pos = (x1 + 2, y1 + 18)
        screen.blit(self.spell_icon, pos)
        self.rect.topleft = pos
        if self.player.mana < self.mana_cost:
            screen.blit(self.locked, pos)
        screen.blit(self.FRAME, position)
        # Смещение между иконкой заклинания и кнопкой для переключения

        pos = (x1 + 10, y1 + 14)
        # Если подключён джойстик, то рисуется специальная иконка
        if is_joystick:
            screen.blit(SpellContainer.JOYSTICK_ICONS[spell_key], pos)
        # Иначе просто текст
        else:
            button_text = SpellContainer.font.render(spell_key, True, (255, 255, 255))
            screen.blit(button_text, pos)

        # При наведении курсора на заклинание, рисуется табличка с информацией
        if self.rect.collidepoint(*self.player.scope.rect.center):
            if self.hover_time >= self.delay_time:
                self.massage_box.rect.bottomleft = self.player.scope.rect.center
                self.massage_box.draw(screen)
            else:
                self.hover_time += 1
        else:
            self.hover_time = 0

        pos = (x1 + self.h - 6, y1 + self.w - 2)
        cost_text = SpellContainer.mini_font.render(str(self.mana_cost), True, (255, 255, 255))
        screen.blit(cost_text, pos)


class PlayerIcon:
    """
    Класс представляет UI элемент с отображением данных о заклинании.
    """
    # В этом случае фонт всегда будет общий у всех, поэтому это атрибут класса
    font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 32)
    # Иконки кнопок джойстика, чтобы отображать кнопки для переключения заклиананий
    size = (40, 40)
    FACE = pygame.transform.scale2x(load_image('elf_face.png', 'assets\\UI\\icons'))
    FRAME = load_image('player_icon_frame.png', 'assets\\UI\\icons')
    POISON_ICON = pygame.transform.scale(load_image('poison_icon.png', 'assets\\UI\\icons'), size)

    def __init__(self, position: tuple, player):
        self.position = position
        self.player = player

    def draw(self, screen: pygame.surface.Surface):
        """
        Рисует UI элемент на экране screen
        :param screen: Экран для отрисовки
        """
        # Иконка заклинания
        x1, y1 = self.position

        health_line = pygame.sprite.Sprite()
        health_length = round(260 * (self.player.health / self.player.full_health) + 0.5)
        health_line.image = pygame.surface.Surface((health_length, 24))
        health_line.image.fill((255, 30, 30))
        screen.blit(health_line.image, (x1 + 136, y1 + 12))
        screen.blit(self.font.render(f'{round(self.player.health + 0.5)}/{self.player.full_health}', True, (255, 255, 255)), (x1 + 220, y1 + 10))

        mana_line = pygame.sprite.Sprite()
        mana_length = round(260 * (self.player.mana / self.player.full_mana) + 0.5)
        mana_line.image = pygame.surface.Surface((mana_length, 24))
        mana_line.image.fill((30, 30, 255))
        screen.blit(mana_line.image, (x1 + 136, y1 + 52))
        screen.blit(self.font.render(f'{round(self.player.mana + 0.5)}/{self.player.full_mana}', True, (255, 255, 255)), (x1 + 220, y1 + 50))

        screen.blit(self.FACE, (x1 + 25, y1 + 20))
        screen.blit(self.FRAME, self.position)

        pos = (self.position[0] + 8, self.position[1] + 14)
        text_surface = self.font.render('', True, (255, 255, 255))
        screen.blit(text_surface, pos)


class LogoImage(pygame.sprite.Sprite):
    """
    UI элемент с лого игры. Является классом,
    т.к. нужен не один раз."""

    def __init__(self, position: tuple, *args):
        super().__init__(*args)

        # Изображение
        self.image = load_image("game_logo.png", path_to_folder="assets\\UI")
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position


class AnimatedBackground(pygame.sprite.Sprite):
    def __init__(self, filename: str, frames_start: int, frames_end: int, delay: int,
                 screen_size: tuple, path_to_folder="assets\\UI\\animated_backgrounds"):
        """
        Инициализация
        :param filename: Имя файла в виде f строки для замены номера кадра
        :param frames_start: Номер первого кадра в папке
        :param frames_end: Количество кадров, до которого
        нужно воспроизводить анимацию
        :param delay: Задержка между сменой кадров
        :param screen_size: Размеры экрана
        :param path_to_folder: Путь до папки с кадрами
        """

        super().__init__()
        self.current_frame_number = frames_start
        # Номер первого и последнего кадров
        self.frames_start = frames_start
        self.frames_end = frames_end
        # Пути
        self.base_filename = filename
        self.path_to_folder = path_to_folder

        self.screen_size = screen_size
        self.image = load_image(self.base_filename.format(self.current_frame_number),
                                path_to_folder=self.path_to_folder)
        self.image = pygame.transform.scale(self.image, self.screen_size)

        self.last_update_time = pygame.time.get_ticks()
        self.delay = delay

    def update(self):
        # Проверка для смены кадра
        if pygame.time.get_ticks() - self.last_update_time > self.delay:
            self.current_frame_number += 1
            if self.current_frame_number > self.frames_end:
                # Переводим счётчик на начало
                self.current_frame_number = self.frames_start

            self.image = load_image(self.base_filename.format(self.current_frame_number),
                                    path_to_folder=self.path_to_folder)
            self.image = pygame.transform.scale(self.image, self.screen_size)
            self.last_update_time = pygame.time.get_ticks()
