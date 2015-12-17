import hashlib


def uid(name):
  """Give a unique id to any name"""
  return "personhash" + hashlib.md5(name).hexdigest()


"""
Take `biglist` as would be returned from a .yaml file
and return corresponding lists

    (fathers, mothers, spouses, name_to_uid, person_names)

where the dict `name_to_uid` takes each person's name to their uid
and `person_names` is a set containing only the names of people

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
def split_biglist(biglist):
  fathers_dict = biglist[0]['father']
  mothers_dict = biglist[1]['mother']
  spouses_dict = biglist[2]['spouse']

  # Make lists so that index in the lists gives a unique identifier
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
