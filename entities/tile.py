import pygame
from engine import load_tile
from config import TILE_SIZE


class Tile(pygame.sprite.Sprite):
    IMAGES = {
        '1':  load_tile('RIGHT_WALL.png'),
        '2':  load_tile('TOP_RIGHT_WALL.png'),
        '3':  load_tile('DOWN_WALL.png'),
        '4':  load_tile('TOP_LEFT_WALL.png'),
        '5':  load_tile('LEFT_WALL.png'),
        '6':  load_tile('DOWN_LEFT_WALL.png'),
        '7':  load_tile('DOWN_WALL.png'),
        '8':  load_tile('DOWN_RIGHT_WALL.png'),
        '9':  load_tile('TOP_RIGHT_WALL_2.png'),
        '0':  load_tile('TOP_LEFT_WALL_2.png'),
        '-':  load_tile('DOWN_LEFT_WALL_2.png'),
        '=':  load_tile('DOWN_RIGHT_WALL_2.png'),
        'r':  load_tile('DOOR_RIGHT.png'),
        'l':  load_tile('DOOR_LEFT.png'),
        'b':  load_tile('DOOR_TOP.png'),
        't':  load_tile('DOOR_BOTTOM.png'),
        'B':  load_tile('BOX.png'),
        'B1': load_tile('BARREL.png'),
        'P':  load_tile('UPSTAIRS.png'),
        'C':  load_tile('CHEST.png'),
        'T':  load_tile('TORCH.png'),
        'E':  load_tile('DOWNSTAIRS.png'),
        '.':  load_tile('FLOOR.png'),
        '.0': load_tile('FLOOR_CRACKED_0.png'),
        '.1': load_tile('FLOOR_CRACKED_1.png'),
        '.2': load_tile('FLOOR_CRACKED_2.png'),
        '.3': load_tile('FLOOR_CRACKED_3.png')
    }

    def __init__(self, tile_type: str, x: int, y: int, *groups):
        super().__init__(*groups)

        self.tile_type = tile_type  # тип тайла
        self.image = Tile.IMAGES[self.tile_type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
