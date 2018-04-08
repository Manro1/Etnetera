# Etnetera - Hrava hlava
# Kod byl zalozen na spouste experimentu, takze neni, slusne receno, v produkcni kvalite. Jak kod +- funguje:
# 1. Projedu v nahodnem poradi cisla a na kazde provedu dotaz, kde je prvni pulka pole vyplnena cislem a zbytek nulami
# 	=> tim rovnou zjistim kolik cisel je v leve pulce pole a kolik na prave (fce getCnt).
# 2. Projedu v poradi od nejfrekventovanejsiho cisla k tomu s nejmene vyskyty vsechna cisla, ktera se v poli vyskytuji
#    a snazim se zjistit jejich pozice za pomoci binarniho vyhledavani. Jako dobra optimalizace pomaha uvazovat v
#    binarnim vyhledavani pouze dosud neobsazene pozice.
# 3. Jako dobra optimalizace zafungovalo i vyuziti hrube sily (fce bruteforce), kdy uvazuju poslednich 10 jenotlive se 
#    vyskytujicich cisel. Pro ne si vygeneruju vsechny permutace a nasledne je ruzne umistuji do pole. Vzdycky udelam
#    test a odstranim ze seznamu kombinace, ktere rozhodne nevedou k reseni. V prumeru na poslednich 10ti cislech
#    oproti binaru usetrim cca 15 dotazu, coz tim ze bruteforce pouzivam pro 10 poslednich cisel pro levou a pro
#    pravou pulku zvlast, je uz docela znat.
# 4. Samozrejme i zarezavam hry, ktere by mi zhorsily vysledek

from itertools import permutations
import random
import requests
import sys

URL       = 'https://ikariera.etnetera.cz/veletrhy/'
SLOTS     = 100
THRESHOLD = 10
LIMIT     = 440

cnt    = {}
pcnt   = {}

def start():
    response = requests.post(URL + 'start', json={
                                                'nickname': '***',
                                                'email':    '***',
                                                'slots':    SLOTS
    })
    gameId = response.json()['gameId']
    print('Game started with game id = {}'.format(gameId))
    return gameId

def guess(gameId, arr):
    response = requests.post(URL + 'guess', json={'gameId': gameId, 'guess': arr})
    # print(response.json())
    black, white = response.json()['evaluation']['black'], response.json()['evaluation']['white']
    guesses      = response.json()['guessCount']
    if black == 100:
        print('Congratulations, you solved the task after {} attempts.'.format(guesses))
        sys.exit()
    if guesses >= LIMIT:
        print('F*** off you imbecil, {} attempts was not enough'.format(guesses))
        print(black, white, placed, arr)
        sys.exit()
    # print('black =', black, 'white =', white)
    if guesses % 10 == 0:
        print('Guess number {}'.format(guesses))
    return black, white

def getCnt(gameId):
    global cnt
    arr    = [0] * SLOTS
    toTest = [i for i in range(1, SLOTS + 1)]
    random.shuffle(toTest)

    # find out number of occurences
    for number in toTest:
        total = 0
        for num in cnt:
            total += cnt[num][0] + cnt[num][1]
        if total == SLOTS:
            break
        low = 0
        high = SLOTS - 1
        mid = (low + high) // 2
        for index in empty:
            if index > mid:
                break
            arr[index] = number
        black, white = guess(gameId, arr)
        if black + white > 0:
            cnt[number] = (black, white)
            pcnt[number] = [0,0]
        arr = [0] * SLOTS

    # order numbers the way they are meant to be tested
    toTest = []
    for number in cnt:
        toTest.append((number, cnt[number][0] + cnt[number][1]))
    toTest = sorted(toTest, key=lambda x: x[1], reverse=True)

    print('Found out frequency of numbers {}'.format(cnt))
    return toTest

