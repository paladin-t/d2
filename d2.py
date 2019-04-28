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
    print('Using CPython')

    from functools import reduce
elif Utils.isSkulpt:
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

    Kidding = 13
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

# Player.

class Player:
    def __init__(self):
        self.isCpu = False
        self.isLandLord = False

        self.hand = [ ]

        self.demanding = 0

        self.score = 100

    def clear(self):
        del self.hand[:]

        return self

    def add(self, card):
        self.hand.append(Card(card.suit, card.index))

        return self

    def remove(self, card):
        for i in range(len(self.hand)):
            c = self.hand[i]
            if c == card or (c.suit == card.suit and c.index == card.index):
                del self.hand[i]

                return self

        return self

    def sort(self):
        self.hand.sort()

        return self

    def demand(self, index, board, evaluated):
        return False

    def pick(self, indices, auxiliary = None, cond = None):
        def pick(index, orders, cards, hand):
            order = Pattern.indexOf(hand, None, index)
            card = Pattern.cardOf(hand, None, index)
            if order < 0 or card == None:
                return False
            if cond != None and not cond(card):
                return False

            orders.append(order)
            cards.append(card)
            hand[order] = None

            return True

        orders = [ ]
        cards = [ ]
        hand = self.hand[:]

        for index in indices:
            if not pick(index, orders, cards, hand):
                return ( None, None )

        if auxiliary != None:
            piles = Pile.of(hand, False)
            for aux in auxiliary:
                got = False
                for i in range(len(piles)):
                    pile = piles[i]
                    if pile.count >= 4 or pile.count < aux:
                        continue

                    for j in range(aux):
                        pick(pile.index, orders, cards, hand)
                    del piles[i]
                    got = True

                    break
                if not got:
                    return ( None, None )
            indices = indices[:]
            for i in range(len(auxiliary)):
                aux = auxiliary[i]
                v = chr(ord('a') + i)
                if aux > 1:
                    v += '*' + str(aux)
                indices.append(v)

        Utils.debug('Picking orders: ' + str(orders) + ' of indices ' + str(indices))

        return ( orders, cards )

    def search(self, index, board):
        valid = [ ]
        holding = Pile.of(self.hand, False)
        hand = board.stack[-1].hand

        if hand == Pattern.Invalid:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3_2n)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3_n)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x2)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Quadruple_2_2)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Quadruple_1_1)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple_2)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple_1)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Double)
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Single)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Single:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Single)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Double:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Double)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Triple:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Triple_1:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple_1)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Triple_2:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Triple_2)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Quadruple:
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Quadruple_1_1:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Quadruple_1_1)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Quadruple_2_2:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Quadruple_2_2)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Straight:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Straight_x2:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x2)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Straight_x3:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Straight_x3_n:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3_n)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
        elif hand == Pattern.Straight_x3_2n:
            valid += Pattern.pickSome(board, self, index, holding, Pattern.Straight_x3_2n)
            valid += Pattern.pickQuadruple(board, self, index, holding)
            valid += Pattern.pickJokers(board, self, index, holding)
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

