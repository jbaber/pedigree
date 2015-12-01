#!/usr/bin/env python

import yaml
import hashlib
import subprocess
from docopt import docopt
import os

version = '0.1.0'

def main(yaml_filename, file_basename):

  with open(yaml_filename) as f:
    biglist = list(yaml.load_all(f))

  fathers_dict = biglist[0]['father']
  mothers_dict = biglist[1]['mother']
  spouses_dict = biglist[2]['spouse']

  # Make lists so that index in the lists gives a unique identifier
  # Also makes room for later information
  fathers = []
  mothers = []
  spouses = []
  for father in fathers_dict:
    fathers.append(
      {'name': father, 'children': fathers_dict[father]}
    )
  for mother in mothers_dict:
    mothers.append(
      {'name': mother, 'children': mothers_dict[mother]}
    )
  for prime_spouse in spouses_dict:
    spouses.append(
      {'name': prime_spouse, 'spouses': spouses_dict[prime_spouse]}
    )

  # Give everyone a unique id
  def uid(name):
    return "personhash" + hashlib.md5(name).hexdigest()

  # Make a backwards lookup table and record every person
  person_names = set()
  name_to_uid = {}
  for father in fathers:
    name_to_uid[father['name']] = uid(father['name'])
    person_names.add(father['name'])
    for child in father['children']:
      name_to_uid[child] = uid(child)
      person_names.add(child)
  for mother in mothers:
    name_to_uid[mother['name']] = uid(mother['name'])
    person_names.add(mother['name'])
    for child in mother['children']:
      name_to_uid[child] = uid(child)
      person_names.add(child)
  for prime_spouse in spouses:
    name_to_uid[prime_spouse['name']] = uid(prime_spouse['name'])
    person_names.add(prime_spouse['name'])
    for spouse in prime_spouse['spouses']:
      name_to_uid[spouse] = uid(spouse)
      person_names.add(spouse)

  # Generate d3 html page
  with open('{}.html'.format(file_basename), 'w') as f:
    f.write("""
  <!DOCTYPE html>
  <meta charset="utf-8">
  <style>

  .link {
    fill: none;
    stroke: #666;
    stroke-width: 1.5px;
  }

  #mother {
    fill: red;
  }
  .link.mother {
    stroke: red;
  }

  #father {
    fill: blue;
  }
  .link.father {
    stroke: blue;
  }

  .link.spouse {
    stroke-dasharray: 0,7 1;
  }

  circle {
    fill: #ccc;
    stroke: #333;
    stroke-width: 1.5px;
  }

  text {
    font: 10px sans-serif;
    pointer-events: none;
    text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff;
    background:red;
  }

  </style>
  <body>
  <script src="http://d3js.org/d3.v3.min.js"></script>
  <script>

  var links = [];

  function addRelation(sourcey, targety, relationy, listy) {
    listy.push({source: sourcey, target: targety, type: relationy})
  }
  family = {
  """)
    f.write('"father": {\n')
    for father in fathers:
      f.write('"{}": [\n'.format(father['name']))
      for child in father['children']:
        f.write('"{}",\n'.format(child))
      f.write('],\n')
    f.write('},\n')
    f.write('"mother": {\n')
    for mother in mothers:
      f.write('"{}": [\n'.format(mother['name']))
      for child in mother['children']:
        f.write('"{}",\n'.format(child))
      f.write('],\n')
    f.write('},\n')
    f.write('"spouse": {\n')
    for prime_spouse in spouses:
      f.write('"{}": [\n'.format(prime_spouse['name']))
      for spouse in prime_spouse['spouses']:
        f.write('"{}",\n'.format(spouse))
      f.write('],\n')
    f.write('}\n')
    f.write("""
  }

  for (var relation in family) {
    for (var relator in family[relation]) {
      if (family[relation].hasOwnProperty(relator)) {
        numChildren = family[relation][relator].length;
        for (var i = 0; i < numChildren; i++) {
          addRelation(relator, family[relation][relator][i], relation, links);
        }
      }
    }
  }

  var nodes = {};

  // Compute the distinct nodes from the links.
  links.forEach(function(link) {
    link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
    link.target = nodes[link.target] || (nodes[link.target] = {name: link.target});
  });

  var width = 2 * 1260,
      height = 2 * 800;

  var force = d3.layout.force()
      .nodes(d3.values(nodes))
      .links(links)
      .size([width, height])
      .chargeDistance(400)
      .linkDistance(60)
      .gravity(0.01)
      .charge(-300)
      .on("tick", tick)
      .start();

  var svg = d3.select("body").append("svg")
      .attr("width", width)
      .attr("height", height);

  // Per-type markers, as they don't inherit styles.
  svg.append("defs").selectAll("marker")
      .data(["father", "mother", "spouse"])
    .enter().append("marker")
      .attr("id", function(d) { return d; })
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 15)
      .attr("refY", -1.5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
    .append("path")
      .attr("d", "M0,-5L10,0L0,5");

  var path = svg.append("g").selectAll("path")
      .data(force.links())
    .enter().append("path")
      .attr("class", function(d) { return "link " + d.type; })
      .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });

  var circle = svg.append("g").selectAll("circle")
      .data(force.nodes())
    .enter().append("circle")
      .attr("r", 6)
      .call(force.drag);

  var text = svg.append("g").selectAll("text")
      .data(force.nodes())
    .enter().append("text")
      .attr("x", 8)
      .attr("y", ".31em")
      .text(function(d) { return d.name; });

  // Use elliptical arc path segments to doubly-encode directionality.
  function tick() {
    path.attr("d", linkArc);
    circle.attr("transform", transform);
    text.attr("transform", transform);
  }

  function linkArc(d) {
    var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);
    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
  }

  function transform(d) {
    return "translate(" + d.x + "," + d.y + ")";
  }

  </script>

  """)

  # Generate graphviz .dot file
  with open('{}.dot'.format(file_basename), 'w') as f:
    f.write("""digraph family_tree {
  """)

    # Set up the nodes
    for person_name in person_names:
      f.write('{} [label="{}", shape="box"];\n'.format(uid(person_name),
          person_name))

    # Set up the connections
    f.write("\n\n")
    for father in fathers:
      for child in father['children']:
        f.write('{} -> {} [color=blue];\n'.format(uid(father['name']), 
            uid(child)))
    f.write("\n\n")
    for mother in mothers:
      for child in mother['children']:
        f.write('{} -> {} [color=orange];\n'.format(
            uid(mother['name']), uid(child)))
    f.write("\n\n")
    for prime_spouse in spouses:
      for spouse in prime_spouse['spouses']:
        f.write('{} -> {} [style="dotted"];\n'.format(
            uid(prime_spouse['name']), uid(spouse)))
    f.write("""
  }
  """)

  # Generate .svg from .dot file
  with open('{}.svg'.format(file_basename), 'w') as svg_file:
    subprocess.Popen(['dot', '-Tsvg', '{}.dot'.format(file_basename)],
        stdout=svg_file)

if __name__ == "__main__":
  help_text = """generate.py

Usage:
  generate.py [--yaml-filename=<filename>] [--base-filename=<filename>]
  generate.py cleanup
  generate.py -h | --help
  generate.py --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -y --yaml-filename=<filename>  .yaml file containing relations for tree.
                                 [DEFAULT: relations.yaml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  cleanup                        Delete generated files (XXX.svg, etc.)"""

  args = docopt(help_text, version=version)

  base_filename = args['--base-filename']
  yaml_filename = args['--yaml-filename']

  if args['cleanup']:
    for extension in 'svg', 'dot', 'html':
      os.remove('{}.{}'.format(base_filename, extension))
  else:
    main(yaml_filename, base_filename)
