import hashids
import re
import networkx as nx
import tempfile
from urllib.request import pathname2url
import webbrowser
import os
import subprocess
import time
import logging
from collections import Iterable
import toml

"""
Family is kept as a "directed multigraph" with Persons as
nodes.  Nodes can have more than one directed edge between
them.  Edges have a relation_type attribute that takes one
of the values "spouse", "father", "spouse"

Persons have the attributes "gender" and "other" to be
filled with anything else useful to the person.
"""

class GenderError(Exception):
  pass

class GenealogicalError(Exception):
  pass

class PersonExistsError(Exception):
  pass


class Person:
  """
  Two Persons are identical if they have identical uids.

  `uid` is cast to an integer by the constructor
  `given_names` should be iterable
  """
  def __init__(self, uid, *, surname="", given_names=None, gender="?", nickname=None, notes=None):
    if given_names == None:
      given_names = ["???"]
    if notes == None:
      notes = []
    self.surname = surname
    self.gender = gender
    self.nickname = nickname
    self.notes = notes
    self.uid = int(uid)
    if not isinstance(given_names, Iterable):
      raise TypeError("Person constructor given non-iterable `given_names`")
    if len(given_names) < 1:
      raise TypeError("Person needs at least one given name.")
    self.given_names = given_names

  def from_dict(some_dict):
    try:
      args = {'uid': some_dict['uid']}
      for arg in ("surname", "given_names", "gender", "nickname", "notes",):
        if arg in some_dict:
          args[arg] = some_dict[arg]
      return Person(**args)
    except TypeError as e:
      print("Person.from_dict's argument needs a uid field")
      raise e

  def __hash__(self):
    return self.uid

  def __eq__(self, other):
    return self.uid == other.uid

  def __ne__(self, other):
    return (self.uid != other.uid)

  def __str__(self):
    return " ".join(self.given_names) + " " + self.surname

  def display_string(self, style, with_uid=True):
    if style == "full name":
      to_return = " ".join(self.given_names) + f" {self.surname}"
    elif style == "last initial":
      to_return = " ".join(self.given_names) + f" {self.surname[0]}."
    elif style == "last initial, no middle names":
      to_return = self.given_names[0] + f" {self.surname[0]}."
    elif style == "no middle names":
      to_return = self.given_names[0] + f" {self.surname}"
    else:
      raise ValueError(f"Unknown style '{style}'")

    if with_uid:
      to_return += f" ({self.uid})"

    return to_return

  def __repr__(self):
    return self.surname + ", " + ", ".join(self.given_names) + f"({self.gender})"

  def first_name(self):
    return self.given_names[0]


