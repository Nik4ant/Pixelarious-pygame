from random import randint

import pygame

from engine import load_tile, cut_sheet, load_image, concat_two_file_paths, true_with_chance
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME
from entities.base_entity import Entity, Collider
from entities.items import spawn_item


class Tile(pygame.sprite.Sprite):
    IMAGES = {
        '1':  load_tile('RIGHT_WALL.png'),
        '2':  load_tile('TOP_RIGHT_WALL_FLAT.png'),
        '3':  load_tile('WALL.png'),
        '4':  load_tile('TOP_LEFT_WALL_FLAT.png'),
        '5':  load_tile('LEFT_WALL.png'),
        '6':  load_tile('DOWN_LEFT_WALL.png'),
        '7':  load_tile('DOWN_WALL.png'),
        '8':  load_tile('DOWN_RIGHT_WALL.png'),
        '9':  load_tile('TOP_RIGHT_WALL.png'),
        '0':  load_tile('TOP_LEFT_WALL.png'),
        '-':  load_tile('DOWN_LEFT_WALL_FLAT.png'),
        '=':  load_tile('DOWN_RIGHT_WALL_FLAT.png'),
        'P':  load_tile('UPSTAIRS.png'),
        'E':  load_tile('DOWNSTAIRS.png'),
        '.':  load_tile('FLOOR.png'),
        '.0': load_tile('FLOOR_CRACKED_0.png'),
        '.1': load_tile('FLOOR_CRACKED_1.png'),
        '.2': load_tile('FLOOR_CRACKED_2.png'),
        '.3': load_tile('FLOOR_CRACKED_3.png')
    }

    def __init__(self, tile_type: str, x: float, y: float, *groups):
        super().__init__(*groups)

        self.type = tile_type    # тип тайла
        self.image = Tile.IMAGES[self.type]    # Изображение по типу
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)

        # Переменные для удобства
        half = TILE_SIZE // 2
        quarter = TILE_SIZE // 4
        # Далее код, в котором каждому виду стены будет присвоен свой размер коллайдера.
        # Размер и расположение подобраны так, что стены не имеют промежутков между собой, если они смежные
        # (Как это происходит с ящиками и бочками, кстати это так и задумано)
        # Но при этом игрок не слишком жестко взаимодействует с ними при перемещении
        if self.type in ('1', '5'):
            self.collider = Collider(x, y, (half, half * 3))
        elif self.type in ('3', '7'):
            self.collider = Collider(x, y, (half * 3, half))

        elif self.type in ('2', '9'):
            self.collider = Collider(x - quarter, y + quarter, (half * 2, half * 2))
        elif self.type in ('4', '0'):
            self.collider = Collider(x + quarter, y + quarter, (half * 2, half * 2))
        elif self.type in ('6', '-'):
            self.collider = Collider(x + quarter, y - quarter, (half * 2, half * 2))
        elif self.type in ('8', '='):
            self.collider = Collider(x - quarter, y - quarter, (half * 2, half * 2))

        else:
            self.collider = Collider(x, y)


class Furniture(pygame.sprite.Sprite):
    IMAGES = {
        'B1':  load_tile('BARREL.png'),
        'B2': load_tile('BOX.png'),
        'B3':  load_tile('BOX_1.png'),
    }

    def __init__(self, tile_type: str, x: float, y: float, new_boxes_seed, index, *groups):
        super().__init__(*groups)
        # Сохраняем ссылку на сид и индекс, чтоб потом удалить по индексу из сида этот ящик,
        # если он будет разрушен
        self.seed = new_boxes_seed
        self.index = index
        self.image = self.IMAGES[tile_type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        self.collider = Collider(x, y)

    def kill(self):
        # Убираем из сида, чтоб в следующей игре они не появились
        self.seed[self.index] = '0'

        # С малым щансом выпадают вещи
        if true_with_chance(5):
            spawn_item(*self.rect.center, all_sprites=Entity.all_sprites)
        super().kill()


class Torch(pygame.sprite.Sprite):
    frames = cut_sheet(load_image('TORCH.png', 'assets\\tiles'), 8, 1, (round(TILE_SIZE / 4 * 3),) * 2)[0]

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(0)
    min_distance_to_player = 100
    update_sounds_channel = 0

    # Звуки
    BURNING_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "torch_sound.mp3"))
    BURNING_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x: float, y: float, *groups):
        super().__init__(*groups)
        self.image = Torch.frames[randint(0, len(Torch.frames) - 1)]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)

        self.cur_frame = 0
        self.update_time = pygame.time.get_ticks()

    def update(self, player=None) -> None:
        ticks = pygame.time.get_ticks()
        # Через каждые назначенные промежутки времени обновляем минимальное расстояние до игрока
        if ticks - Torch.update_sounds_channel > 100:
            Torch.update_sounds_channel = ticks + randint(-20, 20)
            Torch.min_distance_to_player = 100
            return
        if ticks - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            while 1:
                n = randint(0, len(self.frames) - 1)
                if n != self.cur_frame:
                    self.cur_frame = n
                    break
            self.image = Torch.frames[self.cur_frame]

        # Вычисляем расстояние до игрока и ставим с этим коэффиццентом громкость звука
        # Так он будет меняться, когда мы подходим к факелам и отходим
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        Torch.min_distance_to_player = min(max((dx ** 2 + dy ** 2) ** 0.5, 0.000001), Torch.min_distance_to_player)
        self.BURNING_SOUND.set_volume(min(DEFAULT_SOUNDS_VOLUME / (Torch.min_distance_to_player / TILE_SIZE) * 3, 1.2))
        if not self.sounds_channel.get_busy():
            self.sounds_channel.play(self.BURNING_SOUND)


