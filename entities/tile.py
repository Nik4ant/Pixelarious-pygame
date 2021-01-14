import pygame
from engine import load
from config import TILE_SIZE


class Tile(pygame.sprite.Sprite):
    IMAGES = {
        '1':  load('RIGHT_WALL.png'),
        '2':  load('TOP_RIGHT_WALL.png'),
        '3':  load('DOWN_WALL.png'),
        '4':  load('TOP_LEFT_WALL.png'),
        '5':  load('LEFT_WALL.png'),
        '6':  load('DOWN_LEFT_WALL.png'),
        '7':  load('DOWN_WALL.png'),
        '8':  load('DOWN_RIGHT_WALL.png'),
        '9':  load('TOP_RIGHT_WALL_2.png'),
        '0':  load('TOP_LEFT_WALL_2.png'),
        '-':  load('DOWN_LEFT_WALL_2.png'),
        '=':  load('DOWN_RIGHT_WALL_2.png'),
        'r':  load('DOOR_RIGHT.png'),
        'l':  load('DOOR_LEFT.png'),
        'b':  load('DOOR_TOP.png'),
        't':  load('DOOR_BOTTOM.png'),
        'B':  load('BOX.png'),
        'B1': load('BARREL.png'),
        'M':  load('MONSTER.png'),
        'P':  load('UPSTAIRS.png'),
        'C':  load('CHEST.png'),
        'T':  load('TORCH.png'),
        'E':  load('DOWNSTAIRS.png'),
        ' ':  load('DARK.png'),
        '.':  load('FLOOR.png'),
        '.0': load('FLOOR_CRACKED_0.png'),
        '.1': load('FLOOR_CRACKED_1.png'),
        '.2': load('FLOOR_CRACKED_2.png'),
        '.3': load('FLOOR_CRACKED_3.png')
    }

    def __init__(self, tile_type: str, x: int, y: int, all_sprites_list: pygame.sprite.Group, *args):
        super().__init__(all_sprites_list, *args)

        self.tile_type = tile_type  # тип тайла
        self.image = Tile.IMAGES[self.tile_type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