class Family:
  """
  Family is kept as a "directed multigraph" with Persons as
  nodes.  Nodes can have more than one directed edge between
  them.  Edges have a relation_type attribute that takes one
  of the values "mother", "father", "spouse"

  Represent a family as a collection of Persons each with a
  unique .name property and connections between them.
  """
  def __init__(self, persons=None):
    # Full directed multipgraph of Persons with mother, father,
    # and spouse as all the relation_type's.
    self.graph = nx.MultiDiGraph()
    if persons == None:
      self.graph.add_nodes_from([])
    else:
      self.graph.add_nodes_from(persons)

    # Interesting data about individuals is kept in the
    # `notes` dict, keyed by Persons.  May add pairs
    # of Persons as a key so that notes can be made on
    # edges.
    self.notes = {}

  def __eq__(self, other):
    # Two families are the same if they have the same lists of
    # fathers, mothers, spouses, and same relations between them.
    our_persons = self.persons()
    their_persons = other.persons()
    our_mothers = self.mothers()
    their_mothers = other.mothers()
    our_fathers = self.fathers()
    their_fathers = other.fathers()
    our_spouses = self.spouses()
    their_spouses = other.spouses()
    if sorted(our_persons) != sorted(their_persons):
      return False
    if sorted(our_mothers) != sorted(their_mothers):
      return False
    if sorted(our_fathers) != sorted(their_fathers):
      return False
    if sorted(our_spouses) != sorted(their_spouses):
      return False
    for father in our_fathers:
      if sorted(self.children(father)) != \
          sorted(other.children(father)):
        return False
    for mother in our_mothers:
      if sorted(self.children(mother)) != \
          sorted(other.children(mother)):
        return False
    for spouse in our_spouses:
      if sorted(self.all_spouses(spouse)) != \
          sorted(other.all_spouses(spouse)):
        return False

    return True

  def __ne__(self, other):
    return not (self == other)

  def add_person(self, person):
    self.graph.add_node(person)

  def persons(self):
    return self.graph.nodes()

  def uids(self):
    return [person.uid for person in self.persons()]

  def names(self):
    return [str(person) for person in self.persons()]

  def name_to_person(self, name):
    for person in self.persons():
      if person.name == name:
        return person
    return None

  def uid_to_person(self, uid):
    for person in self.persons():
      if person.uid == uid:
        return person
    raise TypeError(f"No person has UID {uid}")

  def change_name(self, person, new_name):
    person.name = new_name

  def add_note(self, person, new_note):
    if person not in self.notes:
      self.notes[person] = [new_note]
    else:
      self.notes[person].append(new_note)

  def delete_note(self, person, to_be_deleted):
    if person in self.notes:
      if to_be_deleted in self.notes[person]:
        self.notes[person].remove(to_be_deleted)

  def add_child(self, parent, child):

    # Does nothing if `parent` already present
    self.graph.add_node(parent)

    relation_type = None
    if parent.gender == "m":
      relation_type = "father"
    elif parent.gender == "f":
      relation_type = "mother"
    else:
      raise GenderError("Without a gender on {}, can't tell"
          " whether she should be added "
          "as a mother or father.".format(parent))

    self.graph.add_edge(parent, child,
        relation_type=relation_type)

  def add_children(self, parent, children):
    for child in children:
      self.add_child(parent, child)

  def add_spouse(self, person, spouse):
    # Does nothing if `parent` already present
    self.graph.add_node(person)
    self.graph.add_edge(person, spouse, relation_type="spouse")

  def add_spouses(self, person, spouses):
    for spouse in spouses:
      self.add_spouse(person, spouse)

  def add_full_sibling(self, person, sibling):
    if person not in self.persons():
      raise PersonExistsError(
          "{} isn't in the family yet.".format(person))
    # Does nothing if `sibling` already present
    self.graph.add_node(sibling)

    # Add either parent if they don't exist
    if not self.father(person):
      self.add_father(person,
          Person(name=self.new_anonymous_name(), gender="male"))
    if not self.mother(person):
      self.add_mother(person,
          Person(name=self.new_anonymous_name(), gender="female"))

    self.graph.add_edge(self.father(person), sibling,
        relation_type="father")
    self.graph.add_edge(self.mother(person), sibling,
        relation_type="mother")


  def new_anonymous_name(self):
    """
    Collect all names of the form '????...'
    and return a new string of ?'s one longer than the
    longest
    """
    anon_lengths = [
      len(anon)
      for anon
      in self.names()
      if re.match('^\?+$', anon)
    ]
    if anon_lengths == []:
      longest = 0
    else:
      longest = max(anon_lengths)
    return '?' * (longest + 1)

  def add_mother(self, child, mother):

    # Error on already existing mother
    if self.mother(child) != None:
      raise GenealogicalError(
          "{0} already has a mother ({1})".format(child,
              self.mother(child)))

    # Error on mother and child the same
    if child == mother:
      raise GenealogicalError(
          "{0} can't mother herself".format(child))

    # Error on non-female mother
    if mother.gender != "female":
      raise GenderError("{0} isn't female, so can't " \
          "be a mother.".format(mother))

    # If already a mother of someone else, add to children
    # list
    mom_found = False
    for cur_mom in self.mothers():
      if cur_mom == mother:
        mom_found = True
        if child not in self.children(cur_mom):
          self.add_child(cur_mom, child)

    # Otherwise, add the mother and add the child
    if not mom_found:
      self.add_person(mother)
      self.add_child(mother, child)

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

    # Error on non-male father
    if father.gender != "male":
      raise GenderError("{0} isn't male, so can't " \
          "be a father.".format(father))

    # If already a father of someone else, add to children
    # list
    dad_found = False
    for cur_dad in self.fathers():
      if cur_dad == father:
        dad_found = True
        if child not in self.children(cur_dad):
          self.add_child(cur_dad, child)

    # Otherwise, add the father and add the child
    if not dad_found:
      self.add_person(father)
      self.add_child(father, child)


  def children(self, parent):
    if parent not in self.persons():
      raise PersonExistsError(
          "{} isn't in the family yet.".format(parent))

    return [
      edge[1]
      for edge in self.graph.edges(data=True)
      if (edge[2]['relation_type'] == "father" or \
          edge[2]['relation_type'] == "mother") and \
         edge[0] == parent
    ]

  def fathers(self):
    return set([
        edge[0]
        for edge in self.graph.edges(data=True)
        if edge[2]['relation_type'] == "father"
    ])
  def mothers(self):
    return set([
        edge[0]
        for edge in self.graph.edges(data=True)
        if edge[2]['relation_type'] == "mother"
    ])
  def spouses(self):
    return set([
        edge[0]
        for edge in self.graph.edges(data=True)
        if edge[2]['relation_type'] == "spouse"
    ])

  def couples(self):
    """
    Return pairs `sorted([one, two])` for any pairs of people
    `one` and `two` who share at least one child *or* are
    spouses
    """
    to_return = []
    for father in self.fathers():
      for child in self.children(father):
        mother = self.mother(child)
        if mother:
          if sorted([father, mother]) not in to_return:
            to_return.append(sorted([father, mother]))
    for super_spouse in self.spouses():
      for sub_spouse in self.all_spouses(super_spouse):
        if sorted([super_spouse, sub_spouse]) not in to_return:
          to_return.append(sorted([super_spouse, sub_spouse]))
    return to_return

  def father(self, person):
    for edge in self.graph.edges(data=True):
      if edge[2]['relation_type'] == "father" and \
          edge[1] == person:
        return edge[0]
    return None
  def mother(self, person):
    for edge in self.graph.edges(data=True):
      if edge[2]['relation_type'] == "mother" and \
          edge[1] == person:
        return edge[0]
    return None
  def all_spouses(self, person):
    cur_spouses = []
    for edge in self.graph.edges(data=True):
      if edge[2]['relation_type'] == "spouse" and \
        edge[0] == person:
          cur_spouses.append(edge[1])
    return cur_spouses
  def persons(self):
    return self.graph.nodes()

  def gui_choose_person(self, message, title, persons=None):
    if persons == None:
      persons = self.persons()
    chosen = easygui.choicebox(message, title,
      [person.name for person in persons]
    )
    return self.name_to_person(chosen)

  def gui_choose_note(self, person, title):
    if person not in self.notes:
      return None

    chosen = easygui.choicebox("Which note?", title,
      ["- " + note for note in self.notes[person]]
    )
    return chosen[2: ]

  def gui_display_notes(self, person):
    easygui.textbox(
      person.name,
      "",
      "\n".join(["- " + note for note in self.notes[person]])
    )

  def gui_choose_person_or_add(self, message, title, gender=None):
    chosen = easygui.choicebox(message, title,
        [person.name for person in self.persons()] + \
        ["**** Add a new person ****"]
      )
    if not chosen:
      return None
    if chosen == "**** Add a new person ****":
      new_name = easygui.enterbox(
        "Enter the new person's name", title)
      if not new_name:
        return None
      if not gender:
        given = easygui.choicebox("Gender", title,
          ["Male", "Female"]
        )
        gender = given.lower()
      new_person = Person(new_name, gender)
      self.add_person(new_person)
      return new_person
    else:
      return self.name_to_person(chosen)

  def people_with_notes(self):
    return [
        person
        for person in self.persons()
        if person in self.notes
      ]

  def string_to_couple(self, string):
    """
    Given "Larry and Bill" return the pair of Persons
    (Larry, Bill)
    """
    first_name, second_name = string.split(" and ", 1)
    return (self.name_to_person(first_name),
        self.name_to_person(second_name))

  def gui_choose_couple_or_add(self, message, title):
    chosen = easygui.choicebox(message, title,
        ["{} and {}".format(couple[0].name, couple[1].name)
          for couple in self.couples()] + \
        ["**** Add a new couple ****"]
      )
    if not chosen:
      return None
    if chosen == "**** Add a new couple ****":
      person_1 = self.gui_choose_person_or_add("First member of the couple:", title)
      person_2 = self.gui_choose_person_or_add("Second member of the couple:", title)
      if person_1 and person_2:
        return (person_1, person_2)
      return None
    else:
      return self.string_to_couple(chosen)

  def gui_add_person(self, message, title, gender=None):
    new_name = easygui.enterbox(message, title)
    if not new_name:
      return None
    if not gender:
      given = easygui.choicebox("Gender", title,
        ["Male", "Female"]
      )
      gender = given.lower()
    new_person = Person(new_name, gender)
    self.add_person(new_person)
    return new_person


