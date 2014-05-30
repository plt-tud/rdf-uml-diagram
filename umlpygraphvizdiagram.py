# -*- coding: utf-8 -*-

from pygraphviz import AGraph
import logging

trantab = str.maketrans("./:-#", "_____")

def graphviz_id(uri):
    return str(uri).translate(trantab)


class UmlPygraphVizDiagram():
    """
    Creates a diagram similar to the class diagrams and objects diagrams from UML using GraphViz
    """
    def __init__(self, filename='output.png'):
        logging.basicConfig()
        self.filename_png = filename
        self.graph = AGraph(directed=True, strict=False)
        self.graph.node_attr['shape']='record'
        self.graph.graph_attr['fontsize']='8'
        self.graph.graph_attr['fontname']="Bitstream Vera Sans"
        self.graph.graph_attr['label']=""

        self.connected_nodes = set()
        self.described_nodes = set()

    def add_node(self, node_id, node_label):
        self.graph.add_node(node_id, label=node_label)

    def add_class_node(self, class_name, attributes):
        self.described_nodes.add(class_name)
        label = "<{<b>%s</b> | " % class_name
        for a in attributes:
            label += '%s<br/>' % a
        label += '}>'
        self.subgraph.add_node(graphviz_id(class_name), label=label)

    def add_object_node(self, object_name, class_name, attributes):
        self.described_nodes.add(class_name)
        label = '<{<b><u>%s (%s)</u></b>| ' % (object_name, class_name)
        for a in attributes:
            label += '%s<br/>' % a
        label += '}>'
        self.subgraph.add_node(graphviz_id(object_name), label=label)

    def add_edge(self, src, dst, name):
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open")

    def add_subclass_edge(self, src, dst):
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), arrowhead="empty")

    def add_label(self, label):
        self.graph.graph_attr['label'] += label

    def start_subgraph(self, graph_name):
        self.subgraph = self.graph.add_subgraph(name="cluster_%s" % graphviz_id(graph_name))
        self.subgraph.graph_attr['label']=graph_name

    def close_subgraph(self):
        pass

    def close(self):
        pass

    def add_undescribed_nodes(self):
        s = self.connected_nodes-self.described_nodes
        for node in s:
            self.graph.add_node(graphviz_id(node), node)

    def visualize(self):
        #print(self.graph.string())
        self.graph.layout(prog='dot')
        self.graph.draw(self.filename_png)
        print("png created: " + self.filename_png)
