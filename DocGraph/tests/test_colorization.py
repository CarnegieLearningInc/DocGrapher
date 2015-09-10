
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
        self.g1n2 = DocNode("g1n2", "/g1n2")
        self.g1n3 = DocNode("g1n3", "/g1n3")

        self.g1n2.add_edge("g1n1", DocNode.EDGE_TYPE_PARENT)
        self.g1n3.add_edge("g1n1", DocNode.EDGE_TYPE_PARENT)

        self.g1_nodes = [self.g1n1, self.g1n2, self.g1n3]
        self.g1 = self.create_subgraph(self.g1_nodes)

        # subgraph 2
        # one child, two parents, one sibling
        self.g2n1 = DocNode("g2n1", "/g2n1")
        self.g2n2 = DocNode("g2n2", "/g2n2")
        self.g2n3 = DocNode("g2n3", "/g2n3")
        self.g2n4 = DocNode("g2n4", "/g2n4")

        self.g2n3.add_edge("g2n1", DocNode.EDGE_TYPE_PARENT)
        self.g2n3.add_edge("g2n2", DocNode.EDGE_TYPE_PARENT)
        self.g2n4.add_edge("g2n2", DocNode.EDGE_TYPE_SIBLING)

        self.g2_nodes = [self.g2n1, self.g2n2, self.g2n3, self.g2n4]
        self.g2 = self.create_subgraph(self.g2_nodes)

        # subgraph 3
        # substantially more complex - loops & everything
        self.g3n1 = DocNode("g3n1", "/g3n1")
        self.g3n2 = DocNode("g3n2", "/g3n2")
        self.g3n3 = DocNode("g3n3", "/g3n3")
        self.g3n4 = DocNode("g3n4", "/g3n4")
        self.g3n5 = DocNode("g3n5", "/g3n5")
        self.g3n6 = DocNode("g3n6", "/g3n6")
        self.g3n7 = DocNode("g3n7", "/g3n7")
        self.g3n8 = DocNode("g3n8", "/g3n8")
        self.g3n9 = DocNode("g3n9", "/g3n9")

        self.g3n2.add_edge("g3n1", DocNode.EDGE_TYPE_PARENT)
        self.g3n2.add_edge("g3n5", DocNode.EDGE_TYPE_PARENT)
        self.g3n3.add_edge("g3n1", DocNode.EDGE_TYPE_PARENT)
        self.g3n4.add_edge("g3n2", DocNode.EDGE_TYPE_PARENT)
        self.g3n4.add_edge("g3n3", DocNode.EDGE_TYPE_PARENT)
        self.g3n5.add_edge("g3n4", DocNode.EDGE_TYPE_PARENT)
        self.g3n6.add_edge("g3n5", DocNode.EDGE_TYPE_PARENT)
        self.g3n7.add_edge("g3n6", DocNode.EDGE_TYPE_PARENT)

        self.g3n5.add_edge("g3n1", DocNode.EDGE_TYPE_SIBLING)
        self.g3n7.add_edge("g3n5", DocNode.EDGE_TYPE_SIBLING)
        self.g3n8.add_edge("g3n7", DocNode.EDGE_TYPE_SIBLING)
        self.g3n9.add_edge("g3n7", DocNode.EDGE_TYPE_SIBLING)

        self.g3_nodes = [self.g3n1, self.g3n2, self.g3n3,
                         self.g3n4, self.g3n5, self.g3n6,
                         self.g3n7, self.g3n8, self.g3n9]
        self.g3 = self.create_subgraph(self.g3_nodes)

        self.assigner = ColorAssigner()

    def tearDown(self):
        pass

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
