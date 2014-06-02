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

from os.path import splitext
from rdflib import Dataset

from umlpygraphvizdiagram import UmlPygraphVizDiagram
from umlgraphvizdiagram import UmlGraphVizDiagram

class RDFtoUmlDiagram():
    """
    Transform a RDF dataset to an UML diagram
    """
    def __init__(self, output_filename='output.png'):
        self.ds = Dataset()
        #self.d = UmlGraphVizDiagram(output_filename)
        self.d = UmlPygraphVizDiagram(output_filename)

    def load_rdf(self, filename, input_format=None):
        if input_format:
            rdf_format = input_format
        elif filename is not sys.stdin:
            format_list = {'.xml': 'xml',
                           '.rdf': 'xml',
                           '.owl': 'xml',
                           '.n3': 'n3',
                           '.ttl': 'turtle',
                           '.nt': 'nt',
                           '.trig': 'trig',
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
        self.d.add_label("Namespaces:\l")
        for ns in sorted(self.ds.namespaces()):
            self.d.add_label("%s:\t%s \l" % (ns[0], ns[1]))

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
            graph_name = graph.n3()
            if graph_name == "[<urn:x-rdflib:default>]":
                break
            graph = graph.skolemize()

            query_nodes = """SELECT DISTINCT ?node
                        WHERE {
                            ?node a ?class.
                        } ORDER BY ?node"""
            result_nodes = graph.query(query_nodes)

            if result_nodes:
                self.start_subgraph(graph_name)
            else:
                print("Warning: No instances (rdf:type) defined in graph %s" % graph_name)
                
            for row_nodes in result_nodes:
                # adding the classes to the node (can be more than one)
                query_classes = """SELECT DISTINCT ?class
                        WHERE {
                            %s a ?class.
                        } ORDER BY ?class""" % row_nodes['node'].n3()
                result_classes = graph.query(query_classes)
                classes = []
                for row_classes in result_classes:
                    classes.append(self.ds.namespace_manager.qname(row_classes['class']))
                # adding the attributes to the node
                query_attributes = """SELECT DISTINCT ?p ?o
                            WHERE {
                                %s ?p ?o.
                                FILTER (isLiteral(?o))
                            } ORDER BY ?p ?o""" % row_nodes['node'].n3()
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
                        } ORDER BY ?c1 ?p ?c2"""
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
            graph_name = graph.n3()
            if graph_name == "[<urn:x-rdflib:default>]":
                break
            graph = graph.skolemize()

            query2 = """SELECT DISTINCT ?class
                        WHERE {
                            {?class a <http://www.w3.org/2000/01/rdf-schema#Class>.}
                            UNION
                            {?class a <http://www.w3.org/2002/07/owl#Class>.}
                        } ORDER BY ?class"""
            result2 = graph.query(query2)
            if result2:
                self.start_subgraph(graph_name)
            for row2 in result2:
                query3 = """SELECT DISTINCT ?property
                            WHERE {
                                ?property rdfs:domain %s;
                                    a <http://www.w3.org/2002/07/owl#DataTypeProperty>.
                            } ORDER BY ?property""" % row2['class'].n3()
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
                        } ORDER BY ?src ?property ?dest"""
            result4 = graph.query(query4)
            for row4 in result4:
                self.add_edge(row4['src'], row4['dest'], row4['property'])

            query_subclass = """SELECT DISTINCT ?src ?dest
                        WHERE {
                           ?src rdfs:subClassOf ?dest.
                        } ORDER BY ?src ?dest"""
            result_subclass = graph.query(query_subclass)
            for row_subclass in result_subclass:
                self.add_subclass_edge(row_subclass['src'],row_subclass['dest'])
        self.close_and_visualize()



if __name__ == '__main__':
    import argparse
    import sys

    # Initialize command line parser
    parser = argparse.ArgumentParser(description='Creates UML Object Diagram from RDF(S) files')
    parser.add_argument('filename', nargs='+', type=argparse.FileType('r'), help='RDF file')
    parser.add_argument('-o', '--output', dest='png_file', nargs=1, help='Output graphics file (default is FILENAME.png)')
    parser.add_argument('-s', '--rdfs', action='store_true', help='Input files should be treated as RDFS providing a class diagram instead of an object diagram')
    parser.add_argument('-n', '--namespace', metavar=('PREFIX', 'NAMESPACE'), nargs=2, action='append', help='Additional namespaces')
    parser.add_argument('-i', '--input', dest='format', nargs=1, default=(None,), help='Input format (xml, n3, turtle, nt, trix, trig). When blank than it is guessed from file name extension')
    args = parser.parse_args()

    if args.png_file:
        output = args.png_file[0]
    else:
        output = args.filename[0].name + '.png'

    if args.rdfs:
        d = RDFStoUmlClassDiagram(output)
    else:
        d = RDFtoUmlObjectDiagram(output)
    for f in args.filename:
        d.load_rdf(f, args.format[0])
    d.add_namespaces(args.namespace)
    d.create_diagram()
