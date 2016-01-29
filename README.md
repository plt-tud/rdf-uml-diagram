rdf-uml-diagram
===============

Graphical representation of RDF set similar to UML diagrams

*rdfUmlDiagram.py* is a python3 script which converts RDF files to PNG diagrams. These are similar to UML diagrams. There are both object diagrams and class diagrams available depending on the command line parameter.

The layout is done by Graphviz (http://www.graphviz.org/) which has to be installed (version>2.30)

[![DOI](https://zenodo.org/badge/10866/plt-tud/rdf-uml-diagram.svg)](http://dx.doi.org/10.5281/zenodo.16013)

Dependencies
------------
The tool needs the following tools
* GraphViz (http://www.graphviz.org/)
* Python3 and the following Python3 libraries
    * rdflib (https://github.com/RDFLib)
    * pygraphviz (https://pygraphviz.github.io/)



You can install them via pip (take care to use )
```
apt-get install libgraphviz-dev
pip3 install rdflib pygraphviz
```

Examples
--------
```
python3 rdfUmlDiagram.py test/test.trig
```
![Sample1](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/test.trig.png "test.trig.png")




```
python3 rdfUmlDiagram.py test/cae_example1.ttl
```
![Sample2](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/cae_example1.ttl.png "cae_example1.ttl.png")



```
python3 rdfUmlDiagram.py test/cae_meta.ttl
```
![Sample3](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/cae_meta.ttl.png "cae_meta.ttl.png")



```
python3 rdfUmlDiagram.py test/rdftest.ttl
```
![Sample4](https://github.com/plt-tud/rdf-uml-diagram/blob/master/test/rdftest.ttl.png "rdftest.ttl.png")
