from generation_map import initialise_level, generate_new_level
from UI import game_menu
from config import *
from engine import *


class Camera:
    """
    Класс представляющий камеру
    """
    def __init__(self, screen_width, screen_height):
        # инициализация начального сдвига для камеры
        self.dx = 0
        self.dy = 0
        # размеры экрана
        self.screen_width = screen_width
        self.screen_height = screen_height

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # Функция сдвигает точку спавна существа и точку, к которой он идет
    def apply_point(self, obj):
        obj.start_position = obj.start_position[0] + self.dx, obj.start_position[1] + self.dy
        if obj.point:
            obj.point = obj.point[0] + self.dx, obj.point[1] + self.dy

    # метод позиционирования камеры на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.width * 0.5 - self.screen_width * 0.5)
        self.dy = -(target.rect.y + target.rect.height * 0.5 - self.screen_height * 0.5)


def start(screen: pygame.surface.Surface, user_seed: str = None):
    """
    Сама игра (генерация уровня и затем цикл)

    :param screen: экран
    :param user_seed: если есть, создаем по нему уровень и мобов
    :return: None
    """
    # Ставим загрузочный экран
    loading_screen(screen)
    
    screen_width, screen_height = screen.get_size()

    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов
    collidable_tiles_group = pygame.sprite.Group()
    # Группа со спрайтами врагов
    enemies_group = pygame.sprite.Group()
    # Группа со спрайтами дверей
    doors_group = pygame.sprite.Group()
    # Группа со спрайтами факелов
    torches_group = pygame.sprite.Group()

    is_game_open = True
    clock = pygame.time.Clock()  # Часы

    # Создаем уровень с помощью функции из generation_map
    level, level_seed = generate_new_level(user_seed.split('\n')[0].split() if user_seed else 0)
    # Создаем монстров и плитки, проходя по уровню
    player, monsters_seed = initialise_level(level, all_sprites, collidable_tiles_group,
                                             enemies_group, doors_group, torches_group,
                                             user_seed.split('\n')[1].split() if user_seed else 0)
    # Сохранение созданного уровня
    if 'data' not in os.listdir():
        os.mkdir('data')
    with open('data/data.txt', 'w') as data:
        data.write(' '.join(level_seed))
        data.write('\n')
        data.write(' '.join(monsters_seed))

    # Создаем камеру
    camera = Camera(screen_width, screen_height)

    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player.scope.init_scope_position((screen_width * 0.5, screen_height * 0.5))
    player_sprites.add(player.scope)  # прицел игрока
    all_sprites.add(player)

    # Фоновая музыка
    pygame.mixer.music.load(concat_two_file_paths("assets/audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    fps_font = pygame.font.Font('assets\\UI\\pixel_font.ttf', 50)    # Шрифт вывода фпс

    # Игровой цикл
    while is_game_open:
        was_pause_activated = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

            if event.type == pygame.KEYDOWN:
                # Проверка на активацию паузы
                if event.key == CONTROLS["KEYBOARD_PAUSE"]:
                    was_pause_activated = True

        # Текущий джойстик находится в игроке, поэтому кнопки проверяем по нему же
        if player.joystick:
            # Только если joystick подключен проверяем нажатие кнопки
            if player.joystick.get_button(CONTROLS["JOYSTICK_UI_PAUSE"]):
                was_pause_activated = True

        if was_pause_activated:
            pygame.mixer.music.pause()
            game_menu.execute(screen)
            pygame.mixer.music.unpause()

        # Обновление спрайтов
        player_sprites.update()
        all_sprites.update()
        enemies_group.update(player)
        torches_group.update(player)
        doors_group.update(player, enemies_group, player_sprites)

        # Обновление объектов относительно камеры
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        # Очистка экрана
        screen.fill((20, 20, 20))

        # Отрисовка всех спрайтов
        all_sprites.draw(screen)
        doors_group.draw(screen)
        enemies_group.draw(screen)
        player_sprites.draw(screen)

        for enemy in enemies_group:
            camera.apply_point(enemy)
            enemy.draw_health_bar(screen)
            enemy.draw_sign(screen)

        # Отрисовка фпс
        fps_text = fps_font.render(str(int(clock.get_fps())), True, (100, 255, 100))
        screen.blit(fps_text, (20, 10))

        clock.tick(FPS)
        pygame.display.flip()
