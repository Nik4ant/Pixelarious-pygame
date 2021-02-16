from random import choice

from entities.base_entity import Entity
from entities.tile import *
from entities.player import Player, PlayerAssistant
from entities.enemies import random_monster
from entities.spells import Spell
from config import TILE_SIZE
from engine import true_with_chance


SHORT_BLOCK_CHANCE = 45
LONG_BLOCK_CHANCE = 35

CRACKED_FLOOR_CHANCE = 0


# "0-9" + "-=" - Walls
# . - Floor
# r, t, l, b - Doors
# M - Mob (Monster)
# P - Player, start stairs
# C - Chest
# T - Torch
# E - End stairs
# B - Box/Barrel


# Карты комнат
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
5..B...B.B1
5.....B.M.1
5..B......1
8.B....B.B6
l.........r
2B..B.....4
5......T..1
5.M...B..B1
5..B...B..1
-7772b4777=
'''

EVIL_ROOM_2 = '''
03338t63339
5M......MC1
5.47777777=
5B633333339
8...BB.B.B6
l...M.....r
2.TBB.B.B.4
-77777772.1
033333338.1
5.........1
-7772b4777=
'''

EVIL_ROOM_3 = '''
03338t63339
5........B1
5......B..1
5..T......1
8.........6
l....B.M..r
2.B.......4
5....M....1
5...B.....1
5.......B.1
-7772b4777=
'''

EVIL_ROOM_4 = '''
03338t63339
5B....B...1
-2.......4=
08..B....69
8........B6
l.........r
2B.....T..4
-2.M.....4=
08....B..69
5.........1
-7772b4777=
'''

EVIL_ROOM_5 = '''
03338t63339
5B.....B..1
5....B....1
5..47772..1
8B.1   5B.6
l..1   5..r
2.B1   5..4
5..63338B.1
5.T..M...B1
5..B....BB1
-7772b4777=
'''

EVIL_ROOM_6 = '''
03338t6339 
5.M.B....69
5B....B..M1
5.B.......1
8..B..B..B6
l....T....r
2B....B..B4
5..M......1
5......B.B1
-2.B...BBB1
 -772b4777=
'''

EVIL_ROOM_7 = '''
03338t63339
5.B...B.BB1
5..B.....B1
5M..B.....1
8..B...B..6
l...T...B.r
2.B.......4
5.....B..B1
5.B..M....1
5.B...B477=
-7772b4=   
'''

EVIL_ROOM_8 = '''
03908t69039
5.15..B15M1
5M68...68.1
5..B..M...1
8..BB....B6
l....T.B..r
2.B.......4
5...B.B..B1
5.42...42.1
5B15..B15.1
-7=-2b4=-7=
'''

EVIL_ROOM_9 = '''
 0338t6339 
08B.B..BB69
5........B1
5B.B....B.1
8..B..B..B6
l...BT....r
2......B.B4
5.BB..M...1
5.....B.BB1
-2.B...B.4=
 -772b477= 
'''

EVIL_ROOM_10 = '''
  038t639  
  5....B1  
038B....639
5B..M..B..1
8...472...6
l..T1 5M..r
2.M.638B..4
5.B..B...B1
-72.....47=
  5...BB1  
  -72b47=  
'''

EVIL_ROOM_11 = '''
03338t63339
5..B...B..1
5.BB...B..1
5...B.....1
8B....B..B6
l....T..B.r
2B.....B..4
5..B..M...1
5.....B..B1
5.M....B..1
-7772b4777=
'''

EVIL_ROOM_12 = '''
03338t63339
5.......B.1
5B........1
5.....M...1
8.........6
l...BT.B..r
2......B.B4
5.BB..BB.B1
5M.BB...BB1
5B....BB.B1
-7772b4777=
'''

EVIL_ROOM_13 = '''
03338t63339
5B..B...BB1
5B........1
5.B....B..1
8...M....B6
l...BTM...r
2B..M.....4
5......B.B1
5.B.......1
5..B...B..1
-7772b4777=
'''

EVIL_ROOM_14 = '''
03338t639  
5B.B...B69 
5M..B....69
5..B...B..1
8.........6
l....T..B.r
2...B.B...4
5BBM....B.1
-2B..B...M1
 -2.B...B.1
  -72b4777=
