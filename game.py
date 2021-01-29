from generation_map import initialise_level, generate_new_level
from UI import end_screen, game_menu, UIComponents
from config import *
from engine import *


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

    # Функция сдвигает точку спавна существа и точку, к которой он идет
    def apply_point(self, obj):
        if obj.start_position:
            obj.start_position = obj.start_position[0] + self.dx, obj.start_position[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    # метод позиционирования камеры на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.width * 0.5 - self.screen_width * 0.5)
        self.dy = -(target.rect.y + target.rect.height * 0.5 - self.screen_height * 0.5)


def start(screen: pygame.surface.Surface,
          level_number: int, user_seed: str = None) -> int:
    """
    Сама игра (генерация уровня и затем цикл)
    :param screen: экран
    :param user_seed: если есть, создаем по нему уровень и мобов
    :return: Код завершения игры. 0 - выход из игры,
    1 - переход на новый уровень, -1 в остальных случаях
    """
    # Ставим загрузочный экран
    loading_screen(screen)

    screen_width, screen_height = screen.get_size()

    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов
    tiles_group = pygame.sprite.Group()
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
    clock = pygame.time.Clock()

    # Создаем уровень с помощью функции из generation_map
    level, level_seed = generate_new_level(user_seed.split('\n')[0].split() if user_seed else 0)
    # Создаем монстров и плитки, проходя по уровню
    player, monsters_seed = initialise_level(level, all_sprites, tiles_group, collidable_tiles_group,
                                             enemies_group, doors_group, torches_group, end_of_level,
                                             user_seed.split('\n')[1].split() if user_seed else 0)

    # Создаем камеру
    camera = Camera(screen_width, screen_height)

    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
    player_sprites.add(player.scope)
    all_sprites.add(player)

    # Фоновая музыка
    pygame.mixer.music.load(concat_two_file_paths("assets/audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    fps_font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 48)

    level_number_icon = load_tile('UPSTAIRS.png', (TILE_SIZE,) * 2)
    level_number_font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 64)

    # Иконки для отображения частей UI с заклинаниями
    spells_containers = (
        UIComponents.SpellContainer("fire_spell.png", (120, 150)),
        UIComponents.SpellContainer("ice_spell.png", (120, 250)),
        UIComponents.SpellContainer("light_spell.png", (120, 350)),
        UIComponents.SpellContainer("poison_spell.png", (120, 450)),
        UIComponents.SpellContainer("void_spell.png", (120, 550))
    )

    # Игровой цикл
    while is_game_open :
        was_pause_activated = False
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot('fire', enemies_group)
                else:
                    player.shoot('poison', enemies_group)

        # Текущий джойстик находится в игроке, поэтому кнопки проверяем по нему же
        if player.joystick:
            # Только если joystick подключен проверяем нажатие кнопки
            if player.joystick.get_button(CONTROLS["JOYSTICK_UI_PAUSE"]):
                was_pause_activated = True

            elif player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_FIRE"]):
                player.shoot('fire', enemies_group)
            elif player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_ICE"]):
                player.shoot('ice', enemies_group)
            elif player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_LIGHT"]):
                player.shoot('flash', enemies_group)
            elif player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_POISON"]):
                player.shoot('poison', enemies_group)
            elif player.joystick.get_button(CONTROLS["JOYSTICK_SPELL_VOID"]):
                player.shoot('void', enemies_group)
        # Иначе ввод с клавиатуры
        else:
            if keys[CONTROLS["KEYBOARD_PAUSE"]]:
                was_pause_activated = True

            if keys[CONTROLS["KEYBOARD_SPELL_FIRE"]]:
                player.shoot('fire', enemies_group)
            elif keys[CONTROLS["KEYBOARD_SPELL_ICE"]]:
                player.shoot('ice', enemies_group)
            elif keys[CONTROLS["KEYBOARD_SPELL_LIGHT"]]:
                player.shoot('flash', enemies_group)
            elif keys[CONTROLS["KEYBOARD_SPELL_POISON"]]:
                player.shoot('poison', enemies_group)
            elif keys[CONTROLS["KEYBOARD_SPELL_VOID"]]:
                player.shoot('void', enemies_group)

        if was_pause_activated:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.pause()
            pygame.mixer.music.pause()
            # Если была нажата кнопка выйти из игры, то цикл прерывается
            if game_menu.execute(screen) == -1:
                return -1
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()

        # Очистка экрана
        screen.fill((20, 20, 20))

        # Обновление спрайтов
        player_sprites.update()
        # Если игрок умер, то надо открыть экран конца игры
        if pygame.sprite.spritecollideany(player, end_of_level):
            # TODO: переход на уровень слишком резкий!!!!
            return 1
        # Если игрок умер, то игра заканчивается
        if not player.alive:
            # Останавливаем все звуки (даже музыку)
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            end_screen.execute(screen)
            return -1

        enemies_group.update(all_sprites, player)
        torches_group.update(player)
        doors_group.update(player, enemies_group, [player])

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        for spell in player.spells:
            camera.apply(spell)
            camera.apply_point(spell)

        # Отрисовка всех спрайтов
        tiles_group.draw(screen)
        end_of_level.draw(screen)
        collidable_tiles_group.draw(screen)
        torches_group.draw(screen)
        doors_group.draw(screen)
        enemies_group.draw(screen)
        player_sprites.draw(screen)
        player.draw_health_bar(screen)
        player.spells.update()
        player.spells.draw(screen)

        # Индивидуальная обработка спрайтов врагов
        for enemy in enemies_group:
            camera.apply_point(enemy)
            enemy.draw_health_bar(screen)
            enemy.draw_sign(screen)
            for spell in enemy.spells:
                camera.apply_point(spell)
            enemy.spells.draw(screen)

        # Определение параметров для отрисовки контейнеров с заклинаниями
        if player.joystick:
            spell_args = ("o", "x", "triangle", "square", "L1")
        else:
            spell_args = ("1", "2", "3", "4", "5")
        # Отрисовка контейнеров с заклинаниями
        for i in range(len(spells_containers)):
            spells_containers[i].draw(screen, bool(player.joystick), spell_args[i])

        # Отрисовка фпс
        fps_text = fps_font.render(str(int(clock.get_fps())), True, (100, 255, 100))
        screen.blit(fps_text, (20, 10))

        level_number_text = level_number_font.render(str(level_number), True, (255, 255, 255))
        screen.blit(level_number_icon, (screen_width - 70, 10))
        screen.blit(level_number_text, (screen_width - 110, 10))

        clock.tick(FPS)
        pygame.display.flip()

    # Сохранение данных
    if 'data' not in os.listdir():
        os.mkdir('data')
    with open('data/save.txt', 'w') as data:
        data.write(' '.join(level_seed))
        data.write('\n')
        data.write(' '.join(monsters_seed))

    # Код возврата 0 для закрытия игры
    return 0
