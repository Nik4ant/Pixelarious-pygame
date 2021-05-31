from random import randint

import pygame

from engine import load_image, load_sound, load_game_font, true_with_chance
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME
from entities.base_entities import Collider


class GroundItem(pygame.sprite.Sprite):
    sprites_group: pygame.sprite.Group

    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)
    # Звуки
    SOUNDS = {
        "meat": load_sound("assets/audio/sfx/items/meat_sound_1.mp3"),
        "money": load_sound("assets/audio/sfx/items/money_sound.mp3"),
    }
    # Изображения
    size = (int(TILE_SIZE * 0.6),) * 2
    IMAGES = {
        "meat":  load_image("assets/sprites/items/meat.png", size),
        "money": load_image("assets/sprites/items/money.png", size),
    }

    def __init__(self, item_type: str, count: int, x: float, y: float, all_sprites, *groups):
        super().__init__(all_sprites, GroundItem.sprites_group, *groups)

        self.type = item_type  # тип предмета
        self.count = abs(int(count))

        if not self.count:
            self.kill()

        self.image, self.sound = GroundItem.IMAGES[self.type], GroundItem.SOUNDS[self.type]
        self.sound.set_volume(DEFAULT_SOUNDS_VOLUME * 3)
        self.image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.collider = Collider(x, y)

        for other in pygame.sprite.spritecollide(self, GroundItem.sprites_group, False):
            other: GroundItem
            if self.type == other.type and other != self:
                self.count = self.count + other.count
                other.kill()

        font = load_game_font(32)

        if self.count > 1:
            count_text = font.render(str(self.count), True, (255, 255, 255))
            rect = count_text.get_rect()
            rect.center = self.rect.right - rect.w // 2, self.rect.bottom - rect.h // 2
            self.image.blit(count_text, count_text.get_rect(bottomright=self.image.get_rect().bottomright))


def spawn_item(x: float, y: float, all_sprites, k=1, meat_chance=50):
    if true_with_chance(meat_chance):
        GroundItem("meat", int(1 * k), x, y, all_sprites)
    else:
        n = 20 * k
        GroundItem("money", n + randint(-n // 2, n // 2), x, y, all_sprites)
