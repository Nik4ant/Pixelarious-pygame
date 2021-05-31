import os
import time

from config import *
from engine import load_image, load_game_font, loading_screen, \
    get_joystick, check_any_joystick

from entities.base_entities import *
from entities.enemies import Monster
from entities.items import GroundItem
from entities.player import Player, PlayerAssistant
from entities.spells import *
from entities.tile import Chest, load_tile

from UI import end_screen, game_menu
from UI.UI_components import SpellContainer, PlayerIcon, Message

from generation_map import initialise_level, generate_new_level


# Функция записи сохранения
def save(current_seed: str) -> None:
    """
    Функция записывает файл сохранения в data/save.txt
    (Если папки data нет, то она создаётся)
    :param current_seed: Данные о текущей игре
    """
    if 'data' not in os.listdir():
        os.mkdir('data')
    with open('data/save.txt', 'w', encoding='utf-8') as file:
        file.write(current_seed)


class Camera:
    """Класс, представляющий камеру"""
    def __init__(self, screen_size, speed_coefficient=0.5):
        """
        Инициализация
        :param screen_size: Размеры экрана
        :param speed_coefficient: Коэфицент скорости камеры
        """
        # Сдвиг камеры (будет меняться при обновлении)
        self.dx = 0
        self.dy = 0

        self.screen_width, self.screen_height = screen_size
        self.speed_coefficient = speed_coefficient

    def apply(self, sprite) -> None:
        """
        Метод сдвигает спрайт на смещение камеры
        :param sprite: Спрайт, который надо сдвинуть
        (к спрайтам относятся и внутреигровые объекты)
        """
        # Смещение
        sprite.rect.x += self.dx
        sprite.rect.y += self.dy
        # Учёт сущностьей, которые могут менять своё положение в пространстве
        if isinstance(sprite, (Entity, Spell)):
            self.apply_point(sprite)

    def apply_point(self, obj) -> None:
        """
        Метод сдвигает точку спавна объекта и точку, к которой он движется
        :param obj: Движущийся объект
        """
        # Смещение точки спавна и точки движения, если они не заданы
        if obj.start_position:
            obj.start_position = obj.start_position[0] + self.dx, obj.start_position[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    def update(self, target) -> None:
        """
        Метод позиционирует камеру на объекте target
        (т.е. подстраивает смещение под него)
        :param target: Объект относительно которого позиционируется камера
        """
        self.dx = -round((target.rect.centerx - self.screen_width // 2) * self.speed_coefficient)
        self.dy = -round((target.rect.centery - self.screen_height // 2) * self.speed_coefficient)


def play(screen: pygame.surface.Surface,
         level_number: int = 1, user_seed: str = None) -> int:
    """
    Функция запуска игрового процесса
    :param screen: Экран для отрисовки
    :param level_number: Номер текущего уровня
    :param user_seed: Сид карты. Если он есть, по нему создаются уровни,
    раставляются враги и прочее
    :return: Код завершения игры (значения описаны в main.py)
    """
    # Псевдо загрузочный экран (для красоты)
    loading_screen(screen)
    # Размеры экрана
    screen_width, screen_height = screen.get_size()
    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов пола
    tiles_group = pygame.sprite.Group()
    # Группа со спрайтами ящиков и бочек
    # (они отдельно, т.к. это разрушаемые объекты)
    furniture_group = pygame.sprite.Group()
    # Группа со спрайтами преград (т.е. все физические объекты)
    collidable_tiles_group = pygame.sprite.Group()
    # Группа со спрайтами врагов
    enemies_group = pygame.sprite.Group()
    # Группа со спрайтами дверей
    doors_group = pygame.sprite.Group()
    # Группа со спрайтами факелов
    torches_group = pygame.sprite.Group()
    # Группа со спрайтом конца уровня (т.е. с лестницой перехода вниз)
    end_of_level = pygame.sprite.Group()
    # Группа с предметаими, которые находятся на полу
    GroundItem.sprites_group = pygame.sprite.Group()
    # Группа с сундуками
    Chest.chest_group = pygame.sprite.Group()

    is_open = True
    # Поверхность для эффекта затемнения
    transparent_grey = pygame.surface.Surface((screen_width, screen_height),
                                              pygame.SRCALPHA).convert_alpha()
    clock = pygame.time.Clock()  # Часы
    current_seed = user_seed  # текущий сид
    # Создаем уровень с помощью функции из generation_map
    level, level_seed = generate_new_level(current_seed.split('\n')[0].split() if current_seed else 0)
    # Игрок (None, т.к. будет переопределён либо при инициализации, либо при по)
    player = None
    if current_seed:
        data = current_seed.split('\n')  # Данные из сида
        # Получение данных об игроке из сида и создание игрока
        _, _, player_level, health, mana, money = data[3].split()[:-1]
        player = Player(0, 0, player_level, all_sprites, health, mana, money)
        # Получение данных об асистентах игрока
        for n in range(int(data[3].split()[-1])):
            # Получениев параметров асистента и его создание
            x1, y1, health, mana, *name = data[4 + n].split()
            assistant = PlayerAssistant(0, 0, player, all_sprites, health, mana, name)
            # Добавление асистента
            player.add_assistant(assistant)
    # Необходимые аргументы для инициализации уровня
    args = (level, level_number, all_sprites, tiles_group, furniture_group, collidable_tiles_group, enemies_group,
            doors_group, torches_group, end_of_level, current_seed.split('\n')[1].split() if current_seed else [],
            current_seed.split('\n')[2].split() if current_seed else [], player)
    # Инициализация уровня и получение данных об игроке и частях сида
    player, monsters_seed, boxes_seed = initialise_level(*args)
    if current_seed:
        # Если сид был передан, сдвигаем игрока на расстояние от начала уровня (лестницы)
        # Которое было записано в сид
        x_from_start, y_from_start = map(float, current_seed.split('\n')[3].split()[:2])
        player.rect.center = player.rect.centerx + x_from_start, player.rect.centery + y_from_start
    # Смещение всех асистентов игрока
    for assistant in player.assistants:
        assistant.rect.center = player.rect.center
    # Обновление и сохранение сида после инициализации уровня
    current_seed = '\n'.join([' '.join(level_seed), ' '.join(monsters_seed), ' '.join(boxes_seed),
                              str(player), str(level_number)])
    save(current_seed)
    camera = Camera(screen.get_size())  # камера
    # Инициализация начальной позиции прицела игрока
    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
    # Шрифт для вывода фпс в левом верхнем углу
    fps_font = load_game_font(48)
    # Иконка рядом с номером уровня (в правом верхнем углу)
    level_number_icon = load_tile('DOWNSTAIRS.png')
    # Иконка рядом с количеством врагов на уровне (в правом верхнем углу)
    monster_number_icon = load_image('assets/sprites/UI/icons/monster_number.png', (TILE_SIZE,) * 2)
    # Шрифт для вывода номера уровня и количества врагов
    level_and_enemies_font = load_game_font(64)
    # Сообщение, которое будет появлятся при приближении игрока к сундуку
    chest_title = Message(screen, 'Нажмите Е (или L2), чтобы открыть сундук', screen.get_height() * 0.1)
    # Сообщение, которое будет появлятся при приближении игрока к спуску вниз
    downstairs_title = Message(screen, 'Нажмите Е (или L2), чтобы перейти на следующий уровень',
                               screen.get_height() * 0.1)
    # Иконки для отображения иконок (контейнеров) с заклинаниями внизу экрана
    spells_containers = (
        SpellContainer("fire_spell.png", FireSpell, player),
        SpellContainer("ice_spell.png", IceSpell, player),
        SpellContainer("poison_spell.png", PoisonSpell, player),
        SpellContainer("void_spell.png", VoidSpell, player),
        SpellContainer("light_spell.png", FlashSpell, player),
        SpellContainer("teleport_spell.png", TeleportSpell, player),
    )
    # Панель с иконкой и информацией об игроке в левом верхнем углу
    player_icon = PlayerIcon(player)
    # Высота для высчитывания позиции отрисовки иконки асистента
    assistants_height = 180
    # Отступ для вывода иконки игрока и его ассистентов
    indent = 20
    # Фоновая музыка
    pygame.mixer.music.load("assets/audio/music/game_bg.ogg")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)
    # Установка событий, обрабатываемых pygame, чтобы не тратить
    # время на обработку ненужных событий (это относится ко всей игре в целом,
    # где обрабатываются события)
    pygame.event.set_allowed((pygame.QUIT, pygame.MOUSEBUTTONUP, pygame.KEYDOWN, ))
    # Игровой цикл
    while is_open:
        was_pause_activated = False  # была ли активирована пауза
        keys = pygame.key.get_pressed()  # нажатые клавиши
        buttons = pygame.mouse.get_pressed(5)  # нажатые кнопки мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_open = False
            if event.type == pygame.KEYDOWN:
                if event.key == CONTROLS["KEYBOARD_PAUSE"]:
                    was_pause_activated = True
        # Провверка использования заклинаний с джойстика
        if player.joystick:
            if player.joystick.get_button(CONTROLS["JOYSTICK_UI_PAUSE"]):
                was_pause_activated = True
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_FIRE"]):
                player.shoot('fire', enemies_group)
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_ICE"]):
                player.shoot('ice', enemies_group)
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_LIGHT"]):
                player.shoot('flash', enemies_group)
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_POISON"]):
                player.shoot('poison', enemies_group)
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_VOID"]):
                player.shoot('void', enemies_group)
            # Используется ось, т.к. назначен триггер R2
            if player.joystick.get_axis(CONTROLS["JOYSTICK_SPELL_TELEPORT"]) > JOYSTICK_SENSITIVITY:
                player.shoot('teleport', tiles_group)
        # Иначе ввод с клавиатуры
        else:
            if keys[CONTROLS["KEYBOARD_SPELL_FIRE"]] or buttons[CONTROLS["MOUSE_SPELL_FIRE"]]:
                player.shoot('fire', enemies_group)
            if keys[CONTROLS["KEYBOARD_SPELL_ICE"]] or buttons[CONTROLS["MOUSE_SPELL_ICE"]]:
                player.shoot('ice', enemies_group)
            if keys[CONTROLS["KEYBOARD_SPELL_LIGHT"]] or buttons[CONTROLS["MOUSE_SPELL_LIGHT"]]:
                player.shoot('flash', enemies_group)
            if keys[CONTROLS["KEYBOARD_SPELL_POISON"]] or buttons[CONTROLS["MOUSE_SPELL_POISON"]]:
                player.shoot('poison', enemies_group)
            if keys[CONTROLS["KEYBOARD_SPELL_VOID"]]:
                player.shoot('void', enemies_group)
            if keys[CONTROLS["KEYBOARD_SPELL_TELEPORT"]]:
                player.shoot('teleport', tiles_group)
        # Обработка паузы
        if was_pause_activated:
            # # Остановка звуков и музыки
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            # Запуск меню паузы
            code = game_menu.execute(screen)
            if code == 1:
                # Псевдо экран загрузки перед следующими действиями (для красоты)
                loading_screen(screen)
                # Очищаем все группы со спрайтами
                all_sprites.empty()
                tiles_group.empty()
                furniture_group.empty()
                collidable_tiles_group.empty()
                enemies_group.empty()
                doors_group.empty()
                torches_group.empty()
                end_of_level.empty()
                Chest.chest_group.empty()
                GroundItem.sprites_group.empty()
                Entity.damages_group.empty()
                # Сохранение данных перед выходом
                save('')
                return 2
            if code is not None:
                # Ставим экран загрузки перед следующими действиями
                loading_screen(screen)
                # Очищаем все группы со спрайтами
                all_sprites.empty()
                tiles_group.empty()
                furniture_group.empty()
                collidable_tiles_group.empty()
                enemies_group.empty()
                doors_group.empty()
                torches_group.empty()
                end_of_level.empty()
                Chest.chest_group.empty()
                GroundItem.sprites_group.empty()
                Entity.damages_group.empty()
                # Сохранение данных перед выходом
                if player.alive:
                    current_seed = '\n'.join([' '.join(level_seed), ' '.join(monsters_seed), ' '.join(boxes_seed),
                                              str(player), str(level_number)])
                    save(current_seed)
                else:
                    save('')
                return -1
            # Возвращение звука и мызыки так, как было до паузы
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()
        screen.fill(BACKGROUND_COLOR)  # Очистка экрана
        player.update()  # Обновление игрока
        # Если игрок умер, то открывается экран конца игры
        if player.destroyed:
            # Остановка звуков и музыки
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            # Подсчёт количества живых асистентов у игрока (для вывода статистики)
            count_of_alive_assistants = 0
            for sprite in player.assistants.sprites():
                sprite: PlayerAssistant
                # Если асистент живой увеличиваем счётчик
                count_of_alive_assistants += int(sprite.alive)
            # Запуск экрана с концом
            end_screen.execute(screen, player.money, count_of_alive_assistants)
            return -1
        # Проверка на столкновение с любым сундуком
        if pygame.sprite.spritecollideany(player, Chest.chest_group):
            # Обновление времени столкновения с сундуком для
            # красивой отрисовки сообщения
            chest_title.last_collide_time = pygame.time.get_ticks()
            # Проверка на использование (с джойстика или клавиатуры)
            if ((player.joystick and
                 player.joystick.get_axis(CONTROLS['JOYSTICK_USE']) > JOYSTICK_SENSITIVITY)
                    or (keys[CONTROLS['KEYBOARD_USE']])):
                pygame.sprite.spritecollide(player, Chest.chest_group, False)[0].open()

        enemies_group.update(player)  # обновление врагов
        player.assistants.update(enemies_group)  # обновление асистентов
        Entity.spells_group.update()  # обновление заклинаний
        # Обновление факелов (для звука огня по расстоянию до факела)
        torches_group.update(player)
        # Обновление всех дверей
        doors_group.update(player, enemies_group, [player] + list(player.assistants))
        Chest.chest_group.update()  # обновление сундуков
        Entity.damages_group.update()  # обновление текста с выводом урона
        # Проверка перехода на следующий уровень, при соприкосновении с лестницой вниз
        if pygame.sprite.spritecollideany(player.collider, end_of_level):
            # Обновление времени столкновения с лестницой вниз для
            # красивой отрисовки сообщения
            downstairs_title.last_collide_time = pygame.time.get_ticks()
            if (keys[pygame.K_e] or
                    (player.joystick and
                     player.joystick.get_axis(CONTROLS['JOYSTICK_USE']) > JOYSTICK_SENSITIVITY)):
                # Затухание музыки и звуком
                pygame.mixer.fadeout(1000)
                pygame.mixer.music.fadeout(1000)
                # Псевдо загрузочный экран для красоты
                loading_screen(screen)
                # Если игрок прошёл 10 уровней, то это победа
                if level_number == 10:
                    # Подсчёт количества живых асистентов у игрока (для вывода статистики)
                    count_of_alive_assistants = 0
                    for sprite in player.assistants.sprites():
                        sprite: PlayerAssistant
                        # Если асистент живой увеличиваем счётчик
                        count_of_alive_assistants += int(sprite.alive)
                    # Победный экран
                    end_screen.execute(screen, player.money, count_of_alive_assistants, is_win=True)
                    return -1
                # Иначе перезагружаются параметры для нового уровня
                else:
                    # Очистка всех групп со спрайтами
                    all_sprites.empty()
                    tiles_group.empty()
                    furniture_group.empty()
                    collidable_tiles_group.empty()
                    enemies_group.empty()
                    doors_group.empty()
                    torches_group.empty()
                    end_of_level.empty()
                    Chest.chest_group.empty()
                    GroundItem.sprites_group.empty()
                    Entity.damages_group.empty()
                    level_number += 1  # увеличение номер уровня
                    # Создание целиком нового уровень функцией из generation_map
                    level, level_seed = generate_new_level(0)
                    # Необходимые аргументы для инициализации уровня
                    args = (level, level_number, all_sprites, tiles_group, furniture_group, collidable_tiles_group,
                            enemies_group, doors_group, torches_group, end_of_level, [], [])
                    # Инициализация уровня и получение данных об игроке и частях сида
                    player, monsters_seed, boxes_seed = initialise_level(*args, player=player)
                    # Добавление игрока и асистентов
                    all_sprites.add(player)
                    all_sprites.add(player.assistants)
                    # Смещение асистентов к игроку
                    for assistant in player.assistants:
                        assistant.rect.center = player.rect.center
                    # Изменение текущего сида и файла сохранения
                    current_seed = '\n'.join([' '.join(level_seed), ' '.join(monsters_seed), ' '.join(boxes_seed),
                                              str(player), str(level_number)])
                    save(current_seed)
                    # Установка начальной позиции приуела
                    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
                    # Иконки для отображения иконок (контейнеров) с заклинаниями внизу экрана
                    spells_containers = (
                        SpellContainer("fire_spell.png", FireSpell, player),
                        SpellContainer("ice_spell.png", IceSpell, player),
                        SpellContainer("poison_spell.png", PoisonSpell, player),
                        SpellContainer("void_spell.png", VoidSpell, player),
                        SpellContainer("light_spell.png", FlashSpell, player),
                        SpellContainer("teleport_spell.png", TeleportSpell, player),
                    )
                    # Включение музыки после обновления параметров
                    pygame.mixer.music.play(-1)
                    continue
        # Применение смещения камеры относительно игрока
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        # Отрисовка спрайтов в определённом порядке,
        # чтобы они не перекрывали друг друга
        tiles_group.draw(screen)  # тайлы пола
        torches_group.draw(screen)  # факеда
        # Сундуки
        for chest in Chest.chest_group:
            chest.draw_back_image(screen)
        # предметы на земле (мясо и деньги)
        GroundItem.sprites_group.draw(screen)
        collidable_tiles_group.draw(screen)  # физические объекты не являющиеся стенами
        doors_group.draw(screen)  # двери
        enemies_group.draw(screen)  # враги
        player.assistants.draw(screen)  # асистенты
        # Шкалы здоровья у асистентов
        for assistant in player.assistants:
            assistant.draw_health_bar(screen)
        player.draw(screen)  # игрок
        Entity.spells_group.draw(screen)  # заклинания
        player.draw_health_bar(screen)  # шкала здоровья у игрока
        # Шкала здоровья у врагов
        for enemy in enemies_group:
            enemy.draw_health_bar(screen)
        Entity.damages_group.draw(screen)  # текст с уроном
        chest_title.draw(screen)  # сообщение по мере приближении к сундуку
        # сообщение по мере приближении к лестнице вниз
        downstairs_title.draw(screen)
        # Значения для определения того, какие иконки текст,
        # нужно отображать на иконках с заклинаниями (нужно, чтобы игроку было
        # проще привыкнуть к управлению)
        is_joystick = player.joystick is not None
        if is_joystick:
            spell_args = ("o", "x", "triangle", "square", "L1", "L2")
        else:
            spell_args = ("1", "2", "3", "4", "5", "Space")
        # Контейнеры с заклинаниями
        for i in range(len(spells_containers) - 1, -1, -1):
            pos = (screen_width * (0.375 + 0.05 * i), screen_height * 0.9)
            spells_containers[i].draw(screen, pos, is_joystick, spell_args[i])
        # Панель с игроком в левом верхнем углу
        player_icon.draw(screen, (indent, indent))
        # Иконоки у асистентов
        for number_of_assistant, assistant in enumerate(player.assistants):
            if not assistant.icon:
                assistant.icon = PlayerIcon(assistant)
            assistant.icon.draw(screen, (indent + 20, assistants_height + number_of_assistant * 80), 0.5)
        # фпс
        fps_text = fps_font.render(str(round(clock.get_fps())), True, (100, 255, 100))
        screen.blit(fps_text, (2, 2))
        # Иконка и количество врагов на уровне
        monster_number_text = level_and_enemies_font.render(str(len(enemies_group)), True,
                                                            (255, 255, 255))
        screen.blit(monster_number_icon, (screen_width - 70, 80))
        screen.blit(monster_number_text, (screen_width - 120, 80))
        # Иконка и номер уровня
        level_number_text = level_and_enemies_font.render(str(level_number), True,
                                                          (255, 255, 255))
        screen.blit(level_number_icon, (screen_width - 70, 10))
        screen.blit(level_number_text, (screen_width - 120, 10))
        # Прицел игрока
        player.scope.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()

    # Запись сохранения после закрытия игры
    save(current_seed)
    return 0
