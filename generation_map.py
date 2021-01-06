from random import choice, random
import os
import pygame
import sys
from time import time


def load_image(filename, colorkey=None):
    fullname = os.path.join('assets\\tiles', filename)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
        image = pygame.transform.scale(image, (tile_width, tile_height))
    return image


# функция вывода уровня в консоль
def pprint(level):
    for i in level:
        print(*i, sep='   ')
    print()


def load_level(seed=None):
    level_map = [line.strip('\n') for line in generate_new_level()]
    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map)),\
           max_width, len(level_map)


def generate_level(level):
    new_player = None
    level = [list(i) for i in level]
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'P':
                Tile('.', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '.':
                Tile(choice(list('.' * 12) + ['.0', '.1', '.2', '.3']), x, y)
            else:
                Tile(level[y][x], x, y)
    # вернем игрока
    return new_player


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.pos = pos_x, pos_y
        self.type = tile_type
        self.image = tile_images[self.type]
        self.rect = pygame.Rect(
            0, 0, tile_width, tile_height).move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(player_image, (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y,)
        self.rect.x = self.rect.x    # + tile_width // 2 - self.rect.w // 2
        self.rect.y = self.rect.y    # + tile_height // 2 - self.rect.h // 2
        self.pos = [pos_x, pos_y]
        self.last_move = time() - 1

    def move(self, keys):
        if time() - self.last_move < 0.02:
            return
        x, y = self.pos
        if keys[4] or keys[80]:
            if possible(x - 1, y, level_x, level_y):
                if level[y][x - 1] in EMPTY:
                    self.rect.x -= tile_width
                    self.pos[0] -= 1
                    x, y = self.pos

        if keys[7] or keys[79]:
            if possible(x + 1, y, level_x, level_y):
                if level[y][x + 1] in EMPTY:
                    self.rect.x += tile_width
                    self.pos[0] += 1
                    x, y = self.pos

        if keys[26] or keys[82]:
            if possible(x, y - 1, level_x, level_y):
                if level[y - 1][x] in EMPTY:
                    self.rect.y -= tile_height
                    self.pos[1] -= 1
                    x, y = self.pos

        if keys[22] or keys[81]:
            if possible(x, y + 1, level_x, level_y):
                if level[y + 1][x] in EMPTY:
                    self.rect.y += tile_height
                    self.pos[1] += 1

        self.last_move = time()


def possible(x, y, w, h):
    if 0 <= x < w and 0 <= y < h:
        return True


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        if width // 2 // tile_width <= target.pos[0] < level_x - width // 2 // tile_width:
            self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        else:
            self.dx = 0
        if height // 2 // tile_height <= target.pos[1] < level_y - height // 2 // tile_height:
            self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        else:
            self.dy = 0


def terminate():
    pygame.quit()
    sys.exit()


# 1-8 - Walls
# . - Floor
# D - Door
# M - Mob (Monster)
# P - Player
# C - Chest
# H - Health fountain (fontan)
# L - Lower fountain
# T - Torgovec
# E - End portal/End stair/End platform


START_ROOM = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D....P....D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

EVIL_ROOM_1 = '''
43338D63332
5.........1
5.M.....M.1
5........C1
8.........6
D.........D
2.........4
5.........1
5.M.....M.1
5.........1
67772D47778
'''

EVIL_ROOM_2 = '''
43338D63332
5.......MC1
5.433333338
5.677777772
8.........6
D.........D
2.........4
633333332.1
477777778.1
5CM.......1
67772D47778
'''

EVIL_ROOM_3 = '''
43338D63332
5.........1
5.........1
5....M....1
8.........6
D..M.C.M..D
2.........4
5....M....1
5.........1
5.........1
67772D47778
'''

EVIL_ROOM_4 = '''
43338D63332
5.........1
62.....M.48
48.......62
8.........6
D.........D
2.........4
62.M.....48
48.......62
5.........1
67772D47778
'''

EVIL_ROOM_5 = '''
43338D63332
5.........1
5....M....1
5..47772..1
8..1   5..6
D..1   5..D
2..1   5..4
5..63338..1
5....M....1
5.........1
67772D47778
'''

EVIL_ROOM_6 = '''
43338D6332 
5........62
5.........1
5.........1
8.........6
D.........D
2.........4
5..M......1
5.........1
62........1
 6772D47778
'''

EVIL_ROOM_7 = '''
43338D63332
5T.M......1
5.........1
5M........1
8.........6
D.........D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

EVIL_ROOM_8 = '''
43248D62432
5.15...15.1
5.68...68.1
5......M..1
8.........6
D.........D
2.........4
5.........1
5.42...42.1
5.15...15.1
67862D48678
'''

EVIL_ROOM_9 = '''
 4338D6332 
48.......62
5.........1
5.........1
8.........6
D.........D
2.........4
5.....M...1
5.........1
62.......48
 6772D4778 
'''

EVIL_ROOM_10 = '''
  438D632  
  5.....1  
438.....672
5.........1
8...472...6
D...1 5...D
2...638...4
5.........1
672.....478
  5.....1  
  672D478  
'''

EVIL_ROOM_11 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D.........D
2.........4
5.........1
5.........1
5M.......M1
67772D47778
'''

EVIL_ROOM_12 = '''
43338D63332
5M.......M1
5.........1
5.........1
8.........6
D.........D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

EVIL_ROOM_13 = '''
43338D63332
5.........1
5.........1
5.........1
8...M.....6
D....CM...D
2...M.....4
5.........1
5.........1
5.........1
67772D47778
'''

EVIL_ROOM_14 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D.........D
2.........4
5.........1
5........M1
5.......MC1
67772D47778
'''

EVIL_ROOM_15 = '''
   48D62   
   62.48   
    5.1    
42  5.1  42
86338.63386
D.........D
24772.47724
68  5.1  68
    5.1    
   48.62   
   62D48   
'''

EVIL_ROOM_16 = '''
43338D63332
5.........1
5....M....1
5..47772..1
8..14338..6
D..15C....D
2..16772..4
5..63338..1
5....M....1
5.........1
67772D47778
'''

DOUBLE_EVIL_ROOM_1 = '''
43338D6333333338D63332
5....................1
5....................1
5..42.....42.....42..1
8..68.....68.....68..6
D....................D
2..42.....42.....42..4
5..68.....68.....68..1
5....................1
5....................1
67772D4777777772D47778
'''

DOUBLE_EVIL_ROOM_2 = '''
43338D6333333338D63332
5....................1
5.........M..........1
5..M.............M...1
8....................6
D........C.C.........D
2....................4
5..M.............M...1
5.........M..........1
5....................1
67772D4777777772D47778
'''

DOUBLE_EVIL_ROOM_3 = '''
43338D6333333338D63332
5....................1
5.M..................1
5....................1
8...M....4772..M.....6
D........5  1........D
2.....M..6338....M...4
5....................1
5..................M.1
5....................1
67772D4777777772D47778
'''

CHEST_ROOM_1 = '''
   48D62   
   5...1   
   62.48   
43248.62432
8.68...68.6
D....C....D
2.42...42.4
67862.48678
   48.62   
   5...1   
   62D48   
'''

CHEST_ROOM_2 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D...C.C...D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

CHEST_ROOM_3 = '''
43338D632  
5C......632
67772.....1
43325.....1
8..68.....6
D.........D
2.....42..4
5.....16778
5.....63332
672......C1
  672D47778
'''

CHEST_ROOM_4 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D....H....D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

CHEST_ROOM_5 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D....L....D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

CHEST_ROOM_6 = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D....T....D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

CHEST_ROOM_7 = '''
43338D63332
5.........1
5.........1
5.........1
8....C....6
D...C.C...D
2....C....4
5.........1
5.........1
5.........1
67772D47778
'''

CHEST_ROOM_8 = '''
   48D62   
   62.48   
    5.1    
42 48.62 42
8638...6386
D....C....D
2472...4724
68 62.48 68
    5.1    
   48.62   
   62D48   
'''

EMPTY_ROOM = '''           \n           \n           \n           \n           \n           \n           
           \n           \n           \n           '''

END_ROOM = '''
43338D63332
5.........1
5.........1
5.........1
8.........6
D....E....D
2.........4
5.........1
5.........1
5.........1
67772D47778
'''

STANDART_ROOMS = {
      'E1': EVIL_ROOM_1,
      'E2': EVIL_ROOM_2,
      'E3': EVIL_ROOM_3,
      'E4': EVIL_ROOM_4,
      'E5': EVIL_ROOM_5,
      'E6': EVIL_ROOM_6,
      'E7': EVIL_ROOM_7,
      'E8': EVIL_ROOM_8,
      'E9': EVIL_ROOM_9,
      'E10': EVIL_ROOM_10,
      'E11': EVIL_ROOM_11,
      'E12': EVIL_ROOM_12,
      'E13': EVIL_ROOM_13,
      'E14': EVIL_ROOM_14,
      'E15': EVIL_ROOM_15,
      'E16': EVIL_ROOM_16,
      'C1': CHEST_ROOM_1,
      'C2': CHEST_ROOM_2,
      'C3': CHEST_ROOM_3,
      'C4': CHEST_ROOM_4,
      'C5': CHEST_ROOM_5,
      'C6': CHEST_ROOM_6,
      'C7': CHEST_ROOM_7,
      'C8': CHEST_ROOM_8
      }

DOUBLE_ROOMS = {
    'D1': DOUBLE_EVIL_ROOM_1,
    'D2': DOUBLE_EVIL_ROOM_2,
    'D3': DOUBLE_EVIL_ROOM_3
    }

TEST_LEVEL = '''
S R R R R R R R 
 R R R R R R R R
'''

LEVEL_1 = '''
  RR RRR RR  
 RSRR RRRRR  
RRR RRRR RRE 
 DDRR RR RRRR
RRR RDDRR    
  RR R RRRRR 
'''      # 50

LEVEL_2 = '''
   R  RSR RR 
 RRRR R RRRRR
RRR RRRRR   R
RR RRR    RRR
 RDDRR RDDR  
RER RRRRR    
'''      # 50

LEVEL_3 = '''
 RR   R   RR 
  RRDDRRERR  
RRR  RRR  RRR
  RRR   RRR  
RRR  RRR  RRR
  RSRRRDDRR  
 RR   R   RR 
'''      # 50

LEVEL_4 = '''
RRDD RRR RS  
 R  R RRRRR R
RR RRR R RRRR
R R R  R  RR 
 DDRR  R RRRE
RRR RRRRRR  R
'''      # 50

LEVEL_5 = '''
 R   RR RRRER
 RR R RRR R  
  RRDDR RRR  
RRR  R R R RR
R R RRRRRRRR 
  RSR R   R  
   R  RRDDR  
'''      # 50

FORMS = {'L1': LEVEL_1, 'L2': LEVEL_2, 'L3': LEVEL_3, 'L4': LEVEL_4, 'L5': LEVEL_5}


# Сама функция генерации
def generate_new_level(user_seed=None) -> [str, ..., str]:
    level = []
    seed = []
    if user_seed:
        seed.append(user_seed[0])
        del user_seed[0]
    else:
        seed.append(choice(list(FORMS)))
    level_form = FORMS[seed[-1]]
    level_form = TEST_LEVEL

    level_form = level_form.strip('\n').split('\n')
    doubled = False
    for i in range(len(level_form)):
        room_row = level_form[i]
        rooms = []
        for j in room_row:
            if doubled:
                doubled = False
                continue
            if j == 'S':
                room = START_ROOM
            elif j == 'E':
                room = END_ROOM
            elif j == 'D':
                if user_seed:
                    seed.append(user_seed[0])
                    del user_seed[0]
                else:
                    seed.append(choice(list(DOUBLE_ROOMS)))
                room = DOUBLE_ROOMS[seed[-1]]
                doubled = True
            elif j == 'R':
                if user_seed:
                    seed.append(user_seed[0])
                    del user_seed[0]
                else:
                    seed.append(choice(list(STANDART_ROOMS)))
                room = STANDART_ROOMS[seed[-1]]
            else:
                room = EMPTY_ROOM
            rooms.append(room.strip('\n').split('\n'))

        for number_row in range(len(rooms[0])):
            row = []
            for room_a in rooms:
                row += list(room_a[number_row])
            level.append(row)

    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] != 'D':
                continue

            if level[i - 1][j] == '6' and level[i + 1][j] == '4':
                if j + 1 >= len(level[i]) or level[i][j + 1] not in 'Dlrtb':     # СПРАВА
                    if level[i + 2][j - 2] == '.' and true_with_chance(45, seed, user_seed):
                        level[i - 1][j] = '8'
                        level[i + 1][j] = '2'
                        level[i][j] = ' '

                        if true_with_chance(35, seed, user_seed) and level[i][j - 3] == '.':
                            level[i][j - 1] = ' '
                            level[i - 1][j - 1] = '7'
                            level[i + 1][j - 1] = '3'
                            level[i][j - 2] = '1'
                            level[i - 1][j - 2] = '4'
                            level[i + 1][j - 2] = '6'
                        else:
                            level[i][j - 1] = '1'
                            level[i - 1][j - 1] = '4'
                            level[i + 1][j - 1] = '6'
                    else:
                        level[i][j] = level[i - 1][j] = level[i + 1][j] = '1'
                else:
                    level[i][j] = 'r'

            elif level[i][j - 1] == '8' and level[i][j + 1] == '6':     # СВЕРХУ
                if i == 0 or level[i - 1][j] not in 'Dlrtb':
                    if level[i + 2][j - 1] == '.' and true_with_chance(45, seed, user_seed):
                        level[i][j + 1] = '4'
                        level[i][j - 1] = '2'
                        level[i][j] = ' '

                        if true_with_chance(35, seed, user_seed) and level[i + 3][j] == '.':
                            level[i + 2][j] = '3'
                            level[i + 2][j - 1] = '6'
                            level[i + 2][j + 1] = '8'
                            level[i + 1][j] = ' '
                            level[i + 1][j - 1] = '1'
                            level[i + 1][j + 1] = '5'
                        else:
                            level[i + 1][j] = '3'
                            level[i + 1][j - 1] = '6'
                            level[i + 1][j + 1] = '8'
                    else:
                        level[i][j] = level[i][j - 1] = level[i][j + 1] = '3'
                else:
                    level[i][j] = 'b'

            elif level[i - 1][j] == '8' and level[i + 1][j] == '2':     # СЛЕВА
                if j == 0 or level[i][j - 1] not in 'Dlrtb':
                    if level[i + 2][j + 2] == '.' and true_with_chance(45, seed, user_seed):
                        level[i - 1][j] = '6'
                        level[i + 1][j] = '4'
                        level[i][j] = ' '

                        if true_with_chance(35, seed, user_seed) and level[i][j + 3] == '.':
                            level[i][j + 2] = '5'
                            level[i - 1][j + 2] = '2'
                            level[i + 1][j + 2] = '8'
                            level[i][j + 1] = ' '
                            level[i - 1][j + 1] = '3'
                            level[i + 1][j + 1] = '7'
                        else:
                            level[i][j + 1] = '5'
                            level[i - 1][j + 1] = '2'
                            level[i + 1][j + 1] = '8'
                    else:
                        level[i][j] = level[i - 1][j] = level[i + 1][j] = '5'
                else:
                    level[i][j] = 'l'

            elif level[i][j - 1] == '2' and level[i][j + 1] == '4':     # СНИЗУ
                if i + 1 >= len(level) or level[i + 1][j] not in 'Dlrtb':
                    if level[i - 2][j + 1] == '.' and true_with_chance(45, seed, user_seed):
                        level[i][j + 1] = '6'
                        level[i][j - 1] = '8'
                        level[i][j] = ' '

                        if true_with_chance(35, seed, user_seed) and level[i - 3][j] == '.':
                            level[i - 2][j] = '7'
                            level[i - 2][j - 1] = '4'
                            level[i - 2][j + 1] = '2'
                            level[i - 1][j] = ' '
                            level[i - 1][j - 1] = '1'
                            level[i - 1][j + 1] = '5'
                        else:
                            level[i - 1][j] = '7'
                            level[i - 1][j - 1] = '4'
                            level[i - 1][j + 1] = '2'
                    else:
                        level[i][j] = level[i][j - 1] = level[i][j + 1] = '7'
                else:
                    level[i][j] = 't'

    # pprint(level)
    # Возвращаем созданный уровень
    print(*seed)
    return [''.join(i) for i in level]


def true_with_chance(chance=50, seed=None, user_seed=None):
    if user_seed:
        seed.append(user_seed[0])
        del user_seed[0]
    else:
        is_true = [0, 1][random() * 100 <= chance]
        if seed:
            seed.append(str(is_true))
    return int(seed[-1])


FPS = 50
EMPTY = ' .@DMPCHLTlrtb'    # + '12345678'
WALL = '#'

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Ла-ла-ла')
    clock = pygame.time.Clock()
    size = width, height = 1450, 1050
    tile_width = tile_height = 50
    screen = pygame.display.set_mode(size)

    my_seed = 'L5 E2 E2 C8 E2 C8 C7 E2 C5 C8 E2 E2 E2 C8 E2 C6 C8 D3 E2 C4 E2 E2 C6 E2 C8 ' \
              'E2 E2 C7 C1 E2 E2 E2 E2 E2 E2 E2 E2 E2 C5 E2 E12 E16 E10 E8 C6 E15 E1 D3 ' \
              'E3 0 0 0 0 1 1 0 0 1 1 0 1 0 0 0 0 1 1 0 0 1 1 0 1 0 1 0 0 0 0 1 0 1 0 0 1 0 0 ' \
              '0 0 0 0 1 1 0 0 0 1 0 1 0 0 0 0 0 0 1 1 0 0 0 0 0 0 1 0 1 0 0 0 0 1 1 0 0 0 0 0 ' \
              '0 1 1 1 1 0 1 0 1 0 0 0 0 0 1 1 0'.split()

    player_image = load_image('mario.png', -1)
    level, level_x, level_y = load_level(my_seed)

    camera = Camera()

    tile_images = {
        '1': load_image('RIGHT_WALL.png'),
        '2': load_image('TOP_RIGHT_WALL.png'),
        '3': load_image('TOP_WALL.png'),
        '4': load_image('TOP_LEFT_WALL.png'),
        '5': load_image('LEFT_WALL.png'),
        '6': load_image('DOWN_LEFT_WALL.png'),
        '7': load_image('DOWN_WALL.png'),
        '8': load_image('DOWN_RIGHT_WALL.png'),
        'D': load_image('DOOR_VERTICAL.png'),
        'r': load_image('DOOR_RIGHT.png'),
        'l': load_image('DOOR_LEFT.png'),
        't': load_image('DOOR_TOP.png'),
        'b': load_image('DOOR_BOTTOM.png'),
        'M': load_image('EMPTY.png'),
        'P': load_image('EMPTY.png'),
        'C': load_image('EMPTY.png'),
        'H': load_image('EMPTY.png'),
        'L': load_image('EMPTY.png'),
        'T': load_image('EMPTY.png'),
        'E': load_image('EMPTY.png'),
        ' ': load_image('DARK.png'),
        '.': load_image('FLOOR.png'),
        '.0': load_image('FLOOR_CRACKED_0.png'),
        '.1': load_image('FLOOR_CRACKED_1.png'),
        '.2': load_image('FLOOR_CRACKED_2.png'),
        '.3': load_image('FLOOR_CRACKED_3.png')
        }

    player = generate_level(level)
    if not player:
        print('Отсутствие игрока на поле повергает в инфаркт игру')

    while True:
        keys = list(pygame.key.get_pressed())
        screen.fill('white')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key in (45, 61):
                    if event.key == 45:
                        EMPTY = ' .@DMPCHLTlrtb'
                    else:
                        EMPTY = ' .@DMPCHLTlrtb' + '12345678'

        if any(keys):
            player.move(keys)

        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.draw(screen)
        player_group.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
