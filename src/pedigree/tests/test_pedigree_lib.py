from pedigree import pedigree_lib
import pytest
import networkx as nx
import copy
import sys
import os

@pytest.fixture
def example_yaml_path():
  return os.path.join(sys.prefix, 'examples/example.yaml')
@pytest.fixture
def example2_yaml_path():
  return os.path.join(sys.prefix, 'examples/example2.yaml')
@pytest.fixture
def example_html_path():
  return os.path.join(sys.prefix, 'examples/example.html')
@pytest.fixture
def example2_html_path():
  return os.path.join(sys.prefix, 'examples/example2.html')
@pytest.fixture
def example2_dot_path():
  return os.path.join(sys.prefix, 'examples/example2.dot')

@pytest.fixture
def persons_dict():
  to_return = {}
  to_return['a'] = pedigree_lib.Person(name='a', gender="male")
  to_return['b'] = pedigree_lib.Person(name='b', gender="female")
  to_return['c'] = pedigree_lib.Person(name='c', gender="female")
  to_return['d'] = pedigree_lib.Person(name='d', gender="male")
  to_return['e'] = pedigree_lib.Person(name='e', gender="female")
  to_return['f'] = pedigree_lib.Person(name='f', gender="female")
  to_return['g'] = pedigree_lib.Person(name='g', gender="female")
  to_return['h'] = pedigree_lib.Person(name='h', gender="female")
  to_return['i'] = pedigree_lib.Person(name='i', gender="female")
  to_return['j'] = pedigree_lib.Person(name='j', gender="female")
  to_return['k'] = pedigree_lib.Person(name='k', gender="male")
  to_return['l'] = pedigree_lib.Person(name='l', gender="male")
  to_return['m'] = pedigree_lib.Person(name='m', gender="female")
  to_return['n'] = pedigree_lib.Person(name='n', gender="female")
  to_return['o'] = pedigree_lib.Person(name='o', gender="male")
  return to_return

@pytest.fixture
def persons(persons_dict):
  return persons_dict.values()

@pytest.fixture
def p():
  p = pedigree_lib.Person(name='p', gender='female')

@pytest.fixture
def family(persons_dict):
  """
  fathers: a -> b, c     d -> e, k
  mothers: i -> j, c     f -> g, h
  spouses: k <-> l, m    n <-> o
  NB l and m aren't spouses
  """
  to_return = pedigree_lib.Family()
  to_return.add_children(persons_dict['a'],
      [persons_dict['b'], persons_dict['c']])
  to_return.add_child(persons_dict['d'], persons_dict['e'])
  to_return.add_child(persons_dict['d'], persons_dict['k'])
  to_return.add_child(persons_dict['i'], persons_dict['j'])
  to_return.add_child(persons_dict['i'], persons_dict['c'])
  to_return.add_children(persons_dict['f'], [persons_dict['g'],
      persons_dict['h']])
  to_return.add_spouses(persons_dict['k'], [persons_dict['l'],
      persons_dict['m']])
  to_return.add_spouse(persons_dict['l'], persons_dict['k'])
  to_return.add_spouse(persons_dict['m'], persons_dict['k'])
  to_return.add_spouse(persons_dict['n'], persons_dict['o'])
  to_return.add_spouse(persons_dict['o'], persons_dict['n'])
  to_return.notes[persons_dict['a']] = ["This guy is named a"]
  to_return.notes[persons_dict['d']] = ["This guy is named d"]
  return to_return

@pytest.fixture
def fathers(persons_dict):
  return [persons_dict['a'], persons_dict['d']]
@pytest.fixture
def mothers(persons_dict):
  return [persons_dict['i'], persons_dict['f']]
@pytest.fixture
def spouses(persons_dict):
  return [persons_dict['k'], persons_dict['l'], persons_dict['m'],
      persons_dict['n'], persons_dict['o']]
@pytest.fixture
def couples(persons_dict):
  return [
    sorted([persons_dict['a'], persons_dict['i']]),
    sorted([persons_dict['k'], persons_dict['l']]),
    sorted([persons_dict['k'], persons_dict['m']]),
    sorted([persons_dict['n'], persons_dict['o']]),
  ]

@pytest.fixture
def notes(persons_dict):
  return {persons_dict['a']: ["This guy is named a"],
          persons_dict['d']: ["This guy is named d"],
  }

@pytest.fixture
def name_to_uid():

  return {
     'a': 'r0E',
     'b': 'vgm',
     'c': 'wjR',
     'd': 'g56',
     'e': 'j25',
     'f': 'k5X',
     'g': 'lO6',
     'h': 'mw0',
     'i': 'nZl',
     'j': 'oYK',
     'k': 'pg6',
     'l': 'qjr',
     'm': 'r06',
     'n': 'vgr',
     'o': 'wjw',
    }
