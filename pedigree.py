#!/usr/bin/env python

import yaml
import hashlib
import subprocess
from docopt import docopt
import os
import pedigree_lib

version = '0.1.0'

help_text = """pedigree.py

Usage:
  pedigree.py [--yaml-filename=<filename>] [--base-filename=<filename>]
  pedigree.py cleanup
  pedigree.py -h | --help
  pedigree.py --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -y --yaml-filename=<filename>  .yaml file containing relations for tree.
                                 [DEFAULT: relations.yaml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  cleanup                        Delete generated files (XXX.svg, etc.)"""


def main(yaml_filename, file_basename):

  # Open the YAML file or fail gracefully
  try:
    with open(yaml_filename) as f:
      biglist = list(yaml.load_all(f))
  except IOError, e:
    print("\n\033[91mCouldn't open {}\033[0m\n".format(e.filename))
    print(help_text)
    exit(1)

  # Split into individual lists
  fathers, mothers, spouses, name_to_uid, person_names = \
      pedigree_lib.split_biglist(biglist)

  # Generate d3 html page
  with open('{}.html'.format(file_basename), 'w') as f:
    for line in pedigree_lib.d3_html_page_generator(fathers,
        mothers, spouses):
      f.write(line)


  # Generate graphviz .dot file
  with open('{}.dot'.format(file_basename), 'w') as f:
    f.write("""digraph family_tree {
  """)

    # Set up the nodes
    for person_name in person_names:
      f.write('{} [label="{}", shape="box"];\n'.format(pedigree_lib.uid(person_name),
          person_name))

    # Set up the connections
    f.write("\n\n")
    for father in fathers:
      for child in father['children']:
        f.write('{} -> {} [color=blue];\n'.format(pedigree_lib.uid(father['name']), 
            pedigree_lib.uid(child)))
    f.write("\n\n")
    for mother in mothers:
      for child in mother['children']:
        f.write('{} -> {} [color=orange];\n'.format(
            pedigree_lib.uid(mother['name']), pedigree_lib.uid(child)))
    f.write("\n\n")
    for prime_spouse in spouses:
      for spouse in prime_spouse['spouses']:
        f.write('{} -> {} [style="dotted"];\n'.format(
            pedigree_lib.uid(prime_spouse['name']), pedigree_lib.uid(spouse)))
    f.write("""
  }
  """)

  # Generate .svg from .dot file
  with open('{}.svg'.format(file_basename), 'w') as svg_file:
    subprocess.Popen(['dot', '-Tsvg', '{}.dot'.format(file_basename)],
        stdout=svg_file)

if __name__ == "__main__":
  args = docopt(help_text, version=version)

  base_filename = args['--base-filename']
  yaml_filename = args['--yaml-filename']

  if args['cleanup']:
    for extension in 'svg', 'dot', 'html':
      os.remove('{}.{}'.format(base_filename, extension))
  else:
    main(yaml_filename, base_filename)
