#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A Python implementaton of the Dou Dizhu deck game
# GitHub: https://github.com/paladin-t/d2
# Copyright 2019 Tony
#
# License: GPLv3
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    def nameToIndex(n):
        n = n.upper()
        if n == ':)':
            return 13 + 1
        elif n == ':D':
            return 14 + 1

        if not n in Points.Names:
            return -1

        i = Points.Names.index(n)
        if i >= 0:
            i += 1

        return i

class Card:
    def namesOf(cards):
        if cards == None or len(cards) == 0:
            return '[]'

        msg = '['
        for i in range(len(cards)):
            c = cards[i]
            msg += str(c)
            if i == len(cards) - 1:
                msg += ']'
            else:
                msg += ', '

        return msg

    def __init__(self, s, i):
        self.suit = s
        self.index = i # Starts from 1.

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

        self.wait = None

    def clear(self):
        self.isLandLord = False

        del self.hand[:]

        self.demanding = 0

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
        def pick(index, orders, cards, hand, cond):
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
            if not pick(index, orders, cards, hand, cond):
                return ( None, None, None )

        if auxiliary != None:
            piles = Pile.of(hand, False)
            for aux in auxiliary:
                got = False
                for i in range(len(piles)):
                    pile = piles[i]
                    if pile.count >= 4 or pile.count < aux:
                        continue

                    for j in range(aux):
                        pick(pile.index, orders, cards, hand, None)
                    del piles[i]
                    got = True

                    break
                if not got:
                    return ( None, None, None )
            indices = indices[:]
            for i in range(len(auxiliary)):
                aux = auxiliary[i]
                v = chr(ord('a') + i)
                if aux > 1:
                    v += '*' + str(aux)
                indices.append(v)

        piles = Pile.of(cards)
        cards.sort(key = lambda card: Pattern.firstIndexOf(piles, lambda p, c: p.index == c.index, card))

        msg = 'Picking cards: ' + Card.namesOf(cards) + ' of indices ' + str(indices)
        Utils.debug(msg)

        hand = list(filter(lambda c: c != None, hand))

        return ( orders, cards, hand )

    def search(self, index, board, hand):
        valid = [ ]
        holding = Pile.of(self.hand, False)

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
        valid.sort(key = lambda v: v[2])

        return valid

    def think(self, index, board, put):
        n = board.reader.turn(('CPU\'s' if self.isCpu else 'YOUr') + '@' + str(index))
        if n == None:
            return True

        n = list(filter(lambda s: len(s) > 0, n.split(' ')))

        indices = list(map(lambda name: Points.nameToIndex(name), n))
        if -1 in indices:
            return False

        ( orders, cards, _1 ) = self.pick(indices)

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
        if self.wait != None and not self.wait.demanding():
            return False

        d = [ n for n, v in enumerate(evaluated) if v[1] == index ][0]
        d += 1
        if d == 2:
            d = 3
        self.demanding = d

        return True

    def think(self, index, board, put):
        if self.wait != None and not self.wait.thinking():
            return False

        handed = board.stack[-1].handed(index)
        whose = None if board.stack[-1].owner == None else board.players[board.stack[-1].owner]
        friendly = not self.isLandLord and (whose != None and not whose.isLandLord)
        hyped = len(board.stack[-1].cards) >= 4 or (whose != None and len(whose.hand) <= 2)
        mine = board.stack[-1].owner == index

        if friendly and hyped and not mine:
            return True

        valid = self.search(index, board, handed)
        for v in valid:
            cards = v[1]
            score = v[2]
            msg = 'Considering cards: ' + Card.namesOf(cards) + ' with score ' + str(score)
            Utils.debug(msg)

        if len(valid) == 0:
            return True

        v = valid[0]
        orders = v[0]
        cards = v[1]

        put[0] = orders
        put[1] = cards

        return True

class You(Player):
    def __init__(self):
        Player.__init__(self)

    def demand(self, index, board, evaluated):
        if self.wait != None and not self.wait.demanding():
            return False

        d = board.reader.demand()
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
        if self.wait != None and not self.wait.thinking():
            return False

        handed = board.stack[-1].handed(index)
        mine = board.stack[-1].owner == index

        ret = Player.think(self, index, board, put)
        if ret and put[0] == None and put[1] == None:
            if handed == Pattern.Invalid or mine:
                return False

        return ret

# Board.

