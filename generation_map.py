from random import *


# функция вывода уровня в консоль
def pprint(level):
    for i in level:
        print(*i, sep='   ')
    print()


# Создание прямоугольника с закрытыми краями
def ramka(level, w, h):
    level[0] = ['#'] * w
    level.append(['#'] * w)
    for i in range(h):
        level[i][0] = '#'
        level[i][-1] = '#'
    return level


# Проверка на то, правильный ли создался уровень
def checking(new_level, w, h):
    check_level = [[(-1, -1) if j == '#' else j for j in i] for i in new_level]
    nmax = -1
    smax = 1000, 1000
    points = []
    for i in range(h):
        for j in range(w):
            if check_level[i][j] != (-1, -1):
                if check_level[i - 1][j] == (-1, -1) and check_level[i][j - 1] == (-1, -1):
                    s = (1, 1)
                elif check_level[i - 1][j] == (-1, -1):
                    s = (check_level[i][j - 1][0] + 1, 1)
                elif check_level[i][j - 1] == (-1, -1):
                    s = (1, check_level[i - 1][j][0] + 1)
                else:
                    s = (check_level[i][j - 1][0] + 1, check_level[i - 1][j][1] + 1)
                check_level[i][j] = s
                if s[0] * s[1] > nmax:
                    nmax = s[0] * s[1]
                    smax = s
                if check_level[i + 1][j] == check_level[i][j + 1] == (-1, -1):
                    points.append(check_level[i][j])
    return check_level, points, smax


# Сама функция генерации
def generate_level(rooms: int, level_size: (int, int)):
    w, h = sorted(level_size)
    min_size = h // (rooms // 2)
    max_size = w // 2 + 1
    while 1:
        trying = 0

        level = ramka([[' '] * w for _ in range(h - 1)], w, h)

        # задаем почти посредине вертикальную линию
        mid = w // 2 + randint(-(w // 7), w // 7)
        lenght_mid = h - randint(min_size, max_size)
        for i in range(lenght_mid):
            level[i][mid] = '#'
        for i in range(w):
            level[lenght_mid - 1][i] = '#'

        while 1:
            # пробуем создавать комнаты на уровне 10 раз
            new_rooms = rooms
            new_level = [i[:] for i in level]
            while new_rooms - 3:
                x, y = randrange(2, w - 2), randrange(2, h - 2)
                s = [new_level[y][x], new_level[y][x + 1], new_level[y][x - 1]]
                if all([i.isspace() for i in s + [new_level[y - 1][x], new_level[y - 1][x]]]):
                    new_rooms -= 1
                    new_level[y][x] = '#'
                    if y < lenght_mid:
                        i = x
                        while new_level[y][i - 1].isspace():
                            new_level[y][i - 1] = '#'
                            i -= 1
                        i = x
                        while new_level[y][i + 1].isspace():
                            new_level[y][i + 1] = '#'
                            i += 1
                    else:
                        i = y
                        while new_level[i - 1][x].isspace():
                            new_level[i - 1][x] = '#'
                            i -= 1
                        i = y
                        while new_level[i + 1][x].isspace():
                            new_level[i + 1][x] = '#'
                            i += 1

            check_level, points, smax = checking(new_level, w, h)

            pprint(check_level)

            trying += 1
            print('POINTS: ', points)
            all_more = []
            # Проверка на правильность уровня
            for i, j in points:
                print(min_size, ' <= ', i, j, ' <= ', max_size)
                if min_size <= i <= max_size and min_size <= j <= max_size:
                    all_more.append(True)
                else:
                    all_more.append(False)
            print(all_more)
            if all(all_more) or trying >= 10:
                # Уровень готов, либо попытки истекли
                break
            # иначе пробуем ещё раз
        if trying < 10:
            pprint(new_level)
            level = new_level
            break

    # создаем игрока в неизвестном месте (создано для отладки)
    level[randrange(h)][randrange(w)] = '@'
    # Возвращаем созданный уровень
    return [''.join(i) for i in level]


if __name__ == '__main__':
    level = generate_level(7, (30, 60))
    file = open('data\\new level.txt', 'w')
    file.write('\n'.join([''.join(i) for i in level]))
    file.close()
