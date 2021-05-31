from math import dist

from entities.enemies import *
from entities.base_entities import *
from engine import *
from config import *


class Player(Entity):
    """Класс, представляющий за игрока """
    # Эти значения прибавляются к здоровью и мане каждую итерацию update()
    MANA_UP = 0.4
    HEALTH_UP = 0.01
    MEAT_HEALTH_UP = 25
    # (Всё время далее будет указано в миллисекундах)
    # Время неуязвимости, после атаки врагом
    INVULNERABILITY_TIME_AFTER_HIT = 300
    # Время между кастами заклинаний
    between_shoots_range = 300
    # Время фффекта замедления после атаки заклинанием
    after_spell_freezing = 300
    # время перезарядки дэша
    dash_reload_time = 2000
    # сила дэша, которая устанавливается в самом начале
    dash_force_base = 5
    # сила замедляющая дэш со временем
    dash_force_slower = 0.24
    # Минимальгая скорость дэша
    dash_minimum_speed = 0.8
    # Скорость по умолчанию (используется при эффекте замедления)
    default_speed = TILE_SIZE * 0.017
    # отметка при превышении которой, скорость игрока автоматически возврастает
    min_delta_to_start_run = 1.5
    # Максимальное ускорение игрока (при перемещении, на дэш не влияет)
    max_delta_movements = 2
    # сила с которой игрок будет набирать/уменьшать свою скорость до
    # превышения отметки min_delta_to_start_run
    delta_changer = 0.3
    size = (TILE_SIZE * 7 // 8, TILE_SIZE)  # размер для анимаций ниже
    # Кадры анимации передвижений игрока
    frames = cut_sheet(load_image("assets/sprites/player/player.png"), 4, 4, size)
    # Кадры анимации использования заклинаний игроком
    cast_frames = cut_sheet(load_image("assets/sprites/player/player_cast.png"), 5, 4, size)
    # Кадры анимации получения урона игроком
    get_damage_frames = cut_sheet(load_image("assets/sprites/player/player_get_damage.png"), 4, 1, size)[0]
    # Кадры анимации смерти игрока
    death_frames = cut_sheet(load_image("assets/sprites/player/player_death.png"), 28, 1, size)[0]
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
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)
    # Звуки
    FOOTSTEP_SOUND = load_sound("assets/audio/sfx/player/footstep.ogg")
    DASH_SOUND = load_sound("assets/audio/sfx/player/dash.wav")
    NO_MANA_SOUND = load_sound("assets/audio/sfx/player/no_mana_sound.ogg")

    def __init__(self, x: float, y: float, level: int, all_sprites: pygame.sprite.Group,
                 health=0, mana=0, money=0):
        # Получение параметров и приведение к нужному типу (т.к. на вход могут
        # передать не сразу нужные типы, например, при инициализации уровня)
        level = int(level)
        health, mana = float(health), float(mana)
        money = int(money)
        # Уровень игрока. Он влияет на урон заклинаний асистента
        self.level = level
        # Конструктор класса Entity
        super().__init__(float(x), float(y), all_sprites)
        self.alive = True  # жив ли игрок
        self.destroyed = False
        # Установка игрока в базовом классе сущности, для того, чтобы другие
        # сущности могли взаимодействовать с ним и получать данные об игроке
        Entity.player = self
        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.speed = 1  # Скорость
        self.dx = self.dy = 0
        # Т.к. игрок и есть игрок, то растояние до него максимально маленькое
        # (не равно 0, т.к. в таком случае обработка некоторых звуком и прочего
        # сломается от деления на 0)
        self.distance_to_player = 0.0001
        self.extra_damage = 1
        # Максимальное здоровье
        self.full_health = 500
        # Текущее здоровье
        self.health = health if health else self.full_health
        # Максимальная мана
        self.full_mana = 500
        # Текущая мана
        self.mana = mana if mana else self.full_mana
        # Монеты
        self.money = money
        # Помошники
        self.assistants = pygame.sprite.Group()
        # Последнее время выстрела
        self.shoot_last_time = pygame.time.get_ticks()
        # Последняя время получения урона
        self.last_hit_time = 0
        # Направление взгляда
        self.look_direction_x = 0
        self.look_direction_y = 1
        # Флаг, для проверки отталкивается ли игрок от врага
        self.is_boosting_from_enemy = False
        # Направление и сила дэша
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
        # Разница
        delta_pos = self.rect.centerx - self.start_position[0], self.rect.centery - self.start_position[1]
        # Аргументы игрока для строковых данных
        player_args = [*delta_pos, self.level, self.health, self.mana, self.money, len(self.assistants)]
        args = [" ".join(map(str, player_args))]
        # Аргументы асистентов
        for assistant in self.assistants:
            assistant: PlayerAssistant
            args.append(str(assistant))
        return "\n".join(args)

    def update(self):
        if self.alive:
            # Увеличение параметров маны и здоровья
            self.mana = min(self.mana + Player.MANA_UP, self.full_mana)
            self.health = min(self.health + Player.HEALTH_UP, self.full_health)
        else:
            # Если игрок мёртв, надо обновить анимацию
            self.update_frame_state()
        # Обновляем состояние джойстика
        self.joystick = get_joystick() if check_any_joystick() else None
        # Новая позиция для прицела игрока для общей обработки игрока внезависимости от
        # типа управления (геймпад/клавиатура)
        new_scope_x, new_scope_y = self.scope.rect.centerx, self.scope.rect.centery
        # Если джойстик подключен, то управление идёт с него
        if self.joystick:
            # Получение направления куда указывают нажатые стрелки геймпада
            current_direction_x = int(self.joystick.get_button(CONTROLS["JOYSTICK_RIGHT"])) - \
                                  int(self.joystick.get_button(CONTROLS["JOYSTICK_LEFT"]))
            current_direction_y = int(self.joystick.get_button(CONTROLS["JOYSTICK_DOWN"])) - \
                                  int(self.joystick.get_button(CONTROLS["JOYSTICK_UP"]))
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
        # Скорость игрока замедляется на время после использования заклинания
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
        # Обработка сил дэша, действующих на игрока
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

        """
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
        (Этот эффект хоть и не так заметен, но важно знать, что он присутствует!!!)
        """
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
                    # то устанавливается максимальная скорость игрока по x
                    self.dx = current_direction_x * Player.max_delta_movements
                # Плавное изменение ускорение по y (если движение присутствует)
                if abs(self.dy) < Player.min_delta_to_start_run and current_direction_y:
                    self.dy += Player.delta_changer * current_direction_y
                else:
                    # Если значение "разгона" было превышено,
                    # то устанавливается максимальная скорость игрока по y
                    self.dy = current_direction_y * Player.max_delta_movements
        # Если игрок не совершает дэш и направления движения нет, то
        # ускорение сбрасывается
        elif (self.dash_force_x == 0 and self.dash_force_y == 0 and
              not self.is_boosting_from_enemy):
            self.dx = self.dy = 0
            # Если игрок жив и ни один из других эффектов (анимаций)
            # не прырывается устанавливается первый кадр
            if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing and self.alive:
                self.set_first_frame()
        # Обработка ускорения от столкновения с врагом
        elif self.is_boosting_from_enemy:
            # Ускорение до изменений
            previous_dx, previous_dy = self.dx, self.dy
            # Высчитывание ускорения
            self.dx -= 0.35 * -1 if self.dx < 0 else 1
            self.dy -= 0.35 * -1 if self.dy < 0 else 1
            # Если ускорение перешло от + к - или наоборот, то ускорение сбрасывается
            # и ускорение от столкновения с врагом больше не обрабатывается
            if previous_dx > 0 > self.dx or previous_dx < 0 < self.dx:
                self.dx = 0
                self.is_boosting_from_enemy = False
            if previous_dy > 0 > self.dy or previous_dy < 0 < self.dy:
                self.dy = 0
                self.is_boosting_from_enemy = False
        # Если игрок движется и при этом не совершается дэш, то
        # воспроизводится звук ходьбы
        # (При этом проверяется текущий канал со звуками, чтобы не
        # было эффекта "наложения" звуков)
        if ((abs(self.dx) > Player.delta_changer or
             abs(self.dy) > Player.delta_changer)
                and self.dash_force_x == self.dash_force_y == 0 and
                not Player.sounds_channel.get_busy() and self.alive):
            Player.sounds_channel.play(Player.FOOTSTEP_SOUND)
        # Если игрок движется по диагонали, то его скорость надо уменьшить, т.к.
        # по теореме пифагора получается, что движение по диагонали быстрее в
        # корень из двух раз
        if self.dx != 0 and self.dy != 0:
            # 0.0388905 = 0.055 * 0.7071, где  0.055 - множитель для скорости
            # относительно TILE_SIZE, а 0.7071 - приближённое значение корня
            # из двух для выравнивание скорости при диагональном движении
            self.speed *= TILE_SIZE * 0.0388905
        else:
            self.speed *= TILE_SIZE * 0.055
        # Перемещение игрока, если он жив
        if self.alive:
            self.move(self.dx * self.speed, self.dy * self.speed)
        # Обновление базовых параметров из Entity
        super().update()
        # Обновление анимации, если игрок жив и может двигаться
        if pygame.time.get_ticks() - self.shoot_last_time > Player.after_spell_freezing and self.alive:
            # Если движение есть, анимация обновляется
            if self.dx or self.dy:
                self.update_frame_state()
            else:
                # При отсутсвии движения игрок не отталкивается от врагов +
                # надо прекратить анимацию
                self.is_boosting_from_enemy = False
                self.set_first_frame()
        # Обработка столкновений с предметами на земле
        for item in pygame.sprite.spritecollide(self.collider, GroundItem.sprites_group, False):
            item: GroundItem
            # Если мясо, то игрок получает отрицательный урон (т.е. хилится)
            if item.type == "meat":
                self.get_damage(-self.MEAT_HEALTH_UP * item.count)
            # Увеличение кол-ва денег
            elif item.type == "money":
                self.money += item.count
            # Воспроизведение звука предмета и его уничтожение
            self.sounds_channel.play(item.sound)
            item.kill()
        # Обновление прицела
        self.scope.update(new_scope_x, new_scope_y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def add_assistant(self, assistant) -> None:
        self.assistants.add(assistant)

    def shoot(self, spell_type: str, group) -> None:
        if not self.alive:
            return
        # Время с момента инициализации для проверок связаных со временем
        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - Player.between_shoots_range < self.shoot_last_time:
            return

        # Получение угла относительно прицела и оружия
        dx, dy = self.rect.centerx - self.scope.rect.centerx, self.rect.centery - self.scope.rect.centery
        angle = (degrees(atan2(dx, 0.00001 if not dy else dy)) + 360) % 360
        args_for_spell = (*self.rect.center, *self.scope.rect.center, self.extra_damage, group, Entity.all_sprites)
        # Получение класса заклинания взависимости от типа заклинания.
        # (Сам класс нужен чтобы получить параметры и инициализировать заклинание)
        if spell_type == Spell.FIRE:
            CurrentSpellClass = FireSpell
        elif spell_type == Spell.ICE:
            CurrentSpellClass = IceSpell
        elif spell_type == Spell.FLASH:
            CurrentSpellClass = FlashSpell
        elif spell_type == Spell.POISON:
            CurrentSpellClass = PoisonSpell
        elif spell_type == Spell.VOID:
            CurrentSpellClass = VoidSpell
        elif spell_type == Spell.TELEPORT:
            CurrentSpellClass = TeleportSpell
            # Для телепорта параметры отличаются, т.к. само заклинание
            # телепорта отличается от всех остальных
            args_for_spell = (*self.rect.center, *self.scope.rect.center, self.extra_damage, [self], Entity.all_sprites)
        else:
            return
        # Если достаточно маны заклинание появится
        if self.mana >= CurrentSpellClass.mana_cost:
            # Если заклинание телепорт, то нельзя позволить игроку
            # переместиться куда не надо, например в текстуры
            if spell_type == Spell.TELEPORT:
                self.collider.update(*self.scope.rect.center)
                if (pygame.sprite.spritecollideany(self.collider, Entity.collisions_group)
                        or not pygame.sprite.spritecollideany(self.collider, group)):
                    # Если препятствие не даёт телепортироваться, то звук
                    # тот же, что и при нехватке маны
                    self.sounds_channel.play(Player.NO_MANA_SOUND)
                    return
            # Вычитание маны
            self.mana -= CurrentSpellClass.mana_cost
            # Создание заклинания
            spell = CurrentSpellClass(*args_for_spell)
            self.spells_group.add(spell)
            # У телепорта есть дополнительные эффекты,
            if spell_type == Spell.TELEPORT:
                self.spells_group.add(spell.start_sprite)
            # Звук кастования (создания) заклинания
            self.sounds_channel.play(spell.CAST_SOUND)
            # Определение кадра для анимации атаки заклинанием
            number_of_frame = (round((angle - 0) / 18) + 47) % 20
            self.image = Player.cast_frames[number_of_frame // 5][number_of_frame % 5]
            # Замедление после атаки заклинанием
            self.ice_buff += 10
            # Обновление времени
            self.shoot_last_time = current_ticks
        else:
            Player.sounds_channel.play(Player.NO_MANA_SOUND)

    def get_damage(self, damage, spell_type="", action_time=0) -> None:
        """
        Метод по получению урона игроком
        :param damage: Столько здоровья надо отнять
        :param spell_type: Тип урона, чтоб узнавать, на кого действует сильнее
        :param action_time: Время действия (для льда и отравления)
        """
        if not self.alive:
            return
        # Обновление эффектов льда и отравления
        if spell_type == "ice":
            self.ice_buff += action_time
        if spell_type == "poison" and damage >= 5:
            self.poison_buff += action_time
        # Если игрок получает урон, а не лечится меняется анимация
        if damage >= 0:
            # Направление взгляда
            look = self.__class__.look_directions[self.look_direction_x, self.look_direction_y]
            self.image = self.get_damage_frames[look]  # текущий кадр
            # Последнее время обновления и получения урона
            self.last_update = pygame.time.get_ticks() + 50
            self.last_damage_time = pygame.time.get_ticks()
        # Домножение и деление на 1000 нужно для учёта дробных чисел ниже
        damage *= 1000
        damage += randint(-abs(round(-damage * 0.4)), abs(round(damage * 0.4)))
        damage /= 1000
        # Позиция для отрисовки текста с уроном
        x, y = self.rect.midtop
        # Создание текста с уроном разного цвета в зависимости от параметров
        if damage >= 0:
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages_group, color=(255, 30, 30))
        elif spell_type == "poison":
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages_group, color=(100, 35, 35))
        else:
            ReceivingDamage(x, y, damage, Entity.all_sprites, Entity.damages_group, color=(30, 255, 30))
        # Изменение здоровья и проверка на смерть
        self.health = min(self.health - damage, self.full_health)
        if self.health <= 0:
            self.health = 0
            self.death()

    # Метод для обработки смерти игрока
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
        # Последнее время удара
        self.last_hit_time = pygame.time.get_ticks()


