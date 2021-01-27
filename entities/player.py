from math import *

from entities.base_entity import Entity
from entities.spells import *
from engine import *
from config import *


class Player(Entity):
    """
    Класс отвечающий за игрока
    """

    # Кадры для анимации игрока
    size = (TILE_SIZE * 7 // 8, TILE_SIZE)
    frames = cut_sheet(load_image('player_sprite_sheet.png', 'assets'), 4, 4, size)
    death_frames = []

    # Словарь типа (направлениями взгляда): *индекс ряда в frames для анимации*
    look_directions = {
        (-1, -1): 3,
        (-1, 0): 3,
        (0, -1): 1,
        (-1, 1): 3,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 2,
        (1, 0): 2,
        (1, 1): 2
    }

    # время перезарядки заклинания в миллисекундах
    spell_reload_time = 1000
    
    # время перезарядки дэша в миллисекундах
    dash_reload_time = 2000
    # сила дэша, которая устанавливается в самом начале
    dash_force_base = 1.8
    # сила замедляющая дэш со временем
    dash_force_slower = 0.04

    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 1.96
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 2
    # сила с которой игрок будет набирать/уменьшать свою скорость
    delta_changer = 0.06

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/audio", "footstep.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    DASH_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets/audio", "dash.wav"))
    DASH_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x: float, y: float, all_sprites, *args):
        # Конструктор класса Entity
        super().__init__(x, y, all_sprites, *args)

        # Ширина и высота изображения после инициализации
        self.width, self.height = self.image.get_size()

        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Скорость
        self.speed = TILE_SIZE * 50
        self.dx = self.dy = 0
        self.distance_to_player = 0.0001
        self.health = 300
        self.full_health = self.health

        # Группа со спрайтами заклинаний
        self.spells = pygame.sprite.Group()
        self.shoot_last_time = pygame.time.get_ticks()

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

        # Дэш
        self.dash_direction_x = self.dash_direction_y = 0
        self.dash_force_x = self.dash_force_y = 0

        # Время последнего использования дэша
        # (Нужно для определения перезарядился дэш или нет)
        self.dash_last_time = pygame.time.get_ticks()

        self.wand = PlayerWand(all_sprites)

        # Инициализация прицеда для игрока
        self.scope = PlayerScope(x, y)
        # Установка начального состояния джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

    def update(self):
        # Обновляем состояние джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

        # Ниже переменные, нужные для общей обработки игрока внезависимости от
        # типа управления (геймпад/клавиатура)

        # Новая позиция для прицела игрока (по умолчанию изменений нет)
        new_scope_x, new_scope_y = self.scope.rect.centerx, self.scope.rect.centery

        # Если джойстик подключен, то управление идёт с него
        if self.joystick:
            # Получение направления куда указываеют нажатые стрелки геймпада
            current_direction_x = self.joystick.get_button(13) * -1 + self.joystick.get_button(14)
            current_direction_y = self.joystick.get_button(11) * -1 + self.joystick.get_button(12)

            # Получение позиции правой оси у контроллера
            axis_right_x = self.joystick.get_axis(2)
            axis_right_y = self.joystick.get_axis(3)

            # Проверка на использование дэша
            # Переменная отвечает за проверку на то, была ли нажата кнопка дэша.
            # (Но нет гарантии того, что дэш уже перезарядился, это проверяется при использовании)
            was_dash_activated = self.joystick.get_button(CONTROLS["JOYSTICK_DASH"])

            # Проверяем, что действительно игрок подвигал правую ось
            if (abs(axis_right_x) > JOYSTICK_SENSITIVITY or
                    abs(axis_right_y) > JOYSTICK_SENSITIVITY):
                # Если игрок двигал правую ось, то прицел двигается по ней
                new_scope_x = self.scope.rect.centerx + self.scope.speed * axis_right_x
                new_scope_y = self.scope.rect.centery + self.scope.speed * axis_right_y
        # Иначе с клавиатуры
        else:
            # Список с клавишами
            keys = pygame.key.get_pressed()

            # Направления движения по x и y
            current_direction_x = int(int(keys[CONTROLS["KEYBOARD_LEFT"]]) * -1
                                      + int(keys[CONTROLS["KEYBOARD_RIGHT"]]))
            current_direction_y = int(int(keys[CONTROLS["KEYBOARD_UP"]]) * -1
                                      + int(keys[CONTROLS["KEYBOARD_DOWN"]]))

            # Проверка на использование дэша
            was_dash_activated = keys[CONTROLS["KEYBOARD_DASH"]]

            # Позиция для прицела
            new_scope_x, new_scope_y = pygame.mouse.get_pos()

        # Обработка активации дэша
        if (was_dash_activated and pygame.time.get_ticks() -
                self.dash_last_time > Player.dash_reload_time):
            self.dash_force_x = self.dash_force_y = self.dash_force_base
            # Обновляем время последнего использования дэша
            self.dash_last_time = pygame.time.get_ticks()
            # Определение направления для дэша.
            if current_direction_x != 0 or current_direction_y != 0:
                self.dash_direction_x = current_direction_x
                self.dash_direction_y = current_direction_y
            else:
                self.dash_direction_x = self.look_direction_x
                self.dash_direction_y = self.look_direction_y

            # Установка силы дэша
            self.dx = self.dash_force_x * self.dash_direction_x
            self.dy = self.dash_force_y * self.dash_direction_y

            # Звук для дэша
            if Player.sounds_channel.get_busy():
                # Проверка нужна, чтобы не прервать собственный звук дэша
                if Player.sounds_channel.get_sound() != Player.DASH_SOUND:
                    Player.sounds_channel.get_sound().stop()
                    Player.sounds_channel.play(Player.DASH_SOUND)
            else:
                Player.sounds_channel.play(Player.DASH_SOUND)

        # Обработка силы дэша, действующей на игрока
        # по x
        if self.dash_force_x > self.dash_force_slower:
            self.dash_force_x -= self.dash_force_slower
            self.dx = self.dash_force_x * self.dash_direction_x
        else:
            self.dash_force_x = 0
            self.dash_direction_x = 0
        # по y
        if self.dash_force_y > self.dash_force_slower:
            self.dash_force_y -= self.dash_force_slower
            self.dy = self.dash_force_y * self.dash_direction_y
        else:
            self.dash_force_y = 0
            self.dash_direction_y = 0

        '''
        Управление игрока сделано так, что при начале движения игрок не сразу
        получает максимальную скорость, а постепеноо разгоняется. При этом
        если во время набора скорости игрок меняет направление, то разгон будет
        продолжаться. Но если игрок уже достиг своей максимальной скорости, он
        может моментально менять направления, а не крутиться как черепаха (это
        повышает динамичность геймплея и заставляет игрока больше двигаться, а
        не стоять на месте). Но при этом, нельзя просто взять отпустить кнопку, 
        зажать другую и ожидать, что скорость сохранится, если бы так всё 
        работало, то это было бы неправильно, поэтому чтобы при изменении 
        направления сохранить скорость, надо не отпуская текущую клавишу, 
        зажать другие клавиши, а затем отпустить текущие.
        '''
        # Проверка, что было было движение
        if current_direction_x != 0 or current_direction_y != 0:
            # Обновление направления взгляда
            self.look_direction_x = current_direction_x
            self.look_direction_y = current_direction_y

            # Передвижения игрока при обычной ходьбе
            if self.dash_force_x == 0 and self.dash_force_y == 0:
                # Плавное изменение ускорение по x (если движение присутствует)
                if abs(self.dx) < Player.min_delta_to_start_run and current_direction_x:
                    self.dx += Player.delta_changer * current_direction_x
                else:
                    # Если значение "разгона" было превышено,
                    # то устанавливается максимальная скорость игрока
                    self.dx = current_direction_x * Player.max_delta_movements
                # Плавное изменение ускорение по y (если движение присутствует)
                if abs(self.dy) < Player.min_delta_to_start_run and current_direction_y:
                    self.dy += Player.delta_changer * current_direction_y
                else:
                    # Если значение "разгона" было превышено,
                    # то устанавливается максимальная скорость игрока
                    self.dy = current_direction_y * Player.max_delta_movements
            # Дополнительное ослабленное воздействие на игрока при дэше
            else:
                self.dx += current_direction_x * 0.4
                self.dy += current_direction_y * 0.4

        # Если игрок не совершает дэш и направления движения нет, то
        # ускорение збрасывается
        elif self.dash_force_x == 0 and self.dash_force_y == 0:
            self.dx = self.dy = 0
            self.set_first_frame()

        # Если игрок движется и при этом не совершается дэш,
        # то воспроизводится звук ходьбы
        # (При этом проверяется текущий канал со звуками, чтобы не
        # было наложения эффекта "наложения" звуков)
        if ((abs(self.dx) > Player.delta_changer or
             abs(self.dy) > Player.delta_changer)
                and self.dash_force_x == self.dash_force_y == 0 and
                not Player.sounds_channel.get_busy()):
            Player.sounds_channel.play(Player.FOOTSTEP_SOUND)

        # Если игрок движется по диагонали, то его скорость надо
        if self.dx != 0 and self.dy != 0:
            # 0.0388905 = 0.055 * 0.7071, где  0.055 - множитель для скорости
            # относительн TILE_SIZE, а 0.7071 - приближённое значение корня
            # из двух для выравнивание скорости при диагональном движении
            self.speed = TILE_SIZE * 0.0388905
        else:
            self.speed = TILE_SIZE * 0.055

        # Перемещение игрока относительно центра
        self.move(self.dx * self.speed, self.dy * self.speed)

        # Обновление анимации
        self.update_frame_state()

        # Обновление прицела
        self.scope.update(new_scope_x, new_scope_y)
        self.wand.update(self.rect.center, self.scope.rect.center)

    def shoot(self, spell_type: str, enemies_group):
        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - Player.spell_reload_time < self.shoot_last_time or not self.alive:
            return

        # Получение угла относительно прицела и оружия
        angle = degrees(atan2(self.wand.rect.centery - self.scope.rect.centerx,
                              self.wand.rect.centerx - self.scope.rect.centery))
        fixer = 1
        if angle >= 180:
            fixer = -1
        args = (self.wand.rect.centerx, self.wand.rect.centery + self.wand.offset.y * fixer,
                self.scope.rect.right, self.scope.rect.centery, enemies_group, self.spells)

        if spell_type == 'fire':
            FireSpell(*args)
        elif spell_type == 'ice':
            IceSpell(*args)
        elif spell_type == 'flash':
            FlashSpell(*args)
        elif spell_type == 'poison':
            PoisonSpell(*args)
        elif spell_type == 'void':
            VoidSpell(*args)

        self.shoot_last_time = current_ticks

    def death(self):
        # Уделние прицела
        # for group in self.scope.groups():
        #     group.remove(self.scope)

        # Удаление палочки
        for group in self.wand.groups():
            group.remove(self.wand)


