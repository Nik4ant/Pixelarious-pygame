import pygame
from engine import *
from config import *


class Player(pygame.sprite.Sprite):
    """
    Класс отвечающий за игрока
    """

    def __init__(self, x: float, y: float):
        # Конструктор класса Sprite
        super().__init__()

        # Remove this later
        self.width = self.height = TILE_SIZE // 4 * 3

        # Изображение
        # TODO: заменить на spritesheet
        # self.image = load_image("test_player.png", "assets")
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        # self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()

        # Начальное положение
        self.rect.x, self.rect.y = x, y
        # Скорость
        self.speed = PLAYER_SPEED
        self.dx = self.dy = 0

        # Направление взгляда
        # TODO: юзать при анимации
        self.look_direction_x = 0
        self.look_direction_y = 1

        # Дэш
        self.dash_direction_x = self.dash_direction_y = 0
        self.dash_force_x = self.dash_force_y = 0
        # TODO: зелье/свиток забабахать на силы ниже
        # сила дэша, которая устанавливается в самом начале
        # (является свойство объекта, т.к. может менятся)
        self.dash_force_base = 1.65
        # сила замедляющая дэш
        # (является свойство объекта, т.к. может менятся)
        self.dash_force_slower = 0.04
        # FIXME: это нормальный способ? (вряд ли)
        self.dash_last_time = pygame.time.get_ticks()

        # Инициализация прицеда для игрока
        self.scope = PlayerScope(self.rect.x - self.width, self.rect.y - self.height)
        # Установка начального состояния джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

    def update(self):
        # Обновляем состояние джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

        # TODO: некоторые вещи можно зарефакторить и вынести из if'а, но пока НУЖНО оставить так
        # Если джойстик подключен, то управление идёт с него
        if self.joystick:
            # Получение направления куда указываеют нажатые стрелки геймпада
            pads_x = self.joystick.get_button(13) * -1 + self.joystick.get_button(14)
            pads_y = self.joystick.get_button(11) * -1 + self.joystick.get_button(12)

            # Получение позиции правой оси у контроллера
            axis_right_x = self.joystick.get_axis(2)
            axis_right_y = self.joystick.get_axis(3)

            # Проверка на использование дэша
            if (self.joystick.get_button(CONTROLS["JOYSTICK_DASH"]) and
                    pygame.time.get_ticks() - self.dash_last_time > DASH_RELOAD_TIME):
                # Направления дэша
                # Для этого использется текущее направление, либо направление взгляда
                self.dash_direction_x, self.dash_direction_y = pads_x, pads_y

                # Если направление дэша не определено, берётся направление взгляда
                if self.dash_direction_x == 0 and self.dash_direction_y == 0:
                    self.dash_direction_x = self.look_direction_x
                    self.dash_direction_y = self.look_direction_y

                self.dash_force_x = self.dash_force_y = self.dash_force_base
                # Обновляем последнее время использования дэша
                self.dash_last_time = pygame.time.get_ticks()

            # Обработка дэша (если он был)
            if self.dash_force_x != 0 or self.dash_direction_y != 0:
                # Применение силы дэша
                self.dx = self.dash_force_x * self.dash_direction_x
                self.dy = self.dash_force_y * self.dash_direction_y
                # Естественное замедление дэша
                # Замедление по x
                if self.dash_force_x - self.dash_force_slower > 0:
                    self.dash_force_x -= self.dash_force_slower
                else:
                    self.dash_force_x = 0
                    self.dash_direction_x = 0
                # Замедление по y
                if self.dash_force_y - self.dash_force_slower > 0:
                    self.dash_force_y -= self.dash_force_slower
                else:
                    self.dash_force_y = 0
                    self.dash_direction_y = 0

            # Проверка, что было было движение
            if pads_x != 0 or pads_y != 0:
                # Если сейчас происходит дэш, то игрок не может его прервать.
                # Но он может дать дополнительное ускорение замедляющее или ускоряющее
                if self.dash_force_x != 0 or self.dash_force_y != 0:
                    self.dx += pads_x * (self.dash_force_base / self.speed * 2)
                    self.dy += pads_y * (self.dash_force_base / self.speed * 2)
                else:
                    self.dx, self.dy = pads_x, pads_y
                    self.look_direction_x, self.look_direction_y = pads_x, pads_y

            # Если движений джойстика нет и дэш не происходит,
            # то тогда обнуляем ускорение
            elif not (self.dash_force_x != 0 or self.dash_direction_y != 0):
                self.dx = self.dy = 0

            # Проверяем, что действительно игрок подвигал правую ось
            new_scope_x, new_scope_y = self.scope.rect.x, self.scope.rect.y
            if abs(axis_right_x) > JOYSTICK_SENSITIVITY or abs(axis_right_y) > JOYSTICK_SENSITIVITY:
                # Если игрок двигал правую ось, то прицел двигается по ней
                new_scope_x = self.scope.rect.x + self.scope.speed * axis_right_x
                new_scope_y = self.scope.rect.y + self.scope.speed * axis_right_y

            # Обновление прицела
            self.scope.update(new_scope_x, new_scope_y)

        # Иначе с клавиатуры
        else:
            # Список с клавишами
            keys = pygame.key.get_pressed()

            current_direction_x = float(float(int(keys[CONTROLS["KEYBOARD_LEFT"]]) * -1 +
                                        int(keys[CONTROLS["KEYBOARD_RIGHT"]])) * 0.5)
            current_direction_y = float(float(int(keys[CONTROLS["KEYBOARD_UP"]]) * -1 +
                                        int(keys[CONTROLS["KEYBOARD_DOWN"]])) * 0.5)

            self.dx = current_direction_x
            self.dy = current_direction_y

            # Если зажата клавиша бега, то игрок двигается быстрее
            self.dx *= 2 if keys[CONTROLS["KEYBOARD_RUN"]] else 1
            self.dy *= 2 if keys[CONTROLS["KEYBOARD_RUN"]] else 1

            # Обновляем состояние прицела
            self.scope.update(*pygame.mouse.get_pos())

        # Перемещение игрока относительно ускорения
        self.rect.x = self.rect.x + self.dx * self.speed
        self.rect.y = self.rect.y + self.dy * self.speed


class PlayerScope(pygame.sprite.Sprite):
    """
    # TODO: возможно переписать
    Этот класс отвечает за прицел игрока, относительно него будут
    выполнятся дэш и кастование заклинаний
    """
    def __init__(self, x: float, y: float):
        """
        # TODO: возможно дописать инфы
        Инициализация
        """

        # Конструктор класса Sprite
        super().__init__()
        self.width = self.height = TILE_SIZE / 4 * 2
        # TODO: заменить на нормальный спрайт
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(pygame.Color("blue"))
        self.rect = self.image.get_rect()
        # Начальное местоположение
        self.rect.x = x
        self.rect.y = y
        # Скорость перемещения
        # TODO: сделать как чуствительность у прицела
        self.speed = 15

    def update(self, *args):
        if args:
            # Где args[0] - позиция по x, а args[1] - позиция по y
            self.rect.x, self.rect.y = args[0], args[1]