def split_biglist(biglist):
  """
  Take `biglist` as would be returned from a .yaml file
  and return corresponding lists

      (fathers, mothers, spouses, notes)

  e.g. `biglist` like

      biglist = [                                  \
        {'father': {'a': ['b', 'c'], 'd': ['e']}}, \
        {'mother': {'f': ['g', 'h'], 'i': ['j']}}, \
        {'spouse': {'k': ['l', 'm'], 'n': ['o']}}, \
        {'notes': {'f': ['This one', 'and another'], 'k': ['more notes']}}, \
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
      [{'name': 'f', 'notes': ['This one', 'and another']},
      {'name': 'k', 'notes': ['more notes']},
      ]
  """
  fathers_dict = biglist[0]['father']
  mothers_dict = biglist[1]['mother']
  spouses_dict = biglist[2]['spouse']
  notes_dict = biglist[2]['notes']

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


def toml_to_family(toml_filename, style):
  family = Family()

  try:
    big_dict = toml.load(toml_filename)
  except toml.decoder.TomlDecodeError as e:
    print(f"\033[0;31m{toml_filename} is not a well-formed toml file.")
    print("  Maybe some names have special characters in them?\033[0m")
    raise e

  # TODO Do this with defaultdict somehow not too verbosely
  people  = big_dict['people'] if 'people' in big_dict else []

  father_uids = []
  if 'father' in big_dict:
    father_uids = [
      father_tuple[0]
      for father_tuple in big_dict['father']
    ]

  mother_uids = []
  if 'mother' in big_dict:
    mother_uids = [
      mother_tuple[0]
      for mother_tuple in big_dict['mother']
    ]

  spouse_uids = []
  if 'spouse' in big_dict:
    spouse_uids = [
      spouse_tuple[0]
      for spouse_tuple in big_dict['spouse']
    ]

  for person in people:
    if "uid" not in person:
      print("Warning: Person with no uid will not be included:")
      print(person)
      print("Every person needs a unique integer associated to them")
      continue

    if person["uid"] in family.uids():
      print("Warning: Next person with uid {person['uid']} will not")
      print("be included.  uids should be unique integers")
      print(person)
      continue

    family.add_person(Person.from_dict(person))

  for father_uid in father_uids:
    try:
      father = family.uid_to_person(father_uid)
    except TypeError as e:
      print(f"Warning: Nobody has uid {uid}, so he can't be anyone's")
      print("father.  Skipping.")
      continue
    children = [
      family.uid_to_person(relation[1])
      for relation in big_dict['father']
      if relation[0] == father_uid
    ]
    family.add_children(father, children)

  for mother_uid in mother_uids:
    try:
      mother = family.uid_to_person(mother_uid)
    except TypeError as e:
      print(f"Warning: Nobody has uid {uid}, so she can't be anyone's")
      print("mother.  Skipping.")
      continue
    children = [
      family.uid_to_person(relation[1])
      for relation in big_dict['mother']
      if relation[0] == mother_uid
    ]
    family.add_children(mother, children)

  for spouse_uid in spouse_uids:
    try:
      spouse = family.uid_to_person(spouse_uid)
    except TypeError as e:
      print(f"Warning: Nobody has uid {uid}, so they can't be anyone's")
      print("spouse.  Skipping.")
      continue
    spouses = [
      family.uid_to_person(relation[1])
      for relation in big_dict['spouse']
      if relation[0] == spouse_uid
    ]
    family.add_spouses(spouse, spouses)

  return family