class PlayerScope(pygame.sprite.Sprite):
    """
    Этот класс отвечает за прицел игрока, нарпимер,
    относительно него будут создаваться заклинания
    """

    def __init__(self, x: float, y: float):
        # Конструктор класса Sprite
        super().__init__()

        self.image = load_image("assets/sprites/player/player_scope.png")
        self.image = pygame.transform.scale(self.image, (round(TILE_SIZE * 0.5),) * 2)
        self.rect = self.image.get_rect()
        # Начальное местоположение
        self.rect.center = x, y
        # Скорость перемещения
        self.speed = 30

    def update(self, x: int, y: int):
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
    """Класс, представляющий асистента (т.е. помошника игрока)"""

    # Размер помошника игрока
    size = (TILE_SIZE * 6 // 8, TILE_SIZE * 7 // 8)
    # Кадры перемещения
    frames = cut_sheet(load_image("assets/sprites/assistant/assistant.png"), 4, 4, size)
    # Кадры атаки заклинанием
    cast_frames = cut_sheet(load_image("assets/sprites/assistant/assistant_cast.png"), 5, 4, size)
    # Кадры получения урона
    get_damage_frames = cut_sheet(load_image("assets/sprites/assistant/assistant_get_damage.png"), 4, 1, size)[0]
    # Кадры смерти
    death_frames = cut_sheet(load_image("assets/sprites/assistant/assistant_death.png"), 28, 1, size)[0]
    # Переменные добавляющие эти значения к здоровью и мане каждую итерацию update()
    MANA_UP = 0.4
    HEALTH_UP = 0.1
    # Время неуязвимости, после атаки врагом (в миллисекундах)
    INVULNERABILITY_TIME_AFTER_HIT = 500

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
    # Дальность между игроком и асистентом, при которой асистент
    # телепортируется к игроку (если маны хватает)
    teleport_range = TILE_SIZE * 12
    # Область видимости врагов
    visible_range = TILE_SIZE * 10
    # Переменная для обработки дистанции до игрока (т.е. надо ли асистенту
    # идти в сторону игрока или телепортироваться к нему)
    keeping_distant_to_player = TILE_SIZE * 1.5
    # Список возможных имён помошника
    names = [
        "Aдрахил", "Aлмариан", "Aндвайс", "Aнкалагон", "Aнкалимон", "Aулендил", "Авель",
        "Адалдрида", "Аделард", "Анакин", "Антон",  "Ариан", "Аркан", "Аркана", "Армандо",
        "Асия", "Аскаланте", "Астор", "Аттилло", "Барлиман", "Бенедикт", "Бофаро", "Брооклин",
        "Вассиан", "Ваучер", "Вербер", "Вилкольм", "Виринея", "Вирсавия", "Виссарион",
        "Витольд", "Владигор", "Володар", "Гарий", "Гермоген", "Гимилзагар", "Гликерий",
        "Графиелита", "Гринат", "Громель", "Гус", "Дан", "Данаида", "Дарий", "Доримедонт",
        "Евстафий", "Зородал", "Иагон", "Иаоса", "Изаура", "Илларий", "Илларион", "Калистрат",
        "Калисфен", "Каллист", "Капитон", "Каспиан", "Кассиопея", "Клементий", "Лаврентий",
        "Ларион", "Лика", "Луара", "Люцифер", "Максимиан", "Меланфий", "Мефодий", "Неолина",
        "Никита", "Нимфадора", "Максим", "Обафеми", "Оллард", "Офелия", "Памфил", "Парфён", "Рик_Астли",
        "Патрикий", "Пафнутий", "Ратибор", "Ревмир", "Револьд", "Рубентий", "Рувим", "Селиван",
        "Серапион", "Серафим", "Согдиана", "Софрон", "Телемах", "Тирион", "Тодор", "Трифилий",
        "Троадий", "Фабиан", "Фалькор", "Феанор", "Феникс", "Финарфин", "Флавиан", "Фрумгар", "Хамфаст",
        "Хартвиг", "Хейнер", "Хродрик", "Эвмей", "Эгнор", "Эктелион", "Эланор", "Элеммакил",
        "Элим", "Элуна", "Эмельдир", "Эмметт", "Эрандир", "Эрендис", "Эрестор", "Эрнест",
        "Эстелмо", "Ювеналий", "Юст", "Юстиниан", "Киссамос", "Малиме", "Ханья", "Мурниес",
        "Палеохора", "Гиалос", "Ираклион", "Тимбаки", "Асимион", "Гудурас", "Орейнон", "Ластрос"
    ]
    # ВАЖНО!!! Ниже идёт переопределение параметров из класса игрока.
    # Это нужно, т.к. скорость и другие параметры движений асистента отличаются
    # от тех, что у игрока

    # Скорость по умолчанию (используется при эффекте замедления)
    default_speed = TILE_SIZE * 0.118
    # отметка при превышении которой, скорость асистента автоматически возврастает
    MIN_DELTA_TO_START_RUN = 1.5
    # Максимальное ускорение асистента при перемещении
    max_delta_movements = 2
    # сила с которой асистент будет набирать/уменьшать свою скорость
    DELTA_CHANGER = 0.3
    # Шрифт
    font = load_game_font(32)
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(7)
    # Звук ходьбы
    FOOTSTEP_SOUND = load_sound("assets/audio/sfx/assistant/footstep.ogg")

    def __init__(self, x, y, player, all_sprites, health=0, mana=0, name=()):
        # Получение параметров и приведение к нужному типу (т.к. на вход могут
        # передать не сразу нужные типы, например, при инициализации уровня)
        x, y, health, mana = float(x), float(y), float(health), float(mana)
        # Инициализация с полученными параметрами в игроке
        super(Player, self).__init__(x, y, all_sprites)
        # Ссылка на игрока для получение информации о нём
        self.player = player
        # Если имя не переданно, берётся случайно из списка
        self.name = " ".join(name) if name else choice(PlayerAssistant.names)
        # Иконка
        self.icon = None
        # Уровень асистента (влияет на урон)
        self.level = player.level
        self.alive = True
        # Графический прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        # Скорость
        self.speed = 0.5
        self.dx = self.dy = 0  # ускорение
        # Растояние до игрока (по умолчанию маленькое, т.к.
        # спавнится с ним в одной точке)
        self.distance_to_player = 0.0001
        # Последнее время, когда асистент переходил в сторону вокруг игрока
        self.stopping_time = pygame.time.get_ticks()
        # Текущая цель
        self.target = None
        # Отталкивается ли компаньён от врагов
        self.is_boosting_from_enemy = False
        # Видна ли цель
        self.target_observed = False
        # Ближайший враг
        self.nearest_enemy = None
        # Максимально здоровье
        self.full_health = 300
        # Текущее здоровье
        self.health = health if health else self.full_health
        # Максимальная мана
        self.full_mana = 300
        # Текущая мана
        self.mana = mana if mana else self.full_mana
        # Последнее время выстрела, получения урона и обновления целей
        self.shoot_last_time = pygame.time.get_ticks()
        self.last_hit_time = 0
        self.last_target_update = 0

    def __str__(self):
        args = [*self.rect.center, self.health, self.mana, self.name]
        return " ".join(map(str, args))

    def update(self, *args):
        if self.alive:
            # Регенерация здоровья и маны
            self.mana = min(self.mana + self.MANA_UP, self.full_mana)
            self.health = min(self.health + self.HEALTH_UP, self.full_health)
        else:
            # Если компаньён умер обновляется анимация
            super(Player, self).update_frame_state()
            return
        # Обновление базовых параметров от игрока и сущности (Entity)
        super(Player, self).update()
        enemies_group = args[0]
        # Сокращение написания координат объекта
        self_x, self_y = self.rect.center
        # Местоположение игрока
        player_x, player_y = self.player.rect.center
        # Находим расстояние между собой и игроком
        self.distance_to_player = max(dist((self_x, self_y), (player_x, player_y)), self.speed)
        line = self.distance_to_player

        self.dx = self.dy = 0  # Текущее ускорение
        # Если компаньён привысил отметку дистанции между игроком
        if line > self.keeping_distant_to_player:
            # Если разница слишком большая, компаньён
            # телепортируется к игроку, если это возможно
            if line >= self.teleport_range:
                self.shoot(self.player)
                self.point = None
            # Вычисление ускорения для движения к игроку
            part_move = max(line / self.speed, 0.5)
            self.dx = round((player_x - self_x) / part_move)
            self.dy = round((player_y - self_y) / part_move)
            self.point = None
        elif pygame.time.get_ticks() - self.stopping_time > self.WAITING_TIME:
            if not self.point or self.point == self.rect.center:
                self.stopping_time = pygame.time.get_ticks() + randint(-500, 500)
                self.point = (player_x + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75),
                              player_y + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75))
            player_x, player_y = self.point
            line = max(((player_x - self_x) ** 2 + (player_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((player_x - self_x) / part_move)
            self.dy = round((player_y - self_y) / part_move)
        # Передвижение
        self.move(self.dx, self.dy)

        ticks = pygame.time.get_ticks()
        # Обновление цели
        if ticks - self.last_target_update > 50:
            self.nearest_enemy = self.update_target(enemies_group)
        # Если виден ближайший враг, асистент атакует его
        if self.nearest_enemy:
            self.shoot(self.nearest_enemy, enemies_group)
            self.target_observed = True
        else:
            self.target_observed = False
        # Определение направления взгляда от ускорения
        if self.dx or self.dy:
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
            # Обновление анимации
            super(Player, self).update_frame_state()
        # Иначе устанавливается начальный кадр, т.к. асистент не двигается
        else:
            self.set_first_frame()
        # Сбор вещей и отдача их игроку (кроме хилки)
        for item in pygame.sprite.spritecollide(self.collider, GroundItem.sprites_group, False):
            item: GroundItem
            # Мясо асистент съедает сам (хилится)
            if item.type == "meat":
                self.get_damage(-self.MEAT_HEALTH_UP * item.count)
            # А деньги отдаются игроку, т.к. к концу игры этот счётчик
            # всё равно общий
            elif item.type == "money":
                self.player.money += item.count
            # Звук предмета и последующее удаление предмета
            self.sounds_channel.play(item.sound)
            item.kill()

    def shoot(self, target, enemies_group=None):
        if not self.alive or not target or not target.alive:
            return

        current_ticks = pygame.time.get_ticks()
        # Если не прошло время перезарядки, то заклинания не создаются
        if current_ticks - self.between_shoots_range < self.shoot_last_time:
            return
        self.shoot_last_time = current_ticks + randint(-50, 50)

        if isinstance(target, Player):
            spell = TeleportSpell
            poses = *self.rect.center, *target.rect.center
            args = *poses, 0.5 + 0.05 * self.level, [self], Entity.spells_group, Entity.all_sprites
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
            args = *poses, 0.5 + 0.05 * self.level, enemies_group, Entity.spells_group, Entity.all_sprites

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
        self.last_target_update = pygame.time.get_ticks() + randint(-10, 10)

        min_dist_to_enemy = self.visible_range + 1
        nearest_enemy = None
        for enemy in enemies_group:
            if not enemy.alive:
                continue

            dist_to_enemy = dist(self.rect.center, enemy.rect.center)
            if dist_to_enemy < min_dist_to_enemy:
                min_dist_to_enemy = dist_to_enemy
                nearest_enemy = enemy

        return nearest_enemy

    # Метод по обработке смерти асистента
    def death(self):
        if not self.alive:
            return

        self.alive = False
        self.cur_frame = 0
        self.speed = 0.00001
