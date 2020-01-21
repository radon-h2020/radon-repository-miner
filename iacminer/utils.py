import csv
import os

def load_repositories():
    repositories = []
    with open(os.path.join('data','repositories.csv'), 'r') as infile:
        reader = csv.reader(infile)
        next(reader, None)
        
        for row in reader:
            repositories.append('{}/{}'.format(row[0], row[1]))

    return repositories