def family_to_yaml(family):
  people_part = [
    {person.name: person.gender}
    for person in family.persons()
  ]
  fathers = family.fathers()
  mothers = family.mothers()
  spouses = family.spouses()
  notes = family.notes
  fathers_part = {}
  for father in fathers:
    kids = []
    for child in family.children(father):
      kids.append(child.name)
    fathers_part[father.name] = kids
  mothers_part = {}
  for mother in mothers:
    kids = []
    for child in family.children(mother):
      kids.append(child.name)
    mothers_part[mother.name] = kids
  spouses_part = {}
  for spouse in spouses:
    sub_spouses = []
    for sub_spouse in family.all_spouses(spouse):
      sub_spouses.append(sub_spouse.name)
    spouses_part[spouse.name] = sub_spouses
  notes_part = {}
  for person in notes:
    notes_part[person.name] = notes[person]
  return yaml.dump_all([
    {'people': people_part},
    {'father': fathers_part},
    {'mother': mothers_part},
    {'spouse': spouses_part},
    {'notes': notes_part},
  ])

def create_example_toml(filename):
  example_toml = """
father = [[2, 7], [2, 16], [7, 9], [9, 11], [12, 15], [4, 3], [3, 13], [3, 6]]

mother = [[5, 3], [10, 15], [1, 7], [1, 16], [15, 11], [11, 6], [11, 13], [8, 9]]

spouse = [[9, 14]]

[[people]]
surname = ""
given_names = ["???"]
gender = "f"
uid = 1

[[people]]
surname = ""
given_names = ["???"]
gender = "m"
uid = 2

[[people]]
surname = "Rubble"
given_names = ["Bamm-Bamm"]
gender = "m"
uid = 3

[[people]]
given_names = ["Barney"]
surname = "Rubble"
gender = "m"
uid = 4

[[people]]
given_names = ["Betty", "Jean"]
surname = "McBricker"
gender = "f"
uid = 5

[[people]]
given_names = ["Chip"]
surname = "Rubble"
gender = "m"
uid = 6

[[people]]
given_names = ["Ed"]
surname = "Flintstone"
gender = "m"
uid = 7

[[people]]
given_names = ["Edna", "Hardrock"]
surname = "Flintstone"
gender = "f"
uid = 8

[[people]]
given_names = ["Frederick", "Joseph"]
nickname = "Fred"
surname = "Flintstone"
gender = "m"
uid = 9

[[people]]
given_names = ["Pearl", "Pebble"]
surname = "Slaghoople"
gender = "f"
uid = 10

[[people]]
given_names = ["Pebbles"]
surname = "Flintstone"
gender = "f"
uid = 11

[[people]]
given_names = ["Ricky"]
surname = "Slaghoople"
gender = "m"
uid = 12

[[people]]
given_names = ["Roxy"]
surname = "Rubble"
gender = "f"
uid = 13

[[people]]
given_names = ["Secret"]
surname = "Ex-Wife"
gender = "f"
uid = 14
notes = ["Gossip", "More gossip"]

[[people]]
given_names = ["Wilma", "Pebbles"]
surname = "Slaghoople"
gender = "f"
uid = 15

[[people]]
given_names = ["Zeke"]
surname = "Flintstone"
gender = "m"
uid = 16
  """
  with open(filename, 'w') as toml_file:
    toml_file.write(example_toml)


