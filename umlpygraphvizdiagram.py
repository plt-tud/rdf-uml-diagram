# -*- coding: utf-8 -*-

import logging
import re
from pygraphviz import AGraph

trantab = str.maketrans("./:-#", "_____")

def graphviz_id(uri):
    return str(uri).translate(trantab)


class UmlPygraphVizDiagram():
    """
    Creates a diagram similar to the class diagrams and objects diagrams from UML using pygraphviz
    """

    def __init__(self):
        logging.basicConfig()
        self.graph = AGraph(directed=True, strict=False)
        self.graph.node_attr['shape']='record'
        self.graph.graph_attr['fontsize']='8'
        self.graph.graph_attr['fontname']="Bitstream Vera Sans"
        self.graph.graph_attr['label']=""

        self.connected_nodes = set()
        self.described_nodes = set()

    def _add_node(self, node_id, node_label):
        self.graph.add_node(node_id, label=node_label)

    def add_class_node(self, class_name, attributes):
        self.described_nodes.add(class_name)
        label = "<{<b>%s</b> | %s }>" % (
            class_name, "<br align='left'/>".join(attributes).strip() + "<br align='left'/>")
        self.subgraph.add_node(graphviz_id(class_name), label=label)

    def add_object_node(self, object_name, class_name, attributes):
        self.described_nodes.add(object_name)
        if class_name:
            label = "<{<b><u>%s (%s)</u></b>| %s }>" % (
                object_name, class_name, "<br align='left'/>".join(attributes) + "<br align='left'/>")
        else:
            label = "<{<b><u>%s</u></b>| %s }>" % (
                object_name, "<br align='left'/>".join(attributes) + "<br align='left'/>")
        self.subgraph.add_node(graphviz_id(object_name), label=label)

    def add_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open")

    def add_cardinality_edge(self, src, dst, name, card):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", labeldistance=2.0,
                            headlabel=card + "..." + card, labelangle=-65.0)

    def add_min_cardinality_edge(self, src, dst, name, card):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", labeldistance=2.0,
                            headlabel=card + "...*", labelangle=-65.0)

    def add_max_cardinality_edge(self, src, dst, name, card):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", labeldistance=2.0,
                            headlabel="0..." + card, labelangle=-65.0)

    def add_min_max_cardinality_edge(self, src, dst, name, min, max):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", labeldistance=2.0,
                            headlabel=min + "..." + max, labelangle=-65.0)

    def add_list_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowtail="ediamond", dir="back",
                            headlabel="0...*", labeldistance=2.0, labelfontcolor="black", labelangle=-65.0)

    # self.graph.add_edge(graphviz_id(src), graphviz_id(dst),label=name,arrowtail="ediamond", dir="back",headlabel="0...*", taillabel=(dst.split(":")[1])+"s",labeldistance=2.0,labelfontcolor="black")

    def add_symmetric_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="none")

    def add_functional_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", headlabel="1...1",
                            taillabel="0...*", labeldistance=2.0, labelfontcolor="black", labelangle=-65.0)

    def add_inversefunctional_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label=name, arrowhead="open", headlabel="0...*",
                            taillabel="1...1", labeldistance=2.0, labelfontcolor="black", labelangle=-65.0)

    def add_equivalentclass_edge(self, src, dst):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label="\<\<equivalentClass\>\>", arrowhead="none",
                            style="dashed")

    def add_unionof_edge(self, src, dst):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label="\<\<unionOf\>\>", arrowhead="open",
                            style="dashed")

    def add_oneof_edge(self, src, dst):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), label="\<\<instanceOf\>\>", arrowhead="open",
                            style="dashed", dir="back")

    def add_subclass_edge(self, src, dst):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.graph.add_edge(graphviz_id(src), graphviz_id(dst), arrowhead="empty")


    def set_label(self, label):
        self.graph.graph_attr['label'] = label

    def start_subgraph(self, graph_name):
        self.subgraph = self.graph.add_subgraph(name="cluster_%s" % graphviz_id(graph_name))
        self.subgraph.graph_attr['label']=graph_name

    def add_undescribed_nodes(self):
        s = self.connected_nodes-self.described_nodes
        for node in s:
            self.graph.add_node(graphviz_id(node), label=node)

    def write_to_file(self, filename_dot):
        f = open(filename_dot, 'w')
        f.write(self.graph.string())
        print("dot file created: " + filename_dot)

    def visualize(self, filename, namespaceList=None):
        self.graph.layout(prog='dot')
        self.graph.draw(filename)
        if filename.endswith(".svg"):
            self._add_links_to_svg_file(filename, namespaceList)
        print("graphic file created: " + filename)


    def _add_links_to_svg_file(self, output, namespaceList=None):
        # SVG Datei anpassen
        svg_string = open(output).read()

        # Titel der SVG Datei anpassen
        svg_string = svg_string.replace("%3", output)

        # Hyperlinks mit den Internetseiten hinzufügen
        for ns in namespaceList:
            namespace = str(ns[0])  # Präfix des Namespaces
            url = str(ns[1])  # URL des Namespaces
            if namespace:  	    
                regex_str = """%s:(\w+)""" % namespace
                regex = re.compile(regex_str)
                svg_string = regex.sub("""<a xlink:href='%s\\1'>%s:\\1</a>""" % (url, namespace), svg_string)

        # Datei schreiben
        svg_file = open(output, "w")
        svg_file.write(svg_string)
        svg_file.close()
