from random import choice

from entities.base_entity import Entity
from entities.items import *
from entities.spells import *
from engine import *
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME


class Monster(Entity):
    """
    Класс монстров ближнего боя.
    Если игрок дальше их видимости, они ходят вокруг точки спавна.
    Если они видят игрока, они идут к нему
    """
    def __init__(self, x, y, level, seed, *args):
        super().__init__(x, y, *args)
        self.level = level
        self.seed = seed

    def death(self):
        if not self.alive:
            return

        if true_with_chance(33.33):
            pos = (self.rect.centerx + randint(-20, 20),
                   self.rect.centery + randint(-20, 20))
            spawn_item(*pos, all_sprites=Entity.all_sprites,
                       k=randint(1, [2, 3][isinstance(self, (VoidWizard, DirtySlime))]))

        if self.seed:
            self.seed[self.index_in_seed] = '0'
        self.alive = False
        self.cur_frame = 0
        self.speed = 0.0001


class WalkingMonster(Monster):
    """
    Класс монстров ближнего боя.
    Умом они не блещут, ИИ пока такой:
    Если игрок дальше их видимости, они ходят вокруг точки спавна.
    Если они видят игрока, они идут к нему
    """
    def __init__(self, x: float, y: float, level: int, seed, *args):
        super().__init__(x, y, level, seed, *args)

        self.target_observed = False
        # Значения по-умолчанию
        self.stun_time = 0
        self.visibility_range = TILE_SIZE * 6
        self.stopping_time = pygame.time.get_ticks() + randint(-750, 750)
        self.distance_to_player = 100
        self.speed = 1

    def update(self, *args):
        player = args[0]

        if not self.alive:
            super().update_frame_state()
            return

        if hypot(self.rect.center, player.rect.center) > TILE_SIZE * 25:
            return

        target = player
        min_dist = hypot(self.rect.center, player.rect.center)
        for assistant in player.assistants:
            if hypot(self.rect.center, assistant.rect.center) < min_dist and assistant.alive:
                target = assistant

        # Сокращаем написание координат объекта
        self_x, self_y = self.rect.center
        delta = 0

        point_x, point_y = target.rect.center
        # Находим расстояние между врагом и игроком
        self.distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
        line = self.distance_to_player

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range or not target.alive:
            if pygame.time.get_ticks() - self.stopping_time < Entity.WAITING_TIME:
                # Обновляем спрайты со сдвигом в 2 (спрайты без движения)
                super().update_frame_state(2)
                super().update()
                return
            if not self.point or self.point == self.rect.center:
                # Если точки нет или мы дошли, ставим время стояния и создаем новую точку
                self.stopping_time = pygame.time.get_ticks() + randint(-250, 250)
                self.point = (self.start_position[0] + randint(-TILE_SIZE * 1, TILE_SIZE * 1),
                              self.start_position[1] + randint(-TILE_SIZE * 1, TILE_SIZE * 1))
            point_x, point_y = self.point
            # Находим расстояние до точки
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            # Если монстр ушел далеко от точки, то надо быстрее идти обратно, а то слишком долго
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3
            self.target_observed = False

        else:
            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) * 4 / part_move
            self.dy = (point_y - self_y) * 4 / part_move
            self.target_observed = True

        if pygame.time.get_ticks() - self.stun_time > 300:
            self.move(self.dx, self.dy)

        self.collider.update(*self.rect.center)

        if pygame.sprite.collide_rect(self.collider, target.collider):
            if self.alive:
                ticks = pygame.time.get_ticks()
                # 2.17 - это коээфицент ускорения, был высчитан путём проб и ошибок
                # (не является константой, т.к. используется только здесь)
                boost_dx = (self.dx + player.max_delta_movements) * 2.17
                boost_dy = (self.dy + player.max_delta_movements) * 2.17
                # Чтобы игрок не умирал мгновенно, не понимая, что случилось
                if ticks - target.last_hit_time > target.INVULNERABILITY_TIME_AFTER_HIT:
                    target.get_damage(self.damage)
                target.boost_from_enemy(boost_dx, boost_dy)

            self.rect.center = self_x, self_y
            self.stun_time = pygame.time.get_ticks()

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

        # Если координаты не изменились, монстр стоял
        # Обновляем спрайты со свдигом 2 (стояние) (записывается в дельта)
        if (self_x, self_y) == self.rect.center:
            delta = 2
            self.point = None
            self.stopping_time = pygame.time.get_ticks()

        # Обновляем спрайт
        super().update()
        super().update_frame_state(delta)


