import pygame
from engine import load_image


class Button(pygame.sprite.Sprite):
    # Типы событий
    PRESS_TYPE = pygame.USEREVENT + 1
    HOVER_TYPE = pygame.USEREVENT + 2

    def __init__(self, position: tuple, text: str, text_size: int):
        super().__init__()

        # События, которые будут вызываться pygame внутри update
        # (с помощью sender_text будет определено какая кнопка нажата)
        self.PRESS_EVENT = pygame.event.Event(Button.PRESS_TYPE, {"sender_text": text})
        self.HOVER_EVENT = pygame.event.Event(Button.HOVER_TYPE, {"sender_text": text})

        self.image = load_image("button.png", path_to_folder="assets/UI")
        # Текст
        self.text = text
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), text_size)
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
                pygame.event.post(self.HOVER_EVENT)
            # Меняем изображение
            self.image = load_image("button_hover.png", path_to_folder="assets/UI")
        else:
            self.image = load_image("button.png", path_to_folder="assets/UI")

        # Заного выводим текст поверх кнопки
        self.image.blit(self.text_surface, self.text_surface.get_rect(center=self.image.get_rect().center))

