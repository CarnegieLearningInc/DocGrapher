
import re


class ImportIdentifier_R:

    def __init__(self):
        self.regex = re.compile("(library|require|source)\([\"'](.*\.(R|r))[\"']\).*\n")

    def can_help(self, filepath):
        return filepath.lower().endswith('.r')

    def get_imports(self, text):
        # get rid of all comments (lines that start with #)
        text = '\n'.join([t for t in text.split('\n')
                          if not t.strip().startswith('#')])

        # returns tuples of the form (library, foobar.R, R)
        # so we only want to grab the middle item
        result = re.findall(self.regex, text)
        imports = set([r[1] for r in result])
        return imports
