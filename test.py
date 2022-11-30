import json
a = {}
for x in range(40000, 40200):
    a[str(x)] = '00'

with open('db.json', 'w')as test:
    json.dump(a, test)
