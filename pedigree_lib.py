import hashlib
import re


class GenealogicalError(Exception):
  pass


class Family:
  """
  Represent a family as a collection of `fathers`, `mothers`,
  and `spouses`.  Each member is identified as just a unique
  name.  i.e. just a string
  """
  def __init__(self, fathers, mothers, spouses):
    self.fathers = fathers
    self.mothers = mothers
    self.spouses = spouses
    self.person_names = set()

    # Record every individual in `person_names`
    for father in fathers:
      self.person_names.add(father['name'])
      for child in father['children']:
        self.person_names.add(child)
    for mother in mothers:
      self.person_names.add(mother['name'])
      for child in mother['children']:
        self.person_names.add(child)
    for prime_spouse in spouses:
      self.person_names.add(prime_spouse['name'])
      for spouse in prime_spouse['spouses']:
        self.person_names.add(spouse)

  def father(self, person):
    for father in self.fathers:
      if person in father['children']:
        return father['name']
    return None

  def mother(self, person):
    for mother in self.mothers:
      if person in mother['children']:
        return mother['name']
    return None

  def new_anonymous_name(self):
    """
    Collect all names of the form '????...'
    and return a new string of ?'s one longer than the
    longest
    """
    anons = [
      len(anon)
      for anon
      in self.person_names
      if re.match('^\?+$', anon)
    ]
    if anons == []:
      longest = 0
    else:
      longest = max(anons)
    return '?' * (longest + 1)

  def add_father(self, child, father):

    # Error on already existing father
    if self.father(child) != None:
      raise GenealogicalError(
          "{0} already has a father ({1})".format(child,
              self.father(child)))

    # Error on father and child the same
    if child == father:
      raise GenealogicalError(
          "{0} can't father himself".format(child))

    # If already a father of someone else, add to children
    # list
    dad_found = False
    for cur_dad in self.fathers:
      if cur_dad['name'] == father:
        dad_found = True
        if child not in cur_dad['children']:
          cur_dad['children'].append(child)
    # Otherwise, invent the father and add the child
    if not dad_found:
      self.person_names.add(father)
      self.fathers.append({'name': father, 'children': [child]})

  def name_to_uid(self, name):
    return uid(name)


def uid(name):
  """Give a unique id to any name"""
  return "personhash" + hashlib.md5(name).hexdigest()


def biglist_to_family(biglist):
  """
  Take `biglist` as would be returned from a .yaml file
  and return corresponding Family instance
  """
  return Family(*split_biglist(biglist))


def split_biglist(biglist):
  """
  Take `biglist` as would be returned from a .yaml file
  and return corresponding lists

      (fathers, mothers, spouses)

  e.g. `biglist` like

      biglist = [                                  \
        {'father': {'a': ['b', 'c'], 'd': ['e']}}, \
        {'mother': {'f': ['g', 'h'], 'i': ['j']}}, \
        {'spouse': {'k': ['l', 'm'], 'n': ['o']}}, \
      ]

  yields

      [{'name': 'a', 'children': ['b', 'c']},
      {'name': 'd', 'children': ['e']},
      ],
      [{'name': 'i', 'children': ['j']},
      {'name': 'f', 'children': ['g', 'h']},
      ],
      [{'name': 'k', 'spouses': ['l', 'm']},
      {'name': 'n', 'spouses': ['o']},
      ]
  """
  fathers_dict = biglist[0]['father']
  mothers_dict = biglist[1]['mother']
  spouses_dict = biglist[2]['spouse']

  # Make lists so that index in the lists gives a unique
  # identifier
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

  return fathers, mothers, spouses


def join_biglist(fathers, mothers, spouses):
  """
  This function should be the inverse of `split_biglist`.
  
  e.g.

      fathers = [{'name': 'a', 'children': ['b', 'c']},
      {'name': 'd', 'children': ['e']},
      ]
      mothers = [{'name': 'i', 'children': ['j']},
      {'name': 'f', 'children': ['g', 'h']},
      ]
      spouses = [{'name': 'k', 'spouses': ['l', 'm']},
      {'name': 'n', 'spouses': ['o']},
      ]

  should yield
      [                                            \
        {'father': {'a': ['b', 'c'], 'd': ['e']}}, \
        {'mother': {'f': ['g', 'h'], 'i': ['j']}}, \
        {'spouse': {'k': ['l', 'm'], 'n': ['o']}}, \
      ]

  """
  return [
    {'father': dict( (father['name'], father['children'])
          for father
          in fathers
    )},
    {'mother': dict( (mother['name'], mother['children'])
          for mother
          in mothers
    )},
    {'spouse': dict( (spouse['name'], spouse['spouses'])
          for spouse
          in spouses
    )}
  ]


def d3_html_page_generator(family):
  """Yield lines of an html page showing connections"""
  yield """<!DOCTYPE html>
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
  """
  yield '"father": {\n'
  for father in family.fathers:
    yield '"{}": [\n'.format(father['name'])
    for child in father['children']:
      yield '"{}",\n'.format(child)
    yield '],\n'
  yield '},\n'
  yield '"mother": {\n'
  for mother in family.mothers:
    yield '"{}": [\n'.format(mother['name'])
    for child in mother['children']:
      yield '"{}",\n'.format(child)
    yield '],\n'
  yield '},\n'
  yield '"spouse": {\n'
  for prime_spouse in family.spouses:
    yield '"{}": [\n'.format(prime_spouse['name'])
    for spouse in prime_spouse['spouses']:
      yield '"{}",\n'.format(spouse)
    yield '],\n'
  yield '}\n'
  yield """
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
</body>
</html>
"""


def dot_file_generator(family):
  """Generate a graphviz .dot file"""

  yield "digraph family_tree {\n"

  # Set up the nodes
  for person_name in family.person_names:
    yield '  {} [label="{}", shape="box"];\n'.format(
        uid(person_name), person_name)

  # Set up the connections
  yield "\n\n"
  for father in family.fathers:
    for child in father['children']:
      yield '  {} -> {} [color=blue];\n'.format(
          uid(father['name']), 
          uid(child))
  yield "\n\n"
  for mother in family.mothers:
    for child in mother['children']:
      yield '  {} -> {} [color=orange];\n'.format(
          uid(mother['name']),
          uid(child))
  yield "\n\n"
  for prime_spouse in family.spouses:
    for spouse in prime_spouse['spouses']:
      yield '  {} -> {} [style="dotted"];\n'.format(
          uid(prime_spouse['name']),
          uid(spouse))
  yield "\n}\n"
