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


def load_level(user_seed=None):
    level_map, seed = generate_new_level(user_seed)
    level_map = [line.strip('\n') for line in level_map]
    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map)),\
           max_width, len(level_map)


def generate_level(level):
    new_player = None
    level = [list(i) for i in level]
    for y in range(len(level)):
        for x in range(len(level[y])):
            Tile(choice(list('.' * 12) + ['.0', '.1', '.2', '.3']), x, y)
            if level[y][x] == 'P':
                new_player = Player(x, y)
            elif level[y][x] in '.F':
                pass
            elif level[y][x] == 'B':
                Tile(choice(('B', 'B1')), x, y)
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
        self.time = 0.02

    def move(self, keys):
        if time() - self.last_move < self.time:
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
# T - Torch
# H - Health fountain (fontan)
# L - Lower fountain
# D - Dealer (Torgovec)
# E - End portal/End stair/End platform
# B - Box/Bochka


START_ROOM = '''
03338t63339
5.........1
5.........1
5....T....1
8.........6
l..T.P.T..r
2.........4
5....T....1
5.........1
5.........1
-7772b4777=
'''

EVIL_ROOM_1 = '''
03338t63339
5.........1
5.M.....M.1
5..B.....C1
8.........6
l.........r
2...B.....4
5......T..1
5.M.....M.1
5.........1
-7772b4777=
'''

EVIL_ROOM_2 = '''
03338t63339
5.......MC1
5.43333333=
5.677777779
8....B...B6
l.........r
2.T.......4
-33333332.1
077777778.1
5CM.......1
-7772b4777=
'''

EVIL_ROOM_3 = '''
03338t63339
5........B1
5.........1
5..T.M....1
8.........6
l..M.C.M..r
2.........4
5....M....1
5...B.....1
5.........1
-7772b4777=
'''

EVIL_ROOM_4 = '''
03338t63339
5B........1
-2.....M.4=
08.......69
8........B6
l.........r
2B.....T..4
-2.M.....4=
08.......69
5.........1
-7772b4777=
'''

EVIL_ROOM_5 = '''
03338t63339
5.........1
5....M....1
5..47772..1
8..1   5..6
l..1   5..r
2..1   5..4
5..63338..1
5.T..M...B1
5.......BB1
-7772b4777=
'''

EVIL_ROOM_6 = '''
03338t6339 
5........69
5.........1
5.........1
8.........6
l....T....r
2.........4
5..M......1
5......B..1
-2.....BBB1
 -772b4777=
'''

EVIL_ROOM_7 = '''
03338t63339
5..M....BB1
5.........1
5M........1
8.........6
l...T.....r
2.........4
5.........1
5.B.......1
5......477=
-7772b4=   
'''

EVIL_ROOM_8 = '''
03908t69039
5.15..B15.1
5.68...68.1
5......M..1
8.........6
l....T....r
2.........4
5.........1
5.42...42.1
5B15...15.1
-7=-2b4=-7=
'''

EVIL_ROOM_9 = '''
 0338t6339 
08......B69
5........B1
5.........1
8.........6
l....T....r
2.........4
5.....M...1
5.........1
-2.......4=
 -772b477= 
'''

EVIL_ROOM_10 = '''
  038t639  
  5.....1  
038.....679
5B........1
8...472...6
l..T1 5...r
2...638...4
5.........1
-72.....47=
  5...BB1  
  -72b47=  
'''

EVIL_ROOM_11 = '''
03338t63339
5..B...B..1
5.BB......1
5...B.....1
8........B6
l....T....r
2......B..4
5..B......1
5.....B...1
5M.......M1
-7772b4777=
'''

EVIL_ROOM_12 = '''
03338t63339
5M.......M1
5.........1
5.........1
8.........6
l...BT.B..r
2....B.B.B4
5.BB.BBB.B1
5..BB...BB1
5B....BBBB1
-7772b4777=
'''

EVIL_ROOM_13 = '''
03338t63339
5B......BB1
5B........1
5.........1
8...M.....6
l...TCM...r
2...M.....4
5.........1
5.........1
5.........1
-7772b4777=
'''

EVIL_ROOM_14 = '''
03338t639  
5B......69 
5........69
5.........1
8.........6
l....T....r
2.........4
5B........1
-2B......M1
 -2.....MC1
  -72b4777=
'''

