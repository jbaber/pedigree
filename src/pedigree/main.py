#!/usr/bin/env python3

import subprocess
from docopt import docopt
import os
from pedigree import pedigree_lib

version = '1.0.0'

help_text = """pedigree

For a quick example, generate the example .toml file

    pedigree -f new_relations.toml

then generate output based on it

    pedigree -f new_relations.toml generate

Usage:
  pedigree [options] generate
  pedigree [options] cleanup
  pedigree [options]
  pedigree --help
  pedigree --version

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -f --toml-filename=<filename>  .toml file containing relations for tree.
                                 If <filename> doesn't exist, a new file
                                 with that name will be created with an
                                 example inside.
                                 [DEFAULT: relations.toml]
  -b --base-filename=<filename>  XXX in output filenames XXX.svg, XXX.html, ...
                                 [DEFAULT: family_tree]
  -x --exclude-surnames          Only show the initial letter of surnames making
                                 your tree safe(r) to share publicly.  This is
                                 necessary since "Mother's maiden name" is used
                                 as a sort of password for lots of sensitive
                                 applications
  -X --exclude-middle-names      Don't show middle names (some family
                                 naming conventions would reveal maiden
                                 names via middle names)
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
    if args["--exclude-surnames"] and args["--exclude-middle-names"]:
      style = "last initial, no middle names"
    elif args["--exclude-surnames"]:
      style = "last initial"
    elif args["--exclude-middle-names"]:
      style = "no middle names"
    else:
      style = "full name"

    pedigree_lib.generate_files(toml_filename, base_filename, style)


if __name__ == "__main__":
  main()
