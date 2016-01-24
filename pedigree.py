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
  pedigree.py [--base-filename=<filename>] [--yaml-filename=<filename>] 
  pedigree.py interact [--yaml-filename=<filename>] 
  pedigree.py cleanup [--base-filename=<filename>] 
  pedigree.py -h | --help
  pedigree.py --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -y --yaml-filename=<filename>  .yaml file containing relations for tree.
                                 [DEFAULT: relations.yaml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  cleanup                        Delete generated files (XXX.svg, etc.)
  interact                       Start a GUI to alter the database"""


def main(yaml_filename, file_basename):

  # Open the YAML file or fail gracefully
  try:
    with open(yaml_filename) as f:
      family = pedigree_lib.yaml_to_family(f)
  except IOError, e:
    print("\n\033[91mCouldn't open {}\033[0m\n".format(e.filename))
    print(help_text)
    exit(1)

  # Generate d3 html page
  with open('{}.html'.format(file_basename), 'w') as f:
    for line in pedigree_lib.d3_html_page_generator(family):
      f.write(line)

  # Generate graphviz .dot file
  with open('{}.dot'.format(file_basename), 'w') as f:
    for line in pedigree_lib.dot_file_generator(family):
      f.write(line)

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
  elif args['interact']:
    pedigree_lib.interact(yaml_filename)
  else:
    main(yaml_filename, base_filename)