EVIL_ROOM_15 = '''
   08t69   
   -2.4=   
    5.1    
09  5.1  09
86338.63386
l.........r
24772.47724
-=  5.1  -=
    5.1    
   08.69   
   -2b4=   
'''

EVIL_ROOM_16 = '''
03338t63339
5.........1
5....M....1
5..47772..1
8..10338..6
l..15C....r
2..1-772T.4
5..63338..1
5....MB...1
5.........1
-7772b4777=
'''

EVIL_ROOM_17 = '''
   08t69   
  08...69  
 08.....69 
08.......69
8B........6
l....T....r
2.........4
-2.......4=
 -2M...M4= 
  -2...4=  
   -2b4=   
'''

EVIL_ROOM_18 = '''
   08t69   
  08...69  
 08....B69 
08.....B.69
8.....B...6
l....T....r
2.........4
-2.......4=
 -2M...M4= 
  -2B..4=  
   -2b4=   
'''

EVIL_ROOM_19 = '''
   08t69   
  08...69  
 08.....69 
08.......69
8.........6
l.........r
2BB.......4
-2.T.....4=
 -2M...M4= 
  -2B..4=  
   -2b4=   
'''

EVIL_ROOM_20 = '''
   08t69   
  08...69  
 08.....69 
08.......69
8......B..6
l.....BB..r
2...T.....4
-2......C4=
 -2M...M4= 
  -2...4=  
   -2b4=   
'''

EVIL_ROOM_21 = '''
03338t63339
5.........1
-7772.4777=
    5.69   
33338.C6333
l...MT....r
77772.47777
    5M1    
03338.63339
5.........1
-7772b4777=
'''

EVIL_ROOM_22 = '''
03338t63339
-7772.4777=
    5.1    
    5.69   
33338.C6333
l.........r
77772.47777
    5.69   
03338.C6339
5.M.T.....1
-7772b4777=
'''

EVIL_ROOM_23 = '''
    5t1    
03338.63339
5.BB......1
5..B.BB.B.1
8B...B....6
l.B....B..r
2..T.B.BBB4
5...B.B...1
5.......B.1
-7772.4777=
    5b1    
'''

EVIL_ROOM_24 = '''
    5t1    
 0338.6339 
 5......B1 
 5.......1 
38.M.....63
l....T....r
72.......47
 5..M...C1 
 5.B..B.B1 
 -772.477= 
    5b1    
'''

EVIL_ROOM_25 = '''
    5t1    
    5.1    
  038.639  
  5....B1  
338M...C633
l....T....r
772.....477
  5M....1  
  -72.47=  
    5.1    
    5b1    
'''

EVIL_ROOM_26 = '''
03338t639  
5.......639
5MBBT.....1
5.DB......1
8BBB...M..6
l.........r
2.........4
5........B1
5B..M.....1
-72......B1
  -72b4777=
'''

EVIL_ROOM_27 = '''
03338t69   
5.B...B6339
5.M.......1
5B........1
8.........6
l....T....r
2.........4
5......B.M1
5.B.....B.1
-772....BC1
   -2b4777=
'''

EVIL_ROOM_28 = '''
    5t1    
    5.1    
    5.1    
   08.69   
3338M..6333
l....T....r
7772..M4777
   -2.4=   
    5.1    
    5.1    
    5b1    
'''

EVIL_ROOM_29 = '''
    5t1    
    5.1    
    5.1    
    5.1    
33338.63333
l.........r
77772.47777
    5.1    
    5.1    
    5.1    
    5b1    
'''

EVIL_ROOM_30 = '''
   08t69   
  08...69  
 08.....69 
08.......69
8......B..6
l.....BB..r
2...T.M...4
-2......C4=
 -2M....4= 
  -2...4=  
   -2b4=   
'''

DOUBLE_EVIL_ROOM_1 = '''
03338t6333903338t63339
5.........68.........1
-2...............B..4=
08.42B....42C....42.69
8..68..T..68..T..68..6
l....................r
2B.42..T..42..T..42..4
-2.68.....68B...B68.4=
08..................69
5.........42.........1
-7772b4777=-7772b4777=
'''

