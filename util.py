#!/usr/bin/env python

import csv

def read_csv(fname, unpack=True):
    with open(fname, 'rb') as f:
        reader = csv.reader(f)
        data = [[int(d) for d in row] for row in reader
                if len(row) != 1]
    if unpack:
        return zip(*data)
    else:
        return data

