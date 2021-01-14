import os
import pygame

from generation_map import initialise_level, generate_level
from config import *
from engine import *

imported = True
try:
    import win32api
except ModuleNotFoundError:
    imported = False


# TODO: В этом месте Никита впадает в ступор, т.к. куда запихать камеру,
#  вроде бы в entities не хочется, но здесь хранить её как-то странно, наверное
# FIXME: короче нужны идеи срочно
class Camera:
    """
    Класс отвечающий за поведение камеры в игровом цикле
    """
    def __init__(self):
        self.dx = 0
        self.dy = 0
        tiles = tiles_group.sprites()
        self.first, self.last = tiles[0], tiles[-1]

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # сдвинуть курсор, вместе с прицелом
    def apply_cursor(self):
        if imported:
            win32api.mouse_event(1, self.dx // 2 + self.dx // 15, self.dy // 2 + self.dy // 15)

    # TODO: remove comment down bellow
    # NOTE: на самом деле я вообще хз какого типа будет target (Никита)
    # NOTE: таргет в основном будет игрок (Максим)
    # позиционировать камеру на объекте target
    def update(self, target, width, height):
        """
        Камера будет позиционированна относительно объекта target
        :param target: объект относительно которого будет происходить позиционирование
        :param width: ширина экрана, на  котором будет отрисовка
        :param height: высота экрана, на  котором будет отрисовка
        """
        indent = TILE_SIZE * 2

        if self.first.rect.x - indent + width // 2 < target.rect.x < self.last.rect.x + indent - width // 2:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        else:
            self.dx = 0

        if self.first.rect.y - indent + height // 2 < target.rect.y < self.last.rect.y + indent - height // 2:
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        else:
            self.dy = 0


def start(screen: pygame.surface.Surface):
    loading_screen(screen)
    
    width, height = screen.get_size()
    
    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами тайлов
    tiles_group = pygame.sprite.Group()

    # Фоновая музыка
    # FIXME: место на котором игра пролагивает (Никита пофиксит)
    pygame.mixer.music.load(os.path.join("assets/audio", "game_bg.ogg"))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)

    is_game_open = True
    clock = pygame.time.Clock()  # Часы

    level, new_seed = generate_level()
    player = initialise_level(level, all_sprites, tiles_group)
    camera = Camera(tiles_group)

    # Игрок
    # Группа со всеми спрайтами
    all_sprites = pygame.sprite.Group()
    # Группа со спрайтами игрока и прицелом
    player_sprites = pygame.sprite.Group()
    player_sprites.add(player)
    player_sprites.add(player.scope)  # прицел игрока

    # Игровой цикл
    while is_game_open:
        # Очистка экрана
        screen.fill((20, 20, 20))
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_open = False

        # Обновляем и выводим все спрайты
        player_sprites.update()
        player_sprites.draw(screen)

        # Обновление объектов относительно камеры
        camera.update(player, width, height)
        for sprite in all_sprites:
            camera.apply(sprite)
        camera.apply_cursor()

        # TODO: возможно этот коммент можно улучшить, моя формулировка так себе
        # Отрисовка всех групп спрайтов в определённом порядке
        all_sprites.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()

    # TODO: возможно забахать terminate, но ПОКА ЧТО он не нужен
    #  (если не понятно почему так писать Никите, либо посмотрите стек вызова)
