import os

import pygame

from engine import load_image, concat_two_file_paths
from config import DEFAULT_HOVER_SOUND_VOLUME


class Button(pygame.sprite.Sprite):
    """
    Класс отвечающий за кнопку в UI элементах
    """

    # Типы событий
    PRESS_TYPE = pygame.USEREVENT + 1
    HOVER_TYPE = pygame.USEREVENT + 2
    # Звук при наведении
    HOVER_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/audio", "button_hover.wav"))
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
        self.base_image = load_image(base_button_filename, path_to_folder="assets/UI")
        # Изображение при наведении
        self.hover_image = load_image(hover_button_filename, path_to_folder="assets/UI")
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


class Message_box:
    """
    Класс представляющий диалог с сообщением, который закрывается
    при нажатии в любую область экрана
    """

    def __init__(self, text: str, text_size: int, position: tuple):
        # Фон
        self.image = load_image("dialog_box.png", path_to_folder="assets/UI")
        size = (round(self.image.get_width() * 1.2),
                round(self.image.get_height() * 1.2))
        self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = self.image.get_rect()
        # Корректирование позиции в соответствии с размерами фона
        self.rect = self.rect.move(position[0] - self.image.get_width() * 0.5,
                                   position[1] - self.image.get_height() * 0.5)
        # Текст для диалога
        self.texts = text.split('\n')
        self.font = pygame.font.Font("assets\\UI\\pixel_font.ttf", text_size)
        # Так нужно для вывода сразу нескольких строк
        self.text_surfaces = [self.font.render(part, True, pygame.Color("white")) for part in self.texts]

        # Флаг для отрисовки (если True, то диалог рисуется)
        self.need_to_draw = True

    def update(self, was_click=False):
        if was_click:
            self.need_to_draw = False

    def draw(self, screen: pygame.surface.Surface):
        # Фоновое изображение
        screen.blit(self.image, self.rect)

        # Вывод текста
        MARGIN = 24
        # Чтобы избежать пустого отступа
        next_y = 0

        for text_surface in self.text_surfaces:
            y_pos = self.rect.centery + next_y - text_surface.get_height()
            screen.blit(text_surface, text_surface.get_rect(center=(self.rect.centerx, y_pos)))
            next_y += MARGIN


class Logo_image(pygame.sprite.Sprite):
    def __init__(self, position: tuple, *args):
        super().__init__(*args)

        # Изображение
        self.image = load_image("game_logo.png", path_to_folder="assets/UI")
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