'''

EVIL_ROOM_15 = '''
   08t69   
   -2.4=   
    5.1    
09  5.1  09
86338.63386
l..B..M...r
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
8B.10338BM6
l..15C.MM.r
2..1-772TM4
5..63338..1
5..B.BBB..1
5BB...B..B1
-7772b4777=
'''

EVIL_ROOM_17 = '''
   08t69   
  08...69  
 08..B..69 
08.....B.69
8B.B......6
l....T..B.r
2..M......4
-2.......4=
 -2..B..4= 
  -2...4=  
   -2b4=   
'''

EVIL_ROOM_18 = '''
   08t69   
  08...69  
 08....B69 
08.B...B.69
8.....B...6
l....T....r
2..B....M.4
-2.......4=
 -2..B..4= 
  -2B..4=  
   -2b4=   
'''

EVIL_ROOM_19 = '''
   08t69   
  08...69  
 08.....69 
08..B....69
8.........6
l.....M...r
2BB..B....4
-2.T.....4=
 -2....M4= 
  -2B..4=  
   -2b4=   
'''

EVIL_ROOM_20 = '''
   08t69   
  08...69  
 08.....69 
08...B...69
8.M....B..6
l.....BB..r
2...T.....4
-2.B..M..4=
 -2.....4= 
  -2...4=  
   -2b4=   
'''

EVIL_ROOM_21 = '''
03338t63339
5.........1
-7772.4777=
    5.69   
33338.C6333
l....T....r
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
33338.M6333
l.M.......r
77772.47777
    5.69   
03338.B6339
5...TM...M1
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
5B..B.B...1
5.M.....B.1
-7772.4777=
    5b1    
'''

EVIL_ROOM_24 = '''
    5t1    
 0338.6339 
 5M.....B1 
 5.B...B.1 
38.......63
l..B.T....r
72.....B.47
 5..M....1 
 5.B..B.B1 
 -772.477= 
    5b1    
'''

EVIL_ROOM_25 = '''
    5t1    
    5.1    
  038.639  
  5MB..B1  
338....B633
l..B.T....r
772....M477
  5BM.B.1  
  -72.47=  
    5.1    
    5b1    
'''

EVIL_ROOM_26 = '''
03338t639  
5M......639
5.BBT.....1
5M.BB.....1
8BBBB.....6
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
5......B..1
5B....BM..1
8.........6
l..M.TBB..r
2.B...BB..4
5B....BBMM1
5.B....BB.1
-772...BBC1
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
l....M....r
77772.47777
    5.1    
    5.1    
    5.1    
    5b1    
'''

EVIL_ROOM_30 = '''
   08t69   
  08...69  
 08B....69 
08M......69
8....M.B.M6
l..B..BB..r
2...T.....4
-2.B...MC4=
 -2.....4= 
  -2...4=  
   -2b4=   
'''

EVIL_ROOM_31 = '''
   08t69   
   5..M1   
   -2.4=   
03908.69039
8.68...68B6
l....MT...r
2.42...42.4
-7=-2.4=-7=
   08.69   
   5...1   
   -2b4=   
'''

EVIL_ROOM_32 = '''
03338t639  
5CM....M639
-7772M...B1
03395B..B.1
8..68..B..6
l..B......r
2T....42.M4
5...B.1-77=
5B.M..63339
-72.....B.1
  -72b4777=
'''

DOUBLE_EVIL_ROOM_1 = '''
03338t6333903338t63339
5.....B...68.........1
-2.B....B....B...B..4=
08.42B....42.....42.69
8..68..TB.68..T.B68..6
l.....B.....B........r
2B.42..T..42..T..42..4
-2.68.....68B...B68.4=
08B....B......B.....69
5...B.....42.....BB..1
-7772b4777=-7772b4777=
'''

DOUBLE_EVIL_ROOM_2 = '''
 0338t6333903338t6339 
