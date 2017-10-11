from unittest import TestCase
import networkx as nx

from idleiss.universe import Universe

class UserTestCase(TestCase):

    def setUp(self):
        pass

    def test_generate_constellation_raises_error(self):
        uni = Universe(42, 5100, 340, 68, 1.35)
        with self.assertRaises(ValueError):
            constellation = uni.generate_constellation(0)
        with self.assertRaises(ValueError):
            constellation = uni.generate_constellation(1)

    def test_generate_constellation_2_systems(self):
        uni = Universe(42, 5100, 340, 68, 0)
        constellation = uni.generate_constellation(2)
        #uni.generate_networkx(uni.sys)
        graph = uni.generate_networkx(constellation)
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertEqual(nx.is_connected(graph), True)
        self.assertIs(constellation[0].connections[0], constellation[1])
        self.assertIs(constellation[1].connections[0], constellation[0])

    def test_generate_constellation_15_systems_connected(self):
        uni = Universe(42, 5100, 340, 68, 1.35)
        for x in range(5):
            constellation = uni.generate_constellation(15)
            #uni.generate_networkx(uni.sys)
            graph = uni.generate_networkx(constellation)
            self.assertEqual(graph.number_of_nodes(), 15)
            self.assertEqual(nx.is_connected(graph), True)

#from idleiss.universe import Universe
#uni = Universe(42, 5100, 340, 68, 1.35)
#uni.generate_constellation(15)
#uni.generate_wolfram_alpha_output(uni.sys)
#uni.generate_networkx(uni.sys)

#from idleiss.universe import Universe; uni = Universe(42, 5100, 340, 68, 1.74); uni.generate_constellation(15); uni.generate_networkx(uni.sys)

#uni.generate_constellation(15); uni.generate_networkx(uni.sys)