class ShootingMonster(Monster):
    """
    Класс монстров дальнего боя.
    Чуть сложнее устроен:
    Если игрок слишком далеко, крутимся у стартовой токи.
    Если игрок чуть ближе, подходим к нему, чтоб наладить дистанцию и контакт для выстрела.
    (В этот момент если монстр не сдвинулся, значит преграда, так что стреляем)
    Если игрок на достаточном расстоянии, стреляем.
    Если игрок подходит слишком близко, отходим, разрываем дистанцию.
    (В этот момент если монстр не сдвинулся, значит преграда, так что снова стреляем)
    """
    def __init__(self, x: float, y: float, level: int, seed, *args):
        # Конструктор класса Sprite
        super().__init__(x, y, level, seed, *args)

        # Значения по-умолчанию
        self.visibility_range = TILE_SIZE * 13
        self.distance_to_player = 100
        self.target_observed = False

        self.collider = Collider(*self.rect.center, self.size)

        self.last_shot_time = pygame.time.get_ticks()
        self.reload_time = 1500
        self.assistants = pygame.sprite.Group()

        self.stopping_time = pygame.time.get_ticks() + randint(-500, 500)

    def update(self, *args):
        player = args[0]

        if not self.alive:
            super().update_frame_state()
            return

        super().update()
        if hypot(self.rect.center, player.rect.center) > TILE_SIZE * 25:
            return

        self_x, self_y = self.rect.center
        delta = 0

        target = player
        min_dist = hypot(self.rect.center, player.rect.center)
        for assistant in player.assistants:
            if hypot(self.rect.center, assistant.rect.center) < min_dist and assistant.alive:
                target = assistant

        point_x, point_y = target.rect.centerx, target.rect.centery
        # Расстояние между врагом и игроком
        self.distance_to_player = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)
        line = self.distance_to_player

        # Если игрок далеко, крутимся у своей стартовой точки
        if line >= self.visibility_range or not target.alive:
            if pygame.time.get_ticks() - self.stopping_time < Entity.WAITING_TIME:
                super().update_frame_state(2)
                return
            if not self.point or self.point == self.rect.center:
                self.stopping_time = pygame.time.get_ticks() + randint(-500, 500)
                self.point = (self.start_position[0] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75),
                              self.start_position[1] + randint(-TILE_SIZE * 0.75, TILE_SIZE * 0.75))
            point_x, point_y = self.point
            line = max(((point_x - self_x) ** 2 + (point_y - self_y) ** 2) ** 0.5, self.speed)

            part_move = max(line / self.speed, 0.5)
            self.dx = round((point_x - self_x) / part_move)
            self.dy = round((point_y - self_y) / part_move)
            if line > 1.5 * TILE_SIZE:
                self.dx *= 3
                self.dy *= 3
            self.target_observed = False

        # Если игрок слишком близко, отходим, мы же дальний бой
        elif line <= self.visibility_range * 0.4:
            for assistant in self.assistants:
                assistant.point = target.rect.center
                assistant.target_observed = True

            part_move = max(line / self.speed, 1)
            self.dx = -(point_x - self_x) * 4 / part_move
            self.dy = -(point_y - self_y) * 4 / part_move
            self.target_observed = True

        # Если игрок пытается уйти из радиуса нашего поражения, догоняем
        elif line >= self.visibility_range * 0.6:
            for assistant in self.assistants:
                assistant.point = target.rect.center
                assistant.target_observed = True

            part_move = max(line / self.speed, 1)
            self.dx = (point_x - self_x) * 4 / part_move
            self.dy = (point_y - self_y) * 4 / part_move
            self.target_observed = True

        # Иначе стоим и постреливаем (чуть дальше)
        else:
            for assistant in self.assistants:
                assistant.point = target.rect.center
                assistant.target_observed = True

            self.dx = self.dy = 0
            self.target_observed = True

        self.move(self.dx, self.dy)
        # Если не сдвинулись с места
        if (self_x, self_y) == self.rect.center:
            # Выбираем спрайты стояния
            delta = 2
            reload_time = self.reload_time
            if self.ice_buff:
                reload_time *= 2
            if self.distance_to_player <= self.visibility_range:
                if pygame.time.get_ticks() - self.last_shot_time > reload_time:
                    self.last_shot_time = pygame.time.get_ticks()
                    # Стреляем в игрока
                    if self.alive and target.alive:
                        self.shoot(player)

        # Направление взгляда
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

        # Обновление спрайта
        super().update_frame_state(delta)

    def shoot(self, player):
        if not self.alive:
            return
        enemies_group = self.groups()[-1]
        enemies_group.remove(self)
        for assistant in self.assistants:
            if assistant in enemies_group:
                enemies_group.remove(assistant)
        args = (*self.rect.center, *player.rect.center, self.extra_damage,
                list(enemies_group) + [player] + list(player.assistants), self.spells_group, Entity.all_sprites)
        for assistant in self.assistants:
            enemies_group.add(assistant)
        enemies_group.add(self)

        if isinstance(self, FireWizard):
            spell = FireSpell(*args)

        elif isinstance(self, VoidWizard):
            if len(self.assistants) < 7 and true_with_chance(15):
                spell = CallZombiesSpell
                args = (self.level, [], Entity.all_sprites, self.assistants, enemies_group)
                for m in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    i, j = m
                    if true_with_chance(75):
                        if true_with_chance(20):
                            zombie = Demon(*(self.rect.center + args))
                        else:
                            zombie = Zombie(*(self.rect.center + args))

                        while True:
                            zombie.rect.center = (self.rect.centerx + randint(-TILE_SIZE, TILE_SIZE),
                                                  self.rect.centery + randint(-TILE_SIZE, TILE_SIZE))
                            zombie.collider.update(*zombie.rect.center)
                            if not pygame.sprite.spritecollideany(zombie.collider, Entity.collisions_group):
                                break

                        zombie.point = self.rect.centerx + i * TILE_SIZE, self.rect.centery + j * TILE_SIZE
                self.last_shot_time = pygame.time.get_ticks() + self.reload_time * 3
            else:
                spell = VoidSpell(*args)

        else:
            spell = None
            spell.CAST_SOUND = player.NO_MANA_SOUND

        self.sounds_channel.play(spell.CAST_SOUND)