08.B......68...B....69
5.....B...M...B..B.B.1
5..M....B......B.M...1
8....B..T...T........6
l..BB....C.C.....B...r
2.......T...T.B......4
5..M....B........M...1
5.....B...M...B....B.1
-2..B.....42.....B..4=
 -772b4777=-7772b477= 
'''

DOUBLE_EVIL_ROOM_3 = '''
03338t639    038t63339
5.......633338BB.....1
5.M....T......T......1
5........B...........1
8........4772........6
l........1  5........r
2.......B6338....M...4
5........BBM.........1
5......T......T......1
5.......477772.......1
-7772b47=    -72b4777=
'''

DOUBLE_EVIL_ROOM_4 = '''
03338t6333333338t63339
5..M.............MBCB1
5.42.42.42..42.42.42B1
5.68.68.68..68.68.68M1
8..BBB.TB.M..BT..BBB.6
l....M.....BB...M..B.r
2...BB.T..B...T.B.B..4
5.42.42.42..42.42.42.1
5.68.68.68..68.68.68.1
5...............M....1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_5 = '''
03338t6333333338t63339
5....................1
5.472B.472..472..472.1
5.1 5..1 5.B1 5..1 5.1
8.638..638..638..638.6
l.......T....T.......r
2.472..472M.472..472.4
5.1 5..1 5..1 5..1 5.1
5.638..638..638B.638.1
5....................1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_6 = '''
03338t6333333338t63339
5....................1
5.BBBBBBBBBBBBBBBBBB.1
5.B.TM.B.M..T........1
8.B.BB.BBBBB.BBBBBBB.6
l.B.B..MT.CB.BM.T..B.r
2.BMBBBBBBBB.BBBBB.B.4
5.B..T...M....T....B.1
5.BBBBBBBBBBBBBBBBBB.1
5....................1
-7772b4777777772b4777=
'''

DOUBLE_EVIL_ROOM_7 = '''
03338t6333333338t63339
5.B...B...B....B...B.1
5..T.........B....T..1
5.....M....B....B....1
8...B...B....CM....B.6
l.B......B.......B...r
2......MB...B.......B4
5BB.B..B.B...B..B..BB1
5B.T..B..B.B.B.B..TB.1
5.BBB..B.B..B.BB..B.B1
-7772b4777777772b4777=
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
           
 033333339 
 5BB..BB.1 
 5.T..BT.1 
 5...CBB.1 
 5B.CBC..1 
 5...C...1 
 5.T...T.1 
 5.......1 
 -7777777= 
           
'''

COVERT_ROOM_2 = '''
           
 033333339 
 5.B.BB.B1 
 5.T...T.1 
 5B.C.C..1 
 5......B1 
 5B.C.C..1 
 5.T...T.1 
 5B..B...1 
 -7777777= 
           
'''

COVERT_ROOM_3 = '''
           
 033333339 
 5CT...TC1 
 5T.....T1 
 5....B..1 
 5.B.....1 
 5.......1 
 5T...B.T1 
 5CT...TC1 
 -7777777= 
           
'''

COVERT_ROOM_4 = '''
03333333339
5.BBB.B.BB1
5.C.....C.1
5..T..BT.B1
5BB......B1
5..B.B....1
5..B....B.1
5..T...T..1
5.C.....C.1
5.....B...1
-777777777=
'''

COVERT_ROOM_5 = '''
           
  0333339  
  5B..B.1  
  5C..BC1  
  5TB..T1  
  5...B.1  
  5TB..T1  
  5C...C1  
  5.B.BB1  
  -77777=  
           
'''

COVERT_ROOM_6 = '''
           
 033333339 
 5CT..BTC1 
 5T.B..BT1 
 5B....B.1 
 5B....B.1 
 5.B....B1 
 5T..B..T1 
 5CTB..TC1 
 -7777777= 
           
