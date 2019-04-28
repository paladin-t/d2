#!/usr/bin/env python

import math
import random
import sys

# Utilities.

class Utils:
    isCPython = 'Python Software Foundation' in sys.copyright
    isSkulpt = 'Scott Graham' in sys.copyright

    def debug(msg):
        print(msg)

    def read(prompt = None):
        ret = input(prompt)
        if len(ret) == 0:
            return None
        elif ret == 'Y' or ret.lower() == 'yes' or ret.lower() == 'true':
            ret = 'y';
        elif ret == 'N' or ret.lower() == 'no' or ret.lower() == 'false':
            ret = 'n';

        return ret

    def write(msg):
        print(msg)

    def shift(seq, n):
        n = n % len(seq)

        return seq[n:] + seq[:n]

if Utils.isCPython:
    from functools import reduce

    print('Using CPython')
else:
    if Utils.isSkulpt:
        print('Using Skulpt Python')

    def next(g):
        return g.next()

    def reduce(proc, lst):
        if len(lst) == 0:
            raise TypeError('reduce() of empty sequence with no initial value')
        l = lst[0]
        r = lst[0]
        for i in range(1, len(lst)):
            l = r
            r = lst[i]
            r = proc(l, r)

        return r

# Deck.

class Suits:
    Jokers = 0
    Hearts = 1
    Tiles = 2
    Clovers = 3
    Pikes = 4

    Names = [ '', '♥', '♦', '♣', '♠' ]

    def nameOf(s):
        if s >= 0 and s <= 4:
            return Suits.Names[s]

        return None

class Points:
    Names = [ '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', '🙂', '😀' ]

    Joker0 = 14
    Joker1 = 15
    Points = [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1, 2, Joker0, Joker1 ]

    Values = [ 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987 ]

    def nameOf(i):
        if i >= 1 and i <= Points.Joker1:
            return Points.Names[i - 1]

        return None

    def pointOf(i):
        if i >= 1 and i <= Points.Joker1:
            return Points.Points[i - 1]

        return None

    def valueOf(i):
        if i >= 1 and i <= Points.Joker1:
            return Points.Values[i - 1]

        return 0

    def indexFromName(n):
        n = n.upper()
        if n == ':)':
            return 13 + 1
        elif n == ':D':
            return 14 + 1

        i = Points.Names.index(n)
        if i >= 0:
            i += 1

        return i

class Card:
    def __init__(self, s, i):
        self.suit = s
        self.index = i

    def __str__(self):
        return Points.nameOf(self.index) + Suits.nameOf(self.suit)

    def __lt__(self, other):
        if self.index != other.index:
            return self.index < other.index

        return self.suit < other.suit

    def evaluate(board, cards):
        values = list(map(lambda c: Points.valueOf(c.index), cards))

        return reduce(lambda l, r: l + r, values)

# Player.