class Door(pygame.sprite.Sprite):
    frames = [load_tile('DOOR.png'), load_tile('EMPTY.png')]

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(0)
    min_distance_to_player = 100
    update_sounds_channel = 0

    # Звуки
    OPEN_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "door_open.mp3"))
    OPEN_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)
    CLOSE_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "door_close.mp3"))
    CLOSE_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x: float, y: float, *groups):
        super().__init__(*groups)
        self.image = Door.frames[0]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        self.collider = Collider(x, y)

        self.opened = False

    def update(self, player=None, enemies_group=None, player_group=None) -> None:
        ticks = pygame.time.get_ticks()
        if ticks - Door.update_sounds_channel > 100:
            # каждый назначенный промежуток времени сбрасываем минимальную дистанцию до игрока
            Door.update_sounds_channel = ticks
            Door.min_distance_to_player = 100
            return
        collide = pygame.sprite.spritecollide

        # Если дверь была закрыта, а теперь кто-то с ней соприкасается, открываем и издаём звук
        if not self.opened and (collide(self, enemies_group, False) or collide(self, player_group, False)):
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            Door.min_distance_to_player = min(max((dx ** 2 + dy ** 2) ** 0.5, 0.000001), Door.min_distance_to_player)

            volume = min(DEFAULT_SOUNDS_VOLUME / (Door.min_distance_to_player / TILE_SIZE) * 10, 1.2)
            self.OPEN_SOUND.set_volume(volume)
            if self.sounds_channel.get_busy():
                self.sounds_channel.stop()
            self.sounds_channel.play(self.OPEN_SOUND)
            self.opened = True
            self.image = Door.frames[1]

        # Если дверь была открыта, а сейчас никто с ней не соприкасается,
        # закрываем и издаем соответсвующий звук
        elif self.opened and not (collide(self, enemies_group, False) or collide(self, player_group, False)):
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            Door.min_distance_to_player = min(max((dx ** 2 + dy ** 2) ** 0.5, 0.000001), Door.min_distance_to_player)

            volume = min(DEFAULT_SOUNDS_VOLUME / (Door.min_distance_to_player / TILE_SIZE) * 10, 1.2)
            self.CLOSE_SOUND.set_volume(volume)
            if self.sounds_channel.get_busy():
                self.sounds_channel.stop()
            self.sounds_channel.play(self.CLOSE_SOUND)
            self.opened = False
            self.image = Door.frames[0]


class Chest(pygame.sprite.Sprite):
    size = (TILE_SIZE, TILE_SIZE)
    frames = cut_sheet(load_image('CHEST.png', 'assets\\tiles'), 8, 1, size)[0]
    back_of_chest = load_tile('back_of_chest.png')
    chest_group: pygame.sprite.Group
    UPDATE_TIME = 40

    def __init__(self, x, y, new_boxes_seed, index, *args):
        super().__init__(Chest.chest_group, *args)
        # Сохраняем индекс и сид, чтоб потом убрать из сида сундук, как открытый
        self.seed = new_boxes_seed
        self.index = index
        self.opened = False
        self.last_update_time = 0
        self.current_frame = 0
        self.update_time = self.UPDATE_TIME

        self.image = self.frames[self.current_frame]
        self.back_image = self.back_of_chest.copy()
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        self.back_image_rect = self.back_image.get_rect()
        self.collider = Collider(x, y)

    def draw_back_image(self, screen):
        screen.blit(self.back_image, self.rect)

    def open(self):
        self.opened = True

    def update(self):
        # Если сундук не открыт, с ним ничего не происходит
        if not self.opened:
            return

        ticks = pygame.time.get_ticks()
        if ticks - self.last_update_time > self.update_time:
            self.last_update_time = ticks

            # Чтоб анимация замедлялась
            self.update_time *= 1.2

            # Если первый фрейм, убираем из сида и спавним предмет
            if self.current_frame == 0:
                spawn_item(*self.rect.center, all_sprites=Entity.all_sprites, k=5)
                self.seed[self.index] = '0'

            # Если изображения кончились, убиваем
            if self.current_frame >= len(self.frames):
                self.kill()
                return

            # Меняем изображение
            self.image = self.frames[self.current_frame]
            self.current_frame += 1