'''

COVERT_ROOM_7 = '''
           
           
  0333339  
  5CT.TC1  
  5TBB.T1  
  5B..B.1  
  5TB..T1  
  5CT.TC1  
  -77777=  
           
           
'''

COVERT_ROOM_8 = '''
           
  0333339  
  5CTBTC1  
  5T.B.T1  
  5.B...1  
  5..B..1  
  5.BB.B1  
  5T.B.T1  
  5CT.BC1  
  -77777=  
           
'''

COVERT_ROOM_9 = '''
           
           
  0333339  
  5CTBTC1  
  5T.B.T1  
  5B..B.1  
  5T.B.T1  
  5CT.TC1  
  -77777=  
           
           
'''

COVERT_ROOM_10 = '''
           
           
 033333339 
 5CTB.BTC1 
 5T..BB.T1 
 5B.B..B.1 
 5T....BT1 
 5CTBB.TC1 
 -7777777= 
           
           
'''

# Группы комнат по использованию
STANDARD_ROOMS = {
      'E1':  EVIL_ROOM_1,
      'E2':  EVIL_ROOM_2,
      'E3':  EVIL_ROOM_3,
      'E4':  EVIL_ROOM_4,
      'E5':  EVIL_ROOM_5,
      'E6':  EVIL_ROOM_6,
      'E7':  EVIL_ROOM_7,
      'E8':  EVIL_ROOM_8,
      'E9':  EVIL_ROOM_9,
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
      'E31': EVIL_ROOM_31,
      'E32': EVIL_ROOM_32,
}

DOUBLE_ROOMS = {
    'D1': DOUBLE_EVIL_ROOM_1,
    'D2': DOUBLE_EVIL_ROOM_2,
    'D3': DOUBLE_EVIL_ROOM_3,
    'D4': DOUBLE_EVIL_ROOM_4,
    'D5': DOUBLE_EVIL_ROOM_5,
    'D6': DOUBLE_EVIL_ROOM_6,
    'D7': DOUBLE_EVIL_ROOM_7,
}

SECRET_ROOMS = {
    'C1':  COVERT_ROOM_1,
    'C2':  COVERT_ROOM_2,
    'C3':  COVERT_ROOM_3,
    'C4':  COVERT_ROOM_4,
    'C5':  COVERT_ROOM_5,
    'C6':  COVERT_ROOM_6,
    'C7':  COVERT_ROOM_7,
    'C8':  COVERT_ROOM_8,
    'C9':  COVERT_ROOM_9,
    'C10': COVERT_ROOM_10,
}


# Карты комнат в уровнях
LEVEL_1 = '''
RRRSRRR
R    RR
RRR RR 
  RRR C
RRR RR 
R    RR
RRRERRR
'''      # 31

LEVEL_2 = '''
RR R  C
 RRRR R
SR  RRR
 R  R R
 RRRRR 
RE   RR
'''      # 23

LEVEL_3 = '''
  C    
RERRRR 
  R  RR
RRRRR R
  R  RR
RRRRRS 
'''      # 21

LEVEL_4 = '''
SRRRR C
 R  R R
RR  RRR
 R  R R
 RRRR  
    RRE
'''      # 20

LEVEL_5 = '''
ER RRRR
 R R R 
 R RRR 
 RRR R 
RR   RS
C     C
'''      # 21

LEVEL_6 = '''
R RRR R
RRR RRS
 R     
RRRRRR 
  R R  
ERRRRC 
'''      # 21

LEVEL_7 = '''
RE  RRR
 RRRR R
  R RRR
 RR  R 
  RRRRR
RRR   S
'''      # 20

LEVEL_8 = '''
RR RRRR
 RRR  R
RR RRRR
 R R  R
RRRE  S
 R    R
'''      # 20

LEVEL_9 = '''
RER RR
R R  R
R RRRR
RRR  R
  R RS
CRRRR 
'''      # 21

LEVEL_10 = '''
  RRRRS