class PlayerWand(pygame.sprite.Sprite):
    """
    Класс представляющий оружие игрока - волшебную палочку
    """
    def __init__(self, *args):
        super().__init__(*args)

        self.image = load_image("magic_wand.png")
        self.image = pygame.transform.scale2x(self.image)
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.offset = pygame.math.Vector2(0, self.rect.height * -0.5)

    def update(self, player_position: tuple =None, player_scope_position: tuple =None):
        # Если были переданны координаты прицела, то обновляем угол
        if player_scope_position and player_position:
            self.rect.centerx = player_position[0] + TILE_SIZE * 0.5
            self.rect.centery = player_position[1] + TILE_SIZE * 0.1
            # Получение угла относительно прицела и оружия
            dx, dy = self.rect.centery - player_scope_position[1], self.rect.centerx - player_scope_position[0]
            angle = degrees(atan2(dx, 0.00001 if dy == 0 else dy))
            self.rotate_wand(angle)

    def rotate_wand(self, angle: float) -> None:
        self.image = pygame.transform.rotate(self.original_image, 90 - angle)
        offset_rotated = self.offset.rotate(angle)
        self.rect = self.image.get_rect(center=self.rect.center + offset_rotated)


class PlayerScope(pygame.sprite.Sprite):
    """
    Этот класс отвечает за прицел игрока, нарпимер,
    относительно него будут создаваться заклинания
    """

    def __init__(self, x: float, y: float):
        # Конструктор класса Sprite
        super().__init__()

        self.image = load_image("player_scope.png", path_to_folder="assets")
        self.image = pygame.transform.scale(self.image,
                                            (round(self.image.get_width() * 1.3),
                                             round(self.image.get_height() * 1.3)))
        self.rect = self.image.get_rect()
        # Начальное местоположение
        self.rect.centerx = x
        self.rect.centery = y
        # Скорость перемещения
        self.speed = 15

    def update(self, x=None, y=None):
        # Т.к. update вызывается ещё и в игровом цикле, то
        # стоит делать проверку на наличие аргументов x и y
        # (но предполагается, что x и y - это координаты)
        if x is not None and y is not None:
            self.rect.centerx, self.rect.centery = x, y

    def init_scope_position(self, position: tuple):
        """
        Метод устанавливает позицию прицела
        :param position: Кортеж с координатами
        """
        self.rect.centerx, self.rect.centery = position
