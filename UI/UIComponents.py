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

        # События, которые будут вызываться PyGame внутри update
        # (с помощью sender_text будет определено какая кнопка нажата)
        self.PRESS_EVENT = pygame.event.Event(Button.PRESS_TYPE, {"sender_text": text})
        self.HOVER_EVENT = pygame.event.Event(Button.HOVER_TYPE, {"sender_text": text})

        # Свойство, чтобы при наведении звук воспроизводился только один раз
        self.was_sound_played = False

        # Текст
        self.text = text
        self.font = pygame.font.Font("assets\\UI\\pixel_font.ttf", text_size)

        # Базовое изображение
        self.text_surface = self.font.render(text, True, pygame.Color("white"))
        self.base_image = load_image(base_button_filename, path_to_folder="assets\\UI")
        self.base_image.blit(self.text_surface, self.text_surface.get_rect(center=self.base_image.get_rect().center))

        # Изображение при наведении
        self.hover_image = load_image(hover_button_filename, path_to_folder="assets\\UI")
        self.hover_image.blit(self.text_surface, self.text_surface.get_rect(center=self.hover_image.get_rect().center))

        # Текущее изображение
        self.image = self.base_image
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
        text = text.strip()
        size = (max(int(text_size * 0.38 * max(map(len, text.split('\n')))), 300),
                round(indent + len(text.split('\n')) * self.font.get_height() * 0.9))
        self.image = scale_frame(self.image, size, indent)

        self.rect = self.image.get_rect()
        # Корректирование позиции в соответствии с размерами фона
        self.rect.center = position

        # Текст для диалога
        self.texts = text.split('\n')
        # Так нужно для вывода сразу нескольких строк
        self.text_surfaces = [self.font.render(part.strip(), True, (255, 255, 255)) for part in self.texts]

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

    # Задержка курсора на иконке перед показом рамки
    delay_time = 35

    # Иконки кнопок джойстика, чтобы отображать кнопки для вызова заклинаний
    size = (39, 39)
    JOYSTICK_ICONS = {
        "o": pygame.transform.scale(load_image("joystick_o.png", "assets\\UI\\icons"), size),
        "x": pygame.transform.scale(load_image("joystick_x.png", "assets\\UI\\icons"), size),
        "triangle": pygame.transform.scale(load_image("joystick_triangle.png", "assets\\UI\\icons"), size),
        "square": pygame.transform.scale(load_image("joystick_square.png", "assets\\UI\\icons"), size),
        "L1": pygame.transform.scale(load_image("joystick_L1.png", "assets\\UI\\icons"), size),
        "L2": pygame.transform.scale(load_image("joystick_L2.png", "assets\\UI\\icons"), size),
    }
    LOCKED = pygame.surface.Surface((20, 20)).convert_alpha()
    LOCKED.fill((0, 0, 0, 180))
    FRAME = load_image('spell_icon_frame.png', 'assets\\UI\\icons')

    def __init__(self, icon_filename: str, spell_class, player):
        self.spell_icon = load_image(icon_filename, "assets\\UI\\icons")
        self.rect = self.spell_icon.get_rect()
        self.w, self.h = self.spell_icon.get_size()

        # Картинка затемнения
        self.locked = pygame.transform.scale(self.LOCKED, (self.w, self.h))
        self.mana_cost = spell_class.mana_cost    # Стоимость заклинания для игрока
        self.player = player

        # Документация, которая будет показана в рамке при наведении
        self.information = f'''{spell_class.__doc__}

        Урон: {spell_class.damage}{f' + {spell_class.extra_damage}' if spell_class.__name__ == 'PoisonSpell' else ''}
        {'Время действия: ' + str(spell_class.action_time) + ' c' 
        if spell_class.__name__ in ('IceSpell', 'PoisonSpell') else 'Мгновенное действие'}
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
        pos = (x1 + 2, y1 + 18)    # Отступ по размерам края рамки
        screen.blit(self.spell_icon, pos)
        self.rect.topleft = pos

        # Отрисовка затемнения
        if self.player.mana < self.mana_cost or \
                pygame.time.get_ticks() - self.player.shoot_last_time < self.player.between_shoots_range:
            screen.blit(self.locked, pos)
        screen.blit(self.FRAME, position)

        # Смещение между иконкой заклинания и кнопкой для переключения
        pos = (x1 + 5, y1 + 14)
        # Если подключён джойстик, то рисуется специальная иконка кнопки
        if is_joystick:
            screen.blit(SpellContainer.JOYSTICK_ICONS[spell_key], pos)
        # Иначе просто текст кнопки клавиатуры
        else:
            button_text = SpellContainer.font.render(spell_key, True, (255, 255, 255))
            screen.blit(button_text, pos)

        # При наведении курсора на заклинание, рисуется табличка с информацией
        if self.rect.collidepoint(*self.player.scope.rect.center):
            if self.hover_time == self.delay_time:
                self.massage_box.rect.bottomleft = self.player.scope.rect.center
                self.massage_box.draw(screen)
            else:
                self.hover_time += 1
        elif self.hover_time:
            self.hover_time = 0

        # Отрисовка цены за заклинание в правом нижнем углу
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
    PLAYER_FACE = pygame.transform.scale2x(load_image('player_face.png', 'assets\\UI\\icons'))
    ASSISTANT_FACE = pygame.transform.scale2x(load_image('assistant_face.png', 'assets\\UI\\icons'))
    FRAME = load_image('player_icon_frame.png', 'assets\\UI\\icons')
    POISON_ICON = pygame.transform.scale(load_image('poison_icon.png', 'assets\\UI\\icons'), size)

    def __init__(self, player):
        self.player = player

    def draw(self, screen: pygame.surface.Surface, position=(0, 0), size_coefficient=1):
        """
        Рисует UI элемент на экране screen
        :param screen: Экран для отрисовки
        :param position: позиция отрисовки от левого верхнего угла экрана
        :param size_coefficient: Размер иконки
        """
        # Иконка заклинания
        x1, y1 = (0, 0)

        image = pygame.surface.Surface(self.FRAME.get_size(), pygame.SRCALPHA)
        health_length = round(264 * (self.player.health / self.player.full_health) + 0.5)
        health_line = pygame.surface.Surface((health_length, 24))
        health_line.fill((255, 30, 30))
        image.blit(health_line, (x1 + 132, y1 + 12))
        image.blit(self.font.render(f'{round(self.player.health + 0.5)}/{self.player.full_health}',
                                    True, (255, 255, 255)), (x1 + 220, y1 + 10))

        mana_length = round(264 * (self.player.mana / self.player.full_mana) + 0.5)
        mana_line = pygame.surface.Surface((mana_length, 24))
        mana_line.fill((30, 30, 255))
        image.blit(mana_line, (x1 + 132, y1 + 52))
        image.blit(self.font.render(f'{round(self.player.mana + 0.5)}/{self.player.full_mana}',
                                    True, (255, 255, 255)), (x1 + 220, y1 + 50))

        if self.player.__class__.__name__ == 'Player':
            screen.blit(self.font.render(f'{round(self.player.money)}', True, (255, 255, 30)),
                        (self.FRAME.get_width() + 20, 20))

            image.blit(self.PLAYER_FACE, (x1 + 25, y1 + 20))
        else:
            image.blit(self.ASSISTANT_FACE, (x1 + 25, y1 + 20))
        image.blit(self.FRAME, (x1, y1))

        text_surface = self.font.render('', True, (255, 255, 255))
        image.blit(text_surface, (x1 + 8, y1 + 14))
        screen.blit(pygame.transform.scale(image, (int(self.FRAME.get_width() * size_coefficient),
                                                   int(self.FRAME.get_height() * size_coefficient))), position)


class LogoImage(pygame.sprite.Sprite):
    """
    UI элемент с лого игры. Является классом,
    т.к. нужен не один раз."""

    def __init__(self, position: tuple, *args):
        super().__init__(*args)

        # Изображение
        self.image = load_image("game_logo.png", path_to_folder="assets\\UI")
        self.rect = self.image.get_rect()
        self.rect.center = position


class AnimatedBackground(pygame.sprite.Sprite):
    def __init__(self, filename: str, frames_start: int, frames_end: int, delay: int,
                 screen_size: tuple, path_to_folder="assets\\UI\\animated_backgrounds", scale_2n=False):
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
        self.current_frame_number = 0

        self.frames = []
        for frame_number in range(frames_start, frames_end + 1):
            frame = load_image(filename.format(frame_number),
                               path_to_folder=path_to_folder)
            if scale_2n:
                x, y = frame.get_size()
                while x < screen_size[0] and y < screen_size[1]:
                    frame = pygame.transform.scale(frame, (x * 2, y * 2))
                    x, y = frame.get_size()
            else:
                frame = pygame.transform.scale(frame, screen_size)
            self.frames.append(frame)

        self.last_update_time = -delay
        self.delay = delay

    def update(self):
        # Проверка для смены кадра
        if pygame.time.get_ticks() - self.last_update_time > self.delay:
            self.current_frame_number = (self.current_frame_number + 1) % len(self.frames)

            self.image = self.frames[self.current_frame_number]
            self.last_update_time = pygame.time.get_ticks()


class Message(pygame.sprite.Sprite):
    font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 32)
    # Время отрисовки на экране
    DRAWING_TIME = 1000
    # Время угасания, заимствующееся из времени отрисовки
    # (равное количество ставить не стоит)
    FADING_TIME = 500

    def __init__(self, screen, text, height):
        super().__init__()
        self.image = self.font.render(text, True, (255, 244, 79)).convert_alpha()
        self.rect = self.image.get_rect()
        self.last_collide_time = -self.DRAWING_TIME

        screen: pygame.surface.Surface
        self.rect.center = screen.get_width() // 2, int(height)

    def draw(self, screen):
        # Время, прошедшее с последнего вызова
        past_time = pygame.time.get_ticks() - self.last_collide_time
        if past_time <= self.DRAWING_TIME:
            if past_time >= self.DRAWING_TIME - self.FADING_TIME:
                # Коэффицент прозрачности, магическим образом вычисляющийся
                # из времени, прошедшего с последнего вызова, и времени угасания
                k = (past_time - self.DRAWING_TIME + self.FADING_TIME) / self.FADING_TIME
                self.image.set_alpha(255 - round(255 * k))
            else:
                self.image.set_alpha(255)

            screen.blit(self.image, self.rect.topleft)