C R R  
R   RRR
RR  R  
 RRRRRR
ER R  R
'''      # 21

LEVEL_11 = '''
RRRRE
C RRR
RRRR 
 R R 
 RRRR
SRR  
R R C
'''  # 22

LEVEL_12 = '''
RRR E
R RRR
R  R 
R  RR
S RRR
R R  
RRR C
'''  # 19

LEVEL_13 = '''
 C ER
R   R
RRRRR
RRR  
R R C
 RR  
SRRRR
'''      # 24

LEVEL_14 = '''
 RRR  
RR RRR
R   RR
RR   R
S  RER
 C R  
'''      # 21

LEVEL_15 = '''
RRRRRR
  R RE
C R   
 RR   
  RRRR
SRR  R
'''      # 24

LEVEL_16 = '''
 RRRR
 RR R
RS RR
 R   
 RR C
  R  
RRRRE
'''      # 20

LEVEL_17 = '''
ERRRR 
 R  R 
RR   C
 RRR  
  R  S
RRRRRR
'''      # 24

LEVEL_18 = '''
CRRR 
   RR
E   R
RRRRR
 R R 
RR R 
R  RS
'''      # 22

LEVEL_19 = '''
C R E
RRRRR
 R   
 R RR
 RRR 
RR R 
R SRR
'''      # 22

LEVEL_20 = '''
R RRR 
RRR RR
 R   E
RR  C 
RRR  R
 SRRRR
'''      # 24

LEVEL_21 = '''
R RRRRE
RRR R  
R RRRR 
R R  R 
RSR CR 
'''      # 22

LEVEL_22 = '''
S RRRRR
R R   R
RRR   R
R   ERR
RRR C  
'''      # 22

LEVEL_23 = '''
ERRRR
    R
RRRRR
R   C
RRRRR
    R
SRRRR
'''      # 22

LEVEL_24 = '''
RRRS 
R    
RR  C
 R R 
RR R 
 R R 
 RRE 
'''      # 22

LEVEL_25 = '''
ERRRR
 R  R
RR  R
R RRR
RRR  
R S  
  C  
'''      # 20

LEVEL_26 = '''
RRR  E
C RRRR
 RR   
R R RR
RRR S 
 RRRR 
'''      # 22

LEVEL_27 = '''
 R RR
 RSR 
CR RR
 RC R
R R R
RRRRR
E RRR
'''      # 23

LEVEL_28 = '''
 RRRRR 
RR   RR
S C C E
RR   RR
 RRRRR 
'''      # 24

LEVEL_29 = '''
S  R  
RRRRR 
   R  
 R RRR
RRRRR 
C E RR
'''      # 22

LEVEL_30 = '''
 RC  R
RSRRRR
R R R 
 RR R 
 R RRR
 RRR E