def binarySearch(gameId, resarr, low, high, empty, number, counter):
    if counter == 0 or len(empty) == 0:
        return 0
    lo = 0
    hi = len(empty)-1
    while empty[lo] < low:
        lo += 1
    while empty[hi] > high:
        hi -= 1
    if hi - lo + 1 == counter:
        global placed
        placed += counter
        for i in range(lo,hi+1):
            resarr[empty[i]] = number
        for i in range(lo, hi + 1):
            del empty[lo]
        pcnt[number][0 if (high <= SLOTS // 2) else 1] += counter
        # cnt[number][0 if (high <= SLOTS // 2) else 1] -= counter
        return counter
    mi = (lo + hi) // 2
    mid = empty[mi]
    # arr = [0] * SLOTS
    arr = resarr[:]
    for index in empty:
        if index > empty[mi]:
            break
        arr[index] = number
    black, white = guess(gameId, arr)
    black -= placed
    if counter == None:
        counter = black + white
        print('There are {} occurences of {}'.format(counter, number))
    # print(lo, hi, low, high, number, result, counter)
    return  binarySearch(gameId, resarr, low, mid, empty, number, black) + \
            binarySearch(gameId, resarr, mid+1, high, empty, number, counter - black)

def bruteforce(gameId, numbers, indices, black_orig, white_orig):
    global arr
    global cnt
    global empty
    global pcnt
    global placed
    if len(numbers) != len(indices):
        print(numbers)
        print(indices)
        raise SyntaxError
    print('bruteforce')
    possible = list(permutations(numbers))
    while len(possible) > 1:
        print(len(possible))
        perm = random.choice(possible)
        for i in range(len(indices)):
            arr[indices[i]] = perm[i]
        black, white = guess(gameId, arr)
        black -= black_orig
        white -= white_orig
        new_possible = []
        for state in possible:
            cblack = 0
            cwhite = 0
            tmp = [arr[idx] for idx in indices]
            for i in range(len(indices)):
                if state[i] == tmp[i]:
                    cblack += 1
                    tmp[i] = 0
                elif state[i] in tmp:
                    cwhite += 1
            if black == cblack and white == cwhite:
                new_possible.append(state)
        possible = new_possible
    placed += len(indices)
    for number in numbers:
        pcnt[number][0 if (indices[-1] <= SLOTS // 2) else 1] += 1
        # print(cnt[number][0], pcnt[number][0], cnt[number][1], pcnt[number][1])
    for i in range(len(indices)):
        arr[indices[i]] = possible[0][i]
        empty.remove(indices[i])
    # print(guess(gameId, arr), placed)
    print('solved')
    # raise SyntaxError

gameId = start()
empty  = [i for i in range(SLOTS)]
arr    = [0] * SLOTS
placed = 0
toTest = getCnt(gameId)

print('Total of {} numbers'.format(len(toTest)))

for index, (number, counter) in enumerate(toTest):
    print('Placing number {} ({} occurences)'.format(number, counter))
    low  = 0
    high = SLOTS - 1
    mid  = (low + high) // 2
    # print('Placing {} occurences of number {}'.format(counter, number))
    binarySearch(gameId, arr, low, mid, empty, number, cnt[number][0] - pcnt[number][0])
    binarySearch(gameId, arr, mid+1, high, empty, number, cnt[number][1] - pcnt[number][1])

    left = [number for number in cnt if cnt[number][0] == 1 and pcnt[number][0] == 0]
    leftempty = [idx for idx in empty if idx <= SLOTS // 2]
    rightempty = [idx for idx in empty if idx > SLOTS // 2]
    right = [number for number in cnt if cnt[number][1] == 1 and pcnt[number][1] == 0]
    # print("left:", len(left), "right:", len(right))
    if len(left) > 0 and len(left) <= THRESHOLD and len(left) == len(leftempty):
        bruteforce(gameId, left, leftempty, placed, 0)
    if len(right) > 0 and len(right) <= THRESHOLD and len(right) == len(rightempty):
        bruteforce(gameId, right, rightempty, placed, 0)


print('Finished')
# just to be sure
guess(gameId, arr)