DOUBLE_EVIL_ROOM_2 = '''
 0338t6333903338t6339 
08........68........69
5.....B...M...B......1
5..M.............M...1
8.......T...T........6
l..B.....C.C.....B...r
2.......T...T........4
5..M.............M...1
5.....B...M...B......1
-2........42........4=
 -772b4777=-7772b477= 
'''

DOUBLE_EVIL_ROOM_3 = '''
03338t639    038t63339
5.......633338BB.....1
5.M....T......T......1
5........B...........1
8...M....4772..M.....6
l........1  5........r
2.....M.B6338....M...4
5........BBC.........1
5......T......T....M.1
5.......477772.......1
-7772b47=    -72b4777=
'''

DOUBLE_EVIL_ROOM_4 = '''
03338t6333333338t63339
5..M..............M..1
5.42.42.42..42.42.42.1
5.68.68.68..68.68.68.1
8..B...T......T......6
l....................r
2......T......T......4
5.42.42.42..42.42.42.1
5.68.68.68..68.68.68.1
5....M..........M....1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_5 = '''
03338t6333333338t63339
5....................1
5.472B.472..472..472.1
5.1 5..1 5..1 5..1 5.1
8.638..638.M638..638.6
l.......T....T.......r
2.472..472M.472..472.4
5.1 5..1 5..1 5..1 5.1
5.638..638..638B.638.1
5....................1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_6 = '''
03338t6333333338t63339
5M..................M1
5.BBBBBBBBBBBBBBBBBB.1
5.B.T..B....T........1
8.B.BB.BBBBB.BBBBBBB.6
l.B.B...T..B.B..T..B.r
2.B.BBBBBBBB.BBBBB.B.4
5.B..T........T....B.1
5.BBBBBBBBBBBBBBBBBB.1
5M..................M1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_7 = '''
03338t6333333338t63339
5.B.......B..........1
5..T..............T..1
5...............B....1
8...B..M.....CM......6
l....................r
2......MC.....M......4
5BB......B......B....1
5..T..............T..1
5.BB..........B......1
-7772b4777777772b4777=
'''

CHEST_ROOM_1 = '''
   08t69   
   5...1   
   -2.4=   
03908.69039
8.68...68B6
l.....T...r
2.42...42.4
-7=-2.4=-7=
   08.69   
   5...1   
   -2b4=   
'''

CHEST_ROOM_2 = '''
03338t63339
5.B.......1
5.........1
5B........1
8.....B...6
l..BCB....r
2...B..T..4
5........B1
5.........1
5.......BB1
-7772b4777=
'''

CHEST_ROOM_3 = '''
03338t639  
5C......639
-7772....B1
03395B....1
8..68.....6
l.........r
2T....42..4
5.....1-77=
5B....63339
-72......C1
  -72b4777=
'''

CHEST_ROOM_4 = '''
03338t63339
5.B.......1
5.B.......1
5.....B...1
8.........6
l....H....r
2.........4
5..T.B....1
5B........1
5.........1
-7772b4777=
'''

CHEST_ROOM_5 = '''
03338t63339
5.........1
5.........1
5......T..1
8.........6
l....L....r
2.........4
5.BT......1
5..B......1
5..B......1
-7772b4777=
'''

CHEST_ROOM_6 = '''
03338t63339
5.........1
5.........1
5......T..1
8.........6
l....D....r
2.........4
5..T......1
5.........1
5.........1
-7772b4777=
'''

CHEST_ROOM_7 = '''
   08t69   
   -2.4=   
    5.1    
09 08.69 09
8638.T.6386
l...T.T...r
2472.T.4724
-= -2.4= -=
    5.1    
   08.69   
   -2b4=   
