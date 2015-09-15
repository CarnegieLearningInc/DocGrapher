
from import_identifiers import ImportIdentifier_R

import sys
import os


class ImportManager:

    def __init__(self):
        # list of import identifiers
        self.identifiers = []
        self.identifiers.append(ImportIdentifier_R())

    def should_auto_detect_imports(self, docnode):
        for edge in docnode.edges:
            if edge['id'] == 'AUTO' and edge['type'] == 'import':
                return True
        return False

    def add_auto_imports(self, docnodes):
        '''
            Docnodes: list of docnode objects
        '''
        docnode_filepath_map = {node.filepath.lower() : node for node in docnodes}
        for node in docnodes:
            if self.should_auto_detect_imports(node):

                # find a Import Identifier that has registered for this file
                import_identifier_found = False
                for identifier in self.identifiers:
                    if identifier.can_help(node.filepath):

                        # we know we can read this file since it's
                        # in the list of docnodes and it's already
                        # been parsed to grab annotations
                        with open(node.filepath, 'r') as f:
                            text = f.read()

                        dirname = os.path.dirname(node.filepath)
                        imports = identifier.get_imports(text)

                        # get the full path
                        import_paths = [os.path.join(dirname, i) for i in imports]

                        # make sure they are legit paths
                        import_paths = [i.lower() for i in import_paths if os.path.exists(i)]

                        # see which match other docnodes we've found
                        for path in import_paths:
                            if path in docnode_filepath_map:
                                imported_node = docnode_filepath_map[path]
                                node.add_edge(imported_node.name, 'import')

                        ## get out of here!
                        import_identifier_found = True
                        break

                if not import_identifier_found:
                    sys.stderr.write("No Import Identifier found for file {}"
                                     .format(node.filepath))

                # drop the AUTO edge
                node.edges.remove({'id': 'AUTO', 'type': 'import'})