class Player:
    def __init__(self):
        self.isCpu = False
        self.isLandLord = False

        self.hand = [ ]

        self.demanding = 0

        self.score = 100

    def indexOf(hand, suit, index):
        if len(hand) == 0:
            return -1

        for i in range(len(hand)):
            c = hand[i]
            if c == None:
                continue

            if suit == None:
                if c.index == index:
                    return i
            else:
                if c.suit == suit and c.index == index:
                    return i

        return -1

    def cardOf(hand, suit, index):
        if len(hand) == 0:
            return None

        for i in range(len(hand)):
            c = hand[i]
            if c == None:
                continue

            if suit == None:
                if c.index == index:
                    return c
            else:
                if c.suit == suit and c.index == index:
                    return c

        return None

    def clear(self):
        del self.hand[:]

    def take(self, card):
        self.hand.append(Card(card.suit, card.index))

    def sort(self):
        self.hand.sort()

    def demand(self, index, board, evaluated):
        return False

    def pick(self, indices, auxiliary = None):
        orders = [ ]
        cards = [ ]
        hand = self.hand[:]

        for index in indices:
            name = Points.nameOf(index)
            order = Player.indexOf(hand, None, index)
            card = Player.cardOf(hand, None, index)
            if order < 0 or card == None:
                return ( None, None )

            orders.append(order)
            cards.append(card)
            hand[order] = None

        if auxiliary != None:
            for aux in auxiliary:
                pass

                # TODO

        Utils.debug('Picking orders: ' + str(orders) + ' of indices ' + str(indices))

        return ( orders, cards )

    def search(self, index, board):
        valid = [ ]

        p = None
        handPiles = [ ]
        for c in self.hand:
            if p == None:
                p = Pile()
                handPiles.append(p)
            q = p.counts(c)
            if isinstance(q, Pile):
                p = q
                handPiles.append(p)
        handPiles.sort()

        p = None
        putPiles = [ ]
        for c in board.stack[-1].cards:
            if p == None:
                p = Pile()
                putPiles.append(p)
            q = p.counts(c)
            if isinstance(q, Pile):
                p = q
                putPiles.append(p)
        putPiles.sort()

        hand = board.stack[-1].hand

        if hand == Pattern.Invalid:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3_2n)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3_n)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x2)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Quadruple_2_2)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Quadruple_1_1)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple_2)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple_1)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Double)
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Single)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Single:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Single)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Double:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Double)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Triple:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Triple_1:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple_1)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Triple_2:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Triple_2)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Quadruple:
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Quadruple_1_1:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Quadruple_1_1)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Quadruple_2_2:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Quadruple_2_2)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Straight:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Straight_x2:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x2)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Straight_x3:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Straight_x3_n:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3_n)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Straight_x3_2n:
            valid += Pattern.some(board, self, index, handPiles, putPiles, Pattern.Straight_x3_2n)
            valid += Pattern.quadruple(board, self, index, handPiles, putPiles)
            valid += Pattern.jokers(board, self, index, handPiles, putPiles)
        elif hand == Pattern.Jokers:
            pass

        valid = list(filter(lambda v: v != None, valid))
        valid.sort(key = lambda v: -v[1])

        return valid if len(valid) > 0 else None

    def think(self, index, board, put):
        n = board.reader.turn(('CPU\'s' if self.isCpu else 'YOUr') + '@' + str(index))
        n = list(filter(lambda s: len(s) > 0, n.split(' ')))

        indices = list(map(lambda name: Points.indexFromName(name), n))
        ( orders, cards ) = self.pick(indices)

        put[0] = orders
        put[1] = cards

        return True

    def dump(self):
        ret = [ ]
        for c in self.hand:
            ret.append(str(c))

        return ret

class Cpu(Player):
    def __init__(self):
        Player.__init__(self)

        self.isCpu = True

    def demand(self, index, board, evaluated):
        d = [ n for n, v in enumerate(evaluated) if v[1] == index ][0]
        d += 1
        if d == 2:
            d = 3
        self.demanding = d

        return True

    def think(self, index, board, put):
        self.search(index, board)
        # TODO

        return Player.think(self, index, board, put)

class You(Player):
    def __init__(self, reader, writer):
        Player.__init__(self)

        self.reader = reader
        self.writer = writer

    def demand(self, index, board, evaluated):
        d = self.reader.demand()
        if d == None:
            d = 0
        else:
            try:
                d = int(d)
            except:
                d = 0

        if d < 0 or d > 3:
            return False

        self.demanding = d

        return True

    def think(self, index, board, put):
        return Player.think(self, index, board, put)

# Board.

class Put:
    Separator = ' '

    def __init__(self):
        self.owner = None
        self.hand = Pattern.Invalid
        self.cards = [ ]

    def dump(self):
        ret = [ ]
        for c in self.cards:
            ret.append(str(c))

        return ret

class Pile:
    def __init__(self):
        self.index = 0
        self.count = 0

    def __str__(self):
        return '<' + str(self.index) + ', ' + str(self.count) + '>'

    def __lt__(self, other):
        if self.count != other.count:
            return self.count > other.count

        return self.index < other.index

    def counts(self, card):
        if self.index == 0:
            self.index = card.index
            self.count = 1

            return True
        elif self.index == card.index:
            self.count += 1

            return True
        else:
            ret = Pile()
            ret.counts(card)

            return ret

