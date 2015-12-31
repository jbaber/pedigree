import pedigree_lib
import pytest

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

def test_split_biglist(fathers, mothers, spouses, name_to_uid,
    person_names, biglist):
  assert(
      pedigree_lib.split_biglist(biglist) == \
      (fathers, mothers, spouses, name_to_uid, person_names)
  )

def test_join_biglist(fathers, mothers, spouses, biglist):
  assert(
      pedigree_lib.join_biglist(fathers, mothers, spouses) == \
      biglist
  )

def test_d3_html_page_generator(fathers, mothers, spouses):
  with open('examples/example2.html') as f:
    assert(
      "".join(pedigree_lib.d3_html_page_generator(fathers, mothers, spouses)) == f.read()
    )

def test_dot_file_generator(fathers, mothers, spouses,
    person_names):
  received = "".join(pedigree_lib.dot_file_generator(fathers,
      mothers, spouses, person_names))

  with open('examples/example2.dot') as f:
    expected = f.read()

  assert(received == expected)