class Pile:
    def __init__(self):
        self.index = 0
        self.count = 0

    def of(cards, ordered):
        p = None
        piles = [ ]
        for c in cards:
            if c == None:
                continue

            if p == None:
                p = Pile()
                piles.append(p)
            q = p.counts(c)
            if isinstance(q, Pile):
                p = q
                piles.append(p)
        if ordered:
            piles.sort()

        return piles

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
        if hand == Pattern.Invalid:
            return 0
        if hand >= Pattern.Quadruple:
            return 2

        return 1

    def valueOf(cards):
        values = list(map(lambda c: Points.valueOf(c.index), cards))

        return reduce(lambda l, r: l + r, values)

    def cardOf(cards, suit, index):
        if len(cards) == 0:
            return None

        for i in range(len(cards)):
            c = cards[i]
            if c == None:
                continue

            if suit == None:
                if c.index == index:
                    return c
            else:
                if c.suit == suit and c.index == index:
                    return c

        return None

    def indexOf(cards, suit, index):
        if len(cards) == 0:
            return -1

        for i in range(len(cards)):
            c = cards[i]
            if c == None:
                continue

            if suit == None:
                if c.index == index:
                    return i
            else:
                if c.suit == suit and c.index == index:
                    return i

        return -1

    def firstIndexOf(piles, pred, card):
        for i in range(len(piles)):
            pile = piles[i]
            if pred(pile, card):
                return i

        return -1

    def handOf(piles):
        hand = Pattern.Invalid

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
                if p.index == Points.Kidding:
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
            s = Pattern.expectStraight(piles)
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
                elif s == l / 2 and Pattern.expectHigh(piles[s:]) == l / 2:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x3_n
                elif s == l / 2 and Pattern.expectHigh_x2(piles[s:]) == l / 2:
                    if not joking(piles) and not kidding(piles):
                        hand = Pattern.Straight_x3_2n

        return ( hand, piles )

    def expectStraight(piles, count = None):
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

    def expectHigh(piles):
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

    def expectHigh_x2(piles):
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

    def compare(lpiles, rpiles):
        def compare(lhand, rhand, lpiles, rpiles):
            if lhand != rhand:
                if lhand == Pattern.Invalid:
                    return -1
                elif rhand == Pattern.Invalid:
                    return 1
                elif lhand == Pattern.Jokers:
                    return 1
                elif lhand == Pattern.Quadruple and rhand == Pattern.Quadruple:
                    pass
                elif lhand == Pattern.Quadruple and rhand != Pattern.Jokers:
                    return 1
                else:
                    return -1
            else:
                if len(lpiles) != len(rpiles):
                    return -1

                for i in range(len(lpiles)):
                    if lpiles[i].count != rpiles[i].count:
                        return -1

            li = lpiles[0].index
            ri = rpiles[0].index
            if li < ri:
                return -1
            elif li > ri:
                return 1
            else:
                return 0

        lhand = Pattern.handOf(lpiles)
        rhand = Pattern.handOf(rpiles)
        cm = compare(lhand, rhand, lpiles, rpiles)

        hand = lhand
        rel = cm
        times = Pattern.timesOf(lhand)

        return ( hand, rel, times )

    def pickQuadruple(board, player, index, holding):
        indexIsGeq = lambda p, c: p.index >= c.index

        start = 0
        if len(board.stack[-1].cards) > 0 and board.stack[-1].hand == Pattern.Quadruple:
            start = Pattern.firstIndexOf(holding, indexIsGeq, board.stack[-1].cards[0])
            if start == -1:
                start = 0

        possibilities = [ ]
        for i in range(start, len(holding)):
            pile = holding[i]
            if pile.count < 4:
                continue

            indices = [ pile.index ] * 4
            ( _1, cards ) = player.pick(indices)
            score = 0 # TODO

            possibilities.append(( cards, score ))

        return possibilities

    def pickJokers(board, player, index, holding):
        cards = [ ]
        index = Points.indexFromName(':)')
        card0 = Pattern.cardOf(player.hand, None, index)
        index = Points.indexFromName(':D')
        card1 = Pattern.cardOf(player.hand, None, index)
        if card0 != None and card1 != None:
            cards.append(card0)
            cards.append(card1)
        score = 0 # TODO

        return [ ( cards, score ) ]

    def pickSome(board, player, index, holding, hand):
        if hand == Pattern.Quadruple:
            return Pattern.pickQuadruple(board, player, index, holding)
        elif hand == Pattern.Jokers:
            return Pattern.pickJokers(board, player, index, holding)

        indexIsGeq = lambda p, c: p.index >= c.index
        indexIsAny = lambda _1, _2: True

        start = 0
        if len(board.stack[-1].cards) > 0:
            indexIs = indexIsGeq if board.stack[-1].hand == hand else indexIsAny
            start = Pattern.firstIndexOf(holding, indexIs, board.stack[-1].cards[0])
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
                if len(holding) > straight:
                    straight = range(len(holding), straight - 1, -1)
        elif hand == Pattern.Straight_x2:
            pointed = 2
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 2
            else:
                straight = 3
                s = len(holding)
                if s > straight:
                    straight = range(s, straight - 1, -1)
        elif hand == Pattern.Straight_x3:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 3
            else:
                straight = 3
                s = len(holding)
                if s > straight:
                    straight = range(s, straight - 1, -1)
        elif hand == Pattern.Straight_x3_n:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 4
                auxiliary = [ 1 ] * len(board.stack[-1].cards) / 4
            else:
                straight = 3
                s = int(math.ceil(len(holding) * (3 / 4)))
                if s > straight:
                    straight = range(s, straight - 1, -1)
        elif hand == Pattern.Straight_x3_2n:
            pointed = 3
            if board.stack[-1].hand == hand:
                straight = len(board.stack[-1].cards) / 5
                auxiliary = [ 2 ] * len(board.stack[-1].cards) / 5
            else:
                straight = 3
                s = int(math.ceil(len(holding) * (4 / 5)))
                if s > straight:
                    straight = range(s, straight - 1, -1)

        def pick(possibilities, player, indices, auxiliary):
            cond = lambda c: c.index != Points.Kidding and c.index != Points.Joker0 and c.index != Points.Joker1
            ( _1, cards ) = player.pick(indices, auxiliary, cond)
            score = 0 # TODO

            possibilities.append(( cards, score ))

        possibilities = [ ]
        for i in range(start, len(holding)):
            pile = holding[i]
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

class Put:
    Separator = ' '

    def __init__(self):
        self.owner = None
        self.hand = Pattern.Invalid
        self.cards = [ ]
        self.piles = None

    def piles(self):
        if self.piles == None:
            self.piles = Pile.of(self.cards)

        return self.piles

    def dump(self):
        ret = [ ]
        for c in self.cards:
            ret.append(str(c))

        return ret

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
                self.players[j].add(self.deck[n])
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

        assert(n == len(self.deck)), 'Impossible'

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
            handAndReserved = p.hand + self.reserved
            evaluated.append(( Pattern.valueOf(handAndReserved), i ))
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
            p.add(c)
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
                            p.remove(c)
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
        curr = Pile.of(put[1])
        prev = self.stack[-1].piles()
        ( hand, rel, times ) = Pattern.compare(curr, prev)

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
                v = Pattern.valueOf(self.players[i].hand)
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
