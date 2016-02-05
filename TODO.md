- [Package][] properly
- Make `interact` behavior the default
  - Then make it possible for someone to create a brand new family
    interactively.
- Generate `.svg` file from `.dot` in some purely Python way so that
  linux command line isn't necessary.
- Use other output formats from `dot`.
- Make a prettier gui
  - Maybe ncurses, as well
  - Maybe a webpage interface, too
  - Maybe kivy
- Use images in some of the visualizations
- Handle empty `father`, `mother`, `spouse`, and/or `notes` tables.
- Come up with a syntax for attaching notes to edges as well as individuals
- Make colors specifiable
- Give option to favor patriliny over matriliny or vice-versa
  to make a planar graph.
- Add ability to make visualizations that have anonymized names
  and/or only first names.
- Somehow add tests for GUI stuff.

[Package]: http://blog.ionelmc.ro/2015/02/24/the-problem-with-packaging-in-python/
