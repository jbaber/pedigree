`pedigree.py` takes a [yaml][] file like that in `examples/example.yaml` ([source][]) and outputs a
few messy visualizations that do not favor patriliny over matriliny.  See `examples/` for example output.

![Screenshot 1](media/screenshot1.png)
![Screenshot 2](media/screenshot2.png)

Outputs:
--------
  - `.html` file: a [d3][] visualization that can be opened in a web browser
  - `.svg` file: a "Sugiyama style" tree that can be opened in a web browser
  - `.dot` file: the [dot][] file used to generate the `.svg` file

Caveats:
--------
  - Don't put all your genealogical data in one text file that you manipulate via a python script written by some idiot on the internet.  At least make copies of the one text file.
  - This can only recognize the relations `x is the mother of y`, `x is the father of y`, and `x is the spouse of y`.  It has no concept of siblings or partial siblings.
  - The `.yaml` file depends on every name to be unique, so you may need names like `John Smith (2)` and `John Smith (1)`.

Until I figure out [how to make a Python package][ugh] (or someone does it
right in a fork), I will list dependencies here:
  - Python Packages:
    - `pip install --user` [docopt][] [networkx][] [PyYAML][] easygui
  - Linux programs:
    - `sudo apt-get install` [graphviz][dot]

[yaml]: https://en.wikipedia.org/wiki/YAML
[PyYAML]: http://pyyaml.org
[d3]: http://d3js.org/
[dot]: https://en.wikipedia.org/wiki/Graphviz
[ugh]: http://blog.ionelmc.ro/2015/02/24/the-problem-with-packaging-in-python/
[docopt]: http://docopt.org/
[source]: https://en.wikipedia.org/wiki/Template:Flintstones_family_tree
[networkx]: http://networkx.github.io/documentation/latest/overview.html
