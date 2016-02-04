- [Package][] properly
- Protect names with funny characters (e.g. quotaton marks) from interpretation
  by yaml.
- Make `interact` behavior the default
  - Then make it possible for someone to create a brand new family
    interactively.
- Generate `.svg` file from `.dot` in some purely Python way so that
  linux command line isn't necessary.
- Make a menu option to change a person's name
  - Make a family.change_name(person)
- Use other output formats from `dot`.
- Make a prettier gui
  - Maybe ncurses, as well
  - Maybe a webpage interface, too
- Use images in some of the visualizations
- Handle empty `father`, `mother`, `spouse`, and/or `notes` tables.
- Come up with a syntax for attaching notes to edges as well as individuals
- Make colors specifiable
- Give option to favor patriliny over matriliny or vice-versa
  to make a planar graph.
- Add ability to make visualizations that have anonymized names
  and/or only first names.
- Somehow add tests for GUI stuff.
- Handle "add children to a couple"
- Handle "add children to a couple" when no couple exists
- Add spouses to list in "add children to a couple"
- Handle "add children to a couple" when user wants to add a new couple

[Package]: http://blog.ionelmc.ro/2015/02/24/the-problem-with-packaging-in-python/
