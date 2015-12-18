import hashlib


def uid(name):
  """Give a unique id to any name"""
  return "personhash" + hashlib.md5(name).hexdigest()


def split_biglist(biglist):
  """
  Take `biglist` as would be returned from a .yaml file
  and return corresponding lists

      (fathers, mothers, spouses, name_to_uid, person_names)

  where the dict `name_to_uid` takes each person's name to
  their uid and `person_names` is a set containing only the
  names of people

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
      ],
      {'a': 'personhash0cc175b9c0f1b6a831c399e269772661',
      'b': 'personhash92eb5ffee6ae2fec3ad71c777531578f',
      'c': 'personhash4a8a08f09d37b73795649038408b5f33',
      'd': 'personhash8277e0910d750195b448797616e091ad',
      'e': 'personhashe1671797c52e15f763380b45e841ec32',
      'f': 'personhash8fa14cdd754f91cc6554c9e71929cce7',
      'g': 'personhashb2f5ff47436671b6e533d8dc3614845d',
      'h': 'personhash2510c39011c5be704182423e3a695e91',
      'i': 'personhash865c0c0b4ab0e063e5caa3387c1a8741',
      'j': 'personhash363b122c528f54df4a0446b6bab05515',
      'k': 'personhash8ce4b16b22b58894aa86c421e8759df3',
      'l': 'personhash2db95e8e1a9267b7a1188556b2013b33',
      'm': 'personhash6f8f57715090da2632453988d9a1501b',
      'n': 'personhash7b8b965ad4bca0e41ab51de7b31363a1',
      'o': 'personhashd95679752134a2d9eb61dbd7b91c4bcc'
      },
      set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
          'k', 'l', 'm', 'n', 'o']),
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

  return fathers, mothers, spouses, name_to_uid, person_names

def d3_html_page_generator(fathers, mothers, spouses):
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
  for father in fathers:
    yield '"{}": [\n'.format(father['name'])
    for child in father['children']:
      yield '"{}",\n'.format(child)
    yield '],\n'
  yield '},\n'
  yield '"mother": {\n'
  for mother in mothers:
    yield '"{}": [\n'.format(mother['name'])
    for child in mother['children']:
      yield '"{}",\n'.format(child)
    yield '],\n'
  yield '},\n'
  yield '"spouse": {\n'
  for prime_spouse in spouses:
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
