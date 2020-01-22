import csv
import json
import os

def load_repositories():
    repositories = []
    with open(os.path.join('data','repositories.csv'), 'r') as infile:
        reader = csv.reader(infile)
        next(reader, None)
        
        for row in reader:
            repositories.append('{}/{}'.format(row[0], row[1]))

    return repositories


def save_json(fixing_commits, filename: str):
    with open(os.path.join('data', filename), 'w') as outfile:
        return json.dump(fixing_commits, outfile)