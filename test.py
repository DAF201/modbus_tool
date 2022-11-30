import json

a = {'a': 0}

with open('test.json', 'w')as test:
    json.dump(a, test)
