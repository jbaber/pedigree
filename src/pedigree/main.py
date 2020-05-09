#!/usr/bin/env python3

import subprocess
from docopt import docopt
import os
from pedigree import pedigree_lib

version = '0.1.0'

help_text = """pedigree

When run via

    pedigree -y relations.yaml

starts a primitive GUI to interact with and edit your relations.yaml file.  (If you don't give a `relations.yaml` a blank one will
be created for you.)

For a quick example

    pedigree -y examples/example.yaml

Usage:
  pedigree [--yaml-filename=<filename>]
  pedigree generate [--base-filename=<filename>] [--yaml-filename=<filename>] 
  pedigree cleanup [--base-filename=<filename>]
  pedigree -h | --help
  pedigree --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -y --yaml-filename=<filename>  .yaml file containing relations for tree.
                                 [DEFAULT: relations.yaml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  cleanup                        Delete generated files (XXX.svg, etc.)
  generate                       Simply create the .svg, .dot, .html files
"""

def main():
  args = docopt(help_text, version=version)
  base_filename = args['--base-filename']
  yaml_filename = args['--yaml-filename']

  # If yaml file doesn't exist or is completely empty, create a blank one
  if not os.path.exists(yaml_filename) or os.stat(yaml_filename).st_size == 0:
    pedigree_lib.create_blank_yaml(yaml_filename)

  if args['cleanup']:
    pedigree_lib.cleanup_files(yaml_filename, base_filename)

  elif args['generate']:
    pedigree_lib.generate_files(yaml_filename, base_filename)

  else:
    pedigree_lib.interact(yaml_filename)

if __name__ == "__main__":
  main()
