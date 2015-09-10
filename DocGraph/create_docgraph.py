#!/usr/bin/env python3

import sys
import re
import copy
import json
import os
import random
import datetime
import colorsys
import collections

# from pprint import pprint


class DocNode:
    EDGE_TYPE_PARENT = 'parent'
    EDGE_TYPE_SIBLING = 'sibling'

    EDGE_TYPES = [EDGE_TYPE_PARENT, EDGE_TYPE_SIBLING]

    def __init__(self, name, filepath, notes=None):
        self.name = name  # name is unique
        self.filepath = filepath  # file name associated with this doc file
        self.edges = []

        self.notes = notes  # notes are optional

        try:
            statbuf = os.stat(self.filepath)
            date = datetime.datetime.fromtimestamp(statbuf.st_mtime)
            self.last_modified = date.strftime('%b %d, %Y @ %H:%M')
        except:
            self.last_modified = "Error: can't find file"

        self.color = None  # this is used for graphing
        self.seen = False  # this is used when assigning colors (before they've been assigned a color)

        # for when we're assigning colors, we need to keep track of all parents, siblings, AND children
        self.all_connections = set()

    def add_edge(self, identifier, eType):
        if eType not in self.EDGE_TYPES:
            raise Exception("edge type is invalid (type: {}, id: {}"
                            .format(eType, identifier))
        self.edges.append({'id' : identifier, 'type': eType})

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
        edge_type_map = {'parent': 'arrow',
                         'sibling': 'dashed'}

        graph_edges = []
        for idx, edge in enumerate(self.edges):
            graph_edge = copy.copy(config)
            graph_edge['id'] = '{}_e{}'.format(self.name, idx)
            graph_edge['source'] = edge['id']
            graph_edge['target'] = self.name

            graph_edge['type'] = edge_type_map[edge['type']]

            graph_edges.append(graph_edge)

        return graph_edges


def parse_docfile(filepath):
    text = None
    with open(filepath, 'r') as f:
        try:
            text = f.read()
        except UnicodeDecodeError:
            # if we can't read file, can't produce docnode
            return None

    nameResult = re.search("@name:(.*)\n", text)
    parentResult = re.search("@parent[s]?:(.*)\n", text)
    siblingResult = re.search("@sibling[s]?:(.*)\n", text)
    notesResult = re.search("@note[s]?:(.*)\n", text)

    if nameResult is None:
        return None
    name = nameResult.group(1).strip()
    if len(name) == 0:
        return None

    parents = []
    if parentResult is not None:
        parents = [p.strip() for p in parentResult.group(1).split(',')]
        parents = [p for p in parents if len(p) > 0]

    siblings = []
    if siblingResult is not None:
        siblings = [s.strip() for s in siblingResult.group(1).split(',')]
        siblings = [s for s in siblings if len(s) > 0]

    notes = None
    if notesResult is not None:
        notes = notesResult.group(1).strip()
        notes = notes if len(notes) > 0 else None

    docnode = DocNode(name=name, filepath=filepath,
                      notes=notes)
    for parentID in parents:
        docnode.add_edge(parentID, 'parent')
    for siblingID in siblings:
        docnode.add_edge(siblingID, 'sibling')
    return docnode


# in the future, may want to get more intelligent with this...
# --> http://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
# --> https://docs.python.org/2/library/colorsys.html
# - may need to figure out how many subgraphs there are and then use HSV
class ColorAssigner:

    def __init__(self):
        self.reserved_colors = []
        self.latest_hue = 0
        self.latest_lightness = 0
        self.latest_saturation = 0

    def random_hex_color(self):
        color = None
        while color is None or color in self.reserved_colors:
            color = "#%06x" % random.randint(0, 0xFFFFFF)
        self.reserved_colors.append(color)
        return color

    def random_rgba_color(self):
        self.latest_hue = (self.latest_hue + .19) % 1
        self.latest_lightness = (self.latest_lightness + .17) % .3
        self.latest_saturation = (self.latest_saturation + .14) % .3
        red, green, blue = colorsys.hls_to_rgb(self.latest_hue,
                                               .4 + self.latest_lightness,
                                               .4 + self.latest_saturation)
        red *= 255
        green *= 255
        blue *= 255
        color = 'rgba({}, {}, {}, 1)'.format(int(red), int(green), int(blue))
        # print('color: {}'.format(color))
        return color

    def all_colors_assigned(self, node_map):
        for name, node in node_map.items():
            if node.color is None:
                return False
        return True

    def assign_colors(self, node_map):

        for name, node in node_map.items():
            node.all_connections = set()

        # each node should know about its parents, siblings, AND children
        # which we put in the .all_connections property
        for name, node in node_map.items():
            for edge in node.edges:
                node.all_connections.add(edge['id'])

                node_map[edge['id']].all_connections.add(name)

        # while we're not done assigning colors
        while not self.all_colors_assigned(node_map):

            uncolored_node = None
            for name, node in node_map.items():
                if node.color is None:
                    uncolored_node = node
                    break

            color = self.random_rgba_color()

            unassigned = [uncolored_node]
            while len(unassigned) > 0:
                node = unassigned.pop()

                if node.color == color and node.seen:
                    continue

                node.color = color
                node.seen = True

                # bubble up parents
                # unassigned += [node_map[e['id']] for e in node.edges]
                unassigned += [node_map[c] for c in node.all_connections]


def main(args):
    if len(args) < 3:
        sys.stderr.write("usage: {} <directories> <output.json>\n".format(args[0]))
        sys.stderr.write("\t<directories>: list of space-separated directories to examine\n")
        sys.stderr.write("\t<output>: json file describing graphs, interpreted by doc_grapher.html\n")
        sys.exit(1)

    directories = args[1:-1]
    outfname = args[-1]

    # for each file in each directory, recursively on down,
    # search for doc annotations and create objects appropriately
    docnodes = collections.OrderedDict()
    filecount = 0
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                filecount += 1

                path = os.path.join(root, fname)
                docnode = parse_docfile(path)

                if docnode is None:
                    # sys.stderr.write("Error! File is not annotated: {}\n"
                    #                  .format(path))
                    continue
                docnodes[docnode.name] = docnode

    # validate all parents & siblings - make sure they actually exist
    for name in docnodes:
        docnode = docnodes[name]
        verified_edges = []
        for edge in docnode.edges:
            if edge['id'] in docnodes:
                verified_edges.append(edge)
        docnode.edges = verified_edges

    ## assign colors to distinct segments
    ## we do this as follows:
    #### climb up chain of parents
    #### if parent has color assigned, assign same color to all children
    #### if we reach the top of the chain without having assigned a color, assign a color and bubble down
    #### IMPORTANT: remember to mark nodes as "seen" as we do this!
    ####            (because we don't necessary want to force links as a tree structure)
    assigner = ColorAssigner()
    assigner.assign_colors(docnodes)

    nodes = []
    edges = []
    node_config = {'size': 10}
    edge_config = {'size': 3}
    for name in docnodes:
        docnode = docnodes[name]

        nodes.append(docnode.graph_node(node_config))
        edges += docnode.graph_edges(edge_config)

    if len(nodes) == 0:
        sys.stderr.write("No annotated files found! Not writing output file.\n")
        sys.exit(1)

    print("Extracted {} nodes with {} edges from {} files"
          .format(len(nodes), len(edges), filecount))
    graph = {'nodes': nodes, 'edges': edges}
    # pprint(graph)

    with open(outfname, 'w') as f:
        json.dump(graph, f, indent=4)


if __name__ == '__main__':
    main(sys.argv)
