#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Converts RDF files to PNG diagrams which are similar to UML diagrams.
The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)
Its executable 'dot' has to be on PATH. It uses SPARQL to get nodes. Thus, also 'rdflib' is required.

@author: Markus Graube
@contact: markus.graube@tu-dresden.de
@organization: Professur fuer Prozessleittechnik, Technische Universität Dresden (http://www.et.tu-dresden.de/ifa/?id=plt)
@version: 0.4
@date: 2014-02-19
@copyright: Professur fuer Prozessleittechnik, 2013

@todo: Autodetect if graph contains RDFS vocabulary
@todo: Add OWL features
@todo: Use iGraph (http://igraph.sourceforge.net/) for visualizing the graphs
@todo: Use filenames for graph names instead of random names if no named graph available

@license: 
    Licensed under the EUPL, Version 1.1 or – as soon they
    will be approved by the European Commission - subsequent
    versions of the EUPL (the "Licence");
    You may not use this work except in compliance with the
    Licence.
    
    You may obtain a copy of the Licence at:
    http://ec.europa.eu/idabc/eupl

    Unless required by applicable law or agreed to in
    writing, software distributed under the Licence is
    distributed on an "AS IS" basis,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied.
    See the Licence for the specific language governing
    permissions and limitations under the Licence.
"""

from subprocess import call
import logging
from os.path import splitext
from rdflib import Dataset


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


class RDFtoUmlDiagram():
    """
    Transform a RDF dataset to an UML diagram
    """
    def __init__(self, output_filename='output.png'):
        self.ds = Dataset()
        self.d = UmlGraphVizDiagram(output_filename)

    def load_rdf(self, filename):
        if filename is not sys.stdin:
            format_list = {'.xml': 'xml',
                           '.rdf': 'xml',
                           '.owl': 'xml',
                           '.n3': 'n3',
                           '.ttl': 'turtle',
                           '.nt': 'nt',
                           '.nq': 'nquads',
                           '': 'turtle'}
            extension = splitext(filename.name)[1]
            rdf_format = format_list[extension]
        else:
            rdf_format = 'turtle'
        temp = self.ds.graph("file://"+filename.name)
        temp.parse(filename.name, format=rdf_format)

    def add_namespaces(self, namespaces):
        if namespaces:
            for ns in namespaces:
                self.ds.namespace_manager.bind(ns[0],ns[1])
    
    def start_subgraph(self, graph_name):
        self.d.start_subgraph(graph_name.strip('[<>]:_'))
        
    def close_subgraph(self):
        self.d.close_subgraph()

    def add_object_node(self, object_name, classes_name, attributes):
        self.d.add_object_node(self.ds.namespace_manager.qname(object_name), classes_name, attributes)

    def add_class_node(self, class_name, attributes):
        self.d.add_class_node(self.ds.namespace_manager.qname(class_name), attributes)

    def add_edge(self, src, dst, predicate):
        self.d.add_edge(self.ds.namespace_manager.qname(src), self.ds.namespace_manager.qname(dst), self.ds.namespace_manager.qname(predicate))

    def add_subclass_edge(self, src, dst):
        self.d.add_subclass_edge(self.ds.namespace_manager.qname(src), self.ds.namespace_manager.qname(dst))

    def create_namespace_box(self):
        # Create Namespace box
        namespaces = "Namespaces:\l"
        for ns in self.ds.namespaces():
            namespaces += "%s: %s \l" % (ns[0], ns[1])
        self.d.add_label(namespaces)

    def close_and_visualize(self):
        self.create_namespace_box()
        self.d.close()
        self.d.visualize()


class RDFtoUmlObjectDiagram(RDFtoUmlDiagram):
    """
    Transform a RDF dataset to an UML object diagram
    """

    def create_diagram(self):
        # Iterate over all graphs
        for graph in self.ds.contexts():
            self.start_subgraph(graph.n3())
            graph = graph.skolemize()

            query_nodes = """SELECT DISTINCT ?node
                        WHERE {
                            ?node a ?class.
                        }"""
            result_nodes = graph.query(query_nodes)
            
            for row_nodes in result_nodes:
                query_classes = """SELECT DISTINCT ?class
                        WHERE {
                            %s a ?class.
                        }""" % row_nodes['node'].n3()
                result_classes = graph.query(query_classes)
                classes = []
                for row_classes in result_classes:
                    classes.append(self.ds.namespace_manager.qname(row_classes['class']))
                query_attributes = """SELECT DISTINCT ?p ?o
                            WHERE {
                                %s ?p ?o.
                                FILTER (isLiteral(?o))
                            }""" % row_nodes['node'].n3()
                result_attributes = graph.query(query_attributes)
                attributes = []
                for row_attributes in result_attributes:
                    attributes.append(self.ds.namespace_manager.qname(row_attributes['p']) + " = " + str(row_attributes['o']))
                self.add_object_node(row_nodes['node'], ", ".join(classes), attributes)
            self.close_subgraph()
            query_connections = """SELECT DISTINCT ?c1 ?c2 ?p
                        WHERE {
                            ?c1 ?p ?c2.
                            FILTER (!isLiteral(?c2))
                            FILTER (?p != rdf:type)
                        }"""
            result_connections = graph.query(query_connections)
            for row_connections in result_connections:
                self.add_edge(row_connections['c1'], row_connections['c2'], row_connections['p'])
        self.close_and_visualize()



class RDFStoUmlClassDiagram(RDFtoUmlDiagram):
    """
    Transform a RDF dataset with a RDFS vocabulary to an UML class diagram
    """

    def create_diagram(self):
        # Iterate over all graphs
        for graph in self.ds.contexts():
            self.start_subgraph(graph.n3())
            graph = graph.skolemize()

            query2 = """SELECT DISTINCT ?class
                        WHERE {
                            {?class a <http://www.w3.org/2000/01/rdf-schema#Class>.}
                            UNION
                            {?class a <http://www.w3.org/2002/07/owl#Class>.}
                        }"""
            result2 = graph.query(query2)
            for row2 in result2:
                query3 = """SELECT DISTINCT ?property
                            WHERE {
                                ?property rdfs:domain %s;
                                    a <http://www.w3.org/2002/07/owl#DataTypeProperty>.
                            }""" % row2['class'].n3()
                result3 = graph.query(query3)
                attributes = []
                for r in result3:
                    attributes.append(self.ds.namespace_manager.qname(r['property']))
                self.add_class_node(row2['class'], attributes)
            self.close_subgraph()

            query4 = """SELECT DISTINCT ?src ?dest ?property
                        WHERE {
                           ?property a <http://www.w3.org/2002/07/owl#ObjectProperty>;
                                rdfs:domain ?src;
                                rdfs:range ?dest.
                        }"""
            result4 = graph.query(query4)
            for row4 in result4:
                self.add_edge(row4['src'], row4['dest'], row4['property'])

            query_subclass = """SELECT DISTINCT ?src ?dest
                        WHERE {
                           ?src rdfs:subClassOf ?dest.
                        }"""
            result_subclass = graph.query(query_subclass)
            for row_subclass in result_subclass:
                self.add_subclass_edge(row_subclass['src'],row_subclass['dest'])
        self.close_and_visualize()



if __name__ == '__main__':
    import argparse
    import sys

    # Initialize command line parser
    parser = argparse.ArgumentParser(description='Creates UML Object Diagram from RDF(S) files')
    parser.add_argument('filename', nargs='+', type=argparse.FileType('r'), help='rdf file')
    parser.add_argument('-o', '--output', nargs='?', help='Output graphics file')
    parser.add_argument('-s', '--rdfs', action='store_true', help='Input files should be treated as RDFS')
    parser.add_argument('-n', '--namespace', nargs=2, action='append', help='Additional namespaces')
    args = parser.parse_args()

    if args.output:
        output = args.output
    else:
        output = args.filename[0].name + '.png'
    if args.rdfs:
        d = RDFStoUmlClassDiagram(output)
    else:
        d = RDFtoUmlObjectDiagram(output)
    for f in args.filename:
        d.load_rdf(f)
    d.add_namespaces(args.namespace)
    d.create_diagram()