@pytest.fixture
def names():
  return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
      'k', 'l', 'm', 'n', 'o']


def test_family(family, fathers, mothers, spouses,
    names, notes):
  assert(family.fathers() == set(fathers))
  assert(family.mothers() == set(mothers))
  assert(family.spouses() == set(spouses))
  assert(family.notes == notes)
  assert(set(family.names()) == set(names))

def test_name_to_uid(names, name_to_uid):
  for name in names:
    assert(pedigree_lib.name_to_uid(name) == name_to_uid[name])

def test_family_children(family, persons_dict):
  assert set(family.children(persons_dict['a'])) == \
      set([persons_dict['b'], persons_dict['c']])
  assert set(family.children(persons_dict['d'])) == \
      set([persons_dict['e'], persons_dict['k']])
  assert set(family.children(persons_dict['i'])) == \
      set([persons_dict['j'], persons_dict['c']])
  assert set(family.children(persons_dict['f'])) == \
      set([persons_dict['g'], persons_dict['h']])
  for name in ['b', 'c', 'e', 'k', 'j', 'c', 'g', 'h', 'k',
      'l', 'm', 'n', 'o']:
    assert family.children(persons_dict[name]) == []

def test_family_add_full_sibling(family, persons, fathers,
    mothers, persons_dict, names):

  # Add one sibling
  p = pedigree_lib.Person(name='p', gender='female')
  family.add_full_sibling(persons_dict['b'], p)

  # Becomes 
  # fathers: a -> b, c, p  d -> e, k
  # mothers: i -> j, c     f -> g, h   ? -> b, p
  # spouses: k <-> l, m    n <-> o
  mom = pedigree_lib.Person(name='?', gender="female")

  assert sorted(family.persons()) == sorted(persons + [p, mom])
  assert set(family.fathers()) == set(fathers)
  assert sorted(family.mothers()) == sorted(mothers + [mom])
  assert set(family.children(persons_dict['a'])) == \
      set([persons_dict['b'], persons_dict['c'], p])
  assert set(family.children(mom)) == set([persons_dict['b'], p])

  # Leaves spouses alone
  family.spouses == spouses

  # Add another sibling
  q = pedigree_lib.Person(name='q', gender="male")
  family.add_full_sibling(persons_dict['j'], q)

  # Becomes 
  # fathers: a -> b, c, p  d -> e, k  ?? -> j, q
  # mothers: i -> j, c, q  f -> g, h   ? -> b, p
  # spouses: k <-> l, m    n <-> o
  dad = pedigree_lib.Person(name='??', gender="male")
  
  # Creates the sibling and a father
  assert sorted(family.persons()) == \
      sorted(persons + [p, q, mom, dad])
  assert sorted(family.fathers()) == sorted(fathers + [dad])
  assert sorted(family.mothers()) == sorted(mothers + [mom])
  assert sorted(family.children(persons_dict['a'])) == \
      sorted([persons_dict['b'], persons_dict['c'], p])
  assert sorted(family.children(persons_dict['i'])) == \
      sorted([persons_dict['j'], persons_dict['c'], q])
  assert sorted(family.children(mom)) == sorted([persons_dict['b'], p])
  assert sorted(family.children(dad)) == sorted([persons_dict['j'], q])

  # Add a full sibling to an existing nuclear family
  r = pedigree_lib.Person(name='r', gender='female')
  family.add_full_sibling(persons_dict['c'], r)

  # Becomes 
  # fathers: a -> b, c, p, r  d -> e, k  ?? -> j, q
  # mothers: i -> j, c, q, r  f -> g, h   ? -> b, p
  # spouses: k <-> l, m       n <-> o
  assert sorted(family.persons()) == \
      sorted(persons + [p, q, r, mom, dad])
  assert sorted(family.fathers()) == sorted(fathers + [dad])
  assert sorted(family.mothers()) == sorted(mothers + [mom])
  assert sorted(family.children(persons_dict['a'])) == \
      sorted([persons_dict['b'], persons_dict['c'], p, r])
  assert sorted(family.children(persons_dict['i'])) == \
      sorted([persons_dict['j'], persons_dict['c'], q, r])
  assert sorted(family.children(mom)) == sorted([persons_dict['b'], p])
  assert sorted(family.children(dad)) == sorted([persons_dict['j'], q])

