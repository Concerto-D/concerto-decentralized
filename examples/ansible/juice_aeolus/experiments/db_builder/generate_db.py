#!/usr/bin/python3

import sys

def generate_db(nb_entries):
    with open('start.sqlp') as f: 
        for line in f:
            print(line, end='')

    with open('data.sqlp') as f: 
        for line in f:
            line = line.strip()
            if nb_entries is 0:
                break
            if not line.startswith("INSERT"):
                nb_entries-=1
            if nb_entries is 0:
                if line[-1] is ',':
                    line = line[:-1] + ';'
            print(line, end='\n')

if len(sys.argv) < 2:
    print("Error: requires 1 argument, the number of entries.", file=sys.stderr)
    exit(1)
    
nb_entries = int(sys.argv[1])
if (nb_entries < 1 or nb_entries > 1000000):
    print("Error: wrong number of entries (must be between 1 and < 1000000).", file=sys.stderr)
    exit(1)

generate_db(nb_entries)
