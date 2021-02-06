from time import time

from generation_map import initialise_level, generate_new_level
from entities.spells import *
from entities.base_entity import *
from entities.items import GroundItem
from entities.enemies import WalkingMonster, ShootingMonster
from UI import end_screen, game_menu
from UI.UIComponents import SpellContainer, PlayerIcon
from config import *
from engine import *


def save(current_seed: str):
    if 'data' not in os.listdir():
        os.mkdir('data')
    with open('data\\save.txt', 'w') as file:
        file.write(current_seed)


class Camera:
    """Класс представляющий камеру"""

    def __init__(self, screen_width, screen_height):
        # инициализация начального сдвига для камеры
        self.dx = 0
        self.dy = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if isinstance(self, (WalkingMonster, ShootingMonster)):
            print(f'APPLIED WAS {obj.__class__.__name__}     ', (self.dx, self.dy))

    # Функция сдвигает точку спавна существа и точку, к которой он идет
    def apply_point(self, obj):
        if obj.start_position:
            obj.start_position = obj.start_position[0] + self.dx, obj.start_position[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    # метод позиционирования камеры на объекте target
    def update(self, target):
        self.dx = -(target.rect.centerx - self.screen_width * 0.5)
        self.dy = -(target.rect.centery - self.screen_height * 0.5)

    def move(self, target, group):
        self.dx = -(target.rect.centerx - self.screen_width * 0.5)
        self.dy = -(target.rect.centery - self.screen_height * 0.5)
        for sprite in group:
            sprite.rect.x = sprite.rect.x - self.dx
            sprite.rect.y = sprite.rect.y - self.dy
            if isinstance(sprite, (WalkingMonster, ShootingMonster)):
                self.apply_point(sprite)


def play(screen: pygame.surface.Surface,
         level_number: int = 1, user_seed: str = None) -> int:
    """
    Сама игра (генерация уровня и затем цикл)
    :param screen: экран
    :param level_number: Номер уровня, чтобы при подгрузке показывать его
    таким, каким он был задан.
    :param user_seed: сид если есть, создаем по нему уровень и мобов
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

    is_game_open = True

    transition = 0
    transparent_grey = pygame.surface.Surface((screen_width, screen_height), pygame.SRCALPHA).convert_alpha()

    clock = pygame.time.Clock()

    current_seed = user_seed  # текущий сид

    # Создаем уровень с помощью функции из generation_map
    level, level_seed = generate_new_level(current_seed.split('\n')[0].split() if current_seed else 0)
    # Создаем монстров и плитки, проходя по уровню
    player, monsters_seed = initialise_level(level, level_number, all_sprites, tiles_group,
                                             furniture_group, collidable_tiles_group,
                                             enemies_group, doors_group, torches_group, end_of_level,
                                             current_seed.split('\n')[1].split() if current_seed else 0)
    all_sprites.add(player)

    # Обновляем сид после инициализации уровня
    current_seed = ' '.join(level_seed) + '\n' + ' '.join(monsters_seed) + '\n' + str(level_number)
    save(current_seed)

    # Создаем камеру
    camera = Camera(screen_width, screen_height)

    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
    player_sprites.add(player.scope)

    fps_font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 48)

    level_number_icon = load_tile('UPSTAIRS.png', (TILE_SIZE,) * 2)
    level_number_font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 64)

    # Иконки для отображения частей UI с заклинаниями
    spells_containers = (
        SpellContainer("fire_spell.png", FireSpell, player),
        SpellContainer("ice_spell.png", IceSpell, player),
        SpellContainer("poison_spell.png", PoisonSpell, player),
        SpellContainer("void_spell.png", VoidSpell, player),
        SpellContainer("light_spell.png", FlashSpell, player),
        SpellContainer("teleport_spell.png", TeleportSpell, player),
    )
    player_icon = PlayerIcon((20, 20), player)

    # Фоновая музыка
    pygame.mixer.music.load(concat_two_file_paths("assets\\audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    t = time(), pygame.time.get_ticks()
    # Игровой цикл
    while is_game_open:
        if time() - t[0] >= 1:
            print(pygame.time.get_ticks() - t[1])
            t = time(), pygame.time.get_ticks()

        was_pause_activated = False
        keys = pygame.key.get_pressed()
        buttons = pygame.mouse.get_pressed(5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

        # Текущий джойстик находится в игроке, поэтому кнопки проверяем по нему же
        if player.joystick:
            # Только если joystick подключен проверяем нажатие кнопки
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
            if player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_VOID"]):
                player.shoot('teleport', enemies_group)
        # Иначе ввод с клавиатуры
        else:
            if keys[CONTROLS["KEYBOARD_PAUSE"]]:
                was_pause_activated = True

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
            if keys[CONTROLS["KEYBOARD_SPELL_HEAL"]]:
                player.shoot('heal', [player])

        if was_pause_activated:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            # Если была нажата кнопка выйти из игры, то цикл прерывается
            if game_menu.execute(screen) == -1:
                # Сохранение данных перед выходом
                save(current_seed)
                return -1
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()

        # Очистка экрана
        screen.fill(BACKGROUND_COLOR)

        # Обновление спрайтов
        player_sprites.update()

        # Если игрок умер, то надо открыть экран конца игры
        if player.destroyed:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            end_screen.execute(screen)
            return -1

        enemies_group.update(all_sprites, player)
        torches_group.update(player)
        doors_group.update(player, enemies_group, [player])
        Entity.damages.update()

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        for item in GroundItem.item_group:
            camera.apply(item)

        for spell in player.spells:
            camera.apply(spell)
            camera.apply_point(spell)

        # Отрисовка всех спрайтов
        tiles_group.draw(screen)
        collidable_tiles_group.draw(screen)
        torches_group.draw(screen)
        GroundItem.item_group.draw(screen)
        doors_group.draw(screen)
        enemies_group.draw(screen)
        player.draw(screen)
        player.draw_health_bar(screen)
        player.spells.update()
        player.spells.draw(screen)
        Entity.damages.draw(screen)

        # Индивидуальная обработка спрайтов врагов
        for enemy in enemies_group:
            camera.apply_point(enemy)
            enemy.draw_health_bar(screen)
            for spell in enemy.spells:
                camera.apply_point(spell)
            enemy.spells.draw(screen)

        # Определение параметров для отрисовки контейнеров с заклинаниями
        if player.joystick:
            spell_args = ("o", "x", "triangle", "square", "L1", "L2", "")
        else:
            spell_args = ("1", "2", "3", "4", "5", "E", 'H')
        # Отрисовка контейнеров с заклинаниями
        for i in range(len(spells_containers) - 1, -1, -1):
            pos = (screen_width * (0.375 + 0.05 * i), screen_height * 0.9)
            spells_containers[i].draw(screen, pos, bool(player.joystick), spell_args[i])

        player_icon.draw(screen)
        player.scope.draw(screen)

        # Отрисовка фпс
        fps_text = fps_font.render(str(int(clock.get_fps())), True, (100, 255, 100))
        screen.blit(fps_text, (20, 10))

        level_number_text = level_number_font.render(str(level_number), True, (255, 255, 255))
        screen.blit(level_number_icon, (screen_width - 70, 10))
        screen.blit(level_number_text, (screen_width - 110, 10))

        # Проверка перехода на следующий уровень, путём соприкосновением с лестницой вниз
        if pygame.sprite.spritecollideany(player.collider, end_of_level):
            transition += 1
            pygame.mixer.fadeout(1000)
            pygame.mixer.music.fadeout(1000)
            if transition < 20:
                transparent_grey.fill(BACKGROUND_COLOR + (round(transition ** 2 / 4),))
                screen.blit(transparent_grey, (0, 0))
            else:
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
                    all_sprites = pygame.sprite.Group()
                    tiles_group = pygame.sprite.Group()
                    furniture_group = pygame.sprite.Group()
                    collidable_tiles_group = pygame.sprite.Group()
                    enemies_group = pygame.sprite.Group()
                    doors_group = pygame.sprite.Group()
                    torches_group = pygame.sprite.Group()
                    end_of_level = pygame.sprite.Group()
                    GroundItem.item_group = pygame.sprite.Group()
                    Entity.damages = pygame.sprite.Group()

                    level_number += 1  # номер уровня
                    # Создаем целиком новый уровень с помощью функции из generation_map
                    level, level_seed = generate_new_level(0)
                    # Создаем монстров и плитки, проходя по уровню
                    player, monsters_seed = initialise_level(level, level_number, all_sprites, tiles_group,
                                                             furniture_group, collidable_tiles_group,
                                                             enemies_group, doors_group, torches_group, end_of_level,
                                                             current_seed.split('\n')[1].split() if current_seed else 0,
                                                             player)
                    all_sprites.add(player)

                    current_seed = ' '.join(level_seed) + '\n' + ' '.join(monsters_seed) + '\n' + str(level_number)
                    save(current_seed)
                    # Создаем камеру
                    camera = Camera(screen_width, screen_height)
                    camera.move(player, all_sprites)

                    # Заного заполняем индивидуальные спрайты
                    player_sprites.add(player)
                    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
                    player_sprites.add(player.scope)

                    # Иконки для отображения частей UI с заклинаниями
                    spells_containers = (
                        SpellContainer("fire_spell.png", FireSpell, player),
                        SpellContainer("ice_spell.png", IceSpell, player),
                        SpellContainer("poison_spell.png", PoisonSpell, player),
                        SpellContainer("void_spell.png", VoidSpell, player),
                        SpellContainer("light_spell.png", FlashSpell, player),
                        SpellContainer("teleport_spell.png", TeleportSpell, player),
                    )
                    player_icon = PlayerIcon((20, 20), player)
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

    # Очистка UI
    del player_icon, spells_containers, player

    # Код возврата 0 для закрытия игры
    return 0