'''

EMPTY_ROOM = '''           \n           \n           
           \n           \n           \n           
           \n           \n           \n           '''

END_ROOM = '''
03338t63339
5.........1
5.........1
5..T...T..1
8.........6
l....E....r
2.........4
5..T...T..1
5.........1
5.........1
-7772b4777=
'''

COVERT_ROOM_1 = '''
03333F33339
5.........1
5.........1
5..T...T..1
5....C....1
F...C.C...F
5....C....1
5..T...T..1
5.........1
5.........1
-7777F7777=
'''

COVERT_ROOM_2 = '''
03333F33339
5.........1
5.........1
5..T...T..1
5...C.C...1
F.........F
5...C.C...1
5..T...T..1
5.........1
5.........1
-7777F7777=
'''

COVERT_ROOM_3 = '''
03333F63339
5.........1
5.........1
5.........1
5.........1
F.........F
5.........1
5.........1
5........T1
5........C1
-7777F7777=
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
      'E17': EVIL_ROOM_17,
      'E18': EVIL_ROOM_18,
      'E19': EVIL_ROOM_19,
      'E20': EVIL_ROOM_20,
      'E21': EVIL_ROOM_21,
      'E22': EVIL_ROOM_22,
      'E23': EVIL_ROOM_23,
      'E24': EVIL_ROOM_24,
      'E25': EVIL_ROOM_25,
      'E26': EVIL_ROOM_26,
      'E27': EVIL_ROOM_27,
      'E28': EVIL_ROOM_28,
      'E29': EVIL_ROOM_29,
      'E30': EVIL_ROOM_30,
      'C1': CHEST_ROOM_1,
      'C2': CHEST_ROOM_2,
      'C3': CHEST_ROOM_3,
      'C4': CHEST_ROOM_4,
      'C5': CHEST_ROOM_5,
      'C6': CHEST_ROOM_6,
      'C7': CHEST_ROOM_7
}

DOUBLE_ROOMS = {
    'D1': DOUBLE_EVIL_ROOM_1,
    'D2': DOUBLE_EVIL_ROOM_2,
    'D3': DOUBLE_EVIL_ROOM_3,
    'D4': DOUBLE_EVIL_ROOM_4,
    'D5': DOUBLE_EVIL_ROOM_5,
    'D6': DOUBLE_EVIL_ROOM_6,
    'D7': DOUBLE_EVIL_ROOM_7
}

SECRET_ROOMS = {
    'C1': COVERT_ROOM_1,
    'C2': COVERT_ROOM_2,
    'C3': COVERT_ROOM_3
}

LEVEL_1 = '''
  RR RRR RR  
 RSRR RRRR   
RRR RRRR RRE 
 RRRR RR RRRR
RRR RRRRR    
  RR R RRRRRC
'''      # 50

LEVEL_2 = '''
   R  RRR SR 
 RRRR R RRRRR
RRR RRRRR   R
RR RRR    RRR
 RRRRR RRRR C
RER RRRRR    
'''      # 50

LEVEL_3 = '''
 RR   R   RRC
  RRRRRRERR  
RRR  RRR  RRR
  RRR   RRR  
RRR  RRR  RRR
  RSRRRRRRR  
 RR   R   RR 
'''      # 50

LEVEL_4 = '''
RRRR RRR RS C
 R  R RRRRR R
RR RRR R RRRR
R R R  R  RR 
 RRRR  R RRRE
RRR RRRRRR  R
'''      # 50

LEVEL_5 = '''
CR   RR RRRER
 RR R RRR R  
  RRRRR RRR  
RRR  R R R RR
R R RRRRRRRR 
  RSR R   R  
   R  RRRRR  
'''      # 50

LEVEL_6 = '''
  RRR     
 RR RRRRRR
 R     R R
 RRRRR R S
  R    R  
RRR RR RR 
  R  RRR  
R RRRRR   
R R   RRR 
RRE  RR RC
'''      # 50

LEVEL_7 = '''
 E  RRRRRR
 RRRR   R 
  R RR  RR
  R  R   C
  RRRRRR  
  R    RRR
 RRRR  R  
 R  R RRR 
C  RRRR RR
RRRR  RR S
'''      # 50

LEVEL_8 = '''
   RRRRRRR
 ERR  R  R
 R    R  R
 R    R  R
RRRRR RRRR
 R  R  R  
RR  R  R  
 R  R RRRR
 R RRRR  R
CRRR     S
'''      # 50

LEVEL_9 = '''
 ER    RR
  R  RRR 
  RRRR   
RRR  RRRR
  R     R
 RRRR   R
  R R RRR
  R  RR  
 RR   RRR
  S  CR  
'''      # 50

LEVEL_10 = '''
  RRR  S  
    R  RRR
C   RRRR R
RR  R  RRR
 RRRR    R
    R   RR
 RRRR   R 
 R    RRRR
RR R RR  E
 RRRRR  RR
'''      # 50

