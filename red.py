from random import choice, randint

for k in range(20):
    alf = list('                 RRRRRRRRRRRRRRRRRRRRRRRESCC')
    width = randint(5, 7)
    height = 12 - width
    m = []
    for i in range(height):
        n = []
        for j in range(width):
            n.append(choice(alf))
            alf.remove(n[-1])
        m.append(n)

    s = '\n'.join([''.join(i) for i in m])
    print(f"""    'L{k + 11}': LEVEL_{k + 11},""")