class Pattern:
    Invalid = 0
    Single = 1           # 1
    Double = 2           # 1
    Triple = 3           # 1
    Triple_1 = 31        # 2
    Triple_2 = 32        # 2
    Quadruple = 4000     # 1
    Quadruple_1_1 = 411  # 3
    Quadruple_2_2 = 422  # 3
    Straight = 5         # n
    Straight_x2 = 52     # n * 2
    Straight_x3 = 53     # n * 3
    Straight_x3_n = 530  # n * 3 + n
    Straight_x3_2n = 532 # n * 3 + n * 2
    Jokers = 6000        # 2

    Names = {
        Invalid: 'Invalid',
        Single: 'Single',
        Double: 'Double',
        Triple: 'Triple',
        Triple_1: 'Triple+1',
        Triple_2: 'Triple+2',
        Quadruple: 'Quadruple',
        Quadruple_1_1: 'Quadruple+1+1',
        Quadruple_2_2: 'Quadruple+2+2',
        Straight: 'Straight',
        Straight_x2: 'Straight*2',
        Straight_x3: 'Straight*3',
        Straight_x3_n: 'Straight*3+n',
        Straight_x3_2n: 'Straight*3+2n',
        Jokers: 'Jokers'
    }

    def timesOf(hand):
        if hand >= Pattern.Quadruple:
            return 2

        return 1

    def straight(piles, count = None):
        ret = 0
        if len(piles) == 0:
            return ret

        ret = 1
        n = count if count != None else piles[0].count
        v = piles[0].index
        for i in range(1, len(piles)):
            p = piles[i]
            if p.count != n or p.index != v + 1:
                return ret

            v += 1
            ret += 1

        return ret

    def high(piles):
        ret = 0
        if len(piles) == 0:
            return ret

        ret = 1
        n = 1
        for p in piles:
            if p.count != n:
                return ret

            ret += 1

        return ret

    def high_x2(piles):
        ret = 0
        if len(piles) == 0:
            return ret

        ret = 1
        n = 2
        for p in piles:
            if p.count != n:
                return ret

            ret += 1

        return ret

    def firstIndexOf(piles, pred, card):
        for i in range(len(piles)):
            pile = piles[i]
            if pred(pile, card):
                return i

        return -1

    def handOf(cards):
        hand = Pattern.Invalid
        piles = [ ]
        p = None
        for c in cards:
            if p == None:
                p = Pile()
                piles.append(p)
            q = p.counts(c)
            if isinstance(q, Pile):
                p = q
                piles.append(p)
        piles.sort()

        def count(pile):
            return pile.count

        def match(piles, what, how):
            if len(piles) != len(how):
                return False

            for i in range(len(piles)):
                if what(piles[i]) != how[i]:
                    return False

            return True

        def joking(piles):
            for p in piles:
                if p.index == Points.Joker0 or p.index == Points.Joker1:
                    return True

            return False
        def kidding(piles):
            for p in piles:
                if p.index == 13:
                    return True

            return False

        l = len(piles)
        if l == 0:
            pass
        elif l == 1:
            if match(piles, count, ( 1, )):
                hand = Pattern.Single
            elif match(piles, count, ( 2, )):
                hand = Pattern.Double
            elif match(piles, count, ( 3, )):
                hand = Pattern.Triple
            elif match(piles, count, ( 4, )):
                hand = Pattern.Quadruple
        elif l == 2:
            if piles[0].index == Points.Joker0 and piles[1].index == Points.Joker1:
                assert(match(piles, count, ( 1, 1 ))), 'Impossible'
                hand = Pattern.Jokers
            elif match(piles, count, ( 3, 1 )):
                if not joking(piles):
                    hand = Pattern.Triple_1
            elif match(piles, count, ( 3, 2 )):
                if not joking(piles):
                    hand = Pattern.Triple_2
        elif l == 3:
            if match(piles, count, ( 4, 1, 1 )):
                if not joking(piles):
                    hand = Pattern.Quadruple_1_1
            elif match(piles, count, ( 4, 2, 2 )):
                if not joking(piles):
                    hand = Pattern.Quadruple_2_2
        if hand == Pattern.Invalid and l >= 3:
            s = Pattern.straight(piles)
            if piles[0].count == 1:
                if s == l and l >= 5:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight
            elif piles[0].count == 2:
                if s == l:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x2
            elif piles[0].count == 3:
                if s == l:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x3
                elif s == l / 2 and Pattern.high(piles[s:]) == l / 2:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x3_n
                elif s == l / 2 and Pattern.high_x2(piles[s:]) == l / 2:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x3_2n

        return ( hand, piles )

    def compare(lcards, rcards):
        def compareHand(lhand, rhand):
            if lhand[0] != rhand[0]:
                if lhand[0] == Pattern.Invalid:
                    return -1
                elif rhand[0] == Pattern.Invalid:
                    return 1
                elif lhand[0] == Pattern.Jokers:
                    return 1
                elif lhand[0] == Pattern.Quadruple and rhand[0] == Pattern.Quadruple:
                    return 0
                elif lhand[0] == Pattern.Quadruple and rhand[0] != Pattern.Jokers:
                    return 1
                else:
                    return -1

            if len(lhand[1]) != len(rhand[1]):
                return -1

            for i in range(len(lhand[1])):
                if lhand[1][i].count != rhand[1][i].count:
                    return -1

            return 0
        def comparePiles(lpiles, rpiles):
            lp = lpiles[0].index
            rp = rpiles[0].index
            if lp < rp:
                return -1
            elif lp > rp:
                return 1
            else:
                return 0

        hand = Pattern.Invalid
        rel = 0
        times = 1

        lhand = Pattern.handOf(lcards)
        rhand = Pattern.handOf(rcards)
        cm = compareHand(lhand, rhand)
        if cm == 0:
            hand = lhand[0]
            rel = comparePiles(lhand[1], rhand[1])
            times = Pattern.timesOf(lhand[0])
        elif cm > 0:
            hand = lhand[0]
            rel = 1
            times = Pattern.timesOf(lhand[0])

        return ( hand, rel, times )

    def quadruple(board, player, index, handPiles, putPiles):
        indexIsGeq = lambda p, c: p.index >= c.index

        start = 0
        if len(board.stack[-1].cards) > 0 and board.stack[-1].hand == Pattern.Quadruple:
            start = Pattern.firstIndexOf(handPiles, indexIsGeq, board.stack[-1].cards[0])
            if start == -1:
                start = 0

        possibilities = [ ]
        for i in range(start, len(handPiles)):
            pile = handPiles[i]
            if pile.count < 4:
                continue

            indices = [ pile.index ] * 4
            ( _1, cards ) = player.pick(indices)
            score = 0 # TODO

            possibilities.append(( cards, score ))

        return possibilities

    def jokers(board, player, index, handPiles, putPiles):
        cards = [ ]
        index = Points.indexFromName(':)')
        card0 = Player.cardOf(player.hand, None, index)
        index = Points.indexFromName(':D')
        card1 = Player.cardOf(player.hand, None, index)
        if card0 != None and card1 != None:
            cards.append(card0)
            cards.append(card1)
        score = 0 # TODO

        return [ ( cards, score ) ]

    def some(board, player, index, handPiles, putPiles, hand):
        if hand == Pattern.Quadruple:
            return Pattern.quadruple(board, player, index, handPiles, putPiles)
        elif hand == Pattern.Jokers:
            return Pattern.jokers(board, player, index, handPiles, putPiles)

        indexIsGeq = lambda p, c: p.index >= c.index
        indexIsAny = lambda _1, _2: True

        start = 0
        if len(board.stack[-1].cards) > 0:
            indexIs = indexIsGeq if board.stack[-1].hand == hand else indexIsAny
            start = Pattern.firstIndexOf(handPiles, indexIs, board.stack[-1].cards[0])
            if start < 0:
                start = 0

        pointed = 0
        straight = None
        auxiliary = None
        if hand == Pattern.Single:
            pointed = 1
        elif hand == Pattern.Double:
            pointed = 2
        elif hand == Pattern.Triple:
            pointed = 3
        elif hand == Pattern.Triple_1:
            pointed = 3
            auxiliary = [ 1 ]
        elif hand == Pattern.Triple_2:
            pointed = 3
            auxiliary = [ 2 ]
        elif hand == Pattern.Quadruple_1_1:
            pointed = 4
            auxiliary = [ 1, 1 ]
        elif hand == Pattern.Quadruple_2_2:
            pointed = 4
            auxiliary = [ 2, 2 ]
        elif hand == Pattern.Straight:
            pointed = 1
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards)
            else:
                straight = 5
                if len(handPiles) > straight:
                    straight = range(len(handPiles), straight, -1)
        elif hand == Pattern.Straight_x2:
            pointed = 2
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 2
            else:
                straight = 3
                s = len(handPiles)
                if s > straight:
                    straight = range(s, straight, -1)
        elif hand == Pattern.Straight_x3:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 3
            else:
                straight = 3
                s = len(handPiles)
                if s > straight:
                    straight = range(s, straight, -1)
        elif hand == Pattern.Straight_x3_n:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 4
                auxiliary = [ 1 ] * len(board.stack[-1].cards) / 4
            else:
                straight = 3
                s = int(math.ceil(len(handPiles) * (3 / 4)))
                if s > straight:
                    straight = range(s, straight, -1)
        elif hand == Pattern.Straight_x3_2n:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 5
                auxiliary = [ 2 ] * len(board.stack[-1].cards) / 5
            else:
                straight = 3
                s = int(math.ceil(len(handPiles) * (4 / 5)))
                if s > straight:
                    straight = range(s, straight, -1)

        def pick(possibilities, player, indices, auxiliary):
            ( _1, cards ) = player.pick(indices, auxiliary)
            score = 0 # TODO

            possibilities.append(( cards, score ))

        possibilities = [ ]
        for i in range(start, len(handPiles)):
            pile = handPiles[i]
            if pile.count < pointed:
                continue

            if straight == None:
                indices = [ pile.index ] * pointed

                pick(possibilities, player, indices, auxiliary)
            elif isinstance(straight, int):
                indices = [ ]
                for j in range(0, straight):
                    indices += [ pile.index + j ] * pointed

                pick(possibilities, player, indices, auxiliary)
            elif isinstance(straight, range):
                for k in straight:
                    indices = [ ]
                    for j in range(0, k):
                        indices += [ pile.index + j ] * pointed

                    pick(possibilities, player, indices, auxiliary)

        return possibilities