FORMS = {
    'L1': LEVEL_1,
    'L2': LEVEL_2,
    'L3': LEVEL_3,
    'L4': LEVEL_4,
    'L5': LEVEL_5,
    'L6': LEVEL_6,
    'L7': LEVEL_7,
    'L8': LEVEL_8,
    'L9': LEVEL_9,
    'L10': LEVEL_10
}

SHORT_BLOCK_CHANCE = 45
LONG_BLOCK_CHANCE = 35


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

    if true_with_chance(50, seed, user_seed):
        level_form = level_form.replace('S', '@').replace('E', 'S').replace('@', 'E')

    level_form = level_form.strip('\n').split('\n')
    doubled = False
    for i in range(len(level_form)):
        room_row = list(level_form[i])
        rooms = []
        for j in range(len(room_row)):
            if doubled:
                doubled = False
                continue

            if j + 1 < len(room_row):
                if room_row[j] == room_row[j + 1] == 'R' and true_with_chance(15, seed, user_seed):
                    room_row[j] = room_row[j + 1] = 'D'

            if room_row[j] == 'S':
                room = START_ROOM
            elif room_row[j] == 'E':
                room = END_ROOM
            elif room_row[j] == 'D':
                if user_seed:
                    seed.append(user_seed[0])
                    del user_seed[0]
                else:
                    seed.append(choice(list(DOUBLE_ROOMS)))
                room = DOUBLE_ROOMS[seed[-1]]
                doubled = True
            elif room_row[j] == 'R':
                if user_seed:
                    seed.append(user_seed[0])
                    del user_seed[0]
                else:
                    seed.append(choice(list(STANDART_ROOMS)))
                room = STANDART_ROOMS[seed[-1]]
            elif room_row[j] == 'C':
                if user_seed:
                    seed.append(user_seed[0])
                    del user_seed[0]
                else:
                    seed.append(choice(list(SECRET_ROOMS)))
                room = SECRET_ROOMS[seed[-1]]
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
            if level[i][j] == 'F':
                if j == 0 or level[i][j - 1] == ' ':
                    level[i][j] = '5'
                elif j + 1 == len(level[i]) or level[i][j + 1] == ' ':
                    level[i][j] = '1'
                elif i == 0 or level[i - 1][j] == ' ':
                    level[i][j] = '3'
                elif i + 1 == len(level) or level[i + 1][j] == ' ':
                    level[i][j] = '7'

            if level[i][j] not in 'rtlb':
                continue

            if level[i][j] == 'r':     # СПРАВА
                if j + 1 >= len(level[i]) or level[i][j + 1] != 'l':
                    if level[i + 2][j - 2] == level[i - 1][j - 1] == '.' and \
                            (j + 1 == len(level[i]) or level[i][j + 1] != 'F') and \
                            true_with_chance(SHORT_BLOCK_CHANCE, seed, user_seed):
                        level[i - 1][j] = '='
                        level[i + 1][j] = '9'
                        level[i][j] = ' '

                        if true_with_chance(LONG_BLOCK_CHANCE, seed, user_seed) and \
                                level[i][j - 3] == '.' == level[i - 1][j - 3]:
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
                        if level[i + 2][j] == ' ':
                            level[i + 1][j] = '='
                        if level[i - 2][j] == ' ':
                            level[i - 1][j] = '9'

            elif level[i][j] == 't':     # СВЕРХУ
                if i == 0 or level[i - 1][j] != 'b':
                    if level[i + 2][j - 1] == '.' and level[i + 1][j + 1] == '.' and \
                            (i == 0 or level[i - 1][j] != 'F') and \
                            true_with_chance(SHORT_BLOCK_CHANCE, seed, user_seed):
                        level[i][j - 1] = '9'
                        level[i][j + 1] = '0'
                        level[i][j] = ' '

                        if true_with_chance(LONG_BLOCK_CHANCE, seed, user_seed) and \
                                level[i + 3][j + 2] == '.' and level[i + 2][j - 1] == '.':
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
                        if level[i][j + 2] == ' ':
                            level[i][j + 1] = '9'
                        if level[i][j - 2] == ' ':
                            level[i][j - 1] = '0'

            elif level[i][j] == 'l':     # СЛЕВА
                if j == 0 or level[i][j - 1] != 'r':
                    if level[i + 2][j + 2] == '.' and level[i + 1][j + 1] == '.' and \
                            (j == 0 or level[i][j - 1] != 'F') and \
                            true_with_chance(SHORT_BLOCK_CHANCE, seed, user_seed):
                        level[i - 1][j] = '-'
                        level[i + 1][j] = '0'
                        level[i][j] = ' '

                        if true_with_chance(LONG_BLOCK_CHANCE, seed, user_seed) and \
                                level[i][j + 3] == '.':
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
                        if level[i + 2][j] == ' ':
                            level[i + 1][j] = '-'
                        if level[i - 2][j] == ' ':
                            level[i - 1][j] = '0'

            elif level[i][j] == 'b':     # СНИЗУ
                if i + 1 >= len(level) or level[i + 1][j] != 't':
                    if level[i - 2][j] == level[i - 2][j + 2] == '.' and level[i][j + 2] != ' ' and \
                            (i + 1 == len(level) or level[i + 1][j] != 'F') and \
                            true_with_chance(SHORT_BLOCK_CHANCE, seed, user_seed):
                        level[i][j + 1] = '-'
                        level[i][j - 1] = '='
                        level[i][j] = ' '

                        if true_with_chance(LONG_BLOCK_CHANCE, seed, user_seed) and \
                                level[i - 3][j + 2] == '.':
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
                        if level[i][j + 2] == ' ':
                            level[i][j + 1] = '='
                        if level[i][j - 2] == ' ':
                            level[i][j - 1] = '-'

    # Возвращаем созданный уровень
    # print(*seed)
    return [''.join(i) for i in level], seed


