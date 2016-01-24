- Add screenshots
- [Package][] properly
- Generate `.svg` file from `.dot` in some purely Python way so that
  linux command line isn't necessary.
- Use other output formats from `dot`.
- Simple menu-based program for inputting names as they're
  told to you by relatives.
  - Genealogy is usual spoken as "X and Y had these 3 kids: ..." and
    "X had 3 brothers: ..." both of which are complicated to enter
    into the `.yaml` file directly.
  - One in ncurses for *nix and mac
  - One in qt for windows
  - One with a simple webpage interface.
- Use images in some of the visualizations
- Handle empty `father`, `mother`, `spouse`, and/or notes tables.
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
