import pygame


# TODO: ЕСЛИ БУДЕТ ПРОИСХОДИТЬ ИЗМЕНЕНИЕ ПАРАМЕТРОВ, ТО ТОГДА НУЖНО БУДЕТ СДЕЛАТЬ RELOAD МОДУЛЯ!!!!
# ВОТ ИНФА: https://stackoverflow.com/a/2029546/13940541
# NOTE: Но если не делать этот файл как .py, то нужно внутри окна изменения настроек
FPS = 60
DEFAULT_MUSIC_VOLUME = 35
DEFAULT_HOVER_SOUND_VOLUME = 15
# Чуствительность джойстика
# (только при достижении этого значения игра просчитает движения джойстика)
# TODO: МАКСИМАЛЬНОЕ ЗНАЧЕНИЕ В НАСТРОЙКАХ ДЛЯ ЭТОГО 0.24
JOYSTICK_SENSITIVITY = 0.11
'''
Cross Button    - Button 0
Circle Button   - Button 1
Square Button   - Button 2
Triangle Button - Button 3
Share Button    - Button 4
PS Button       - Button 5
Options Button  - Button 6
L. Stick In     - Button 7
R. Stick In     - Button 8
L1              - Button 9
R1              - Button 10
D-pad Up        - Button 11
D-pad Down      - Button 12
D-pad Left      - Button 13
D-pad Right     - Button 14
Touch Pad Click - Button 15
'''
# Управление
CONTROLS = {
    # Для контроллера
    "JOYSTICK_DASH": 10,  # R1
    # эта кнопка для кликов по UI
    "JOYSTICK_UI_CLICK": 0,  # X

    # Для клавиатуры
    "KEYBOARD_DASH": pygame.K_q,
    "KEYBOARD_LEFT": pygame.K_a,
    "KEYBOARD_RIGHT": pygame.K_d,
    "KEYBOARD_UP": pygame.K_w,
    "KEYBOARD_DOWN": pygame.K_s,
    "KEYBOARD_RUN": pygame.K_LSHIFT,
}
# время перезарядки дэша
DASH_RELOAD_TIME = 500  # в миллисекундах
# сторона одного тайоа
TILE_SIZE = 64
