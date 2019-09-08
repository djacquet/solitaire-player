import datetime
import sys
import unittest

import solvers.tripeaks as tp

ALL_CARDS = (
    'Ac', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc',
    'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd',
    'Ah', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh',
    'As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks'
)


class TestCard(unittest.TestCase):
    def test_card_ranks(self):
        for card in ALL_CARDS:
            self.assertEqual(card[0], tp.card_rank(card))

    def test_is_one_rank_apart(self):
        def expected(card1, card2):
            rank1, rank2 = card1[0], card2[0]
            return rank2 in {
                'A': 'K2',
                '2': 'A3',
                '3': '24',
                '4': '35',
                '5': '46',
                '6': '57',
                '7': '68',
                '8': '79',
                '9': '8T',
                'T': '9J',
                'J': 'TQ',
                'Q': 'JK',
                'K': 'QA',
            }[rank1]

        for card1 in ALL_CARDS:
            for card2 in ALL_CARDS:
                self.assertEqual(expected(card1, card2), tp.is_one_rank_apart(card1, card2))


class TestDeckValidators(unittest.TestCase):
    def test_missing_cards(self):
        self.assertEqual(0, len(tp.missing_cards(ALL_CARDS)))
        self.assertEqual(['Ac'], tp.missing_cards(ALL_CARDS[1:]))

    def test_duplicate_cards(self):
        self.assertEqual(0, len(tp.duplicate_cards(ALL_CARDS)))
        self.assertEqual(['Ac', 'Ac'], tp.duplicate_cards(ALL_CARDS + ('Ac',)))
        self.assertEqual(['Ac', 'Ac', 'Ac'], tp.duplicate_cards(ALL_CARDS + ('Ac', 'Ac')))

    def test_malformed_cards(self):
        self.assertEqual(0, len(tp.malformed_cards(ALL_CARDS)))
        input = ['7S', 'ks', 'KS', 'kS', None, '', 0, 'Ks']
        expected = ['7S', 'ks', 'KS', 'kS', None, '', 0]
        self.assertEqual(expected, tp.malformed_cards(input))

    def test_is_standard_deck(self):
        self.assertTrue(tp.is_standard_deck(ALL_CARDS))
        self.assertFalse(tp.is_standard_deck(ALL_CARDS[1:]))
        self.assertFalse(tp.is_standard_deck([]))


class TestState(unittest.TestCase):
    def setUp(self):
        self.state = tp.State.initial_state(ALL_CARDS)

    def tearDown(self):
        del self.state

    def test_initial_state(self):
        self.assertEqual(tuple(ALL_CARDS[:28]), self.state.tableau)
        self.assertEqual(tuple(ALL_CARDS[29:]), self.state.stock_pile)
        self.assertEqual(ALL_CARDS[28], self.state.waste_card)

    def test_initial_state_nonstandard_deck(self):
        with self.assertRaises(ValueError):
            tp.State.initial_state(ALL_CARDS[1:])

    def test_face_up(self):
        self.assertEqual([False] * 18 + [True] * 10, [self.state.is_face_up(i) for i in range(28)])

    def test_face_up_with_missing_card(self):
        tableau = list(self.state.tableau)
        waste = self.state.tableau[23]
        tableau[22] = None
        tableau[23] = None
        state = tp.State(tuple(tableau), self.state.stock_pile, waste)
        self.assertTrue(state.is_face_up(13))
        self.assertFalse(state.is_face_up(22))
        self.assertFalse(state.is_face_up(23))

    def test_can_be_moved(self):
        waste_card = self.state.waste_card

        for card in self.state.tableau:
            self.assertEqual(tp.is_one_rank_apart(card, waste_card), self.state.can_be_moved(card))

        stock_card = self.state.stock_pile[0]
        self.assertEqual(tp.is_one_rank_apart(stock_card, waste_card), self.state.can_be_moved(stock_card))

    def test_is_tableau_empty(self):
        self.assertFalse(self.state.is_tableau_empty())
        empty_state = tp.State((None,) * 28, self.state.stock_pile, self.state.waste_card)
        self.assertTrue(empty_state.is_tableau_empty())

    def test_successors(self):
        expected = {
            tp.State(self.state.tableau[:-1] + (None,), self.state.stock_pile, self.state.tableau[-1]),
            tp.State(self.state.tableau, self.state.stock_pile[1:], self.state.stock_pile[0]),
        }
        self.assertEqual(expected, set(self.state.successors()))


@unittest.skip('Full solver tests that are too slow to run during development')
class TestSolver(unittest.TestCase):
    def test_all_cards_solution(self):
        # the shortest solution is removing one tableau card after another
        self.assertEqual(list(reversed(ALL_CARDS[:28])), tp.solve(ALL_CARDS))

    def test_tosunkaya_impossible_game(self):
        # reported as impossible by tosunkaya on github
        deck_string = """      Kc          9d          7s
                             7h  6s      2c  Kd      9c  2s
                           3d  Ah  6d  6c  Ad  As  7c  Js  7d
                         Jd  Td  Qc  2h  4s  8d  Th  4h  Qd  5c
                         3s
                         Jh Qs 2d 5d Ts 6h Qh Ac 8c Tc Jc Ks 8s 8h Kh 4c 3h 9h 3c 9s 4d 5h 5s"""
        deck = tuple(deck_string.split())
        self.assertTrue(tp.is_standard_deck(deck))
        self.assertEqual([], tp.solve(deck))


class Test1500ShuffledDecks(unittest.TestCase):
    @staticmethod
    def is_playable(deck, solution):
        """Return true if the solution is playable.

        If there isn't a solution, return true."""
        if not solution:
            return True
        tableau = list(deck[:28])
        # so you can append/pop at the end of the list
        waste_pile = list(deck[28:29])
        stock_pile = list(reversed(deck[29:]))
        for card in solution:
            if stock_pile and (card == stock_pile[-1]):
                stock_pile.pop()
            else:
                if not tp.is_one_rank_apart(card, waste_pile[-1]):
                    return False
                try:
                    tableau[tableau.index(card)] = None
                except ValueError:
                    return False
            waste_pile.append(card)
        return all([card is None for card in tableau])

    def _get_solution_results(self, deck_string):
        deck = tuple(deck_string.split())
        self.assertTrue(tp.is_standard_deck(deck))
        start = datetime.datetime.utcnow().timestamp()
        solution = tp.solve(deck)
        total = datetime.datetime.utcnow().timestamp() - start
        return tuple([deck, solution, total, Test1500ShuffledDecks.is_playable(deck, solution)])

    @unittest.skip('An extremely long test running the solver on 1500 decks')
    def test_all_shuffled_decks(self):
        # make sure the working directory is the pysolvers directory
        with open('../src/test/resources/random-decks.txt') as f:
            for deck_string in f:
                test_results = self._get_solution_results(deck_string)
                print(f'{test_results}')
                sys.stdout.flush()