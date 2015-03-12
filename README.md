rdf-uml-diagram
===============

Graphical representation of RDF set similar to UML diagrams

*rdfUmlDiagram.py* is a python3 script which converts RDF files to PNG diagrams. These are similar to UML diagrams. There are both object diagrams and class diagrams available depending on the command line parameter.

The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)

[![DOI](https://zenodo.org/badge/10866/plt-tud/rdf-uml-diagram.svg)](http://dx.doi.org/10.5281/zenodo.16013)

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




```
./rdfUmlDiagram.py test/cae_example1.ttl
```
![Sample2](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/cae_example1.ttl.png "cae_example1.ttl.png")



```
./rdfUmlDiagram.py test/cae_meta.ttl
```
![Sample4](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/cae_meta.ttl.png "cae_meta.ttl.png")



```
./rdfUmlDiagram.py test/rdftest.ttl
```
![Sample4](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/rdftest.ttl.png "rdftest.ttl.png")

