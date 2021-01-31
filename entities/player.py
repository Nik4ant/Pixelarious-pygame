from random import choice

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
    cast_frames = cut_sheet(load_image('player_cast_sprite_sheet.png', 'assets'), 5, 4, size)

    # Переменные добавляющие эти значиния к здоровью и мане каждую итерацию update()
    MANA_UP = 0.2
    HEALTH_UP = 0.025
    # Время неуязвимости, после атаки врагом (в миллисекундах)
    INVULNERABILITY_TIME_AFTER_HIT = 300

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
    spell_reload_time = 400
    # Время между кастами заклинаний
    between_shoots_range = 80
    # эффект замедления после атаки заклинанием
    after_spell_freezing = 300

    # время перезарядки дэша в миллисекундах
    dash_reload_time = 2000
    # сила дэша, которая устанавливается в самом начале
    dash_force_base = 2.8
    # сила замедляющая дэш со временем
    dash_force_slower = 0.04
    # Минимальгая скорость дэша
    dash_minimum_speed = 0.4

    # Скорость по умолчанию (используется при эффекте замедления)
    default_speed = TILE_SIZE * 0.015
    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 1.5
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 2
    # сила с которой игрок будет набирать/уменьшать свою скорость
    delta_changer = 0.06

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "footstep.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    DASH_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "dash.wav"))
    DASH_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    NO_MANA_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "no_mana_sound.ogg"))
    NO_MANA_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME + 20)

    def __init__(self, x: float, y: float, all_sprites, *args):
        # Конструктор класса Entity
        super().__init__(x, y, all_sprites, *args)
        self.alive = True

        # Ширина и высота изображения после инициализации
        self.width, self.height = self.image.get_size()

        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Скорость
        self.dx = self.dy = 0
        self.distance_to_player = 0.0001

        # Здоровье
        self.health = 450
        self.full_health = self.health

        # Мана
        self.mana = 450
        self.full_mana = self.mana

        # Группа со спрайтами заклинаний
        self.spells = pygame.sprite.Group()
        self.shoot_last_time = pygame.time.get_ticks()
        self.last_hit_time = 0

        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1

        # Флаг, для проверки отталкивается ли игрок от врага
        self.is_boosting_from_enemy = False

        # Дэш
        self.dash_direction_x = self.dash_direction_y = 0
        self.dash_force_x = self.dash_force_y = 0

        # Время последнего использования дэша
        # (Нужно для определения перезарядился дэш или нет)
        self.dash_last_time = pygame.time.get_ticks()

        # Инициализация прицеда для игрока
        self.scope = PlayerScope(x, y)
        # Установка начального состояния джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

    def update(self):
        super().update()

        if self.alive:
            self.mana = min(self.mana + Player.MANA_UP, self.full_mana)
            self.health = min(self.health + Player.HEALTH_UP, self.full_health)

        # Обновляем состояние джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

        # Ниже переменные, нужные для общей обработки игрока внезависимости от
        # типа управления (геймпад/клавиатура)
        was_dash_activated = False
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

        if pygame.time.get_ticks() - self.shoot_last_time < 200:
            self.speed *= 0.8 * Player.default_speed
        else:
            self.speed *= self.default_speed

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
        if self.dash_force_x > Player.dash_minimum_speed:
            self.dash_force_x -= Player.dash_force_slower
            self.dx = self.dash_force_x * self.dash_direction_x
        else:
            self.dash_force_x = 0
            self.dash_direction_x = self.look_direction_x
        # по y
        if self.dash_force_y > Player.dash_minimum_speed:
            self.dash_force_y -= self.dash_force_slower
            self.dy = self.dash_force_y * self.dash_direction_y
        else:
            self.dash_force_y = 0
            self.dash_direction_y = self.look_direction_y

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
        elif (self.dash_force_x == 0 and self.dash_force_y == 0 and
              not self.is_boosting_from_enemy):
            self.dx = self.dy = 0
            if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing:
                self.set_first_frame()
        elif self.is_boosting_from_enemy:
            previous_dx, previous_dy = self.dx, self.dy
            self.dx -= 0.35 * -1 if self.dx < 0 else 1
            self.dy -= 0.35 * -1 if self.dy < 0 else 1
            if (previous_dx > 0 and self.dx < 0) or (previous_dx < 0 and self.dx > 0):
                self.dx = 0
                self.is_boosting_from_enemy = False

            if (previous_dy > 0 and self.dy < 0) or (previous_dy < 0 and self.dy > 0):
                self.dy = 0
                self.is_boosting_from_enemy = False

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
            self.speed *= TILE_SIZE * 0.0388905
        else:
            self.speed *= TILE_SIZE * 0.055

        # Перемещение игрока
        self.move(self.dx * self.speed, self.dy * self.speed)

        # Обновление анимации
        if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing:
            if self.dx or self.dy:
                self.update_frame_state()
            else:
                self.is_boosting_from_enemy = False
                self.set_first_frame()

        # Обновление прицела
        self.scope.update(new_scope_x, new_scope_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def shoot(self, spell_type: str, group):
        if not self.alive:
            return

        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - Player.spell_reload_time < self.shoot_last_time or \
                current_ticks - Player.between_shoots_range < self.shoot_last_time:
            return
        self.shoot_last_time = current_ticks

        # Получение угла относительно прицела и оружия
        dx, dy = self.rect.centerx - self.scope.rect.centerx, self.rect.centery - self.scope.rect.centery
        angle = (degrees(atan2(dx, 0.00001 if not dy else dy)) + 360) % 360
        args = (self.rect.centerx, self.rect.centery,
                self.scope.rect.centerx, self.scope.rect.centery, group)

        if spell_type == Spell.FIRE:
            spell = FireSpell(*args)
        elif spell_type == Spell.ICE:
            spell = IceSpell(*args)
        elif spell_type == Spell.FLASH:
            spell = FlashSpell(*args)
        elif spell_type == Spell.POISON:
            spell = PoisonSpell(*args)
        elif spell_type == Spell.VOID:
            spell = VoidSpell(*args)
        elif spell_type == Spell.TELEPORT:
            spell = TeleportSpell(*args[:-1] + ([self],))
        else:
            return

        if self.mana >= spell.mana_cost:
            if spell_type == Spell.TELEPORT:
                self.collider.update(*self.scope.rect.center)
                if (pygame.sprite.spritecollideany(self.collider, Entity.collisions_group)
                        or not pygame.sprite.spritecollideany(self.collider, group)):
                    self.sounds_channel.play(Player.NO_MANA_SOUND)
                    return

            self.mana -= spell.mana_cost
            self.spells.add(spell)
            if spell_type == Spell.TELEPORT:
                self.spells.add(spell.start_sprite)
            self.sounds_channel.play(spell.CAST_SOUND)

            number_of_frame = (round((angle - 0) / 18) + 47) % 20
            self.image = Player.cast_frames[number_of_frame // 5][number_of_frame % 5]

            self.ice_buff += 10
            self.shoot_last_time = current_ticks
        else:
            self.sounds_channel.play(Player.NO_MANA_SOUND)

    def death(self):
        self.alive = False
        self.cur_frame = 0
        self.speed = 1

    def boost_from_enemy(self, boost_dx: float, boost_dy: float):
        """
        Метод дающий ускорение игроку, в случае если он был атакован
        :param boost_dx: Ускорение по x
        :param boost_dy: Ускорение по y
        """

        # Чтобы ускорить игрока, нужно задать флаг, что игрок отталкивается в сторону.
        # Тогда игрок не сможет прервать ускорение.
        self.is_boosting_from_enemy = True

        self.dx = boost_dx
        self.dy = boost_dy

        self.last_hit_time = pygame.time.get_ticks()


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
        if x and y:
            # Если размер текущего экрана
            self.rect.centerx, self.rect.centery = x, y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def init_scope_position(self, position: tuple):
        """
        Метод устанавливает позицию прицела
        :param position: Кортеж с координатами
        """
        self.rect.centerx, self.rect.centery = position
