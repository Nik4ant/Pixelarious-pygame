from random import randint

import pygame

from engine import load_tile, cut_sheet, load_image, concat_two_file_paths, true_with_chance
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME
from entities.base_entity import Collider
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

        self.type = tile_type  # тип тайла
        self.image = Tile.IMAGES[self.type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        half = TILE_SIZE // 2
        quarter = TILE_SIZE // 4
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

    def __init__(self, tile_type: str, x: float, y: float, *groups):
        super().__init__(*groups)
        self.image = self.IMAGES[tile_type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        self.collider = Collider(x, y)

    def kill(self):
        if true_with_chance(5):
            spawn_item(*self.rect.center)
        super().kill()


class Torch(pygame.sprite.Sprite):
    frames = cut_sheet(load_image('TORCH.png', 'assets\\tiles'), 8, 1, (round(TILE_SIZE / 4 * 3),) * 2)

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(0)
    min_distance_to_player = 100
    update_sounds_channel = 0

    # Звуки
    BURNING_SOUND = pygame.mixer.Sound(concat_two_file_paths("assets\\audio", "torch_sound.mp3"))
    BURNING_SOUND.set_volume(DEFAULT_SOUNDS_VOLUME)

    def __init__(self, x: float, y: float, *groups):
        super().__init__(*groups)
        self.image = Torch.frames[0][randint(0, len(Torch.frames[0]) - 1)]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)

        self.cur_frame = 0
        self.update_time = pygame.time.get_ticks()

    def update(self, player=None) -> None:
        ticks = pygame.time.get_ticks()
        if ticks - Torch.update_sounds_channel > 100:
            Torch.update_sounds_channel = ticks + randint(-20, 20)
            Torch.min_distance_to_player = 100
            return
        if ticks - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            while 1:
                n = randint(0, 7)
                if n != self.cur_frame:
                    self.cur_frame = n
                    break
            self.image = Torch.frames[0][self.cur_frame]

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
            Door.update_sounds_channel = ticks
            Door.min_distance_to_player = 100
            return
        if not player_group[0]:
            Door.min_distance_to_player = 100000
            return
        collide = pygame.sprite.spritecollide

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
    frame = load_tile('CHEST.png')

    def __init__(self, x, y, *args):
        super().__init__(*args)
        self.image = self.frame
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
        self.collider = Collider(x, y)
