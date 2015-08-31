#!/usr/bin/env python3

import sys
import re
import copy
import json
import os
import random
import datetime

from pprint import pprint


class CLDocFile:
    def __init__(self, name, filepath, parentIDs=[], notes=None):
        self.name = name  # name is unique
        self.filepath = filepath  # file name associated with this doc file
        self.parentIDs = parentIDs  # can have multiple parents, optional
        self.notes = notes  # notes are optional

        statbuf = os.stat(self.filepath)
        self.last_modified = str(datetime.datetime.fromtimestamp(statbuf.st_mtime))

        self.color = None  # this is used for graphing
        self.seen = False  # this is used when assigning colors (before they've been assigned a color)

    def graph_node(self, config={}):
        node = copy.copy(config)
        node["id"] = self.name
        node["label"] = self.name

        if self.color:
            node["color"] = self.color

        node["filepath"] = self.filepath
        node["last_modified"] = self.last_modified
        node["notes"] = self.notes if self.notes is not None else "No Notes"

        return node

    def graph_edges(self, config={}):
        edges = []
        for idx, parentID in enumerate(self.parentIDs):
            edge = copy.copy(config)
            edge["id"] = "{}_e{}".format(self.name, idx)
            edge["source"] = parentID
            edge["target"] = self.name

            edges.append(edge)
        return edges


def parse_docfile(filepath):
    text = open(filepath, 'r').read()
    # print(text)

    # TODO: grep around for CLDocName, CLDocParent, CLDocNotes
    #       then create a CLDocFile object
    nameResult = re.search("@CLDocName:(.*)\n", text)
    parentResult = re.search("CLDocParent:(.*)\n", text)
    notesResult = re.search("CLDocNotes:(.*)\n", text)

    name = nameResult.group(1).strip()
    parents = parentResult.group(1).strip().split(',')
    notes = notesResult.group(1).strip()

    docfile = CLDocFile(name=name, filepath=filepath, parentIDs=parents, notes=notes)
    return docfile


# in the future, may want to get more intelligent with this...
# --> http://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
# --> https://docs.python.org/2/library/colorsys.html
# - may need to figure out how many subgraphs there are and then use HSV
class ColorAssigner:

    def __init__(self):
        self.reserved_colors = ['#0000ff', 'rgb(0, 0, 255, 1)']

    def random_hex_color(self):
        color = None
        while color is None or color in self.reserved_colors:
            color = "#%06x" % random.randint(0, 0xFFFFFF)
        self.reserved_colors.append(color)
        return color

    def random_rgba_color(self):
        color = None
        while color is None or color in self.reserved_colors:
            color = 'rgba({}, {}, {}, 1)'.format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))
        self.reserved_colors.append(color)
        return color

    def all_colors_assigned(self, node_map):
        for name, node in node_map.items():
            if node.color is None:
                return False
        return True

    def get_path_to_colored_node(self, node, node_map):
        '''
            Trace node's parents until we find a node with a color.
            Then return the color and the path
        '''
        node_path = []
        unexamined = [node]
        while len(unexamined) > 0:
            current_node = unexamined.pop()

            if not current_node.seen:
                current_node.seen = True
                node_path.append(current_node)
                for parentID in node.parentIDs:
                    unexamined.append(node_map[parentID])

            if current_node.color:
                break

        return (current_node.color, node_path)

    def assign_colors(self, node_map):
        # while we're not done assigning colors
        while not self.all_colors_assigned(node_map):

            uncolored_node = None
            for name, node in node_map.items():
                if node.color is None:
                    uncolored_node = node
                    break

            color, node_path = self.get_path_to_colored_node(uncolored_node, node_map)

            if color is None:
                # color = self.random_hex_color()
                color = self.random_rgba_color()

            unassigned = [uncolored_node]
            while len(unassigned) > 0:
                node = unassigned.pop()

                # since children take care of their parents
                # we don't have to re-assign if we see a parent
                # with the same color
                if node.seen and node.color == color:
                    continue

                node.color = color
                node.seen = True

                # bubble up parents
                unassigned += [node_map[parentID] for parentID in node.parentIDs]


def main(args):
    dirs = args[1:]
    print('dirs: {}'.format(dirs))

    # for each file in each directory, recursively on down,
    # search for CLDoc annotations and create objects appropriately
    docfiles = {}
    for root, dirs, files in os.walk(dirs[0]):
        for fname in files:
            path = os.path.join(root, fname)
            docfile = parse_docfile(path)

            docfiles[docfile.name] = docfile

    # validate all parents - make sure they actually exist
    for name in docfiles:
        docfile = docfiles[name]
        verified_parents = []
        for parentID in docfile.parentIDs:
            if parentID in docfiles:
                verified_parents.append(parentID)
        docfile.parentIDs = verified_parents

    ## assign colors to distinct segments
    ## we do this as follows:
    #### climb up chain of parents
    #### if parent has color assigned, assign same color to all children
    #### if we reach the top of the chain without having assigned a color, assign a color and bubble down
    #### IMPORTANT: remember to mark nodes as "seen" as we do this!
    ####            (because we don't necessary want to force links as a tree structure)
    # assign_colors(docfiles)
    assigner = ColorAssigner()
    assigner.assign_colors(docfiles)

    nodes = []
    edges = []
    node_config = {'size': 10}
    edge_config = {'size': 3}
    for name in docfiles:
        docfile = docfiles[name]

        nodes.append(docfile.graph_node(node_config))
        edges += docfile.graph_edges(edge_config)

    graph = {'nodes': nodes, 'edges': edges}
    # pprint(graph)

    with open('../output.json', 'w') as f:
        json.dump(graph, f, indent=4)


if __name__ == '__main__':
    main(sys.argv)