class Pile:
    def of(cards, ordered = True):
        cards = list(filter(lambda c: c != None, cards[:]))
        cards.sort()

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
        if hand == Pattern.Invalid:
            return 0
        if hand >= Pattern.Quadruple:
            return 2

        return 1

    def valueOf(cards):
        values = list(map(lambda c: Points.valueOf(c.index), cards))

        return reduce(lambda l, r: l + r, values)

    def priorityOf(cards, rest):
        if cards == None:
            return None

        piles = Pile.of(cards)

        hand = Pattern.handOf(piles)

        value = Pattern.valueOf(cards)

        kidding = Pattern.firstIndexOf(piles, lambda p, _1: p.index == Points.Kidding, None)
        kidding = 0 if kidding == -1 else (piles[kidding].count * Points.valueOf(Points.Kidding))

        post = len(rest) / 17 * 20000

        total = (hand + value + kidding) + post

        return total

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
                if not Pattern.joking(piles):
                    hand = Pattern.Triple_1
            elif match(piles, count, ( 3, 2 )):
                if not Pattern.joking(piles):
                    hand = Pattern.Triple_2
        elif l == 3:
            if match(piles, count, ( 4, 1, 1 )):
                if not Pattern.joking(piles):
                    hand = Pattern.Quadruple_1_1
            elif match(piles, count, ( 4, 2, 2 )):
                if not Pattern.joking(piles):
                    hand = Pattern.Quadruple_2_2
        if hand == Pattern.Invalid and l >= 2:
            s = Pattern.expectStraight(piles)
            if piles[0].count == 1:
                if s == l and l >= 5:
                    if not Pattern.joking(piles) and not Pattern.kidding(piles):
                        hand = Pattern.Straight
            elif piles[0].count == 2:
                if s == l and l >= 3:
                    if not Pattern.joking(piles) and not Pattern.kidding(piles):
                        hand = Pattern.Straight_x2
            elif piles[0].count == 3:
                if s == l:
                    if not Pattern.joking(piles) and not Pattern.kidding(piles):
                        hand = Pattern.Straight_x3
                elif s == l / 2 and Pattern.expectHigh(piles[s:]) == l / 2:
                    if not Pattern.joking(piles) and not Pattern.kidding(piles):
                        hand = Pattern.Straight_x3_n
                elif s == l / 2 and Pattern.expectHigh_x2(piles[s:]) == l / 2:
                    if not Pattern.joking(piles) and not Pattern.kidding(piles):
                        hand = Pattern.Straight_x3_2n

        return hand

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

        n = 1
        for p in piles:
            if p.count == n:
                ret += 1

        return ret

    def expectHigh_x2(piles):
        ret = 0
        if len(piles) == 0:
            return ret

        n = 2
        for p in piles:
            if p.count == n:
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

        handed = board.stack[-1].handed(index)

        start = 0
        if len(board.stack[-1].cards) > 0 and handed == Pattern.Quadruple:
            start = Pattern.firstIndexOf(holding, indexIsGeq, board.stack[-1].cards[0])
            if start == -1:
                start = 0

        possibilities = [ ]
        for i in range(start, len(holding)):
            pile = holding[i]
            if pile.count < 4:
                continue

            indices = [ pile.index ] * 4
            ( orders, cards, rest ) = player.pick(indices)
            score = Pattern.priorityOf(cards, rest)

            if orders != None and cards != None and score != None:
                possibilities.append(( orders, cards, score ))

        return possibilities

    def pickJokers(board, player, index, holding):
        cards = None
        orders = None
        index = Points.nameToIndex(':)')
        order0 = Pattern.indexOf(player.hand, None, index)
        card0 = Pattern.cardOf(player.hand, None, index)
        index = Points.nameToIndex(':D')
        order1 = Pattern.indexOf(player.hand, None, index)
        card1 = Pattern.cardOf(player.hand, None, index)
        if card0 != None and card1 != None:
            cards = [ card0, card1 ]
        if order0 != None and order1 != None:
            orders = [ order0, order1 ]
        rest = list(filter(lambda c: c != card0 and c != card1, player.hand[:]))
        score = Pattern.priorityOf(cards, rest)

        if orders != None and cards != None and score != None:
            return [ ( orders, cards, score ) ]

        return [ ]

    def pickSome(board, player, index, holding, hand):
        if hand == Pattern.Quadruple:
            return Pattern.pickQuadruple(board, player, index, holding)
        elif hand == Pattern.Jokers:
            return Pattern.pickJokers(board, player, index, holding)

        indexIsGt = lambda p, c: p.index > c.index
        indexIsAny = lambda _1, _2: True

        possibilities = [ ]

        handed = board.stack[-1].handed(index)

        start = 0
        if len(board.stack[-1].cards) > 0:
            indexIs = indexIsGt if handed == hand else indexIsAny
            start = Pattern.firstIndexOf(holding, indexIs, board.stack[-1].cards[0])
            if start < 0:
                Utils.debug('No key card greater than put')

                return possibilities

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
            if handed == hand:
                straight = len(board.stack[-1].cards)
            else:
                straight = 5
                if len(holding) > straight:
                    straight = range(len(holding), straight - 1, -1)
        elif hand == Pattern.Straight_x2:
            pointed = 2
            if handed == hand:
                straight = len(board.stack[-1].cards) / 2
            else:
                straight = 3
                s = len(holding)
                if s > straight:
                    straight = range(s, straight - 1, -1)
        elif hand == Pattern.Straight_x3:
            pointed = 3
            if handed == hand:
                straight = len(board.stack[-1].cards) / 3
            else:
                straight = 2
                s = len(holding)
                if s > straight:
                    straight = range(s, straight - 1, -1)
        elif hand == Pattern.Straight_x3_n:
            pointed = 3
            if handed == hand:
                straight = len(board.stack[-1].cards) / 4
                auxiliary = [ 1 ] * (len(board.stack[-1].cards) / 4)
            else:
                straight = 2
                s = int(math.ceil(len(holding) * (3 / 4)))
                if s > straight:
                    straight = range(s, straight - 1, -1)
                else:
                    auxiliary = [ 1 ] * straight
        elif hand == Pattern.Straight_x3_2n:
            pointed = 3
            if handed == hand:
                straight = len(board.stack[-1].cards) / 5
                auxiliary = [ 2 ] * (len(board.stack[-1].cards) / 5)
            else:
                straight = 2
                s = int(math.ceil(len(holding) * (4 / 5)))
                if s > straight:
                    straight = range(s, straight - 1, -1)
                else:
                    auxiliary = [ 2 ] * straight

        def pick(possibilities, player, indices, auxiliary, straight):
            cond = None
            if straight != None:
                cond = lambda c: c.index != Points.Kidding and c.index != Points.Joker0 and c.index != Points.Joker1
            ( orders, cards, rest ) = player.pick(indices, auxiliary, cond)
            score = Pattern.priorityOf(cards, rest)

            if orders != None and cards != None and score != None:
                possibilities.append(( orders, cards, score ))

        for i in range(start, len(holding)):
            pile = holding[i]
            if pile.count < pointed:
                continue

            if straight == None:
                indices = [ pile.index ] * pointed

                pick(possibilities, player, indices, auxiliary, straight)
            elif isinstance(straight, int):
                indices = [ ]
                for j in range(0, straight):
                    indices += [ pile.index + j ] * pointed

                pick(possibilities, player, indices, auxiliary, straight)
            elif isinstance(straight, list) or isinstance(straight, range):
                for k in straight:
                    indices = [ ]
                    for j in range(0, k):
                        indices += [ pile.index + j ] * pointed

                    was = auxiliary
                    if hand == Pattern.Straight_x3_n:
                        auxiliary = [ 1 ] * k
                    elif hand == Pattern.Straight_x3_2n:
                        auxiliary = [ 2 ] * k

                    pick(possibilities, player, indices, auxiliary, straight)

                    auxiliary = was

        return possibilities

