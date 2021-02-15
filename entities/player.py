from entities.enemies import *
from entities.base_entity import *
from engine import *
from config import *


class Player(Entity):
    """
    Класс отвечающий за игрока
    """

    # Кадры для анимации игрока
    size = (TILE_SIZE * 7 // 8, TILE_SIZE)
    frames = cut_sheet(load_image('player.png'), 4, 4, size)
    cast_frames = cut_sheet(load_image('player_cast.png'), 5, 4, size)

    get_damage_frames = cut_sheet(load_image('player_get_damage.png'), 4, 1, size)[0]
    death_frames = cut_sheet(load_image('player_death.png'), 28, 1, size)[0]

    # Переменные добавляющие эти значения к здоровью и мане каждую итерацию update()
    MANA_UP = 0.4
    HEALTH_UP = 0.01
    MEAT_HEALTH_UP = 50
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

    # Время между кастами заклинаний
    between_shoots_range = 300
    # эффект замедления после атаки заклинанием
    after_spell_freezing = 300

    # время перезарядки дэша в миллисекундах
    dash_reload_time = 2000
    # сила дэша, которая устанавливается в самом начале
    dash_force_base = 3
    # сила замедляющая дэш со временем
    dash_force_slower = 0.04
    # Минимальгая скорость дэша
    dash_minimum_speed = 0.8

    # Скорость по умолчанию (используется при эффекте замедления)
    default_speed = TILE_SIZE * 0.017
    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 1.5
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 2
    # сила с которой игрок будет набирать/уменьшать свою скорость
    delta_changer = 0.3

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "footstep.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    DASH_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "dash.wav"))
    DASH_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    NO_MANA_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\spells\\audio", "no_mana_sound.ogg"))
    NO_MANA_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME + 20)

    def __init__(self, x: float, y: float, level: int, all_sprites: pygame.sprite.Group,
                 health=0, mana=0, money=0):
        # Конструктор класса Entity
        x, y, level, health, mana, money = float(x), float(y), int(level), float(health), float(mana), int(money)
        super().__init__(x, y, all_sprites)
        self.alive = True
        self.destroyed = False
        Entity.player = self

        self.level = level

        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # Скорость
        self.speed = 1
        self.dx = self.dy = 0
        self.distance_to_player = 0.0001

        self.extra_damage = 1

        # Здоровье
        self.full_health = 500
        if health:
            self.health = health
        else:
            self.health = self.full_health

        # Мана
        self.full_mana = 500
        if mana:
            self.mana = mana
        else:
            self.mana = self.full_mana

        # Монеты
        self.money = money

        # Помощники
        self.assistants = pygame.sprite.Group()

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

        # Инициализация прицела для игрока
        self.scope = PlayerScope(x, y)
        # Установка начального состояния джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

    def __str__(self):
        delta_pos = self.rect.centerx - self.start_position[0], self.rect.centery - self.start_position[1]
        player_args = [*delta_pos, self.level, self.health, self.mana, self.money, len(self.assistants)]
        args = [' '.join(map(str, player_args))]
        for assistant in self.assistants:
            args.append(str(assistant))
        return '\n'.join(args)

    def update(self):
        if self.alive:
            self.mana = min(self.mana + Player.MANA_UP, self.full_mana)
            self.health = min(self.health + Player.HEALTH_UP, self.full_health)
        else:
            self.update_frame_state()

        # Обновляем состояние джойстика
        self.joystick = get_joystick() if check_any_joystick() else None

        # Ниже переменные, нужные для общей обработки игрока внезависимости от
        # типа управления (геймпад/клавиатура)
        # Новая позиция для прицела игрока (по умолчанию изменений нет)
        new_scope_x, new_scope_y = self.scope.rect.centerx, self.scope.rect.centery

        # Если джойстик подключен, то управление идёт с него
        if self.joystick:
            # Получение направления куда указывают нажатые стрелки геймпада
            current_direction_x = round(self.joystick.get_axis(0)) > 0 - round(self.joystick.get_axis(0)) < 0
            current_direction_y = round(self.joystick.get_axis(1)) > 0 - round(self.joystick.get_axis(1)) < 0

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
            current_direction_x = int(keys[CONTROLS["KEYBOARD_LEFT"][0]] or keys[CONTROLS["KEYBOARD_LEFT"][1]]) * -1
            current_direction_x += int(keys[CONTROLS["KEYBOARD_RIGHT"][0]] or keys[CONTROLS["KEYBOARD_RIGHT"][1]])
            current_direction_y = int(keys[CONTROLS["KEYBOARD_UP"][0]] or keys[CONTROLS["KEYBOARD_UP"][1]]) * -1
            current_direction_y += int(keys[CONTROLS["KEYBOARD_DOWN"][0]] or keys[CONTROLS["KEYBOARD_DOWN"][1]])

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
                self.dash_last_time > Player.dash_reload_time and self.alive):
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
        # ускорение сбрасывается
        elif (self.dash_force_x == 0 and self.dash_force_y == 0 and
              not self.is_boosting_from_enemy):
            self.dx = self.dy = 0
            if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing and self.alive:
                self.set_first_frame()
        elif self.is_boosting_from_enemy:
            previous_dx, previous_dy = self.dx, self.dy
            self.dx -= 0.35 * -1 if self.dx < 0 else 1
            self.dy -= 0.35 * -1 if self.dy < 0 else 1
            if previous_dx > 0 > self.dx or previous_dx < 0 < self.dx:
                self.dx = 0
                self.is_boosting_from_enemy = False

            if previous_dy > 0 > self.dy or previous_dy < 0 < self.dy:
                self.dy = 0
                self.is_boosting_from_enemy = False

        # Если игрок движется и при этом не совершается дэш,
        # то воспроизводится звук ходьбы
        # (При этом проверяется текущий канал со звуками, чтобы не
        # было наложения эффекта "наложения" звуков)
        if ((abs(self.dx) > Player.delta_changer or
             abs(self.dy) > Player.delta_changer)
                and self.dash_force_x == self.dash_force_y == 0 and
                not Player.sounds_channel.get_busy() and self.alive):
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
        if self.alive:
            self.move(self.dx * self.speed, self.dy * self.speed)
        super().update()

        # Обновление анимации
        if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing and self.alive:
            if self.dx or self.dy:
                self.update_frame_state()
            else:
                self.is_boosting_from_enemy = False
                self.set_first_frame()

        for item in pygame.sprite.spritecollide(self.collider, GroundItem.item_group, False):
            item: GroundItem
            if item.type == 'meat':
                self.get_damage(-self.MEAT_HEALTH_UP * item.count)
            elif item.type == 'money':
                self.money += item.count
            self.sounds_channel.play(item.sound)
            item.kill()
        # Обновление прицела
        self.scope.update(new_scope_x, new_scope_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def add_assistant(self, assistant):
        self.assistants.add(assistant)

    def shoot(self, spell_type: str, group):
        if not self.alive:
            return

        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - Player.between_shoots_range < self.shoot_last_time:
            return
        self.shoot_last_time = current_ticks

        # Получение угла относительно прицела и оружия
        dx, dy = self.rect.centerx - self.scope.rect.centerx, self.rect.centery - self.scope.rect.centery
        angle = (degrees(atan2(dx, 0.00001 if not dy else dy)) + 360) % 360
        args = (*self.rect.center, *self.scope.rect.center, self.extra_damage, group)

        if spell_type == Spell.FIRE:
            spell = FireSpell
        elif spell_type == Spell.ICE:
            spell = IceSpell
        elif spell_type == Spell.FLASH:
            spell = FlashSpell
        elif spell_type == Spell.POISON:
            spell = PoisonSpell
        elif spell_type == Spell.VOID:
            spell = VoidSpell
        elif spell_type == Spell.TELEPORT:
            spell = TeleportSpell
            args = (args[:-1] + ([self],))
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
            spell = spell(*args)
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

    def get_damage(self, damage, spell_type='', action_time=0):
        """
        Получение дамага

        :param damage: Столько здоровья надо отнять
        :param spell_type: Тип урона, чтоб узнавать, на кого он действует сильнее
        :param action_time: Время действия (для льда и отравления)
        :return: None
        """
        if not self.alive:
            return

        if spell_type == 'ice':
            self.ice_buff += action_time
        if spell_type == 'poison' and damage >= 5:
            self.poison_buff += action_time

        if damage >= 0:
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            self.image = self.get_damage_frames[look]
            self.last_update = pygame.time.get_ticks() + 50
            self.last_damage_time = pygame.time.get_ticks()

        if self.__class__.__name__ == 'Player' and self.joystick:
            pass
            # self.joystick.vibrate(1)

        damage *= 1000
        damage += randint(-abs(round(-damage * 0.4)), abs(round(damage * 0.4)))
        damage /= 1000

        x, y = self.rect.midtop
        if damage >= 0:
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages, color=(255, 30, 30))
        elif spell_type == 'poison':
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages, color=(100, 35, 35))
        else:
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages, color=(30, 255, 30))

        self.health = min(self.health - damage, self.full_health)
        if self.health <= 0:
            self.health = 0
            self.death()

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
        self.image = pygame.transform.scale(self.image, (round(TILE_SIZE * 0.5),) * 2)
        self.rect = self.image.get_rect()
        # Начальное местоположение
        self.rect.center = x, y
        # Скорость перемещения
        self.speed = 15

    def update(self, x, y):
        # Т.к. update вызывается ещё и в игровом цикле, то
        # стоит делать проверку на наличие аргументов x и y
        # (но предполагается, что x и y - это координаты)
        # Если размер текущего экрана
        self.rect.center = x, y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def init_scope_position(self, position: tuple):
        """
        Метод устанавливает позицию прицела
        :param position: Кортеж с координатами
        """
        self.rect.center = position


