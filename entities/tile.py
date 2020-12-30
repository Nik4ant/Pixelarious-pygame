import pygame
from engine import load_image


class Tile(pygame.sprite.Sprite):
    IMAGES = {
        # пол
        "FLOOR": load_image("FLOOR.png", "assets/tiles"),
        # Стены
        "DOWN_WALL": load_image("DOWN_WALL.png", "assets/tiles"),
        "DOWN_LEFT_WALL": load_image("DOWN_LEFT_WALL.png", "assets/tiles"),
        "LEFT_WALL": load_image("LEFT_WALL.png", "assets/tiles"),
        "TOP_LEFT_WALL": load_image("TOP_LEFT_WALL.png", "assets/tiles"),
        "TOP_WALL": load_image("TOP_WALL.png", "assets/tiles"),
        "TOP_RIGHT_WALL": load_image("TOP_RIGHT_WALL.png", "assets/tiles"),
        "RIGHT_WALL": load_image("RIGHT_WALL.png", "assets/tiles"),
        "DOWN_RIGHT_WALL": load_image("DOWN_RIGHT_WALL.png", "assets/tiles"),
    }

    def __init__(self, tile_type: str, x: int, y: int):
        super().__init__(all_sprites_list)

        self.tile_type = tile_type.upper()  # тип тайла
        self.image = Tile.IMAGES[self.tile_type]
        self.rect = self.image.get_rect().move(x * TILE_SIZE, y * TILE_SIZE)