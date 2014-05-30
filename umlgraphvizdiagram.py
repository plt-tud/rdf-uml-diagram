# -*- coding: utf-8 -*-

from subprocess import call
import logging

trantab = str.maketrans("./:-#", "_____")

def graphviz_id(uri):
    return str(uri).translate(trantab)


class UmlGraphVizDiagram():
    """
    Creates a diagram similar to the class diagrams and objects diagrams from UML using GraphViz
    """
    def __init__(self, filename='output.png'):
        logging.basicConfig()
        self.filename_png = filename
        self.filename_dot = self.filename_png + '.dot'
        self.f = open(self.filename_dot, 'w')
        self.f.write("""digraph G {
                            fontname = "Bitstream Vera Sans";
                            fontsize = 8;
                            node [ shape = "record" ];\n""")
        self.connected_nodes = set()
        self.described_nodes = set()

    def add_node(self, node_id, node_label):
        self.f.write('%s [label = <{%s | }>];\n' % (node_id, node_label))

    def add_class_node(self, class_name, attributes):
        self.described_nodes.add(class_name)
        self.f.write('%s [label = <{<b>%s</b> | ' % ( graphviz_id(class_name), class_name))
        for a in attributes:
            self.f.write('%s<br/>' % a)
        self.f.write('}>];\n')

    def add_object_node(self, object_name, class_name, attributes):
        self.described_nodes.add(object_name)
        self.f.write('%s [label = <{<b><u>%s (%s)</u></b>| ' % (graphviz_id(object_name), object_name, class_name))
        for a in attributes:
            self.f.write('%s<br/>' % a)
        self.f.write('}>];\n')

    def add_edge(self, src, dst, name):
        self.connected_nodes.add(src)
        self.connected_nodes.add(dst)
        self.f.write('%s -> %s [label="%s", arrowhead="open"];\n' % (graphviz_id(src), graphviz_id(dst), name))

    def add_subclass_edge(self, src, dst):
        self.f.write('%s -> %s [arrowhead="empty"];\n' % (graphviz_id(src), graphviz_id(dst)))

    def add_label(self, label):
        self.f.write('label="%s";\n' % label)

    def start_subgraph(self, graph_name):
        self.f.write('subgraph cluster_%s {label = "%s";\n' % (
        graphviz_id(graph_name), graph_name))

    def close_subgraph(self):
        self.f.write('}\n')
    
    def add_undescribed_nodes(self):
        s = self.connected_nodes-self.described_nodes
        for node in s:
            self.add_node(graphviz_id(node), node)
    
    def close(self):
        self.add_undescribed_nodes()
        self.f.write("}\n")
        self.f.close()

    def visualize(self, open_png=False):
        call("dot -Tpng -o %s %s" % (self.filename_png, self.filename_dot), shell=True)
        print("png created: " + self.filename_png)
        if open_png:
            call("xdg-open %s" % self.filename_png, shell=True)