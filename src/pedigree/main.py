#!/usr/bin/env python3

import subprocess
from docopt import docopt
import os
from pedigree import pedigree_lib

version = '1.0.0'

help_text = """pedigree

When run via

    pedigree -f relations.toml

starts a primitive GUI to interact with and edit your relations.toml file.  (If you don't give a `relations.toml` a blank one will
be created for you.)

For a quick example, generate the example .toml file

    pedigree -f new_relations.toml

then generate output based on it

    pedigree -f new_relations.toml generate

Usage:
  pedigree [--toml-filename=<filename>]
  pedigree generate [--base-filename=<filename>] [--toml-filename=<filename>] 
  pedigree cleanup [--base-filename=<filename>]
  pedigree -h | --help
  pedigree --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -f --toml-filename=<filename>  .toml file containing relations for tree.
                                 [DEFAULT: relations.toml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  cleanup                        Delete generated files (XXX.svg, etc.)
  generate                       Simply create the .svg, .dot, .html files
"""

def main():
  args = docopt(help_text, version=version)
  base_filename = args['--base-filename']
  toml_filename = args['--toml-filename']

  # If toml file doesn't exist or is completely empty, create a blank one
  if not os.path.exists(toml_filename) or os.stat(toml_filename).st_size == 0:
    pedigree_lib.create_example_toml(toml_filename)

  if args['cleanup']:
    pedigree_lib.cleanup_files(toml_filename, base_filename)

  elif args['generate']:
    pedigree_lib.generate_files(toml_filename, base_filename)


if __name__ == "__main__":
  main()
