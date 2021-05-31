import pygame


FPS = 60
# Громкость музыки во всей игре по умолчанию
DEFAULT_MUSIC_VOLUME = 0.45
# Эта переменная нужна для увеличения громкости звука, если мелодия тихая.
# Такое добавление будет дописываться вручную при установке громкости.
MUSIC_VOLUME_ADDER = 0.2
# Громкость звука наведения по умолчанию
DEFAULT_HOVER_SOUND_VOLUME = 0.5
# Громкость звуков внутри игры по умолчанию
DEFAULT_SOUNDS_VOLUME = 0.5
# Эта переменная нужна для уменьшения громкости звука, если эффект громкий.
# Такое уменьшение будет дописываться вручную при установке громкости.
SOUNDS_VOLUME_REDUCER = 0.12
# Чуствительность джойстика
# (только при достижении этого значения игра просчитает движения джойстика)
JOYSTICK_SENSITIVITY = 0.11
# Скорость курсора при использовании джойстика (не относится к прицелу!!!)
JOYSTICK_CURSOR_SPEED = 20
# Управление
CONTROLS = {
    # Для джойстика
    'JOYSTICK_USE': 4,  # L2 (ось)
    "JOYSTICK_DASH": 10,  # R1
    # эта кнопка для кликов по UI
    "JOYSTICK_UI_CLICK": 0,  # X
    "JOYSTICK_UI_PAUSE": 5,  # кнопка PS
    "JOYSTICK_SPELL_FIRE": 1,  # круг
    "JOYSTICK_SPELL_ICE": 0,  # X
    "JOYSTICK_SPELL_POISON": 3,  # треугольник
    "JOYSTICK_SPELL_VOID": 2,  # квадрат
    "JOYSTICK_SPELL_LIGHT": 9,  # L1
    "JOYSTICK_SPELL_TELEPORT": 5,  # R2 (ось)
    "JOYSTICK_LEFT": 13,  # D-pad влево
    "JOYSTICK_RIGHT": 14,  # D-pad вправо
    "JOYSTICK_UP": 11,  # D-pad вверх
    "JOYSTICK_DOWN": 12,  # D-pad вниз
    # Для клавиатуры
    "KEYBOARD_SPELL_FIRE": pygame.K_1,
    "KEYBOARD_SPELL_ICE": pygame.K_2,
    "KEYBOARD_SPELL_POISON": pygame.K_3,
    "KEYBOARD_SPELL_VOID": pygame.K_4,
    "KEYBOARD_SPELL_LIGHT": pygame.K_5,
    "KEYBOARD_SPELL_TELEPORT": pygame.K_SPACE,
    "KEYBOARD_USE": pygame.K_e,
    "KEYBOARD_PAUSE": pygame.K_ESCAPE,
    "KEYBOARD_DASH": pygame.K_LSHIFT,
    "KEYBOARD_LEFT": (pygame.K_a, pygame.K_LEFT),
    "KEYBOARD_RIGHT": (pygame.K_d, pygame.K_RIGHT),
    "KEYBOARD_UP": (pygame.K_w, pygame.K_UP),
    "KEYBOARD_DOWN": (pygame.K_s, pygame.K_DOWN),
    # Для мышки
    "MOUSE_SPELL_FIRE": 0,
    "MOUSE_SPELL_ICE": 1,
    "MOUSE_SPELL_POISON": 2,
    "MOUSE_SPELL_VOID": 3,
    "MOUSE_SPELL_LIGHT": 4,
}
# Цвет фона в игре, экране загрузки и т.д.
BACKGROUND_COLOR = (20, 10, 20)
# сторона одного тайла
TILE_SIZE = 64
