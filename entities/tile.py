import pygame
from engine import load_tile
from config import TILE_SIZE


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
        '9':  load_tile('TOP_RIGHT_CORNER.png'),
        '0':  load_tile('TOP_LEFT_CORNER.png'),
        '-':  load_tile('DOWN_LEFT_CORNER_FLAT.png'),
        '=':  load_tile('DOWN_RIGHT_CORNER_FLAT.png'),
        'D':  load_tile('DOOR.png'),
        'B':  load_tile('BARREL.png'),
        'B1': load_tile('BOX.png'),
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

    def __init__(self, tile_type: str, x: float, y: float, *groups):
        super().__init__(*groups)

        self.type = tile_type  # тип тайла
        self.image = Tile.IMAGES[self.type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)
