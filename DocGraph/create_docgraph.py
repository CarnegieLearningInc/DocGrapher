#!/usr/bin/env python3

import sys
import re
import copy
import json
import os
import random
import datetime
import colorsys

# from pprint import pprint


class DocNode:
    def __init__(self, name, filepath, parentIDs=[], siblingIDs=[], notes=None):
        self.name = name  # name is unique
        self.filepath = filepath  # file name associated with this doc file
        self.edges = []
        for parentID in parentIDs:
            self.edges.append({'id' : parentID, 'type': 'parent'})
        for siblingID in siblingIDs:
            self.edges.append({'id' : siblingID, 'type' : 'sibling'})

        self.notes = notes  # notes are optional

        try:
            statbuf = os.stat(self.filepath)
            self.last_modified = str(datetime.datetime.fromtimestamp(statbuf.st_mtime))
        except:
            self.last_modified = "Error: can't find file"

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
                      parentIDs=parents, siblingIDs=siblings,
                      notes=notes)
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
        self.latest_hue = (self.latest_hue + .13) % 1
        self.latest_lightness = (self.latest_lightness + .12) % .3
        self.latest_saturation = (self.latest_saturation + .11) % .3
        red, green, blue = colorsys.hls_to_rgb(self.latest_hue,
                                               .4 + self.latest_lightness,
                                               .4 + self.latest_saturation)
        red *= 255
        green *= 255
        blue *= 255
        color = 'rgba({}, {}, {}, 1)'.format(int(red), int(green), int(blue))
        print('color: {}'.format(color))
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
                for edge in node.edges:
                    edgeID = edge['id']
                    unexamined.append(node_map[edgeID])

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
                unassigned += [node_map[e['id']] for e in node.edges]


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
    docfiles = {}
    filecount = 0
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                filecount += 1

                path = os.path.join(root, fname)
                docfile = parse_docfile(path)

                if docfile is None:
                    # sys.stderr.write("Error! File is not annotated: {}\n"
                    #                  .format(path))
                    continue
                docfiles[docfile.name] = docfile

    # validate all parents & siblings - make sure they actually exist
    for name in docfiles:
        docfile = docfiles[name]
        verified_edges = []
        for edge in docfile.edges:
            if edge['id'] in docfiles:
                verified_edges.append(edge)
        docfile.edges = verified_edges

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
