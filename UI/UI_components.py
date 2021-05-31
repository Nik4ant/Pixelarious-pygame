import pygame

from engine import load_image, load_sound, scale_frame, load_game_font
from config import DEFAULT_HOVER_SOUND_VOLUME


class Button(pygame.sprite.Sprite):
    """Класс, представляющий кнопку в UI элементах"""

    # Типы событий
    PRESS_TYPE = pygame.USEREVENT + 1
    HOVER_TYPE = pygame.USEREVENT + 2
    # Звук при наведении
    HOVER_SOUND = load_sound("assets/audio/sfx/UI/button_hover.wav")

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
        self.font = load_game_font(text_size)
        # Базовое изображение
        self.text_surface = self.font.render(text, True, pygame.Color("white"))
        self.base_image = load_image(f"assets/sprites/UI/components/{base_button_filename}")
        self.base_image.blit(self.text_surface, self.text_surface.get_rect(center=self.base_image.get_rect().center))
        # Изображение при наведении
        self.hover_image = load_image(f"assets/sprites/UI/components/{hover_button_filename}")
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
    Класс, представляющий диалог с сообщением, который закрывается
    при нажатии в любую область экрана
    """
    # Загружаем фоновое изображение
    background_image = load_image("assets/sprites/UI/components/dialog_box.png")

    def __init__(self, text: str, text_size: int, position: tuple):
        self.font = load_game_font(text_size)  # шрифт
        self.image = self.background_image  # фон
        indent = 50  # Отступ
        text = text.strip()
        # Высчитывание размера для фона
        size = (max(int(text_size * 0.38 * max(map(len, text.split('\n')))), 300),
                round(indent + len(text.split('\n')) * self.font.get_height() * 0.9))
        # Отмасштабированый фон с текстурой для красоты
        self.image = scale_frame(self.image, size, indent)
        self.rect = self.image.get_rect()
        self.rect.center = position  # местоположение
        # Текст для диалога
        self.texts = text.split('\n')
        # Так нужно для вывода сразу нескольких строк
        self.text_surfaces = [self.font.render(part.strip(), True, (255, 255, 255))
                              for part in self.texts]
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
        # Следующая позиции y (по началу, просто отступ от самого верха)
        next_y = 20
        # Отрисовка поверхностей с текстом
        # (каждая поверхность - отдельная строка)
        for text_surface in self.text_surfaces:
            y_pos = self.rect.top + next_y
            screen.blit(text_surface, text_surface.get_rect(midtop=(self.rect.centerx, y_pos)))
            next_y += margin


class SpellContainer:
    """Класс представляет UI элемент с отображением данных о заклинании"""

    # В этом случае шрифт всегда будет общий у всех, поэтому это атрибут класса
    font = load_game_font(32)
    mini_font = load_game_font(16)
    # Задержка курсора на иконке перед показом рамки
    delay_time = 35
    size = (39, 39)  # размер для иконок ниже
    # Иконки кнопок джойстика, чтобы отображать кнопки для вызова заклинаний
    JOYSTICK_ICONS = {
        "o": load_image("assets/sprites/UI/icons/joystick_o.png", size),
        "x": load_image("assets/sprites/UI/icons/joystick_x.png", size),
        "triangle": load_image("assets/sprites/UI/icons/joystick_triangle.png", size),
        "square": load_image("assets/sprites/UI/icons/joystick_square.png", size),
        "L1": load_image("assets/sprites/UI/icons/joystick_L1.png", size),
        "L2": load_image("assets/sprites/UI/icons/joystick_L2.png", size),
    }
    # Поверхность, которая отображается, если заклинание недоступно
    # (т.е. эффект замедления)
    LOCKED = pygame.surface.Surface((20, 20)).convert_alpha()
    LOCKED.fill((0, 0, 0, 180))
    # Рамка (фон) вокруг иконки с заклинанием
    FRAME = load_image('assets/sprites/UI/icons/spell_icon_frame.png')

    def __init__(self, icon_filename: str, spell_class, player):
        # Иконка заклинания
        self.spell_icon = load_image(f"assets/sprites/UI/icons/{icon_filename}")
        self.rect = self.spell_icon.get_rect()
        self.w, self.h = self.spell_icon.get_size()  # размер иконки
        # Картинка затемнения
        self.locked = pygame.transform.scale(self.LOCKED, (self.w, self.h))
        self.mana_cost = spell_class.mana_cost    # Стоимость заклинания для игрока
        # ссылка на игрока для получение параметров, связанных с заклинаниями
        self.player = player
        # Информация, которая будет показана в рамке при наведении
        self.information = f'''{spell_class.__doc__}

        Урон: {spell_class.damage}{f' + {spell_class.extra_damage}' if spell_class.__name__ == 'PoisonSpell' else ''}
        {'Время действия: ' + str(spell_class.action_time) + ' c' 
        if spell_class.__name__ in ('IceSpell', 'PoisonSpell') else 'Мгновенное действие'}
        Затраты маны: {spell_class.mana_cost}'''.strip()
        # Диалоговое окно для вывода информации при наведении
        self.massage_box = MessageBox(self.information, 30, (0, 0))
        # время наведения, нужное для определение того, когда надо
        # отрисовать окно с информацией
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
        x1, y1 = position  # координаты для отрисовки
        pos = (x1 + 2, y1 + 18)    # учёт отступа по размерам края рамки
        self.rect.topleft = pos
        # Иконка заклинания
        screen.blit(self.spell_icon, pos)
        # Отрисовка затемнения, елси заклинание сейчас недоступно
        if self.player.mana < self.mana_cost or \
                pygame.time.get_ticks() - self.player.shoot_last_time < self.player.between_shoots_range:
            screen.blit(self.locked, pos)
        # Отрисовка рамки вокруг иконки заклинания
        screen.blit(self.FRAME, position)
        # Смещение между иконкой заклинания и кнопкой для переключения
        pos = (x1 + 5, y1 + 14)
        # Если подключён джойстик, то рисуется специальная иконка элемента,
        # которая активирует заклинание
        if is_joystick:
            screen.blit(SpellContainer.JOYSTICK_ICONS[spell_key], pos)
        # Иначе просто текст кнопки с клавиатуры
        else:
            button_text = SpellContainer.font.render(spell_key, True, (255, 255, 255))
            screen.blit(button_text, pos)
        # При наведении курсора на заклинание, рисуется табличка с информацией
        if self.rect.collidepoint(*self.player.scope.rect.center):
            # Если время наведения на иконку с заклинанием привысело порог, то
            # информация выводится
            if self.hover_time == self.delay_time:
                # Смещение окошка в сторону прицела и отрисовка
                self.massage_box.rect.bottomleft = self.player.scope.rect.center
                self.massage_box.draw(screen)
            else:
                self.hover_time += 1
        elif self.hover_time:
            self.hover_time = 0
        # Отрисовка цены маны за заклинание в правом нижнем углу
        pos = (x1 + self.h - 6, y1 + self.w - 2)  # позиция
        cost_text = SpellContainer.mini_font.render(str(self.mana_cost), True,
                                                    (255, 255, 255))  # цена
        screen.blit(cost_text, pos)


class PlayerIcon:
    """
    Класс, представляющий UI элемент с отображением данных об игроке
    или компаньёне
    """
    # В этом случае фонт всегда будет общий у всех, поэтому это атрибут класса
    font = load_game_font(32)
    # Изображение с иконкой игрока
    PLAYER_FACE = pygame.transform.scale2x(load_image('assets/sprites/UI/icons/player_face.png'))
    # Изображение с иконкой помошника
    ASSISTANT_FACE = pygame.transform.scale2x(load_image('assets/sprites/UI/icons/assistant_face.png'))
    # Рамка вокруг иконки
    FRAME = load_image('assets/sprites/UI/icons/player_icon_frame.png')
    # Иконка яда
    size = (40, 40)
    POISON_ICON = load_image('assets/sprites/UI/icons/poison_icon.png', size)

    def __init__(self, player_or_assistant):
        # Ссылка на игрока (или асистента) для получение необходимоых
        # параметров, таких как: здоровье, мана и т.п.
        self.player_or_assistant = player_or_assistant

    def draw(self, screen: pygame.surface.Surface, position=(0, 0), size_coefficient=1):
        """
        Рисует UI элемент на экране screen
        :param screen: Экран для отрисовки
        :param position: позиция отрисовки от левого верхнего угла экрана
        :param size_coefficient: Коэффицент размера иконки
        """
        # Позиция
        x1, y1 = (0, 0)
        # Пустое изображение всей иконки, куда будут отрисовываться части ниже
        image = pygame.surface.Surface(self.FRAME.get_size(), pygame.SRCALPHA)
        # Высчитывание длинны полосы здоровья
        health_length = round(264 * (self.player_or_assistant.health / self.player_or_assistant.full_health) + 0.5)
        # Поверхность со здоровьем
        health_line = pygame.surface.Surface((health_length, 24))
        health_line.fill((255, 30, 30))
        # Отрисовка полоски со здоровьем и количества здоровья
        image.blit(health_line, (x1 + 132, y1 + 12))
        image.blit(self.font.render(f'{round(self.player_or_assistant.health + 0.5)}/' +
                                    f'{self.player_or_assistant.full_health}',
                                    True, (255, 255, 255)), (x1 + 220, y1 + 10))
        # Высчитывание длинны полосы маны
        mana_length = round(264 * (self.player_or_assistant.mana / self.player_or_assistant.full_mana) + 0.5)
        # Поверхность с маной
        mana_line = pygame.surface.Surface((mana_length, 24))
        mana_line.fill((30, 30, 255))
        # Отрисовка полоски с маной и количества маны
        image.blit(mana_line, (x1 + 132, y1 + 52))
        image.blit(self.font.render(f'{round(self.player_or_assistant.mana + 0.5)}/' +
                                    f'{self.player_or_assistant.full_mana}',
                                    True, (255, 255, 255)), (x1 + 220, y1 + 50))
        # Если текущая иконка относится к игроку
        if self.player_or_assistant.__class__.__name__ == 'Player':
            screen.blit(self.font.render(f'{round(self.player_or_assistant.money)}', True, (255, 255, 30)),
                        (self.FRAME.get_width() + 20, 20))
            image.blit(self.PLAYER_FACE, (x1 + 25, y1 + 20))
        else:
            image.blit(self.ASSISTANT_FACE, (x1 + 25, y1 + 20))
        # Отрисовка фона (рамки) на иконку
        image.blit(self.FRAME, (x1, y1))
        # Отрисовка пустого текста на иконке
        # (для смещения, т.е. по сути это декоративный эффект)
        text_surface = self.font.render('', True, (255, 255, 255))
        image.blit(text_surface, (x1 + 8, y1 + 14))
        # Вывод всей иклггки на экран с учётом коэффицента размера
        screen.blit(pygame.transform.scale(image, (int(self.FRAME.get_width() * size_coefficient),
                                                   int(self.FRAME.get_height() * size_coefficient))), position)


class LogoImage(pygame.sprite.Sprite):
    """
    UI элемент с лого игры. Является классом,
    т.к. лого используется не 1 раз.
    """

    def __init__(self, position: tuple, *args):
        super().__init__(*args)
        # Изображение
        self.image = load_image("assets/sprites/UI/components/game_logo.png")
        self.rect = self.image.get_rect()
        self.rect.center = position


class AnimatedBackground(pygame.sprite.Sprite):
    """
    Класс, представляющий анимированный фон
    (НЕ ИСПОЛЬЗОВАТЬ НА БОЛЬШОМ КОЛИЧЕСТВЕ КАДРОВ!)
    """

    def __init__(self, filename: str, path_to_folder: str, frames_start: int,
                 frames_end: int, delay: int, screen_size: tuple, scale_2n=False):
        """
        :param filename: Имя файла в виде f строки для замены номера кадра
        :param path_to_folder: Путь до папки с кадрами
        :param frames_start: Номер первого кадра в папке
        :param frames_end: Количество кадров, до которого
        нужно воспроизводить анимацию
        :param delay: Задержка между сменой кадров
        :param screen_size: Размер экрана
        :param scale_2n: Нужно ли увеличивать размер фона в двое относительно экрана,
        т.е. так, чтобы фон не входил целиком в экран (по умолчанию False)
        """
        super().__init__()

        self.current_frame = frames_start  # текущий кадр
        self.path_to_folder = path_to_folder  # путь до папки
        self.screen_size = screen_size  # размеры экрана
        self.filename = filename  # файла с местом для замены номера кадра
        self.frames_end = frames_end  # номер последнего кадра
        self.frames_start = frames_start  # номер начального кадра
        # Нужно ли увеличивать размер фона в двое относительно экрана,
        # т.е. так, чтобы фон не входил целиком в экран
        self.scale_2n = scale_2n
        self.last_update_time = -delay  # последнее время обновления
        self.delay = delay  # задержка между сменой кадров
        # Список со всеми кадрами
        self.frames = [self.load_frame(i) for i in range(self.frames_start, self.frames_end + 1)]

    def load_frame(self, frame_number: int) -> pygame.surface.Surface:
        """
        Метод загружает кадр анимации по переданному номеру
        :param frame_number: Номер кадра
        :return: Поверхность загруженного кадра
        """
        frame = load_image(f"{self.path_to_folder}/{self.filename.format(frame_number)}")
        # Отдельное масштабирование кадра, если необходимо
        if self.scale_2n:
            width, height = frame.get_size()
            # Вычисление коэффицента для масштабирования и само масштабирование
            coefficient = max(round(self.screen_size[0] / width + 0.5),
                              round(self.screen_size[1] / height + 0.5))
            frame = pygame.transform.scale(frame, (width * coefficient, height * coefficient))
        # Иначе просто приведение размера к размеру экрана
        else:
            frame = pygame.transform.scale(frame, self.screen_size)
        return frame

    def update(self):
        # Проверка для смены кадра
        if pygame.time.get_ticks() - self.last_update_time > self.delay:
            # Изменение изображения
            self.image = self.frames[self.current_frame]
            self.current_frame = (self.current_frame + 1) % self.frames_end
            # Обновление времени смены кадра
            self.last_update_time = pygame.time.get_ticks()


class Message(pygame.sprite.Sprite):
    """
    Класс, представляющий текстовое сообщение появляющиеся при сталкивании
    с каким-либо объектом. Сами колизии и параметр времени последнего столкновения
    обрабатываются вне класса
    """
    font = load_game_font(32)
    # Время отрисовки на экране
    DRAWING_TIME = 1000
    # Время угасания, заимствующееся из времени отрисовки
    # (равное количество ставить не стоит)
    FADING_TIME = 500

    def __init__(self, screen: pygame.surface.Surface,
                 text: str, height: int):
        super().__init__()
        # Изображение
        self.image = self.font.render(text, True, (255, 244, 79)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = screen.get_width() // 2, int(height)
        # Последнее время столкновения
        self.last_collide_time = -self.DRAWING_TIME

    def draw(self, screen):
        # Время, прошедшее с последнего вызова отрисовки
        past_time = pygame.time.get_ticks() - self.last_collide_time
        # Учёт времени, для отрисовки сообщения
        if past_time <= Message.DRAWING_TIME:
            # Обработка эффекта затухании, по мере удаления от объекта
            if past_time >= Message.DRAWING_TIME - Message.FADING_TIME:
                # Коэффицент прозрачности, вычисляющийся из времени,
                # прошедшего с последнего вызова, и времени угасания сообщения
                k = (past_time - Message.DRAWING_TIME + Message.FADING_TIME) / Message.FADING_TIME
                self.image.set_alpha(255 - round(255 * k))
            else:
                self.image.set_alpha(255)

            screen.blit(self.image, self.rect.topleft)
