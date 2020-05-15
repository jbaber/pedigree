`pedigree` takes a [toml][] file like that in `examples/example.toml` ([source][]) and outputs a
few messy visualizations that do not favor patriliny over matriliny.  See `examples/` for example output.

![Screenshot 1](media/screenshot1.png)

Example:
--------
For a quick example, generate the example .toml file

    pedigree -f new_relations.toml

then generate output based on it

    pedigree -f new_relations.toml generate

Outputs:
--------
  - `.html` file: a [d3][] visualization that can be opened in a web browser
  - SVG broken for now
    - `.svg` file: a "Sugiyama style" tree that can be opened in a web browser
    - `.dot` file: the [dot][] file used to generate the `.svg` file

Installation:
-------------

    pip3 install pedigree

`pedigree --help` will tell you your options.

Caveats:
--------
  - Don't put all your genealogical data in one text file that you manipulate via a python script written by some idiot on the internet.  At least make copies of the one text file.
  - This can only recognize the relations `x is the mother of y`, `x is the father of y`, and `x is the spouse of y`.  It has no concept of siblings or partial siblings.


[toml]: https://en.wikipedia.org/wiki/TOML
[d3]: http://d3js.org/
[dot]: https://en.wikipedia.org/wiki/Graphviz
[source]: https://en.wikipedia.org/wiki/Template:Flintstones_family_tree
