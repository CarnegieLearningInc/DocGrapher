
import unittest

from create_docgraph import *


class ColorizationTests(unittest.TestCase):

    def create_subgraph(self, nodes):
        subgraph = {}
        for node in nodes:
            subgraph[node.name] = node
        return subgraph

    def setUp(self):
        # subgraph 1
        # root parent with two children
        self.g1n1 = DocNode("g1n1", "/g1n1")
        self.g1n2 = DocNode("g1n2", "/g1n2", ["g1n1"])
        self.g1n3 = DocNode("g1n3", "/g1n3", ["g1n1"])
        self.g1_nodes = [self.g1n1, self.g1n2, self.g1n3]
        self.g1 = self.create_subgraph(self.g1_nodes)

        # subgraph 2
        # one child, two parents
        self.g2n1 = DocNode("g2n1", "/g2n1")
        self.g2n2 = DocNode("g2n2", "/g2n2")
        self.g2n3 = DocNode("g2n3", "/g2n3", ["g2n1", "g2n2"])
        self.g2_nodes = [self.g2n1, self.g2n2, self.g2n3]
        self.g2 = self.create_subgraph(self.g2_nodes)

        # subgraph 3
        # substantially more complex - loops & everything
        self.g3n1 = DocNode("g3n1", "/g3n1")
        self.g3n2 = DocNode("g3n2", "/g3n2", ["g3n1", "g3n5"])
        self.g3n3 = DocNode("g3n3", "/g3n3", ["g3n1"])
        self.g3n4 = DocNode("g3n4", "/g3n4", ["g3n2", "g3n3"])
        self.g3n5 = DocNode("g3n5", "/g3n5", ["g3n4"])
        self.g3n6 = DocNode("g3n6", "/g3n6", ["g3n5"])
        self.g3_nodes = [self.g3n1, self.g3n2, self.g3n3,
                         self.g3n4, self.g3n5, self.g3n6]
        self.g3 = self.create_subgraph(self.g3_nodes)

        self.assigner = ColorAssigner()

    def tearDown(self):
        pass

    def test_g1n1_path(self):
        color, path = self.assigner.get_path_to_colored_node(self.g1n1,
                                                             self.g1)

        self.assertIsNone(color)
        self.assertEqual(path, [self.g1n1])

        self.assertTrue(self.g1n1.seen)
        self.assertFalse(self.g1n2.seen)
        self.assertFalse(self.g1n3.seen)

    def test_g1n2_path(self):
        color, path = self.assigner.get_path_to_colored_node(self.g1n2,
                                                             self.g1)

        self.assertIsNone(color)
        self.assertEqual(path, [self.g1n2, self.g1n1])

        self.assertTrue(self.g1n1.seen)
        self.assertTrue(self.g1n2.seen)
        self.assertFalse(self.g1n3.seen)

    def test_g1n3_path_withN1Colored(self):
        self.g1n1.color = 'blue'

        color, path = self.assigner.get_path_to_colored_node(self.g1n3,
                                                             self.g1)

        self.assertEqual(color, 'blue')
        self.assertEqual(path, [self.g1n3, self.g1n1])

        self.assertTrue(self.g1n1.seen)
        self.assertFalse(self.g1n2.seen)
        self.assertTrue(self.g1n3.seen)

    def test_g1_colorization(self):
        self.assigner.assign_colors(self.g1)

        thecolor = self.g1n1.color
        self.assertIsNotNone(thecolor)
        for node in self.g1_nodes:
            self.assertEqual(node.color, thecolor)
            self.assertTrue(node.seen)

    def test_g2_colorization(self):
        self.assigner.assign_colors(self.g2)

        thecolor = self.g2n1.color
        self.assertIsNotNone(thecolor)
        for node in self.g2_nodes:
            self.assertEqual(node.color, thecolor)
            self.assertTrue(node.seen)

    def test_g3_colorization(self):
        self.assigner.assign_colors(self.g3)

        thecolor = self.g3n1.color
        self.assertIsNotNone(thecolor)
        for node in self.g3_nodes:
            self.assertEqual(node.color, thecolor)
            self.assertTrue(node.seen)