def true_with_chance(chance=50, seed=None, user_seed=None):
    if user_seed and seed:
        seed.append(user_seed[0])
        del user_seed[0]
    else:
        is_true = [0, 1][random() * 100 <= chance]
        if seed:
            seed.append(str(is_true))
        else:
            seed = [str(is_true)]
    return int(seed[-1])


FPS = 50
EMPTY = ' .@DMPCHLTFlrtb' + '1234567890-=B'
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
    level, level_x, level_y = load_level()

    camera = Camera()

    tile_images = {
        '1':  load_image('RIGHT_WALL.png'),
        '2':  load_image('TOP_RIGHT_WALL.png'),
        '3':  load_image('DOWN_WALL.png'),
        '4':  load_image('TOP_LEFT_WALL.png'),
        '5':  load_image('LEFT_WALL.png'),
        '6':  load_image('DOWN_LEFT_WALL.png'),
        '7':  load_image('DOWN_WALL.png'),
        '8':  load_image('DOWN_RIGHT_WALL.png'),
        '9':  load_image('TOP_RIGHT_WALL_2.png'),
        '0':  load_image('TOP_LEFT_WALL_2.png'),
        '-':  load_image('DOWN_LEFT_WALL_2.png'),
        '=':  load_image('DOWN_RIGHT_WALL_2.png'),
        'D':  load_image('dealer.png'),
        'r':  load_image('DOOR_RIGHT.png'),
        'l':  load_image('DOOR_LEFT.png'),
        'b':  load_image('DOOR_TOP.png'),
        't':  load_image('DOOR_BOTTOM.png'),
        'B':  load_image('BOX.png'),
        'B1': load_image('BARREL.png'),
        'F':  load_image('FLOOR.png'),
        'M':  load_image('MONSTER.png'),
        'P':  load_image('EMPTY.png'),
        'C':  load_image('CHEST.png'),
        'H':  load_image('EMPTY.png'),
        'L':  load_image('EMPTY.png'),
        'T':  load_image('TORCH.png'),
        'E':  load_image('EMPTY.png'),
        ' ':  load_image('DARK.png'),
        '.':  load_image('FLOOR.png'),
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
                if event.key == 46:
                    if EMPTY == ' .@MPHLTFlrtb':
                        EMPTY = ' .@MPHLTFlrtb' + '1234567890-=CBD'
                    else:
                        EMPTY = ' .@MPHLTFlrtb'
                if event.key == 45:
                    player.time += 0.01
                if event.key == 61:
                    player.time -= 0.01

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
