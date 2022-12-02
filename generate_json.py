import json
a = {}
for x in range(40000, 40400):
    a[str(x)] = '0000'

with open('db.json', 'w')as test:
    json.dump(a, test)
