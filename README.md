rdf-uml-diagram
===============

Graphical representation of RDF set similar to UML diagrams

*rdfUmlDiagram.py* is a python3 script which converts RDF files to PNG diagrams. These are similar to UML diagrams. There are both object diagrams and class diagrams available depending on the command line parameter.

The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)
Its executable *dot* has to be on PATH.

It uses SPARQL to get nodes. Thus, also *rdflib* (https://github.com/RDFLib) is required.


