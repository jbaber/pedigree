import pedigree_lib
import pytest

"""
fathers: a -> b, c    d -> e
mothers: i -> j       f -> g, h
spouses: k -> l, m    n -> o
"""

@pytest.fixture
def fathers():
  return [
    {'name': 'a', 'children': ['b', 'c']},
    {'name': 'd', 'children': ['e']},
  ]
@pytest.fixture
def mothers():
  return [
    {'name': 'i', 'children': ['j']},
    {'name': 'f', 'children': ['g', 'h']},
]
@pytest.fixture
def spouses():
  return [
    {'name': 'k', 'spouses': ['l', 'm']},
    {'name': 'n', 'spouses': ['o']},
  ]
@pytest.fixture
def name_to_uid():
  return {'a': 'personhash0cc175b9c0f1b6a831c399e269772661',
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
    }
@pytest.fixture
def person_names():
  return set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
      'k', 'l', 'm', 'n', 'o'])
@pytest.fixture
def biglist():
  return [
    {'father': {'a': ['b', 'c'], 'd': ['e']}},
    {'mother': {'f': ['g', 'h'], 'i': ['j']}},
    {'spouse': {'k': ['l', 'm'], 'n': ['o']}},
  ]
@pytest.fixture
def family(fathers, mothers, spouses):
  return pedigree_lib.Family(fathers, mothers, spouses)

def test_family(fathers, mothers, spouses, name_to_uid,
    person_names):
  f = pedigree_lib.Family(fathers, mothers, spouses)
  assert(f.fathers == fathers)
  assert(f.mothers == mothers)
  assert(f.spouses == spouses)
  received_names = f.person_names
  assert(received_names == person_names)
  for name in received_names:
    assert(f.name_to_uid(name) == name_to_uid[name])

def test_family_add_father(family, mothers, spouses):
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father('b', 'boo')
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father('c', 'boo')
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father('e', 'boo')
  with pytest.raises(pedigree_lib.GenealogicalError):
    family.add_father('i', 'i')
  family.add_father('a', 'boo')
  assert(family.fathers == [
    {'name': 'a', 'children': ['b', 'c']},
    {'name': 'd', 'children': ['e']},
    {'name': 'boo', 'children': ['a']}
  ])
  assert(family.person_names == set(['a', 'b', 'c', 'd', 'e',
      'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'boo']))
  assert(family.mothers == mothers)
  assert(family.spouses == spouses)
  family.add_father('j', 'a')
  assert(family.fathers == [
    {'name': 'a', 'children': ['b', 'c', 'j']},
    {'name': 'd', 'children': ['e']},
    {'name': 'boo', 'children': ['a']}
  ])
  assert(family.mothers == mothers)
  assert(family.spouses == spouses)
  assert(family.person_names == set(['a', 'b', 'c', 'd', 'e',
      'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'boo']))


def test_family_father(fathers, mothers, spouses):
  f = pedigree_lib.Family(fathers, mothers, spouses)

  assert(f.father('a') == None)
  assert(f.father('b') == 'a')
  assert(f.father('c') == 'a')
  assert(f.father('d') == None)
  assert(f.father('e') == 'd')
  assert(f.father('f') == None)
  assert(f.father('g') == None)
  assert(f.father('h') == None)
  assert(f.father('i') == None)
  assert(f.father('j') == None)


def test_family_mother(fathers, mothers, spouses):
  f = pedigree_lib.Family(fathers, mothers, spouses)

  assert(f.mother('a') == None)
  assert(f.mother('b') == None)
  assert(f.mother('c') == None)
  assert(f.mother('d') == None)
  assert(f.mother('e') == None)
  assert(f.mother('f') == None)
  assert(f.mother('g') == 'f')
  assert(f.mother('h') == 'f')
  assert(f.mother('i') == None)
  assert(f.mother('j') == 'i')


def test_new_anonymous_name(family):
  assert(family.new_anonymous_name() == '?')
  assert(family.new_anonymous_name() == '?')
  assert(family.new_anonymous_name() == '?')
  family.person_names.add('?')
  assert(family.new_anonymous_name() == '??')
  assert(family.new_anonymous_name() == '??')
  family.person_names.add('??????')
  assert(family.new_anonymous_name() == '???????')
  assert(family.new_anonymous_name() == '???????')


def test_split_biglist(fathers, mothers, spouses, name_to_uid,
    person_names, biglist):
  assert(
      pedigree_lib.split_biglist(biglist) == \
      (fathers, mothers, spouses)
  )

def test_join_biglist(fathers, mothers, spouses, biglist):
  assert(
      pedigree_lib.join_biglist(fathers, mothers, spouses) == \
      biglist
  )

def test_d3_html_page_generator(fathers, mothers, spouses):
  with open('examples/example2.html') as f:
    assert(
      "".join(pedigree_lib.d3_html_page_generator(
          pedigree_lib.Family(fathers, mothers, spouses))) == \
      f.read()
    )

def test_dot_file_generator(fathers, mothers, spouses,
    person_names):
  received = "".join(pedigree_lib.dot_file_generator(
      pedigree_lib.Family(fathers, mothers, spouses)))

  with open('examples/example2.dot') as f:
    expected = f.read()

  assert(received == expected)