def biglist_to_family(biglist):
  """
  Take `biglist` as would be returned from a .yaml file
  and return corresponding Family instance
  """
  return Family(*split_biglist(biglist))


def d3_html_page_generator(family, style):
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
  family = {"""
  yield '  "father": {'
  for father in family.fathers():
    yield '"{}": ['.format(father.display_string(style))
    for child in family.children(father):
      yield '"{}",\n'.format(child.display_string(style))
    yield '],\n'
  yield '},\n'
  yield '"mother": {\n'
  for mother in family.mothers():
    yield '"{}": [\n'.format(mother.display_string(style))
    for child in family.children(mother):
      yield '"{}",\n'.format(child.display_string(style))
    yield '],\n'
  yield '},\n'
  yield '"spouse": {\n'
  for prime_spouse in family.spouses():
    yield '"{}": [\n'.format(prime_spouse.display_string(style))
    for spouse in family.all_spouses(prime_spouse):
      yield '"{}",\n'.format(spouse.display_string(style))
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

def show_temp_floating_chart(family):
  """
  Create a floating chart in a temporary file and open it in the browser.
  """

  # Create a temporary file
  html_file_descriptor, html_filename = tempfile.mkstemp()

  # Put html of the floating chart in it
  html_file = os.fdopen(html_file_descriptor, 'w')
  for line in d3_html_page_generator(family):
    html_file.write(line)
  html_file.close()

  # Open it in a browser
  webbrowser.open('file:{}'.format(pathname2url(html_filename)))

  # Don't delete it since the user may want to examine it.

def show_temp_rigid_chart(family, first_names_only=False):
  """
  Create a rigid chart in a temporary file and open it in the browser.
  """
  # Create a temporary directory
  temp_dir = tempfile.mkdtemp()

  # Put a .dot file there
  dot_filename = os.path.join(temp_dir, "family_tree.dot")
  with open(dot_filename, 'w') as dot_file:
    for line in dot_file_generator(family, first_names_only):
      dot_file.write(line + "\n")

  # Generate .svg from .dot file
  svg_filename = os.path.join(temp_dir, "family_tree.svg")
  with open(svg_filename, 'w') as svg_file:
    process = subprocess.Popen(['dot', '-Tsvg', dot_filename],
        stdout=svg_file)

    # Wait until it's done writing out
    process.wait()

  # Open it in a browser
  webbrowser.open('file:{}'.format(pathname2url(svg_filename)))

  # Don't delete it since the user may want to examine it.

def dot_file_generator(family, first_names_only=False):
  """Generate a graphviz .dot file"""

  yield "digraph family_tree {"

  # Set up the nodes
  for person in family.persons():
    uid = person.uid
    name = str(person)
    if first_names_only:
      name = person.first_name()
    yield '  "{}" [label="{}", shape="box"];'.format(
        uid, name)

  # Set up the connections
  for father in family.fathers():
    for child in family.children(father):
      yield '  "{}" -> "{}" [color=blue];'.format(
          father.uid, 
          child.uid)
  for mother in family.mothers():
    for child in family.children(mother):
      yield '  "{}" -> "{}" [color=orange];'.format(
          mother.uid,
          child.uid)
  for prime_spouse in family.spouses():
    for spouse in family.all_spouses(prime_spouse):
      yield '  "{}" -> "{}" [style="dotted"];'.format(
          prime_spouse.uid,
          spouse.uid)
  yield "}"

def interact(yaml_filename):
  with open(yaml_filename) as yaml_file:
    family = yaml_to_family(yaml_file)
  titlebar = "Editing {0}".format(yaml_filename)
  quit_yet = False
  while not quit_yet:
    new_relations = {
      "b.  Add a new person as a full sibling":
        ["full sibling", family.add_full_sibling, None],
      "c.  Add a new person as a father":
        ["father", family.add_father, "male"],
      "d.  Add a new person as a mother":
        ["mother", family.add_mother, "female"],
      "e.  Add a new person as a child":
        ["child", family.add_child, None],
    }
    existing_relations = {
      "f.  Add an existing person as a full sibling":
        ["full_sibling", family.add_full_sibling],
      "g.  Add an existing person as a father":
        ["father", family.add_father],
      "h.  Add an existing person as a mother":
        ["mother", family.add_mother],
      "i.  Add an existing person as a child":
        ["child", family.add_child],
    }
    next_move = easygui.choicebox("What would you like to do?",
        titlebar,
        [
        "a. Add a new person",
        ] + \
        list(existing_relations.keys()) + list(new_relations.keys()) + \
        [
        "j. Add new people as children of a couple",
        "k. Add a pair of spouses",
        "l. See a floating chart in the browser",
        "m. See a rigid chart in the browser",
        "n. Change an existing person's name",
        "o. See a rigid chart in the browser (first names only)",
        "p. Add a note to a person",
        "q. Quit",
        "r. See notes about a person",
        "s. Delete a note from a person",
        ]
    )
    change_made = False
    if not next_move:
      quit_yet = True
    if next_move in existing_relations:
      relationship = existing_relations[next_move][0]
      add_function = existing_relations[next_move][1]
      person = family.gui_choose_person("To whom?", titlebar)
      if person:
        rel = family.gui_choose_person(
            "Who is the {}?".format(relationship), titlebar)
        if rel:
          add_function(person, rel)
          change_made = True
    if next_move in new_relations:
      relationship = new_relations[next_move][0]
      add_function = new_relations[next_move][1]
      gender = new_relations[next_move][2]
      person = family.gui_choose_person("To whom?", titlebar)
      if person:
        rel = family.gui_add_person(
            "Who is the new {}?".format(relationship), titlebar,
            gender)
        if rel:
          add_function(person, rel)
          change_made = True
    if next_move == "j. Add new people as children of a couple":
      couple = family.gui_choose_couple_or_add("Choose a couple",
          titlebar)

      # Loop over and over adding kids until the user presses Cancel
      kid = "Fake thing that's just not None"
      while kid:
        kid = family.gui_add_person("Child's name? (Press Cancel to stop)", titlebar)
        if kid:
          family.add_child(couple[0], kid)
          family.add_child(couple[1], kid)
          change_made = True
    if next_move == "n. Change an existing person's name":
      person = family.gui_choose_person("Whom?", titlebar)
      if person:
        new_name = easygui.enterbox(
            "Enter {}'s new name".format(person.name, titlebar))
        if new_name:
            family.change_name(person, new_name)
        change_made = True
    if next_move == "p. Add a note to a person":
      person = family.gui_choose_person("To whom?", titlebar)
      if person:
        new_note = easygui.enterbox(
            "Enter anything about {}".format(person.name))
        if new_note:
            family.add_note(person, new_note)
            change_made = True
    if next_move == "s. Delete a note from a person":
      people = family.people_with_notes()
      person = None
      if len(people) == 0:
        easygui.textbox(titlebar, "", "Nobody has any notes yet.")
      elif len(people) == 1:
        person = people[0] 
      else:
        person = family.gui_choose_person("Whom?", titlebar, people)
      if person:
        to_be_deleted = family.gui_choose_note(person, titlebar)
        if to_be_deleted:
          family.delete_note(person, to_be_deleted)
          change_made = True
    if next_move == "r. See notes about a person":
      people = family.people_with_notes()
      person = None
      if len(people) == 0:
        easygui.textbox(titlebar, "", "Nobody has any notes yet.")
      elif len(people) == 1:
        person = people[0] 
      else:
        person = family.gui_choose_person("Whom?", titlebar, people)
      if person:
        family.gui_display_notes(person)
    if next_move == "k. Add a pair of spouses":
      person_1 = family.gui_choose_person_or_add("First person?",
          titlebar)
      if person_1:
        person_2 = family.gui_choose_person_or_add(
            "Second person?", titlebar)
        if person_2:
          family.add_spouse(person_1, person_2)
          family.add_spouse(person_2, person_1)
          change_made = True
    if next_move == "a. Add a new person":
      person = family.gui_add_person("New person's name?", titlebar)
      if person:
        change_made = True
    wait_num_seconds = 2
    popup_string = "\n\033[91mNew menu in {} seconds\033[0m".format(
        wait_num_seconds)
    if next_move == "l. See a floating chart in the browser":
      print(popup_string)
      show_temp_floating_chart(family)
      time.sleep(wait_num_seconds)
    if next_move == "m. See a rigid chart in the browser":
      print(popup_string)
      show_temp_rigid_chart(family)
      time.sleep(wait_num_seconds)
    if next_move == "o. See a rigid chart in the browser (first names only)":
      print(popup_string)
      show_temp_rigid_chart(family, first_names_only=True)
      time.sleep(wait_num_seconds)
    if next_move == "q. Quit":
      quit_yet = True
    if change_made:
      if easygui.ynbox("Save changes?", titlebar):
        with open(yaml_filename, 'w') as yaml_file:
          yaml_file.write(family_to_yaml(family))


def cleanup_files(yaml_filename, base_filename):
  for extension in 'svg', 'dot', 'html':
    os.remove('{}.{}'.format(base_filename, extension))


def generate_files(toml_filename, file_basename, style):

  # Open the toml file or fail gracefully
  try:
    family = toml_to_family(toml_filename, style)
  except IOError as e:
    print(f"\n\033[91mCouldn't open {toml_filename}\033[0m\n")
    exit(1)

  # Generate d3 html page
  with open('{}.html'.format(file_basename), 'w') as f:
    for line in d3_html_page_generator(family, style):
      f.write(line)

  # # Generate graphviz .dot file
  # with open('{}.dot'.format(file_basename), 'w') as f:
  #   for line in dot_file_generator(family):
  #     f.write(line + "\n")

  # # Generate .svg from .dot file
  # with open('{}.svg'.format(file_basename), 'w') as svg_file:
  #   try:
  #     subprocess.Popen(['dot', '-Tsvg', '{}.dot'.format(file_basename)],
  #         stdout=svg_file)
  #   except FileNotFoundError as e:
  #     print("'dot' executable not available.  You need to install 'graphviz'")
  #     print("from your package manager.")