'''      # 23

# Группа уровней
FORMS = {
    'L1':  LEVEL_1,
    'L2':  LEVEL_2,
    'L3':  LEVEL_3,
    'L4':  LEVEL_4,
    'L5':  LEVEL_5,
    'L6':  LEVEL_6,
    'L7':  LEVEL_7,
    'L8':  LEVEL_8,
    'L9':  LEVEL_9,
    'L10': LEVEL_10,
    'L11': LEVEL_11,
    'L12': LEVEL_12,
    'L13': LEVEL_13,
    'L14': LEVEL_14,
    'L15': LEVEL_15,
    'L16': LEVEL_16,
    'L17': LEVEL_17,
    'L18': LEVEL_18,
    'L19': LEVEL_19,
    'L20': LEVEL_20,
    'L21': LEVEL_21,
    'L22': LEVEL_22,
    'L23': LEVEL_23,
    'L24': LEVEL_24,
    'L25': LEVEL_25,
    'L26': LEVEL_26,
    'L27': LEVEL_27,
    'L28': LEVEL_28,
    'L29': LEVEL_29,
    'L30': LEVEL_30,
}


# Сама функция генерации
def generate_new_level(user_seed=None) -> [str, ..., str]:
    """
    Создаёт список строк, каждый символ в строке означает определенный тайл
    Генерация происходит псевдорандомно, выбирая случайный шаблон уровня,
    а затем для каждого символа формы выбирает случайную комнату. 
    С некоторым шансом из двух комнат может быть создана одна большая.
    Вместо дверей ставится либо стена, либо, если возможно, с некоторым шансом, "блок".
    Если генерация уже происходила и у вас есть сид, вы можете передать его этой функции,
    тогда карта будет сгенерирована по тем же параметрам. 
    Совпадение будет по форме уровня, каждой комнате и блоках из стен в комнатах.

    :param user_seed: Если есть, генерация происходит с установленными в нем параметрами
    :return: Сгенерированный (случайно/по сиду) уровень, его сид
    """
    level = []
    seed = []
    if user_seed:
        seed.append(user_seed.pop(0))
        # del user_seed[0]
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
                    seed.append(choice(list(STANDARD_ROOMS)))
                room = STANDARD_ROOMS[seed[-1]]
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
            if level[i][j] not in ['r', 't', 'l', 'b']:
                continue

            # Убираем двери там, где они не нужны
            # И строим блоки из стен на их месте с некоторым шансом
            if level[i][j] == 'r':     # ДВЕРЬ СПРАВА
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

            elif level[i][j] == 't':     # ДВЕРЬ СВЕРХУ
                if i == 0 or level[i - 1][j] != 'b':
                    if level[i + 2][j - 1] == '.' and level[i + 1][j + 1] == '.' and \
                            (i == 0 or level[i - 1][j] != 'F') and \
                            true_with_chance(SHORT_BLOCK_CHANCE, seed, user_seed):
                        level[i][j - 1] = '9'
                        level[i][j + 1] = '0'
                        level[i][j] = ' '

                        if true_with_chance(LONG_BLOCK_CHANCE, seed, user_seed) and \
                                level[i + 3][j + 2] == '.' and level[i + 2][j - 1] == '.' and \
                                level[i + 2][j + 1] == '.':
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

            elif level[i][j] == 'l':     # ДВЕРЬ СЛЕВА
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
                            level[i - 1][j + 1] = '7'
                            level[i + 1][j + 1] = '3'
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

            elif level[i][j] == 'b':     # ДВЕРЬ СНИЗУ
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

    # Возвращаем созданный уровень и сид
    return [''.join(i) for i in level], seed


def initialise_level(level_map, level, all_sprites, tiles_group, furniture_group, barriers_group, enemies_group,
                     doors_group, torches_group, end_of_level, monster_seed, boxes_seed, player):
    """
    Функция для инициализации уровня
    Проходит по переданной ей карте уровня и на каждый символ карты создает тайл и что-то на нем, если есть
    Если передается сид, монстры будут такие, как записано в сиде
    Разные тайлы пола, предметов на уровне (бочек, коробок) будут всегда одинаковые

    :param level_map: Уровень
    :param level: Номер уровня, нужен для расчета сложности
    :param all_sprites: Группа со всеми спрайтами
    :param tiles_group: Группа со спрайтами плиток пола
    :param furniture_group: Группа со спрайтами ящиков на уровне
    :param barriers_group: Группа для спрайтов с тайлами, сквозь которые нельзя ходить
    :param enemies_group: Группа врагов
    :param doors_group: Группа дверей
    :param torches_group: Группа с факелами
    :param end_of_level: Группа тайла лестницы вниз, при касании с которым произойдет переход на следующий уровень
    :param monster_seed: Сид, по которому будут расставлены монстры
    :param boxes_seed: Сид, по которому будут расставлены бочки
    :param player: Если он передан, просто перемещаем его на новое место, а иначе создаем нового

    :return player: Игрок, размещённый в нужном месте
    :return monster_seed: Враги, размещённые в нужном месте
    :return boxes_seed: Ящики, размещённые или нет в нужном месте
    """
    new_monster_seed = []
    new_boxes_seed = []
    level_map = [list(i) for i in level_map]

    # Установка общих физических объектов для всех сущностей
    Entity.set_global_groups(barriers_group, all_sprites)
    # Установка общих физических объектов для всех заклинаний
    Spell.set_global_collisions_group(barriers_group)
    Spell.set_global_breaking_group(doors_group, furniture_group)

    for y in range(len(level_map)):
        for x in range(len(level_map[y])):
            if level_map[y][x] in 'PMF.BCrbltT':    # объединим те, в которых надо спавнить пол
                if true_with_chance(CRACKED_FLOOR_CHANCE):
                    Tile(choice(['.0', '.1', '.2', '.3']), x, y, all_sprites, tiles_group)
                else:
                    Tile('.', x, y, all_sprites, tiles_group)

                if level_map[y][x] == 'P':    # ИГРОК
                    # Помещаем игрока в центр текущего тайла
                    if not player:
                        player = Player(x * TILE_SIZE + TILE_SIZE * 0.5,
                                        y * TILE_SIZE + TILE_SIZE * 0.5, level, all_sprites)
                        player.add_assistant(PlayerAssistant(-10000, -10000, player, all_sprites))
                    else:
                        player.start_position = (x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE
                        player.rect.center = (x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE
                    Tile(level_map[y][x], x, y, all_sprites, tiles_group)

                elif level_map[y][x] == 'M':    # МОНСТР
                    random_monster(x, y, level, all_sprites, enemies_group, new_monster_seed, monster_seed)

                elif level_map[y][x] == 'B':    # МЕБЕЛЬ (бочки)
                    if boxes_seed:
                        n = int(boxes_seed.pop(0))
                    else:
                        n = randint(0, 3)
                    index = len(new_boxes_seed)

                    if n == 1:
                        Furniture('B1', x, y, new_boxes_seed, index, all_sprites, furniture_group, barriers_group)
                    elif n == 2:
                        Furniture('B2', x, y, new_boxes_seed, index, all_sprites, furniture_group, barriers_group)
                    elif n == 3:
                        Furniture('B3', x, y, new_boxes_seed, index, all_sprites, furniture_group, barriers_group)
                    new_boxes_seed.append(str(n))

                elif level_map[y][x] == 'C':    # СУНДУКИ
                    if boxes_seed:
                        n = int(boxes_seed.pop(0))
                    else:
                        n = [randint(1, 3), 4][true_with_chance(80)]
                    index = len(new_boxes_seed)

                    if n == 4:
                        Chest(x, y, new_boxes_seed, index, all_sprites, barriers_group)
                    elif n == 1:
                        Furniture('B1', x, y, new_boxes_seed, index,
                                  all_sprites, furniture_group, barriers_group)
                    elif n == 2:
                        Furniture('B2', x, y, new_boxes_seed, index,
                                  all_sprites, furniture_group, barriers_group)
                    elif n == 3:
                        Furniture('B3', x, y, new_boxes_seed, index,
                                  all_sprites, furniture_group, barriers_group)
                    new_boxes_seed.append(str(n))

                elif level_map[y][x] in 'ltT':    # ДВЕРИ И ФАКЕЛА
                    if level_map[y][x] == 'l':
                        Door(x - 0.5, y, all_sprites, doors_group)
                    elif level_map[y][x] == 't':
                        Door(x, y - 0.5, all_sprites, doors_group)
                    elif level_map[y][x] == 'T':
                        Torch(x + 0.12, y, all_sprites, torches_group)

            elif level_map[y][x] in '1234567890-=':
                Tile(level_map[y][x], x, y, all_sprites, barriers_group)
            elif level_map[y][x] == 'E':
                Tile('E', x, y, all_sprites, tiles_group, end_of_level)
            elif level_map[y][x] != ' ':
                Tile(level_map[y][x], x, y, all_sprites, tiles_group)

    print(level, len(enemies_group))
    # вернем игрока и сид монстров
    return player, new_monster_seed, new_boxes_seed