def test_family_add_father(family, fathers, mothers, persons,
    spouses, persons_dict):
  boo = pedigree_lib.Person(name='boo', gender='male')
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father(persons_dict['b'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father(persons_dict['c'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father(persons_dict['e'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father(persons_dict['i'], persons_dict['i'])

  family.add_father(persons_dict['a'], boo)
  # Becomes 
  # fathers: a -> b, c     d -> e, k    boo -> a
  # mothers: i -> j, c     f -> g, h
  # spouses: k <-> l, m    n <-> o
  assert set(family.fathers()) == set(fathers + [boo])
  assert set(family.persons()) == set(persons + [boo])
  assert set(family.mothers()) == set(mothers)
  assert set(family.spouses()) == set(spouses)

  family.add_father(persons_dict['j'], persons_dict['a'])
  # Becomes 
  # fathers: a -> b, c, j  d -> e, k    boo -> a
  # mothers: i -> j, c     f -> g, h
  # spouses: k <-> l, m    n <-> o
  assert set(family.fathers()) == set(fathers + [boo])
  assert set(family.persons()) == set(persons + [boo])
  assert set(family.mothers()) == set(mothers)
  assert set(family.spouses()) == set(spouses)
  assert set(family.children(persons_dict['a'])) == \
      set([persons_dict['b'], persons_dict['c'], persons_dict['j']])
  assert set(family.children(persons_dict['i'])) == \
      set([persons_dict['c'], persons_dict['j']])

def test_family_add_mother(family, fathers, mothers, spouses,
    persons_dict, persons):
  boo = pedigree_lib.Person(name='boo', gender='female')
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_mother(persons_dict['g'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_mother(persons_dict['h'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_mother(persons_dict['j'], boo)
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_mother(persons_dict['a'], persons_dict['a'])

  family.add_mother(persons_dict['f'], boo)
  # Becomes
  # fathers: a -> b, c     d -> e, k
  # mothers: i -> j, c     f -> g, h  boo -> f
  # spouses: k <-> l, m    n <-> o
  assert set(family.mothers()) == set(mothers + [boo])
  assert set(family.persons()) == set(persons + [boo])
  assert set(family.fathers()) == set(fathers)
  assert set(family.spouses()) == set(spouses)

  family.add_mother(persons_dict['e'], persons_dict['i'])
  # Becomes
  # fathers: a -> b, c      d -> e, k
  # mothers: i -> j, c, e   f -> g, h  boo -> f
  # spouses: k <-> l, m     n <-> o
  assert set(family.mothers()) == set(mothers + [boo])
  assert set(family.persons()) == set(persons + [boo])
  assert set(family.fathers()) == set(fathers)
  assert set(family.spouses()) == set(spouses)
  assert set(family.children(persons_dict['i'])) == \
      set([persons_dict['j'], persons_dict['c'], persons_dict['e']])
  assert set(family.children(persons_dict['d'])) == \
      set([persons_dict['e'], persons_dict['k']])


def test_family_add_child(family, persons, persons_dict,
    fathers, mothers, p):
  # p = pedigree_lib.Person(name='p', gender='female')
  family.add_child(persons_dict['a'], p)
  # Becomes
  # fathers: a -> b, c, p  d -> e, k
  # mothers: i -> j, c     f -> g, h
  # spouses: k <-> l, m    n <-> o
  assert set(family.persons()) == set(persons + [p])
  assert set(family.fathers()) == set(fathers)
  assert set(family.mothers()) == set(mothers)
  assert set(family.children(persons_dict['a'])) == \
      set([persons_dict['b'], persons_dict['c'], p])


def test_family_father(family, persons, persons_dict):
  assert family.father(persons_dict['a']) == None
  assert family.father(persons_dict['b']) == persons_dict['a']
  assert family.father(persons_dict['c']) == persons_dict['a']
  assert family.father(persons_dict['d']) == None
  assert family.father(persons_dict['e']) == persons_dict['d']
  assert family.father(persons_dict['f']) == None
  assert family.father(persons_dict['g']) == None
  assert family.father(persons_dict['h']) == None
  assert family.father(persons_dict['i']) == None
  assert family.father(persons_dict['j']) == None


def test_family_mother(family, persons, persons_dict):
  assert family.mother(persons_dict['a']) == None
  assert family.mother(persons_dict['b']) == None
  assert family.mother(persons_dict['c']) == persons_dict['i']
  assert family.mother(persons_dict['d']) == None
  assert family.mother(persons_dict['e']) == None
  assert family.mother(persons_dict['f']) == None
  assert family.mother(persons_dict['g']) == persons_dict['f']
  assert family.mother(persons_dict['h']) == persons_dict['f']
  assert family.mother(persons_dict['i']) == None
  assert family.mother(persons_dict['j']) == persons_dict['i']


def test_family_couples(family, persons_dict, couples):
  assert sorted(family.couples()) == sorted(couples)


def test_family_all_spouses(family, persons, persons_dict):
  assert family.all_spouses(persons_dict['a']) == []
  assert family.all_spouses(persons_dict['b']) == []
  assert family.all_spouses(persons_dict['c']) == []
  assert family.all_spouses(persons_dict['d']) == []
  assert family.all_spouses(persons_dict['e']) == []
  assert family.all_spouses(persons_dict['f']) == []
  assert family.all_spouses(persons_dict['g']) == []
  assert family.all_spouses(persons_dict['h']) == []
  assert family.all_spouses(persons_dict['i']) == []
  assert family.all_spouses(persons_dict['j']) == []
  assert set(family.all_spouses(persons_dict['k'])) == set([
      persons_dict['l'], persons_dict['m']])
  assert family.all_spouses(persons_dict['l']) == \
      [persons_dict['k']]
  assert family.all_spouses(persons_dict['m']) == \
      [persons_dict['k']]
  assert family.all_spouses(persons_dict['n']) == \
      [persons_dict['o']]
  assert family.all_spouses(persons_dict['o']) == \
      [persons_dict['n']]

def test_family_change_name(family, persons_dict, names):
  # Change person b's name to boo
  newly_named = pedigree_lib.Person(name='boo', gender='female')
  new_names = list(names)
  new_names[2] = 'boo'
  new_family = pedigree_lib.Family()
  new_family.add_children(persons_dict['a'],
      [persons_dict['b'], newly_named])
  new_family.add_child(persons_dict['d'], persons_dict['e'])
  new_family.add_child(persons_dict['d'], persons_dict['k'])
  new_family.add_child(persons_dict['i'], persons_dict['j'])
  new_family.add_child(persons_dict['i'], newly_named)
  new_family.add_children(persons_dict['f'], [persons_dict['g'],
      persons_dict['h']])
  new_family.add_spouses(persons_dict['k'], [persons_dict['l'],
      persons_dict['m']])
  new_family.add_spouse(persons_dict['l'], persons_dict['k'])
  new_family.add_spouse(persons_dict['m'], persons_dict['k'])
  new_family.add_spouse(persons_dict['n'], persons_dict['o'])
  new_family.add_spouse(persons_dict['o'], persons_dict['n'])
  new_family.notes[persons_dict['a']] = ["This guy is named a"]
  new_family.notes[persons_dict['d']] = ["This guy is named d"]

  assert family != new_family
  assert family.names() != new_names

  family.change_name(persons_dict['c'], 'boo')

  assert family == new_family
  assert set(family.names()) == set(new_names)


def test_family_name_to_person(family, persons_dict, names):
  for name in names:
    assert family.name_to_person(name) == persons_dict[name]

def test_family_string_to_couple(family, persons_dict):
  assert family.string_to_couple("a and b") == \
      (persons_dict['a'], persons_dict['b'])
  assert family.string_to_couple("o and f") == \
      (persons_dict['o'], persons_dict['f'])

def test_new_anonymous_name(family):
  assert(family.new_anonymous_name() == '?')
  assert(family.new_anonymous_name() == '?')
  assert(family.new_anonymous_name() == '?')
  p = pedigree_lib.Person(name='?', gender='female')
  family.add_person(p)
  assert(family.new_anonymous_name() == '??')
  assert(family.new_anonymous_name() == '??')
  q = pedigree_lib.Person(name='??????', gender='female')
  family.add_person(q)
  assert(family.new_anonymous_name() == '???????')
  assert(family.new_anonymous_name() == '???????')


def test_yaml_to_family(family, example2_yaml_path):
  with open(example2_yaml_path) as input_file:
    assert pedigree_lib.yaml_to_family(input_file.read()) == \
        family


def test_family_to_yaml(family, example2_yaml_path):
  with open(example2_yaml_path) as output_file:
    right_side = output_file.read()
  left_side = pedigree_lib.family_to_yaml(family)
  assert pedigree_lib.yaml_to_family(left_side) == \
      pedigree_lib.yaml_to_family(right_side)

@pytest.mark.xfail()
def test_d3_html_page_generator(example_yaml_path, example_html_path):
  with open(example_yaml_path) as input_file:
    left = "\n".join(pedigree_lib.d3_html_page_generator(
        pedigree_lib.yaml_to_family(input_file)))
    with open(example_html_path) as output_file:
      right = output_file.read()
    assert  left == right

  with open(example2_yaml_path) as input_file:
    with open(example2_html_path) as output_file:
      assert(
        "\n".join(pedigree_lib.d3_html_page_generator(
          pedigree_lib.yaml_to_family(input_file))) == \
              output_file.read()
      )

@pytest.mark.xfail()
def test_dot_file_generator(example2_yaml_path, example2_dot_path):
  with open(example2_yaml_path) as input_file:
    with open(example2_dot_path) as output_file:
      received = "\n".join(pedigree_lib.dot_file_generator(
          pedigree_lib.yaml_to_family(input_file))) + "\n"
      assert(received == output_file.read())