class PlayerAssistant(Player):
    """
    Класс отвечающий за игрока
    """

    # Кадры для анимации игрока
    size = (TILE_SIZE * 6 // 8, TILE_SIZE * 7 // 8)
    frames = cut_sheet(load_image('assistant.png'), 4, 4, size)
    cast_frames = cut_sheet(load_image('assistant_cast.png'), 5, 4, size)
    get_damage_frames = cut_sheet(load_image('assistant_get_damage.png'), 4, 1, size)[0]
    death_frames = cut_sheet(load_image('assistant_death.png'), 28, 1, size)[0]

    # Переменные добавляющие эти значения к здоровью и мане каждую итерацию update()
    MANA_UP = 0.4
    HEALTH_UP = 0.1
    # Время неуязвимости, после атаки врагом (в миллисекундах)
    INVULNERABILITY_TIME_AFTER_HIT = 300

    WAITING_TIME = 1000
    TARGET_UPDATE_TIME = 300

    # Словарь типа (направление взгляда): *индекс ряда в frames для анимации*
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

    # Время между кастами заклинаний
    between_shoots_range = 1000
    # эффект замедления после атаки заклинанием
    after_spell_freezing = 300

    # время перезарядки в миллисекундах
    reload_time = 2000

    teleport_range = TILE_SIZE * 12

    visible_range = TILE_SIZE * 10

    keeping_distant_to_player = TILE_SIZE * 1.5

    # Скорость по умолчанию (используется при эффекте замедления)
    default_speed = TILE_SIZE * 0.118
    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 1.5
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 2
    # сила с которой игрок будет набирать/уменьшать свою скорость
    delta_changer = 0.3

    names = [
        'Aдрахил', 'Aлмариан', 'Aндвайс', 'Aнкалагон', 'Aнкалимон', 'Aулендил', 'Авель',
        'Адалдрида', 'Аделард', 'Анакин', 'Ариан', 'Аркан', 'Аркана', 'Армандо', 'Асия',
        'Аскаланте', 'Астор', 'Аттилло', 'Барлиман', 'Бенедикт', 'Бофаро', 'Брооклин',
        'Вассиан', 'Ваучер', 'Вербер', 'Вилкольм', 'Виринея', 'Вирсавия', 'Виссарион',
        'Витольд', 'Владигор', 'Володар', 'Гарий', 'Гермоген', 'Гимилзагар', 'Гликерий',
        'Графиелита', 'Гринат', 'Громель', 'Гус', 'Дан', 'Данаида', 'Дарий', 'Доримедонт',
        'Евстафий', 'Зородал', 'Иагон', 'Иаоса', 'Изаура', 'Илларий', 'Илларион', 'Калистрат',
        'Калисфен', 'Каллист', 'Капитон', 'Каспиан', 'Кассиопея', 'Клементий', 'Лаврентий',
        'Ларион', 'Лика', 'Луара', 'Люцифер', 'Максимиан', 'Меланфий', 'Мефодий', 'Неолина',
        'Нимфадора', 'Обафеми', 'Оллард', 'Офелия', 'Памфил', 'Парфён', 'Патрикий', 'Пафнутий',
        'Пофистал', 'Ратибор', 'Ревмир', 'Револьд', 'Рубентий', 'Рувим', 'Селиван', 'Серапион',
        'Серафим', 'Согдиана', 'Софрон', 'Телемах', 'Тирион', 'Тодор', 'Трифилий', 'Троадий',
        'Фабиан', 'Фалькор', 'Феанор', 'Феникс', 'Финарфин', 'Флавиан', 'Фрумгар', 'Хамфаст',
        'Хартвиг', 'Хейнер', 'Хродрик', 'Эвмей', 'Эгнор', 'Эктелион', 'Эланор', 'Элеммакил',
        'Элим', 'Элуна', 'Эмельдир', 'Эмметт', 'Эрандир', 'Эрендис', 'Эрестор', 'Эрнест',
        'Эстелмо', 'Ювеналий', 'Юст', 'Юстиниан'
    ]

    font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 32)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(7)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "footstep.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, player, all_sprites, health=0, mana=0, name=()):
        x, y, health, mana = float(x), float(y), float(health), float(mana)
        super(Player, self).__init__(x, y, all_sprites)

        self.player = player
        if name:
            self.name = ' '.join(name)
        else:
            self.name = choice(PlayerAssistant.names)
        self.icon = None
        self.level = player.level
        self.alive = True

        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # Скорость
        self.speed = 0.5
        self.dx = self.dy = 0
        self.distance_to_player = 0.0001
        self.stopping_time = pygame.time.get_ticks()
        self.target = None
        self.is_boosting_from_enemy = False

        # Здоровье
        self.full_health = 300
        if health:
            self.health = health
        else:
            self.health = self.full_health

        # Мана
        self.full_mana = 300
        if mana:
            self.mana = mana
        else:
            self.mana = self.full_mana

        # Группа со спрайтами заклинаний
        self.shoot_last_time = pygame.time.get_ticks()
        self.last_hit_time = 0
        self.last_target_update = 0

    def __str__(self):
        args = [*self.rect.center, self.health, self.mana, self.name]
        return ' '.join(map(str, args))

    def update(self, *args):
        if self.alive:
            self.mana = min(self.mana + self.MANA_UP, self.full_mana)
            self.health = min(self.health + self.HEALTH_UP, self.full_health)
        else:
            super(Player, self).update_frame_state()
            return

        player = self.player
        enemies_group = args[0]
        # Сокращаем написание координат объекта
        self_x, self_y = self.rect.center

        point_x, point_y = player.rect.center
        # Находим расстояние между врагом и игроком
        self.distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
        line = self.distance_to_player

        self.dx = self.dy = 0

        if line > self.keeping_distant_to_player:
            if line >= self.teleport_range:
                self.shoot(self.player)
                self.point = None
            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            self.point = None

        else:
            if pygame.time.get_ticks() - self.stopping_time > self.WAITING_TIME:
                if not self.point or self.point == self.rect.center:
                    self.stopping_time = pygame.time.get_ticks() + randint(-500, 500)
                    self.point = (point_x + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75),
                                  point_y + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75))
                point_x, point_y = self.point
                line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

                part_move = max(line / self.speed, 0.5)
                self.dx = round((point_x - self_x) / part_move)
                self.dy = round((point_y - self_y) / part_move)

        self.move(self.dx, self.dy)

        nearest_enemy = self.update_target(enemies_group)

        if nearest_enemy:
            self.shoot(nearest_enemy, enemies_group)

        if self.dx or self.dy:
            # Определяем направление взгляда
            if self.dx > 0:
                self.look_direction_x = 1
            elif self.dx < 0:
                self.look_direction_x = -1
            else:
                self.look_direction_x = 0
            if self.dy > 0:
                self.look_direction_y = 1
            elif self.dy < 0:
                self.look_direction_y = -1
            else:
                self.look_direction_y = 0
            super(Player, self).update_frame_state()
        else:
            self.set_first_frame()

        # Сбор вещей и отдача их игроку
        for item in pygame.sprite.spritecollide(self.collider, GroundItem.item_group, False):
            item: GroundItem
            if item.type == 'meat':
                self.player.get_damage(-self.MEAT_HEALTH_UP * item.count)
            elif item.type == 'money':
                self.player.money += item.count
            self.sounds_channel.play(item.sound)
            item.kill()

        # Обновляем спрайт
        super(Player, self).update()

    def shoot(self, target, enemies_group=None):
        if not self.alive or not target or not target.alive:
            return

        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - self.between_shoots_range < self.shoot_last_time:
            return
        self.shoot_last_time = current_ticks

        if isinstance(target, Player):
            spell = TeleportSpell
            poses = *self.rect.center, *target.rect.center
            args = *poses, 0.5 + 0.05 * self.level, [self], self.player.spells
        else:
            if isinstance(target, Demon):
                spell = IceSpell

            elif isinstance(target, GreenSlime):
                spell = FlashSpell

            elif isinstance(target, DirtySlime):
                spell = VoidSpell

            elif isinstance(target, Zombie):
                spell = FireSpell

            elif isinstance(target, FireWizard):
                spell = PoisonSpell

            elif isinstance(target, VoidWizard):
                spell = FireSpell

            else:
                return
            poses = *self.rect.center, *target.rect.center
            args = *poses, 0.5 + 0.05 * self.level, enemies_group, self.player.spells

        if self.mana >= spell.mana_cost:
            self.mana -= spell.mana_cost
            self.sounds_channel.play(spell.CAST_SOUND)
            spell(*args)

            # Получение угла относительно прицела и оружия
            dx, dy = self.rect.centerx - target.rect.centerx, self.rect.centery - target.rect.centery
            angle = (degrees(atan2(dx, 0.00001 if not dy else dy)) + 360) % 360

            number_of_frame = (round((angle - 0) / 18) + 27) % 20
            self.image = self.cast_frames[number_of_frame // 5][number_of_frame % 5]
            self.last_update = pygame.time.get_ticks() + 300

    def update_target(self, enemies_group) -> Monster:
        self.last_target_update = pygame.time.get_ticks()

        min_dist_to_enemy = self.visible_range + 1
        nearest_enemy = None
        for enemy in enemies_group:
            if not enemy.alive:
                continue

            dist_to_enemy = hypot(self.rect.center, enemy.rect.center)
            if dist_to_enemy < min_dist_to_enemy:
                min_dist_to_enemy = dist_to_enemy
                nearest_enemy = enemy

        return nearest_enemy

    def death(self):
        if not self.alive:
            return

        self.alive = False
        self.cur_frame = 0
        self.speed = 0.00001