class Put:
    Separator = ' '

    def __init__(self):
        self.owner = None
        self.hand = Pattern.Invalid
        self.cards = [ ]
        self.piles = None

    def piled(self):
        if self.piles == None:
            self.piles = Pile.of(self.cards)

        return self.piles

    def handed(self, index):
        hand = self.hand
        if hand != Pattern.Invalid and self.owner == index:
            hand = Pattern.Invalid

        return hand

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
    Over = 0
    Playing = 1
    Idle = 2

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
        self.players.append(You())
        self.players.append(Cpu())
        self.players.append(Cpu())

        self.reserved = [ ]

        self.stack = [ Put() ]

        self.state = None # None for not started, 1 for won, -1 for lost, 0 for playing.
        self.lastWinner = None # None for literally none, numbers for winner's index.

    def clear(self):
        self.times = 1

        for p in self.players:
            p.clear()

        del self.reserved[:]

        del self.stack[:]
        self.stack.append(Put())

        self.state = None

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

        while self.state == 0:
            for i in indices:
                while True:
                    p = self.players[i]
                    u = [ None, None ]
                    while not p.think(i, self, u):
                        yield Board.Idle

                    hrt = self.checkPuttable(u, i)
                    possible = hrt != None and hrt[1] > 0
                    done = u[0] != None and u[1] != None
                    if possible and done:
                        print(('CPU' if p.isCpu else 'YOU') + '@' + str(i) + ' put cards: ' + Card.namesOf(u[1]))
                        put = Put()
                        put.owner = i
                        put.hand = hrt[0]
                        for j in range(len(u[0])):
                            c = u[1][j]
                            put.cards.append(Card(c.suit, c.index))
                            p.remove(c)
                        self.stack.append(put)
                        self.times *= hrt[2]

                        yield Board.Playing

                        break
                    elif possible and not done:
                        print(('CPU' if p.isCpu else 'YOU') + '@' + str(i) + ' put cards: ' + Card.namesOf(u[1]))

                        yield Board.Playing

                        break
                    else:
                        print('Invalid put cards: ' + Card.namesOf(u[1]) + (' with relation ' + str(hrt[1])) if hrt != None else '')

                        yield Board.Playing

                if self.checkGameover():
                    break

        yield Board.Over

    def checkPuttable(self, put, index):
        if put[0] == None and put[1] == None:
            return ( Pattern.Invalid, 1, 1 )

        curr = Pile.of(put[1])
        prev = self.stack[-1].piled()
        ( hand, rel, times ) = Pattern.compare(curr, prev)

        mine = board.stack[-1].owner == index
        if mine:
            rel = 1

        return ( hand, rel, times )

    def checkGameover(self):
        for i in range(len(self.players)):
            p = self.players[i]
            if len(p.hand) > 0:
                continue

            self.lastWinner = i

            if p.isLandLord:
                self.state = -1 if p.isCpu else 1

                return True
            else:
                if not p.isCpu:
                    self.state = 1

                    return True

                for j in range(len(self.players)):
                    if i == j:
                        continue

                    q = self.players[j]
                    if q.isLandLord:
                        continue

                    self.state = -1 if q.isCpu else 1

                    break

                return True

        return False

    def play(self):
        while True:
            if self.state == None:
                self.writer.splitter()

                board.output()

                for y in self.askStart():
                    yield y
            elif self.state == 1:
                self.writer.splitter()

                self.writer.win()

                yield False
            elif self.state == -1:
                self.writer.splitter()

                self.writer.lose()

                yield False
            elif self.state == 0:
                self.writer.splitter()

                board.output()

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
                        if y == Board.Over:
                            factor = 10

                            winner = self.players[self.lastWinner]
                            if winner.isLandLord:
                                loser = list(filter(lambda p: p != winner, self.players))
                                for p in loser:
                                    p.score -= self.times * factor
                                winner.score += (self.times * factor) * 2
                            else:
                                for i in range(len(self.players)):
                                    p = self.players[i]
                                    if p.isLandLord:
                                        p.score -= (self.times * factor) * 2
                                    else:
                                        p.score += self.times * factor

                            yield True

                            break
                        elif y == Board.Playing:
                            self.writer.splitter()

                            board.output()

                            yield True
                        elif y == Board.Idle:
                            yield True
            else:
                raise Exception('Unknown state')

            yield True

    def output(self, players = True, stack = True, reserved = True):
        if reserved:
            print('[Reserved]' + ' - x' + str(self.times) + ' times')
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
                p = self.players[i]
                x = 'CPU' if p.isCpu else 'YOU'
                y = '[' + str(p.score) + ']'
                z = ' * ' if p.isLandLord else ' - '
                v = 0 if len(p.hand) == 0 else Pattern.valueOf(p.hand)
                msg = x + y + z + str(p.dump()) + ' := ' + str(v)
                if p.isCpu:
                    Utils.debug(msg)
                else:
                    print(msg)

class Instantly:
    def __init__(self):
        pass

    def demanding(self):
        return True

    def thinking(self):
        return True

# Variables.

board = Board(Reader(), Writer())

# Entries.

if Utils.isSkulpt:
    #import game

    def __init__():
        pass

    def __update__(delta):
        pass

def main():
    while True:
        for p in board.players:
            p.wait = Instantly()

        board.shuffle()
        board.deal()

        p = board.play()
        while next(p):
            pass

        board.clear()

if __name__ == '__main__':
    if Utils.isCPython:
        main()
