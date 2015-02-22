#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Converts RDF files to PNG diagrams which are similar to UML diagrams.
The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)
It uses SPARQL to get nodes. Thus, also 'rdflib' is required.
Dependencies:
 * pygraphviz
 * rdflib

@author: Markus Graube
@contact: markus.graube@tu-dresden.de
@organization: Professur fuer Prozessleittechnik, Technische Universität Dresden (http://www.et.tu-dresden.de/ifa/?id=plt)
@version: 0.3
@date: 2014-07-21
@copyright: Professur fuer Prozessleittechnik, 2014

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


class RDFtoUmlDiagram():
    """
    Transform a RDF dataset to an UML diagram
    """

    def __init__(self):
        self.ds = Dataset()
        self.d = UmlPygraphVizDiagram()

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
        print("using rdf format: " + rdf_format)
        temp = self.ds.graph("file://"+filename.name)
        temp.parse(filename.name, format=rdf_format)

    def add_namespaces(self, namespaces):
        if namespaces:
            for ns in namespaces:
                self.ds.namespace_manager.bind(ns[0],ns[1])
    
    def start_subgraph(self, graph_name):
        self.d.start_subgraph(graph_name.strip('[<>]:_'))


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
        label = """<
            <table align="left" cellborder="0">
                <tr><td align='center' colspan='2'><b>Namespaces</b></td></tr>"""
        for ns in sorted(self.ds.namespaces()):
            label += "<tr><td align='left'>%s:</td><td align='left'>%s</td></tr>" % (ns[0], ns[1] )
        label += "</table> >"

        self.d.set_label(label)

    def output_dot(self, filename):
        self.d.write_to_file(filename)

    def visualize(self, filename):
        self.d.visualize(filename, self.ds.namespaces())


    def create_diagram(self, object_nodes=True, class_nodes=False):
        # Iterate over all graphs
        for graph in self.ds.contexts():
            graph_name = graph.n3()
            if graph_name == "[<urn:x-rdflib:default>]":
                break
            graph = graph.skolemize()
            if len(graph) > 0:
                self.start_subgraph(graph_name)
                if object_nodes:
                    self.create_object_nodes(graph)
                if class_nodes:
                    self.create_class_nodes(graph)
        self.create_namespace_box()


    def create_object_nodes(self, graph):
        # object nodes
        query_nodes = """ PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    SELECT DISTINCT ?node
                    WHERE {
                        ?node a ?class.
                        FILTER (?class not IN (rdfs:Class, owl:Class, owl:Property, owl:ObjectProperty, owl:DatatypeProperty))
                    } ORDER BY ?node"""
        result_nodes = graph.query(query_nodes)
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
                attributes.append(
                    self.ds.namespace_manager.qname(row_attributes['p']) + " = " + str(row_attributes['o']))
            self.add_object_node(row_nodes['node'], ", ".join(classes), attributes)

        # object node connections
        query_connections = """SELECT DISTINCT ?c1 ?c2 ?p
                    WHERE {
                        ?c1 ?p ?c2.
                        FILTER (!isLiteral(?c2))
                        FILTER (?p not IN (rdf:type, rdfs:domain, rdfs:range, rdfs:subClassOf))
                    } ORDER BY ?c1 ?p ?c2"""
        result_connections = graph.query(query_connections)
        for row_connections in result_connections:
            self.add_edge(row_connections['c1'], row_connections['c2'], row_connections['p'])


    def create_class_nodes(self, graph):
        # RDFS stuff
        query_classes = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    SELECT DISTINCT ?class
                    WHERE {
                        ?class a ?c .
                        FILTER (?c in (rdfs:Class, owl:Class))
                    } ORDER BY ?class"""
        result_classes = graph.query(query_classes)
        for row_classes in result_classes:
            query_datatype_property = """
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT DISTINCT ?property ?range
                        WHERE {
                            ?property rdfs:domain %s;
                                a owl:DatatypeProperty.
                            OPTIONAL{ ?property rdfs:range ?range. }
                        } ORDER BY ?property""" % row_classes['class'].n3()
            result_datatype_property = graph.query(query_datatype_property)
            attributes = []
            for r in result_datatype_property:
                text = self.ds.namespace_manager.qname(r['property'])
                if r['range']:
                    text += " = " + self.ds.namespace_manager.qname(r['range'])
                attributes.append(text)
            self.add_class_node(row_classes['class'], attributes)

        query_object_property = """SELECT DISTINCT ?src ?dest ?property
                    WHERE {
                       ?property a <http://www.w3.org/2002/07/owl#ObjectProperty>;
                            rdfs:domain ?src;
                            rdfs:range ?dest.
                    } ORDER BY ?src ?property ?dest"""
        result_object_property = graph.query(query_object_property)
        for row_object_property in result_object_property:
            self.add_edge(row_object_property['src'], row_object_property['dest'], row_object_property['property'])

        query_subclass = """SELECT DISTINCT ?src ?dest
                    WHERE {
                       ?src rdfs:subClassOf ?dest.
                    } ORDER BY ?src ?dest"""
        result_subclass = graph.query(query_subclass)
        for row_subclass in result_subclass:
            self.add_subclass_edge(row_subclass['src'], row_subclass['dest'])


if __name__ == '__main__':
    import argparse
    import sys

    # Initialize command line parser
    parser = argparse.ArgumentParser(description='Creates UML Object Diagram from RDF(S) files')
    parser.add_argument('filename', nargs='+', type=argparse.FileType('r'), help='RDF file(s)')
    parser.add_argument('-o', '--output', dest='out', nargs=1, help='Output graphics file (default is FILENAME.svg)')
    parser.add_argument('-d', '--dot', action='store_true', help='Save DOT file')
    parser.add_argument('-n', '--namespace', metavar=('PREFIX', 'NAMESPACE'), nargs=2, action='append', help='Additional namespaces')
    # Eigenschaften als Klasse anzeigen default=false
    parser.add_argument('--object-nodes', dest='showobjs', action="store_true", default=True, help='Show Objects')
    # Objekte von Klassen anzeigen default=false
    parser.add_argument('--class-nodes', dest='showclasses', action="store_true", default=False, help='Show Classes')
    #
    parser.add_argument('--ontology', dest='add_ontology', action="store_true",
                        help='Add ontology rdfs:definedBy properties')
    # Eingabeformat der Datei angeben, ansonsten wird es aus Dateiendung geraten.
    parser.add_argument('-i', '--input', dest='format', nargs=1, default=(None,), help='Input format (xml, n3, turtle, nt, trix, trig). When blank than it is guessed from file name extension')
    args = parser.parse_args()

    if args.out:
        output = args.out[0]
    else:
        output = args.filename[0].name + '.svg'

    # Klassendiagramm erzeugen
    d = RDFtoUmlDiagram()

    # Darstellungsoptionen
    print("showing objects: " + str(args.showobjs))
    print("showing classes: " + str(args.showclasses))

    # RDF-Format einstellen
    for f in args.filename:
        d.load_rdf(f, args.format[0])
    d.add_namespaces(args.namespace)
    d.create_diagram(args.showobjs, args.showclasses)
    if args.dot:
        d.output_dot(output + ".dot")
    d.visualize(output)

    print("graphic was created with output file name: " + output)
