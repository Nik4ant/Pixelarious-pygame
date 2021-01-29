import pygame

FPS = 60
# Громкость музыки во всей игре по умолчанию
DEFAULT_MUSIC_VOLUME = 0.45
# Эта переменная нужна для увеличения громкости звука, если мелодия тихая.
# Такое добавление будет дописываться вручную при установке громкости.
MUSIC_VOLUME_ADDER = 0.2
# Громкость звука наведения по умолчанию
DEFAULT_HOVER_SOUND_VOLUME = 0.4
# Громкость звуков внутри игры по умолчанию
DEFAULT_SOUNDS_VOLUME = 0.5
# Чуствительность джойстика
# (только при достижении этого значения игра просчитает движения джойстика)
JOYSTICK_SENSITIVITY = 0.11

# Управление
CONTROLS = {
    # Для контроллера
    "JOYSTICK_DASH": 10,  # R1
    # эта кнопка для кликов по UI
    "JOYSTICK_UI_CLICK": 0,  # X
    "JOYSTICK_UI_PAUSE": 5,  # кнопка PS

    "JOYSTICK_SPELL_FIRE": 1,  # X
    "JOYSTICK_SPELL_ICE": 0,  # кнопка круг
    "JOYSTICK_SPELL_LIGHT": 3,  # кнопка квадрат
    "JOYSTICK_SPELL_POISON": 2,  # кнопка треугольник
    "JOYSTICK_SPELL_VOID": 9,  # L1

    # Для клавиатуры
    "KEYBOARD_SPELL_FIRE": pygame.K_1,  # 1
    "KEYBOARD_SPELL_ICE": pygame.K_2,  # 2
    "KEYBOARD_SPELL_LIGHT": pygame.K_3,  # 3
    "KEYBOARD_SPELL_POISON": pygame.K_4,  # 4
    "KEYBOARD_SPELL_VOID": pygame.K_5,  # 5

    "KEYBOARD_PAUSE": pygame.K_ESCAPE,
    "KEYBOARD_DASH": pygame.K_q,
    "KEYBOARD_LEFT": pygame.K_a,
    "KEYBOARD_RIGHT": pygame.K_d,
    "KEYBOARD_UP": pygame.K_w,
    "KEYBOARD_DOWN": pygame.K_s,
}
# сторона одного тайла
TILE_SIZE = 64
