
import unittest
import unittest.mock

from ImportManager import *
from import_identifiers import *
from create_docgraph import *

NODE1_PATH = '/tmp/test_import_manager-node1.xyz'
NODE2_PATH = '/tmp/test_import_manager-node2.xyz'
NODE1_FNAME = 'test_import_manager-node1.xyz'
NODE2_FNAME = 'test_import_manager-node2.xyz'
NODE1_NAME = 'n1'
NODE2_NAME = 'n2'
NODE1_TEXT = 'node 1 text is here\n'
NODE2_TEXT = 'node 2 text is here\n'


class ImportManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(NODE1_PATH, 'w') as f:
            f.write(NODE1_TEXT)
        with open(NODE2_PATH, 'w') as f:
            f.write(NODE2_TEXT)

    @classmethod
    def tearDownClass(cls):
        os.remove(NODE1_PATH)
        os.remove(NODE2_PATH)

    def setUp(self):
        self.manager = ImportManager()

        self.mock_identifier = unittest.mock.create_autospec(ImportIdentifier)
        self.manager.identifiers = [self.mock_identifier]

        self.node1 = DocNode(NODE1_NAME, NODE1_PATH)
        self.node2 = DocNode(NODE2_NAME, NODE2_PATH)

        self.docnodes = [self.node1, self.node2]

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_addAutoImport_canHelp_SuccessfulImport(self):
        self.node1.add_edge('AUTO', 'import')

        self.mock_identifier.can_help.return_value = True
        self.mock_identifier.get_imports.return_value = [NODE2_FNAME]

        self.manager.add_auto_imports(self.docnodes)

        self.mock_identifier.can_help.assert_called_with(NODE1_PATH)
        self.mock_identifier.get_imports.assert_called_with(NODE1_TEXT)

        self.assertEqual(self.node1.edges, [{'id': 'n2', 'type': 'import'}])

    def test_addAutoImport_canHelp_NoImports(self):
        self.node1.add_edge('AUTO', 'import')

        self.mock_identifier.can_help.return_value = True
        self.mock_identifier.get_imports.return_value = []

        self.manager.add_auto_imports(self.docnodes)

        self.mock_identifier.can_help.assert_called_with(NODE1_PATH)
        self.mock_identifier.get_imports.assert_called_with(NODE1_TEXT)

        self.assertEqual(self.node1.edges, [])

    def test_addAutoImport_cannotHelp(self):
        self.node1.add_edge('AUTO', 'import')

        self.mock_identifier.can_help.return_value = False

        self.manager.add_auto_imports(self.docnodes)

        self.mock_identifier.can_help.assert_called_with(NODE1_PATH)
        self.assertFalse(self.mock_identifier.get_imports.called)

        self.assertEqual(self.node1.edges, [])

    def test_noAutoImport(self):
        self.manager.add_auto_imports(self.docnodes)

        self.assertFalse(self.mock_identifier.can_help.called)
        self.assertFalse(self.mock_identifier.get_imports.called)