class Demon(WalkingMonster):
    """
    Демон

    Мало жизней
    Быстрый
    Больно бьёт
    Устойчивойть к огню
    Слабость к льду
    """
    name = 'Демон'
    damage = 50
    size = (int(TILE_SIZE // 8 * 5),) * 2
    frames = cut_sheet(load_image('demon_run.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('demon_idle.png', 'assets\\enemies'), 4, 2, size)

    get_damage_frames = cut_sheet(load_image('demon_get_damage.png', 'assets\\enemies'), 2, 1, size)[0]
    death_frames = cut_sheet(load_image('demon_dying.png', 'assets\\enemies'), 16, 1, size)[0]

    UPDATE_TIME = 60
    default_speed = TILE_SIZE * 0.03

    look_directions = {
        (-1, -1): 1,
        (-1, 0):  1,
        (-1, 1):  1,
        (0, -1):  1,
        (0, 0):   0,
        (0, 1):   0,
        (1, -1):  0,
        (1, 0):   0,
        (1, 1):   0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "little_steps.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)
        self.alive = True
        self.visibility_range = TILE_SIZE * 8

        self.health = round(40 * (1 + 0.05 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health


class GreenSlime(WalkingMonster):
    """
    Cлизень

    Медленный
    Среднее количество жизней
    Не очень большой урон
    Устойчивость к отравлению
    (я сам отравление)
    Слабость к молниям
    """
    name = 'Слизень'
    damage = 60
    frames = cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('green_slime_any.png', 'assets\\enemies'), 4, 2)

    get_damage_frames = cut_sheet(load_image('green_slime_get_damage.png', 'assets\\enemies'), 2, 1)[0]
    death_frames = cut_sheet(load_image('green_slime_dying.png', 'assets\\enemies'), 16, 1)[0]

    default_speed = TILE_SIZE * 0.015
    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(4)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "slime_sound.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)
        self.alive = True
        self.visibility_range = TILE_SIZE * 7

        self.health = round(100 * (1 + 0.05 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health


class DirtySlime(WalkingMonster):
    """
    Грязный слизень
    Я как , но чуть крепче

    Медленный
    Много жизней
    Не очень большой урон
    Устойчивость к льду
    Слабость к пустоте
    """
    name = 'Грязный слизень'
    damage = 90
    frames = cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('dirty_slime_any.png', 'assets\\enemies'), 4, 2)

    get_damage_frames = cut_sheet(load_image('dirty_slime_get_damage.png', 'assets\\enemies'), 2, 1)[0]
    death_frames = cut_sheet(load_image('dirty_slime_dying.png', 'assets\\enemies'), 16, 1)[0]

    default_speed = TILE_SIZE * 0.02
    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(4)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "slime_sound_1.ogg"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)
        self.alive = True
        self.visibility_range = TILE_SIZE * 8

        self.health = round(200 * (1 + 0.1 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health


class Zombie(WalkingMonster):
    """
    Зомби

    Не медленный, но и не быстрый
    Среднее количество жизней
    Средний урон
    Устойчивость к молниям
    (они двигают мои нейроны)
    Слабость - огонь
    (земля пухом учёным)
    """
    name = 'Зомби'
    damage = 30
    frames = cut_sheet(load_image('zombie_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('zombie_idle.png', 'assets\\enemies'), 4, 2)

    get_damage_frames = cut_sheet(load_image('zombie_get_damage.png', 'assets\\enemies'), 2, 1)[0]
    death_frames = cut_sheet(load_image('zombie_dying.png', 'assets\\enemies'), 16, 1)[0]

    default_speed = TILE_SIZE * 0.02
    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "stone_steps_1.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)
        self.alive = True
        self.visibility_range = TILE_SIZE * 8

        self.health = round(80 * (1 + 0.05 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health


class FireWizard(ShootingMonster):
    """
    Маг

    Подвижный
    Маловато жизней
    Средний урон
    Устойчивость к молниям
    Слабость к льду
    """
    name = 'Маг огня'
    size = (TILE_SIZE // 8 * 7,) * 2
    frames = cut_sheet(load_image('wizard_run.png', 'assets\\enemies'), 4, 2, size)
    frames += cut_sheet(load_image('wizard_idle.png', 'assets\\enemies'), 4, 2, size)

    get_damage_frames = cut_sheet(load_image('wizard_get_damage.png', 'assets\\enemies'), 2, 1, size)[0]
    death_frames = cut_sheet(load_image('wizard_dying.png', 'assets\\enemies'), 16, 1, size)[0]

    default_speed = TILE_SIZE * 0.012
    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(3)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "wizard_rustle.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)
        self.alive = True
        self.visibility_range = TILE_SIZE * 9

        self.extra_damage = 1 + 0.05 * level
        self.health = round(80 * (1 + 0.05 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health


class VoidWizard(ShootingMonster):
    """
    Большой маг

    Подвижный
    Среднее количество жизней
    Большой урон
    Устойчивость к пустоте
    Слабость к огню
    (МОЙ ПЛАЩ ГОРИТ)
    """
    name = 'Древний маг'
    damage = 20
    frames = cut_sheet(load_image('long_wizard_run.png', 'assets\\enemies'), 4, 2)
    frames += cut_sheet(load_image('long_wizard_idle.png', 'assets\\enemies'), 4, 2)

    get_damage_frames = cut_sheet(load_image('long_wizard_get_damage.png', 'assets\\enemies'), 2, 1)[0]
    death_frames = cut_sheet(load_image('long_wizard_dying.png', 'assets\\enemies'), 16, 1)[0]

    default_speed = TILE_SIZE * 0.01
    look_directions = {
        (-1, -1): 1,
        (-1, 0): 1,
        (-1, 1): 1,
        (0, -1): 1,
        (0, 0): 0,
        (0, 1): 0,
        (1, -1): 0,
        (1, 0): 0,
        (1, 1): 0
    }
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(2)

    # Звуки
    FOOTSTEP_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\enemies\\audio", "wizard_rustle.mp3"))
    FOOTSTEP_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x, y, level, *args):
        super().__init__(x, y, level, *args)

        self.visibility_range = TILE_SIZE * 13

        self.extra_damage = 1.25 + 0.07 * level
        self.health = round(130 * (1 + 0.1 * level))
        self.health += randint(-round(self.health * 0.2), round(self.health * 0.2))
        self.full_health = self.health

        self.reload_time = self.reload_time * 4 / 3


def random_monster(x, y, level, all_sprites, enemies_group, seed, user_seed):
    if user_seed:
        n = int(user_seed.pop(0))
    else:
        n = randint(1, round(35 - level * 2))
    args = (x * TILE_SIZE + TILE_SIZE * 0.5, y * TILE_SIZE + TILE_SIZE * 0.5,
            level - 1, seed, all_sprites, enemies_group)

    if n in (1, 2):
        monster = Demon(*args)
    elif n in (3, 4):
        monster = GreenSlime(*args)
    elif n in (5,):
        monster = DirtySlime(*args)
    elif n in (6, 7):
        monster = Zombie(*args)
    elif n in (8, 9):
        monster = FireWizard(*args)
    elif n in (10,):
        monster = VoidWizard(*args)
    else:
        # Специально, чтоб монстры спавнились в этом месте не со 100% шансом
        seed.append('0')
        return None

    # Запишем получившееся значение в сид
    seed.append(str(n))
    monster.index_in_seed = len(seed) - 1
    # Возвращаем монстра, записав ему параметр Индекс в сиде,
    # Чтоб после его смерти удалить его из save.txt
    return monster