class Reader:
    def __init__(self, start = None, demand = None, turn = None):
        self.start = start or (lambda: Utils.read('Would you like to play now [y/n]: '))
        self.demand = demand or (lambda: Utils.read('What is your demonding [0/1/2/3]: '))
        self.turn = turn or (lambda w: Utils.read('What is ' + w + ' put: '))

class Writer:
    def __init__(self, bye = None, win = None, lose = None):
        self.splitter = (lambda: Utils.write('--------------------------------'))
        self.bye = bye or (lambda: Utils.write('Bye'))
        self.win = win or (lambda: Utils.write('Win'))
        self.lose = lose or (lambda: Utils.write('Lose'))

class Board:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

        self.deck = [ ]
        for i in range(4):
            for j in range(13):
                self.deck.append(Card(i + 1, j + 1))
        self.deck.append(Card(0, Points.Joker0))
        self.deck.append(Card(0, Points.Joker1))

        self.times = 1

        self.players = [ ]
        self.players.append(You(self.reader, self.writer))
        self.players.append(Cpu())
        self.players.append(Cpu())

        self.reserved = [ ]

        self.stack = [ Put() ]

        self.state = None # None for not started, 1 for won, -1 for lost, 0 for playing.
        self.lastWinner = None # None for literally none, numbers for winner's index.

    def clear(self):
        self.times = 1

        del self.players[:]
        self.players.append(You(self.reader, self.writer))
        self.players.append(Cpu())
        self.players.append(Cpu())

        del self.reserved[:]

        del self.stack[:]
        self.stack.append(Put())

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        for i in range(3):
            self.players[i].clear()

        n = 0
        for i in range(17):
            for j in range(3):
                self.players[j].take(self.deck[n])
                n += 1
        for i in range(3):
            self.players[i].sort()

        self.reserved.append(Card(self.deck[n].suit, self.deck[n].index))
        n += 1
        self.reserved.append(Card(self.deck[n].suit, self.deck[n].index))
        n += 1
        self.reserved.append(Card(self.deck[n].suit, self.deck[n].index))
        n += 1
        self.reserved.sort()

    def askStart(self):
        s = self.reader.start()
        if s == 'n':
            self.state = None
            self.writer.bye()

            yield False
        elif s == 'y':
            self.state = 0

            yield True
        else:
            yield True

    def askDemand(self):
        evaluated = [ ]
        for i in range(len(self.players)):
            p = self.players[i]
            handWithReserved = sum([ p.hand, self.reserved ], [ ])
            evaluated.append(( Card.evaluate(self, handWithReserved), i ))
        evaluated.sort(key = lambda e: -e[0])
        Utils.debug('Evaluated with reserved: ' + str(evaluated))

        indices = [ ]
        for i in range(len(self.players)):
            indices.append(i)

        while len(indices) > 1:
            m = 0
            n = 0

            for j in range(len(indices)):
                i = indices[j]
                p = self.players[i]
                while not p.demand(i, self, evaluated):
                    yield True
                print(('CPU' if p.isCpu else 'YOU') + '@' + str(i) + ' demanded ' + str(p.demanding))

                if p.demanding > m:
                    m = p.demanding
                    n = 1
                elif p.demanding == m:
                    n += 1
                if p.demanding == 3:
                    break

            for j in reversed(range(len(indices))):
                i = indices[j]
                if self.players[i].demanding < m:
                    del indices[j]

        p = self.players[indices[0]]
        p.isLandLord = True
        for c in self.reserved:
            p.take(c)
        p.sort()
        print('The land lord is: ' + ('CPU' if p.isCpu else 'YOU'))

        yield True

    def askTurns(self):
        indices = [ ]
        for i in range(len(self.players)):
            indices.append(i)
        for i in range(len(self.players)):
            p = self.players[i]
            if p.isLandLord:
                indices = Utils.shift(indices, i)

                break

        while True:
            for i in indices:
                while True:
                    p = self.players[i]
                    u = [ None, None ]
                    while not p.think(i, self, u):
                        yield True

                    hrt = self.checkPuttable(u)
                    if hrt != None and hrt[1] > 0:
                        Utils.debug('Put orders: ' + str(u[0]))
                        put = Put()
                        put.owner = i
                        put.hand = hrt[0]
                        for j in range(len(u[0])):
                            k = u[0][j]
                            c = u[1][j]
                            put.cards.append(Card(c.suit, c.index))
                            del p.hand[k]
                        self.stack.append(put)
                        self.times *= hrt[2]

                        yield True

                        break
                    else:
                        print('Invalid put orders: ' + str(u[0]) + (' of ' + str(hrt[1])) if hrt != None else '')

                        yield True

                if self.checkGameover():
                    break

            yield True

        yield False

    def checkPuttable(self, put):
        prev = self.stack[-1].cards
        ( hand, rel, times ) = Pattern.compare(put[1], prev)

        return ( hand, rel, times )

    def checkGameover(self):
        for i in range(len(self.players)):
            p = self.players[i]
            if len(p.hand) == 0:
                self.state = -1 if p.isCpu else 1
                self.lastWinner = i

                return True

        return False

    def play(self):
        while True:
            self.writer.splitter()

            board.output()

            if self.state == None:
                for y in self.askStart():
                    yield y
            elif self.state == 1:
                self.writer.win()

                for y in self.askStart():
                    yield y
            elif self.state == -1:
                self.writer.lose()

                for y in self.askStart():
                    yield y
            elif self.state == 0:
                ll = -1
                for i in range(len(self.players)):
                    if self.players[i].isLandLord:
                        ll = i

                        break

                if ll == -1:
                    for y in self.askDemand():
                        yield y
                else:
                    for y in self.askTurns():
                        self.writer.splitter()

                        board.output()

                        yield y
            else:
                raise Exception('Unknown state')

            yield True

    def output(self, players = True, stack = True, reserved = True):
        if reserved:
            print('[Reserved]')
            lst = [ ]
            for c in self.reserved:
                lst.append(str(c))
            print(lst)

        if stack:
            print('[Stack]')
            if len(self.stack) > 0:
                print(self.stack[-1].dump(), ':=', Pattern.Names[self.stack[-1].hand])

        if players:
            print('[Players]')
            for i in range(3):
                y = 'CPU' if self.players[i].isCpu else 'YOU'
                z = ' * ' if self.players[i].isLandLord else ' - '
                v = Card.evaluate(self, self.players[i].hand)
                msg = y + z + str(self.players[i].dump()) + ' := ' + str(v)
                if self.players[i].isCpu:
                    Utils.debug(msg)
                else:
                    print(msg)

# Variables.

board = Board(Reader(), Writer())

# Entries.

def __init__():
    pass

def __update__(delta):
    pass

def main():
    board.shuffle()
    board.deal()
    p = board.play()
    while next(p):
        pass

if __name__ == '__main__':
    main()
