
import unittest
import os

from create_docgraph import *

## NOTE: unit tests are run sequentially, not in parallel, so we
##       can get away with using a single file
TEST_FILENAME = '/tmp/TEST_PARSING_TMPFILE'

NAME = 'MyName'
PARENT1 = 'MyParent'
PARENT2 = 'AnotherParent'
NOTE = 'This is a note! It has two sentences, I think.'


class ParsingTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.isfile(TEST_FILENAME):
            os.remove(TEST_FILENAME)

    def test_parse_allFields_singleParent_singularNote(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@parent: {}\n'.format(PARENT1))
            f.write('@note: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)
        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [PARENT1])
        self.assertEqual(docnode.notes, NOTE)

    def test_parse_allFields_multipleParents(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@parents: {},  {} \n'.format(PARENT1, PARENT2))
            f.write('@notes: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [PARENT1, PARENT2])
        self.assertEqual(docnode.notes, NOTE)

    def test_parse_noName(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@parents: {},  {} \n'.format(PARENT1, PARENT2))
            f.write('@notes: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertIsNone(docnode)

    def test_parse_missingName(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name: \n')
            f.write('@parents: {},  {} \n'.format(PARENT1, PARENT2))
            f.write('@notes: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertIsNone(docnode)

    def test_parse_noParent(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@notes: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [])
        self.assertEqual(docnode.notes, NOTE)

    def test_parse_missingParents(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@parents: ,  \n')
            f.write('@notes: {}\n'.format(NOTE))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [])
        self.assertEqual(docnode.notes, NOTE)

    def test_parse_noNotes(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@parents: {},  {} \n'.format(PARENT1, PARENT2))

        docnode = parse_docfile(TEST_FILENAME)

        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [PARENT1, PARENT2])
        self.assertIsNone(docnode.notes)

    def test_parse_missingNotes(self):
        with open(TEST_FILENAME, 'w') as f:
            f.write('@name:{}\n'.format(NAME))
            f.write('@parents: {},  {} \n'.format(PARENT1, PARENT2))
            f.write('@notes: \n')

        docnode = parse_docfile(TEST_FILENAME)

        self.assertEqual(docnode.name, NAME)
        self.assertEqual(docnode.parentIDs, [PARENT1, PARENT2])
        self.assertIsNone(docnode.notes)
