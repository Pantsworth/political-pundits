import csv
import json


def open_panel():
    panel = {}
    with open('panel.csv', 'rw') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pundit = {}
            pundit['name'] = row['Name']
            pundit['title'] = row['Title']
            pundit['links'] = {}
            pundit['links']['twitter'] = row['Twitter']
            pundit['links']['cfr'] = row['CFR']

            for keyword in row['Area'].split(','):
                keyword = keyword.strip()
                keyword = keyword.lower()

                if not panel.has_key(keyword):
                    panel[keyword] = []
                panel[keyword].append(pundit)
    return panel


def dump_panel():
    with open('panel.json', 'w') as outfile:
        json.dump(panel, outfile)


if __name__ == '__main__':
    panel = open_panel()
    print panel
