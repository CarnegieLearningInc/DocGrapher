
import unittest

from import_identifiers import *


class ImportIdentifiersTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_identifier_R(self):
        identifier = ImportIdentifier_R()

        self.assertTrue(identifier.can_help('/foo/bar.r'))
        self.assertTrue(identifier.can_help('/foo/bar.R'))
        self.assertFalse(identifier.can_help('/foo/bar.h'))

        text = """
        library("abc.R")
        require('DEF.r')
        source("gHi.r")
        # this is some
        # other
        library('jKL.R') # some comment
        #  require("mno.R")
        # text
        """

        imports = identifier.get_imports(text)
        self.assertEqual(imports, {'abc.R', 'DEF.r', 'gHi.r', 'jKL.R'})
