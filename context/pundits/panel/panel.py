import csv
import json

panel = {}

with open('panel.csv', 'rw') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pundit = {}
        pundit['name'] = row['Name']
        pundit['links'] = {}
        pundit['links']['twitter'] = row['Twitter']
        pundit['links']['cfr'] = row['CFR']

        for keyword in row['Area'].split(','):
            keyword = keyword.strip()

            if not panel.has_key(keyword):
                panel[keyword] = []

            panel[keyword].append(pundit)

with open('panel.json', 'w') as outfile:
    json.dump(panel, outfile)
