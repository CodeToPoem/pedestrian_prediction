from unittest import TestCase
import numpy as np
from numpy import testing as t

from mdp import GridWorldMDP
from value_iter import forwards_value_iter, backwards_value_iter, _calc_max_update, \
        dijkstra

ni = float('-inf')

class TestUtilities(TestCase):
    def test_calc_max_update(self):
        t.assert_allclose(0, _calc_max_update(np.array([ni, ni]), np.array([ni, ni])))
        t.assert_allclose(1, _calc_max_update(np.array([0, ni]), np.array([-1, ni])))
        t.assert_allclose(np.inf, _calc_max_update(np.array([0, 5]), np.array([-1, ni])))
        t.assert_allclose(2,
                _calc_max_update(np.array([1, 0, ni, 7]), np.array([1.1, 2, ni, 6.5])))

class TestBackwardsValueIter(TestCase):
    def test_initial(self):
        g = GridWorldMDP(3, 1, {(0, 0): -1, (1, 0): 3})
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=0), [0, ni, ni])
        t.assert_allclose(backwards_value_iter(g, 1, max_iters=0), [ni, 0, ni])
        t.assert_allclose(backwards_value_iter(g, 2, max_iters=0), [ni, ni, 0])

    def test_easy_no_rewards(self):
        g = GridWorldMDP(3, 1, {})
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=0), [0, ni, ni])
        t.assert_allclose(backwards_value_iter(g, 1, max_iters=0), [ni, 0, ni])
        t.assert_allclose(backwards_value_iter(g, 2, max_iters=0), [ni, ni, 0])

        t.assert_allclose(backwards_value_iter(g, 0, max_iters=1), [0, 0, ni])
        t.assert_allclose(backwards_value_iter(g, 1, max_iters=1), [0, 0, 0])
        t.assert_allclose(backwards_value_iter(g, 2, max_iters=1), [ni, 0, 0])

        t.assert_allclose(backwards_value_iter(g, 0, max_iters=2), [0, 0, 0])
        t.assert_allclose(backwards_value_iter(g, 1, max_iters=2), [0, 0, 0])
        t.assert_allclose(backwards_value_iter(g, 2, max_iters=2), [0, 0, 0])

        t.assert_allclose(backwards_value_iter(g, 0, max_iters=3), [0, np.log(2), 0])
        t.assert_allclose(backwards_value_iter(g, 1, max_iters=3), [0, 0, 0])
        t.assert_allclose(backwards_value_iter(g, 2, max_iters=3), [0, np.log(2), 0])

    def test_easy_neg_one_reward_plus_special(self):
        g = GridWorldMDP(3, 1, {(2,0): -10}, default_reward=-1)
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=0), [0, ni, ni])
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=1), [0, -1, ni])
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=2), [0, -1, -11])
        V_3 = [0, np.log(np.exp(-1) + np.exp(-12)), -11]
        t.assert_allclose(backwards_value_iter(g, 0, max_iters=3), V_3)

class TestForwardsValueIter(TestCase):
    def test_forward_backwards_consistency(self):
        g = GridWorldMDP(3, 3, {(2,0): -30, (1,1): -40}, default_reward=-10)
        V_b = backwards_value_iter(g, 0)
        for s in range(g.S):
            V_f = forwards_value_iter(g, s)
            t.assert_allclose(V_f[0], V_b[s])

class TestDijkstra(TestCase):
    def test_simple(self):
        g = GridWorldMDP(3, 1, {(2,0): -9}, default_reward=-1)
        t.assert_allclose([0, -1, -10], dijkstra(g, 0))
        t.assert_allclose([-1, 0, -9], dijkstra(g, 1))
        t.assert_allclose([-2, -1, 0], dijkstra(g, 2))
    def test_2d(self):
        g = GridWorldMDP(3, 3, {(2,0): -3, (1,1): -4}, default_reward=-1)
        expected = [-3, -2, -2,
                    -2, -4, -1,
                    -4, -1, 0]
        t.assert_allclose(expected, dijkstra(g, g.coor_to_state(2,2)))
