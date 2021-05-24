from config import *
from engine import *

from entities.base_entities import *
from entities.enemies import Monster
from entities.items import GroundItem
from entities.player import Player, PlayerAssistant
from entities.spells import *
from entities.tile import Chest, load_tile

from UI import end_screen, game_menu
from UI.UI_components import SpellContainer, PlayerIcon, Message

from generation_map import initialise_level, generate_new_level


# Функция сохраняющая игру
def save(current_seed: str):
    if 'data' not in os.listdir():
        os.mkdir('data')
    with open('data/save.txt', 'w', encoding='utf-8') as file:
        file.write(current_seed)


class Camera:
    """
    Класс, представляющий камеру
    """
    def __init__(self, screen_size, speed_coefficient=0.5):
        # инициализация начального сдвига для камеры
        self.dx = 0
        self.dy = 0
        self.screen_width, self.screen_height = screen_size
        self.speed_coefficient = speed_coefficient

    # сдвинуть объект obj на смещение камеры
    def apply(self, sprite):
        sprite.rect.x += self.dx
        sprite.rect.y += self.dy
        if isinstance(sprite, (Entity, Spell)):
            self.apply_point(sprite)

    # Функция сдвигает точку спавна существа и точку, к которой он идет
    def apply_point(self, obj):
        if obj.start_position:
            obj.start_position = obj.start_position[0] + self.dx, obj.start_position[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    # метод позиционирования камеры на объекте target
    def update(self, target):
        self.dx = -round((target.rect.centerx - self.screen_width * 0.5) * self.speed_coefficient)
        self.dy = -round((target.rect.centery - self.screen_height * 0.5) * self.speed_coefficient)


def play(screen: pygame.surface.Surface,
         level_number: int = 1, user_seed: str = None) -> int:
    """
    Функция запуска игры
    :param screen: экран
    :param level_number: Номер уровня, чтобы при подгрузке показывать его
    таким, каким он был задан.
    :param user_seed: сид карты если есть, создаем по нему уровень и мобов
    :return: Код завершения игры. 0 - выход из игры -1 в остальных случаях
    """
    # Ставим загрузочный экран
    loading_screen(screen)

    screen_width, screen_height = screen.get_size()

    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов
    tiles_group = pygame.sprite.Group()
    # Группа со спрайтами ящиков и бочек
    furniture_group = pygame.sprite.Group()
    # Группа со спрайтами преград
    collidable_tiles_group = pygame.sprite.Group()
    # Группа со спрайтами врагов
    enemies_group = pygame.sprite.Group()
    # Группа со спрайтами дверей
    doors_group = pygame.sprite.Group()
    # Группа со спрайтами факелов
    torches_group = pygame.sprite.Group()
    # Группа со спрайтом конца уровня
    end_of_level = pygame.sprite.Group()
    # Группа с предметаими, которые находятся на полу
    GroundItem.sprites_group = pygame.sprite.Group()
    # Группа с сундуками
    Chest.chest_group = pygame.sprite.Group()

    is_game_open = True

    transition = 0
    transparent_grey = pygame.surface.Surface((screen_width, screen_height), pygame.SRCALPHA).convert_alpha()

    # Часы, отвечающие за фпс в игре
    clock = pygame.time.Clock()

    current_seed = user_seed  # текущий сид

    # Создаем уровень с помощью функции из generation_map
    level, level_seed = generate_new_level(current_seed.split('\n')[0].split() if current_seed else 0)

    player = None
    if current_seed:
        # Создание игрока по параметрам из сида, если сид передан
        _, _, player_level, health, mana, money = current_seed.split('\n')[3].split()[:-1]
        player = Player(0, 0, player_level, all_sprites, health, mana, money)

        data = current_seed.split('\n')
        for n in range(int(data[3].split()[-1])):
            x1, y1, health, mana, *name = data[4 + n].split()
            assistant = PlayerAssistant(0, 0, player, all_sprites, health, mana, name)
            player.add_assistant(assistant)

    # Создаем монстров и плитки, проходя по уровню
    args = (level, level_number, all_sprites, tiles_group, furniture_group, collidable_tiles_group, enemies_group,
            doors_group, torches_group, end_of_level, current_seed.split('\n')[1].split() if current_seed else [],
            current_seed.split('\n')[2].split() if current_seed else [], player)
    player, monsters_seed, boxes_seed = initialise_level(*args)

    if current_seed:
        # Если сид был передан, сдвигаем игрока на расстояние от начала уровня (лестницы)
        # Которое было записано в сид
        x_from_start, y_from_start = map(float, current_seed.split('\n')[3].split()[:2])
        player.rect.center = player.rect.centerx + x_from_start, player.rect.centery + y_from_start

    for assistant in player.assistants:
        assistant.rect.center = player.rect.center

    # Обновляем сид после инициализации уровня
    current_seed = '\n'.join([' '.join(level_seed), ' '.join(monsters_seed), ' '.join(boxes_seed),
                              str(player), str(level_number)])
    save(current_seed)

    # Создаем камеру
    camera = Camera(screen.get_size())

    # Инициализируем прицел игрока
    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))

    fps_font = load_game_font(48)

    level_number_icon = load_tile('DOWNSTAIRS.png')
    minster_number_icon = load_image('assets/sprites/UI/icons/monster_number.png', (TILE_SIZE,) * 2)
    level_number_font = load_game_font(64)

    chest_title = Message(screen, 'Нажмите Е (или L2), чтобы открыть сундук', screen.get_height() * 0.1)

    # Иконки для отображения частей UI с заклинаниями
    spells_containers = (
        SpellContainer("fire_spell.png", FireSpell, player),
        SpellContainer("ice_spell.png", IceSpell, player),
        SpellContainer("poison_spell.png", PoisonSpell, player),
        SpellContainer("void_spell.png", VoidSpell, player),
        SpellContainer("light_spell.png", FlashSpell, player),
        SpellContainer("teleport_spell.png", TeleportSpell, player),
    )
    player_icon = PlayerIcon(player)
    # Определение параметров для отрисовки контейнеров с заклинаниями
    if player.joystick:
        spell_args = ("o", "x", "triangle", "square", "L1", "L2", "")
    else:
        spell_args = ("1", "2", "3", "4", "5", "Space", 'H')

    assistants_height = 180
    indent = 20

    # Фоновая музыка
    pygame.mixer.music.load("assets/audio/music/game_bg.ogg")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    # Игровой цикл
    while is_game_open:
        was_pause_activated = False
        keys = pygame.key.get_pressed()
        buttons = pygame.mouse.get_pressed(5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

            if event.type == pygame.KEYDOWN:
                if event.key == CONTROLS["KEYBOARD_PAUSE"]:
                    was_pause_activated = True

        # Текущий джойстик находится в игроке, поэтому кнопки проверяем по нему же
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
            # Используется ось, т.к. назначенн триггер R2
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

        if was_pause_activated:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            # Если была нажата кнопка выйти из игры, то цикл прерывается
            code = game_menu.execute(screen)
            if code == 1:
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
                save('')
                return 2
            if code:
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

            pygame.mixer.unpause()
            pygame.mixer.music.unpause()

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Обновление спрайтов
        player.update()

        # Если игрок умер, то надо открыть экран конца игры
        if player.destroyed:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            end_screen.execute(screen)
            return -1

        if pygame.sprite.spritecollideany(player, Chest.chest_group):
            chest_title.last_collide_time = pygame.time.get_ticks()
            # Проверка на использование (с джойстика или клавиатуры
            if ((player.joystick and
                 player.joystick.get_axis(CONTROLS['JOYSTICK_USE']) > JOYSTICK_SENSITIVITY)
                    or (keys[CONTROLS['KEYBOARD_USE']] or keys[CONTROLS['JOYSTICK_USE']])):
                pygame.sprite.spritecollide(player, Chest.chest_group, False)[0].open()

        enemies_group.update(player)
        player.assistants.update(enemies_group)
        Entity.spells_group.update()
        torches_group.update(player)
        doors_group.update(player, enemies_group, [player] + list(player.assistants))
        Chest.chest_group.update()
        Entity.damages_group.update()

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        # Отрисовка всех спрайтов
        tiles_group.draw(screen)
        torches_group.draw(screen)

        for chest in Chest.chest_group:
            chest: Chest
            chest.draw_back_image(screen)
        GroundItem.sprites_group.draw(screen)
        collidable_tiles_group.draw(screen)

        doors_group.draw(screen)
        enemies_group.draw(screen)
        player.assistants.draw(screen)
        for assistant in player.assistants:
            assistant.draw_health_bar(screen)
        player.draw(screen)
        Entity.spells_group.draw(screen)
        player.draw_health_bar(screen)

        # Индивидуальная обработка спрайтов врагов
        for enemy in enemies_group:
            enemy: Monster
            enemy.draw_health_bar(screen)
        Entity.damages_group.draw(screen)

        chest_title.draw(screen)

        # Отрисовка контейнеров с заклинаниями
        for i in range(len(spells_containers) - 1, -1, -1):
            pos = (screen_width * (0.375 + 0.05 * i), screen_height * 0.9)
            spells_containers[i].draw(screen, pos, bool(player.joystick), spell_args[i])

        player_icon.draw(screen, (indent, indent))
        for number_of_assistant, assistant in enumerate(player.assistants):
            if not assistant.icon:
                assistant.icon = PlayerIcon(assistant)
            assistant.icon.draw(screen, (indent + 20, assistants_height + number_of_assistant * 80), 0.5)

        # Отрисовка фпс
        fps_text = fps_font.render(str(int(clock.get_fps())), True, (100, 255, 100))
        screen.blit(fps_text, (2, 2))

        minster_number_text = level_number_font.render(str(len(enemies_group)), True, (255, 255, 255))
        screen.blit(minster_number_icon, (screen_width - 70, 80))
        screen.blit(minster_number_text, (screen_width - 120, 80))

        level_number_text = level_number_font.render(str(level_number), True, (255, 255, 255))
        screen.blit(level_number_icon, (screen_width - 70, 10))
        screen.blit(level_number_text, (screen_width - 120, 10))

        player.scope.draw(screen)

        # Проверка перехода на следующий уровень, путём соприкосновением с лестницой вниз
        if pygame.sprite.spritecollideany(player.collider, end_of_level):
            transition += 1
            if transition < 10:
                transparent_grey.fill(BACKGROUND_COLOR + (round(transition ** 2 / 4),))
                screen.blit(transparent_grey, (0, 0))
            else:
                # Как только переход завершён, музыка затухает
                pygame.mixer.fadeout(1000)
                pygame.mixer.music.fadeout(1000)
                loading_screen(screen)
                transition = 0
                # Если игрок собирается перейти на 11 уровень, то это победа
                if level_number == 10:
                    # Победный экран
                    end_screen.execute(screen, is_win=True)
                    return -1
                # Иначе перезагрука некоторых данных и новый уровень
                else:
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

                    level_number += 1  # номер уровня
                    # Создаем целиком новый уровень с помощью функции из generation_map
                    level, level_seed = generate_new_level(0)

                    # Создаем монстров и плитки, проходя по уровню
                    args = (level, level_number, all_sprites, tiles_group, furniture_group, collidable_tiles_group,
                            enemies_group, doors_group, torches_group, end_of_level, [], [])
                    player, monsters_seed, boxes_seed = initialise_level(*args, player=player)

                    all_sprites.add(player)
                    all_sprites.add(player.assistants)
                    for assistant in player.assistants:
                        assistant.rect.center = player.rect.center

                    current_seed = '\n'.join([' '.join(level_seed), ' '.join(monsters_seed), ' '.join(boxes_seed),
                                              str(player), str(level_number)])
                    save(current_seed)

                    # Заного заполняем индивидуальные спрайты
                    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))

                    # Иконки для отображения частей UI с заклинаниями
                    spells_containers = (
                        SpellContainer("fire_spell.png", FireSpell, player),
                        SpellContainer("ice_spell.png", IceSpell, player),
                        SpellContainer("poison_spell.png", PoisonSpell, player),
                        SpellContainer("void_spell.png", VoidSpell, player),
                        SpellContainer("light_spell.png", FlashSpell, player),
                        SpellContainer("teleport_spell.png", TeleportSpell, player),
                    )
                    pygame.mixer.music.play(-1)
                    continue
        else:
            transition = 0
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)

        clock.tick(FPS)
        pygame.display.flip()

    # Сохранение данных
    save(current_seed)

    # Код возврата 0 для закрытия игры
    return 0
