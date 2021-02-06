from engine import *
from config import TILE_SIZE, DEFAULT_SOUNDS_VOLUME
from entities.base_entity import Collider


class GroundItem(pygame.sprite.Sprite):
    # Канал для звуков
    sounds_channel = pygame.mixer.Channel(1)

    # Звуки
    meat_sound = pygame.mixer.Sound("assets\\audio\\meat_sound.mp3")
    meat_sound.set_volume(DEFAULT_SOUNDS_VOLUME)
    money_sound = pygame.mixer.Sound("assets\\audio\\money_sound.mp3")
    money_sound.set_volume(DEFAULT_SOUNDS_VOLUME)

    size = (int(TILE_SIZE * 0.6),) * 2
    IMAGES = {
        'meat':  (pygame.transform.scale(load_image('meat.png'), size), meat_sound),
        'money': (pygame.transform.scale(load_image('money.png'), size), money_sound),
    }

    item_group = pygame.sprite.Group()

    def __init__(self, item_type: str, count: int, x: float, y: float, *groups):
        super().__init__(*groups)

        self.type = item_type  # тип предмета
        self.count = int(count)

        self.image, self.sound = GroundItem.IMAGES[self.type]
        self.image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.collider = Collider(x, y)

        for other in pygame.sprite.spritecollide(self.collider, GroundItem.item_group, False):
            if self.type == other.type:
                c = self.count
                self.count = self.count + other.count
                other.kill()
        GroundItem.item_group.add(self)

        font = pygame.font.Font("assets\\UI\\pixel_font.ttf", 32)

        count_text = font.render(str(int(self.count)), True, (255, 255, 255))
        rect = count_text.get_rect()
        rect.center = self.rect.right - rect.w // 2, self.rect.bottom - rect.h // 2
        self.image.blit(count_text, count_text.get_rect(bottomright=self.image.get_rect().bottomright))


def spawn_item(x: float, y: float, k=1, meat_chance=50):
    if true_with_chance(meat_chance):
        GroundItem('meat', int(1 * k), x, y)
    else:
        GroundItem('money', 20 * k + randint(-10, 10), x, y)
