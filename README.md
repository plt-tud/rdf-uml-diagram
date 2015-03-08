rdf-uml-diagram
===============

Graphical representation of RDF set similar to UML diagrams

*rdfUmlDiagram.py* is a python3 script which converts RDF files to PNG diagrams. These are similar to UML diagrams. There are both object diagrams and class diagrams available depending on the command line parameter.

The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)

Dependencies
------------
* Python3
    * rdflib (https://github.com/RDFLib)
    * pygraphviz (https://pygraphviz.github.io/)

Examples
--------
```
./rdfUmlDiagram.py test/test.trig
```
![Sample1](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/test.trig.png "test.trig.png")



